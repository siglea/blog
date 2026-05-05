#!/usr/bin/env python3
"""
ASR 混合调度器 — Groq (云端极速) + whisper.cpp (本地兜底)

调度策略：
  1. 按 Groq 当前小时配额优先分配给 Groq（快 ~100x 实时）
  2. 超出配额的任务分配给 whisper.cpp（慢但无限量）
  3. 持续监测 Groq 配额，恢复后从 whisper.cpp 未开始的队列中接管任务
  4. 不抢占正在跑的 whisper.cpp 任务（避免浪费已有进度）

用法:
    python asr_scheduler.py <音频文件> [--output FILE] [--lang zh] [--chunk-minutes 15]

环境:
    GROQ_API_KEY — ~/.zshrc 中设置
    whisper-cli  — brew install whisper-cpp
    ffmpeg       — brew install ffmpeg
"""

import argparse
import os
import re
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

try:
    from groq import Groq, APIStatusError
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "groq"])
    from groq import Groq, APIStatusError


# ─── 常量 ───────────────────────────────────────────────────
GROQ_QUOTA_PER_HOUR = 7200       # 秒音频/小时 (免费版)
GROQ_MAX_FILE_SIZE  = 25 * 1024 * 1024  # 25MB
WHISPER_MODEL       = os.path.expanduser("~/.cache/whisper/ggml-medium.bin")
WHISPER_THREADS     = 4


# ─── 数据结构 ───────────────────────────────────────────────
class State(Enum):
    PENDING        = "pending"
    GROQ_RUNNING   = "groq_running"
    WHISPER_RUNNING= "whisper_running"
    GROQ_DONE      = "groq_done"
    WHISPER_DONE   = "whisper_done"
    FAILED         = "failed"


@dataclass
class Chunk:
    idx: int
    m4a: str
    wav: str
    duration: float
    state: State = State.PENDING
    result: Optional[str] = None
    elapsed: float = 0.0
    segments: int = 0


# ─── 配额追踪器 (滚动窗口) ─────────────────────────────────
class QuotaTracker:
    """基于滚动窗口追踪 Groq 音频配额"""

    def __init__(self, limit: int = GROQ_QUOTA_PER_HOUR):
        self.limit = limit
        self._log: list[tuple[float, float]] = []  # (timestamp, seconds)
        self._lock = threading.Lock()

    def deduct(self, seconds: float):
        with self._lock:
            self._log.append((time.time(), seconds))

    def remaining(self) -> float:
        with self._lock:
            cutoff = time.time() - 3600
            self._log = [(t, s) for t, s in self._log if t > cutoff]
            used = sum(s for _, s in self._log)
        return max(0.0, self.limit - used)

    def wait_until_available(self, need: float) -> float:
        """返回还需等待多少秒才能凑够 need 秒配额"""
        if self.remaining() >= need:
            return 0.0
        with self._lock:
            if not self._log:
                return 0.0
            deficit = need - self.remaining()
            # 找到释放 deficit 需要等最早的多少条过期
            sorted_log = sorted(self._log, key=lambda x: x[0])
            freed = 0.0
            for t, s in sorted_log:
                freed += s
                if freed >= deficit:
                    return max(0.0, (t + 3600) - time.time())
        return 0.0


# ─── 调度器主体 ─────────────────────────────────────────────
class ASRScheduler:
    def __init__(self, audio: str, output: str = None,
                 chunk_minutes: int = 15, lang: str = "zh"):
        self.audio = os.path.abspath(audio)
        self.output = output or os.path.splitext(self.audio)[0] + ".txt"
        self.chunk_sec = chunk_minutes * 60
        self.lang = lang
        self.chunks: list[Chunk] = []
        self.quota = QuotaTracker()
        self.client: Optional[Groq] = None
        self._stop = threading.Event()
        self._lock = threading.Lock()

    # ── 初始化 ──────────────────────────────────────────────
    def _init_groq(self):
        key = os.environ.get("GROQ_API_KEY")
        if not key:
            r = subprocess.run(
                ["bash", "-c", "source ~/.zshrc 2>/dev/null; echo $GROQ_API_KEY"],
                capture_output=True, text=True)
            key = r.stdout.strip().split("\n")[-1].strip()
        if not key:
            print("❌ GROQ_API_KEY 未设置"); sys.exit(1)
        os.environ["GROQ_API_KEY"] = key
        self.client = Groq()

    def _ff_duration(self, path: str) -> float:
        r = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", path],
            capture_output=True, text=True)
        return float(r.stdout.strip())

    def _load_existing_chunks(self, chunks_dir: str):
        """从已有切片目录加载，跳过切分和 WAV 转换"""
        self.chunks_dir = chunks_dir
        paths = sorted(Path(chunks_dir).glob("chunk_*.m4a"))
        if not paths:
            print(f"❌ 目录 {chunks_dir} 中没有 chunk_*.m4a 文件")
            sys.exit(1)
        for i, p in enumerate(paths):
            d = self._ff_duration(str(p))
            wav = os.path.join(chunks_dir, f"chunk_{i:03d}.wav")
            # 跳过已完成的 Groq 结果
            groq_out = os.path.join(chunks_dir, f"groq_{i:03d}.txt")
            whisper_out = os.path.join(chunks_dir, f"whisper_{i:03d}.txt")
            state = State.PENDING
            result = None
            if os.path.exists(groq_out):
                state = State.GROQ_DONE
                result = groq_out
            elif os.path.exists(whisper_out):
                state = State.WHISPER_DONE
                result = whisper_out

            self.chunks.append(Chunk(
                idx=i, m4a=str(p), wav=wav,
                duration=d, state=state, result=result))
        done = sum(1 for c in self.chunks
                   if c.state in (State.GROQ_DONE, State.WHISPER_DONE))
        print(f"📂 加载已有切片: {len(self.chunks)} 个 ({done} 个已完成)\n")

    def _prepare(self):
        """切分音频 + 生成任务列表"""
        wdir = os.path.join(os.path.dirname(self.audio),
                            f".asr_{int(time.time())}")
        os.makedirs(wdir, exist_ok=True)

        dur = self._ff_duration(self.audio)
        n = int(dur / self.chunk_sec) + 1
        print(f"✂️  切分: {dur:.0f}s → ~{n} 段 (每段≤{self.chunk_sec}s)")

        subprocess.run([
            "ffmpeg", "-y", "-i", self.audio,
            "-f", "segment", "-segment_time", str(self.chunk_sec),
            "-c", "copy", os.path.join(wdir, "chunk_%03d.m4a")
        ], capture_output=True, check=True)

        paths = sorted(Path(wdir).glob("chunk_*.m4a"))
        for i, p in enumerate(paths):
            d = self._ff_duration(str(p))
            self.chunks.append(Chunk(
                idx=i, m4a=str(p),
                wav=os.path.join(wdir, f"chunk_{i:03d}.wav"),
                duration=d))
        print(f"   → {len(self.chunks)} 个切片就绪\n")

    # ── Groq 转录 ──────────────────────────────────────────
    def _groq_transcribe(self, chunk: Chunk) -> bool:
        chunk.state = State.GROQ_RUNNING
        print(f"🚀 Groq → chunk_{chunk.idx:03d} ({chunk.duration:.0f}s 音频)", flush=True)
        t0 = time.time()

        for attempt in range(8):
            if self._stop.is_set():
                chunk.state = State.PENDING; return False
            try:
                with open(chunk.m4a, "rb") as f:
                    resp = self.client.audio.transcriptions.create(
                        model="whisper-large-v3",
                        file=f,
                        response_format="verbose_json",
                        timestamp_granularities=["segment"],
                        language=self.lang)

                offset = sum(c.duration for c in self.chunks[:chunk.idx])
                out = os.path.join(os.path.dirname(chunk.m4a),
                                   f"groq_{chunk.idx:03d}.txt")
                with open(out, "w", encoding="utf-8") as f:
                    for seg in resp.segments:
                        s = seg["start"] + offset
                        e = seg["end"] + offset
                        f.write(f"[{int(s//60):02d}:{int(s%60):02d} - "
                                f"{int(e//60):02d}:{int(e%60):02d}] "
                                f"{seg['text'].strip()}\n")

                chunk.elapsed = time.time() - t0
                chunk.segments = len(resp.segments)
                chunk.result = out
                chunk.state = State.GROQ_DONE
                self.quota.deduct(chunk.duration)
                print(f"✅ Groq → chunk_{chunk.idx:03d} 完成 "
                      f"({chunk.elapsed:.1f}s, {chunk.segments}段)", flush=True)
                return True

            except APIStatusError as e:
                if e.status_code == 429:
                    wait = 60.0
                    m = re.search(r'try again in ([\d.]+)\s*s', str(e))
                    if m:
                        wait = float(m.group(1)) + 5
                    print(f"   ⏳ 429 → 等待 {wait:.0f}s "
                          f"(attempt {attempt+1}/8)", flush=True)
                    if self._stop.wait(wait):
                        return False   # interrupted
                else:
                    print(f"   ❌ Groq 错误: {e}", flush=True)
                    chunk.state = State.FAILED; return False

        chunk.state = State.FAILED
        return False

    # ── whisper.cpp 转录 ────────────────────────────────────
    def _convert_wav(self, chunk: Chunk):
        if os.path.exists(chunk.wav):
            return
        subprocess.run([
            "ffmpeg", "-y", "-i", chunk.m4a,
            "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le",
            chunk.wav], capture_output=True, check=True)

    def _whisper_transcribe(self, chunk: Chunk) -> bool:
        self._convert_wav(chunk)
        chunk.state = State.WHISPER_RUNNING
        print(f"🐌 whisper.cpp → chunk_{chunk.idx:03d} "
              f"({chunk.duration:.0f}s 音频)", flush=True)
        t0 = time.time()

        out_base = os.path.join(os.path.dirname(chunk.m4a),
                                f"whisper_{chunk.idx:03d}")
        try:
            subprocess.run([
                "whisper-cli", "-m", WHISPER_MODEL,
                "-l", self.lang, "-t", str(WHISPER_THREADS),
                "-f", chunk.wav, "-of", out_base, "--output-txt"
            ], capture_output=True, timeout=5400, check=True)
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
            print(f"   ❌ whisper.cpp 错误: {e}", flush=True)
            chunk.state = State.FAILED; return False

        out_txt = out_base + ".txt"
        if not os.path.exists(out_txt):
            chunk.state = State.FAILED; return False

        chunk.elapsed = time.time() - t0
        chunk.result = out_txt
        with open(out_txt) as f:
            chunk.segments = sum(1 for _ in f)
        chunk.state = State.WHISPER_DONE
        print(f"✅ whisper.cpp → chunk_{chunk.idx:03d} 完成 "
              f"({chunk.elapsed:.1f}s)", flush=True)
        return True

    # ── 工作线程 ────────────────────────────────────────────
    def _groq_worker(self):
        """Groq 工作者：有配额就抢 PENDING 任务"""
        while not self._stop.is_set():
            # 找下一个 PENDING
            target = None
            with self._lock:
                for c in self.chunks:
                    if c.state == State.PENDING:
                        c.state = State.GROQ_RUNNING  # 预占
                        target = c
                        break

            if target is None:
                # 没有可分配的任务了
                all_done = all(c.state in (State.GROQ_DONE, State.WHISPER_DONE,
                                           State.FAILED)
                               for c in self.chunks)
                if all_done:
                    break
                self._stop.wait(3)
                continue

            # 检查配额
            if self.quota.remaining() < target.duration:
                # 配额不够，放回 PENDING 让 whisper 有机会接
                with self._lock:
                    target.state = State.PENDING
                # Groq worker 短暂等待后重试（配额可能很快恢复）
                self._stop.wait(30)
                continue

            # 执行
            if not self._groq_transcribe(target):
                with self._lock:
                    if target.state == State.GROQ_RUNNING:
                        target.state = State.PENDING  # 放回

    def _whisper_worker(self):
        """Whisper 工作者：配额不够时立即接手 PENDING 任务
        
        核心原则：只看当前配额够不够，不猜 Groq 什么时候恢复。
        - 配额够 → 让给 Groq（快），自己等
        - 配额不够 → 立刻接手（慢总比不干好）
        - Groq 配额恢复后会抢走还没开始跑的 PENDING 任务
        """
        while not self._stop.is_set():
            target = None
            with self._lock:
                for c in self.chunks:
                    if c.state == State.PENDING:
                        # Groq 当前配额够？让给它
                        if self.quota.remaining() >= c.duration:
                            continue
                        # 配额不够，whisper 直接接手
                        c.state = State.WHISPER_RUNNING  # 预占
                        target = c
                        break

            if target is None:
                all_done = all(c.state in (State.GROQ_DONE, State.WHISPER_DONE,
                                           State.FAILED)
                               for c in self.chunks)
                if all_done:
                    break
                self._stop.wait(5)
                continue

            self._whisper_transcribe(target)

    def _progress_monitor(self):
        """定期打印进度 + 配额恢复时尝试抢占"""
        while not self._stop.is_set():
            done = sum(1 for c in self.chunks
                       if c.state in (State.GROQ_DONE, State.WHISPER_DONE))
            total = len(self.chunks)
            groq_d = sum(1 for c in self.chunks if c.state == State.GROQ_DONE)
            whisp_d = sum(1 for c in self.chunks if c.state == State.WHISPER_DONE)
            groq_r = sum(1 for c in self.chunks if c.state == State.GROQ_RUNNING)
            whisp_r = sum(1 for c in self.chunks if c.state == State.WHISPER_RUNNING)
            pending = sum(1 for c in self.chunks if c.state == State.PENDING)
            q = self.quota.remaining()

            bar_len = 30
            filled = int(bar_len * done / max(total, 1))
            bar = "█" * filled + "░" * (bar_len - filled)
            print(f"\n📊 [{bar}] {done}/{total} | "
                  f"🚀Groq:{groq_d}✅{groq_r}🔄 | "
                  f"🐌Whisper:{whisp_d}✅{whisp_r}🔄 | "
                  f"⏳待:{pending} | 💰配额:{q:.0f}s",
                  flush=True)
            self._stop.wait(30)

    # ── 合并结果 ────────────────────────────────────────────
    def _merge(self):
        lines = []
        for c in sorted(self.chunks, key=lambda x: x.idx):
            if c.result and os.path.exists(c.result):
                with open(c.result, encoding="utf-8") as f:
                    lines.extend(f.readlines())
        with open(self.output, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print(f"\n💾 合并结果 → {self.output} ({len(lines)} 行)")

    # ── 主入口 ──────────────────────────────────────────────
    def run(self):
        print("=" * 60)
        print("🔊 ASR 混合调度器 — Groq ⚡ + whisper.cpp 🐢")
        print("=" * 60)

        self._init_groq()

        # 如果没通过 _load_existing_chunks 加载，就自动切分
        if not self.chunks:
            self._prepare()

        total_dur = sum(c.duration for c in self.chunks)
        quota = self.quota.remaining()
        groq_cap = quota  # 当前可用
        print(f"📋 总时长: {total_dur:.0f}s ({total_dur/60:.1f}min)")
        print(f"💰 Groq 配额: {quota:.0f}s ({quota/60:.1f}min)")
        overflow = max(0, total_dur - quota)
        print(f"🔄 预计溢出到 whisper.cpp: ~{overflow:.0f}s ({overflow/60:.1f}min)")
        print(f"   (配额持续恢复，实际溢出可能更少)\n")

        t0 = time.time()

        threads = [
            threading.Thread(target=self._groq_worker,
                             name="groq-worker", daemon=True),
            threading.Thread(target=self._whisper_worker,
                             name="whisper-worker", daemon=True),
            threading.Thread(target=self._progress_monitor,
                             name="monitor", daemon=True),
        ]
        for t in threads:
            t.start()

        # 等所有任务终态
        while not self._stop.is_set():
            if all(c.state in (State.GROQ_DONE, State.WHISPER_DONE,
                               State.FAILED)
                   for c in self.chunks):
                break
            self._stop.wait(5)

        # 给正在跑的最后一点时间
        time.sleep(2)
        self._stop.set()

        self._merge()

        wall = time.time() - t0
        groq_chunks = [c for c in self.chunks if c.state == State.GROQ_DONE]
        whisp_chunks = [c for c in self.chunks if c.state == State.WHISPER_DONE]
        failed = [c for c in self.chunks if c.state == State.FAILED]

        print(f"\n{'=' * 60}")
        print(f"🏁 转录完成!")
        print(f"{'=' * 60}")
        print(f"⏱️  墙钟: {wall:.1f}s ({wall/60:.1f}min)")
        print(f"🚀 Groq:  {len(groq_chunks)} 段, "
              f"avg {sum(c.elapsed for c in groq_chunks)/max(1,len(groq_chunks)):.1f}s/段")
        print(f"🐌 whisper: {len(whisp_chunks)} 段, "
              f"avg {sum(c.elapsed for c in whisp_chunks)/max(1,len(whisp_chunks)):.1f}s/段")
        print(f"📊 整体: {total_dur/wall:.1f}x 实时")
        if failed:
            print(f"❌ 失败: {[c.idx for c in failed]}")


# ─── CLI ────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(
        description="ASR 混合调度器: Groq(快)+whisper.cpp(稳)")
    p.add_argument("audio", help="音频文件路径")
    p.add_argument("-o", "--output", help="输出文件路径")
    p.add_argument("-l", "--lang", default="zh", help="语言 (默认 zh)")
    p.add_argument("--chunk-minutes", type=int, default=15,
                   help="切片时长/分钟 (默认 15)")
    p.add_argument("--chunks-dir", help="复用已有切片目录 (跳过切分)")
    args = p.parse_args()

    scheduler = ASRScheduler(
        audio=args.audio,
        output=args.output,
        chunk_minutes=args.chunk_minutes,
        lang=args.lang,
    )
    if args.chunks_dir:
        scheduler._load_existing_chunks(args.chunks_dir)
    scheduler.run()


if __name__ == "__main__":
    main()
