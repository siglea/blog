---
layout: post
title:  "BitMap 与 BloomFilter：海量数据处理的两把利刃"
date:   2020-06-07 14:25:00 +0900
comments: true
tags:
- 数据结构与算法
categories:
- 技术
---

在处理海量数据时，常规的数据结构往往面临内存爆炸的困境。比如要判断 40 亿个整数中是否存在某个数、或者检查一个 URL 是否已经被爬虫访问过——如果用 HashSet 直接存储，内存占用将达到数十 GB 甚至上百 GB。这时就需要请出两个内存效率极高的数据结构：**BitMap** 和 **BloomFilter**。

### BitMap（位图）

#### 核心思想

BitMap 的核心非常简洁：**用一个 bit（位）来标记一个元素是否存在**。

传统方式中，一个 int 类型需要 4 字节（32 位）来存储一个数字。而在 BitMap 中，一个 bit 就能表示一个数字的存在与否。这意味着存储空间缩小到原来的 **1/32**。

```
传统存储：[5, 3, 7, 2] → 每个数字 4 字节 → 共 16 字节
BitMap：  00101101       → 用 1 字节（8 bit）表示 0-7 的存在情况
          位置: 76543210
          值:   00101101 → 表示 0, 2, 3, 5 存在
```

#### 基本操作

```java
public class BitMap {
    private byte[] bits;
    
    public BitMap(int maxValue) {
        bits = new byte[(maxValue >> 3) + 1];
    }
    
    // 将第 num 位设为 1（添加元素）
    public void add(int num) {
        int byteIndex = num >> 3;       // num / 8，定位到第几个 byte
        int bitIndex = num & 7;          // num % 8，定位到 byte 内的第几位
        bits[byteIndex] |= (1 << bitIndex);
    }
    
    // 判断第 num 位是否为 1（查询元素）
    public boolean contains(int num) {
        int byteIndex = num >> 3;
        int bitIndex = num & 7;
        return (bits[byteIndex] & (1 << bitIndex)) != 0;
    }
    
    // 将第 num 位设为 0（删除元素）
    public void remove(int num) {
        int byteIndex = num >> 3;
        int bitIndex = num & 7;
        bits[byteIndex] &= ~(1 << bitIndex);
    }
}
```

#### 内存计算

存储 40 亿个整数的存在性：
- 传统方式（HashSet<Integer>）：40 亿 × 16 字节 ≈ **60 GB**
- BitMap 方式：2^32 bit = 512 MB（覆盖整个 int 范围）

#### 适用场景

| 场景 | 说明 |
|------|------|
| 大数据去重 | 判断某个数是否出现过 |
| 排序 | 遍历 BitMap 即可得到有序结果 |
| 用户标签 | 每个 bit 表示一个标签，快速进行交集/并集运算 |
| 活跃用户统计 | 每天一个 BitMap，某位为 1 表示该用户当天活跃 |

#### 局限性

1. **只能存储非负整数**，不适合存储字符串等复杂类型
2. **数据稀疏时浪费空间**：如果只存 3 个数但最大值是 10 亿，仍需分配大量内存
3. **不支持重复计数**：一个位置只能是 0 或 1，无法记录出现次数

### BloomFilter（布隆过滤器）

BloomFilter 是 BitMap 的升级版，它解决了 BitMap 无法处理字符串等非整数类型的问题。

#### 核心思想

BloomFilter 的核心是：**将元素通过多个不同的 Hash 函数映射到 BitMap 的多个位置**。

```
添加元素 "hello"：
  hash1("hello") = 3
  hash2("hello") = 7  
  hash3("hello") = 11
  → 将 BitMap 的第 3、7、11 位设为 1

查询元素 "hello"：
  计算 hash1、hash2、hash3 → 得到 3、7、11
  → 检查第 3、7、11 位是否都为 1
  → 都为 1 → "可能存在"
  → 有任何一个为 0 → "一定不存在"
```

#### 为什么需要多个 Hash 函数

单个 Hash 函数的冲突概率较高。假设 BitMap 大小为 m，已插入 n 个元素：
- 1 个 Hash 函数：误判率 ≈ n/m
- k 个 Hash 函数：误判率 ≈ (1 - e^(-kn/m))^k

通过多次 Hash，只有所有 Hash 位置都发生冲突时才会产生误判，从而大幅降低误判概率。

#### 关键特性

- **判定不存在 → 一定不存在**（零漏报）
- **判定存在 → 可能存在**（有误报）
- **不支持删除**：删除某个元素的 bit 位可能影响其他元素

误报率可以通过调整 BitMap 大小（m）和 Hash 函数个数（k）来控制。

#### Java 实现（使用 Guava）

Google Guava 提供了生产级的 BloomFilter 实现：

```java
import com.google.common.hash.BloomFilter;
import com.google.common.hash.Funnels;

// 创建 BloomFilter：预计插入 100 万个元素，误报率 1%
BloomFilter<String> bloomFilter = BloomFilter.create(
    Funnels.stringFunnel(Charset.defaultCharset()),
    1_000_000,   // 预期元素数量
    0.01         // 可接受的误报率
);

// 添加元素
bloomFilter.put("https://example.com/page1");
bloomFilter.put("https://example.com/page2");

// 查询元素
boolean mightExist = bloomFilter.mightContain("https://example.com/page1"); // true
boolean notExist = bloomFilter.mightContain("https://example.com/page999"); // 大概率 false
```

#### Redis 中的 BloomFilter

Redis 4.0+ 通过 RedisBloom 模块原生支持 BloomFilter，适用于分布式场景：

```bash
# 创建 BloomFilter：误报率 0.01，预期容量 100 万
BF.RESERVE myfilter 0.01 1000000

# 添加元素
BF.ADD myfilter "user:1001"

# 批量添加
BF.MADD myfilter "user:1002" "user:1003" "user:1004"

# 查询是否存在
BF.EXISTS myfilter "user:1001"    # 返回 1（可能存在）
BF.EXISTS myfilter "user:9999"    # 返回 0（一定不存在）
```

#### 实际应用场景

| 场景 | 说明 |
|------|------|
| 短链接去重 | 生成短链接前检查是否已存在，避免重复 |
| 爬虫 URL 去重 | 判断 URL 是否已爬取过 |
| 垃圾邮件过滤 | 检查发件人/关键词是否在黑名单中 |
| 缓存穿透防护 | 在缓存和数据库之间加一层 BloomFilter，拦截不存在的 Key |
| 推荐系统去重 | 避免重复推荐已看过的内容 |

#### 缓存穿透防护示例

```
用户请求 → BloomFilter 判断 Key 是否存在
              ↓ 不存在 → 直接返回空，不查数据库
              ↓ 可能存在 → 查缓存
                           ↓ 缓存命中 → 返回
                           ↓ 缓存未命中 → 查数据库 → 写入缓存 → 返回
```

这种模式可以有效防止恶意请求用大量不存在的 Key 击穿缓存、压垮数据库。

### BitMap vs BloomFilter 对比

| 特性 | BitMap | BloomFilter |
|------|--------|-------------|
| 支持类型 | 非负整数 | 任意类型（通过 Hash） |
| 判断准确性 | 100% 准确 | 存在误报（可控） |
| 支持删除 | 支持 | 不支持（Counting BF 除外） |
| 空间效率 | 高（稀疏数据除外） | 极高 |
| 时间复杂度 | O(1) | O(k)，k 为 Hash 函数个数 |
| 典型实现 | Java BitSet、Redis SETBIT | Guava BloomFilter、RedisBloom |

### 进阶变体

- **Counting BloomFilter**：每个位置用计数器替代单 bit，支持删除操作
- **Cuckoo Filter**：支持删除，且在相同误报率下空间更优
- **Roaring BitMap**：压缩位图，处理稀疏数据时比普通 BitMap 更省空间，广泛应用于 Elasticsearch、Apache Spark 等

### 总结

BitMap 和 BloomFilter 是海量数据场景下的两个经典武器。BitMap 适合处理整数范围内的精确判断，BloomFilter 则将适用范围扩展到任意数据类型，以极低的误报率换取了极高的空间效率。在实际工程中，理解它们的特性和局限，选择合适的工具，才能在性能和资源之间找到最佳平衡。
