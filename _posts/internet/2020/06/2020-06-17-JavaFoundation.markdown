---
layout: post
title:  "Java核心基础精讲：并发机制、内存模型与常见面试要点"
date:   2020-06-17 21:25:00 +0900
comments: true
tags:
- Java
categories:
- 技术
---

### 引言

Java 作为企业级开发的主力语言，其并发机制、内存模型和基础类库是每个 Java 开发者必须深入理解的知识。本文将围绕锁优化、线程协作、内存模型、异常体系和集合框架等核心主题，系统性地梳理 Java 的基础知识要点，既可作为技术复习资料，也可作为面试准备参考。

---

### 锁优化：从偏向锁到重量级锁

HotSpot JVM 的研究表明，在大多数情况下锁不仅不存在多线程竞争，而且总是由同一线程多次获得。基于这一观察，JVM 实现了从偏向锁到重量级锁的逐步升级策略。

#### 偏向锁

偏向锁的目标是在**无多线程竞争**的情况下，消除同一线程锁重入（CAS）的开销。当一个线程首次获得锁时，JVM 会将该线程的 ID 记录在锁对象的 Mark Word 中。后续该线程再次进入同步块时，只需检查 ThreadID 是否匹配，无需执行 CAS 操作。

偏向锁只需要在置换 ThreadID 时依赖一次 CAS 原子指令，而轻量级锁的获取及释放依赖多次 CAS。但一旦出现多线程竞争，偏向锁必须撤销（撤销的性能损耗必须小于节省下来的 CAS 开销），升级为轻量级锁。

#### 轻量级锁

轻量级锁适用于**线程交替执行**同步块的场景。它通过 CAS 操作在线程栈帧中创建锁记录（Lock Record），避免了操作系统级别的线程挂起和唤醒。

#### 升级路径

偏向锁 → 轻量级锁 → 重量级锁。锁只能升级不能降级，这种设计避免了频繁的锁状态切换带来的性能损耗。

---

### 线程协作：join() 方法

在很多场景下，主线程生成并启动子线程后，需要等待子线程的执行结果。`join()` 方法使调用线程等待目标线程执行完毕后再继续：

```java
Thread worker = new Thread(() -> doWork());
worker.start();
worker.join(); // 主线程阻塞，直到 worker 执行完毕
```

`join()` 的底层实现是基于 `Object.wait()` 的，当目标线程结束时会调用 `notifyAll()` 唤醒等待线程。

---

### Java 内存泄漏

Java 虽然有 GC 自动回收内存，但仍然可能出现内存泄漏。一个典型场景是**非静态内部类隐式持有外部类的引用**，形成类似循环引用的结构，导致外部类对象无法被回收。

解决方案：将内部类改为**静态内部类**（`static class`），断开对外部类实例的隐式引用。

---

### 分布式垃圾回收（DGC）

RMI（远程方法调用）涉及跨虚拟机的远程对象引用，传统的 GC 机制无法跨 JVM 追踪对象的可达性。DGC（Distributed Garbage Collection）使用**引用计数算法**来为远程对象提供自动内存管理——当远程对象的引用计数降为零时，对象可以被回收。

---

### volatile vs Synchronized

`volatile` 和 `Synchronized` 是 Java 中最常用的两个并发关键字，它们的核心区别在于：

| 特性 | volatile | Synchronized |
|------|----------|-------------|
| 可见性 | 保证 | 保证 |
| 原子性 | **不保证** | 保证 |
| 使用场景 | 状态标志、双重检查锁定 | 临界区保护、复合操作 |

#### ThreadLocal vs Synchronized

两者都用于解决多线程并发访问共享资源的问题，但思路截然不同：

- **Synchronized**："以时间换空间"——通过锁机制使变量或代码块在某一时刻只能被一个线程访问
- **ThreadLocal**："以空间换时间"——为每个线程维护变量的独立副本，根除了对变量的共享

---

### ThreadLocal 的实现原理

ThreadLocal 为每个线程维护一份变量副本，适用于在整个线程生命周期内传递上下文信息（如事务、Cookie、用户会话等）。

实现原理：`ThreadLocal` 类内部维护一个 `ThreadLocalMap`，每个线程通过 `Thread.currentThread()` 获取自己的 Map，以 ThreadLocal 实例为 Key 存储变量副本。

**注意事项**：使用完毕后必须调用 `remove()` 清理，否则在线程池等线程复用场景下可能导致内存泄漏或数据串扰。

---

### 异常体系

**Throwable** 是 Java 中所有错误和异常的超类，分为两个子类：

#### Error

Java 运行时系统的内部错误和资源耗尽错误（如 `OutOfMemoryError`、`StackOverflowError`）。应用程序通常不应捕获 Error，出现时只能通知用户并尽力安全终止。

#### Exception

Exception 进一步分为两个分支：
- **RuntimeException**（运行时异常/非检查异常）：如 `NullPointerException`、`ArrayIndexOutOfBoundsException`，编译器不强制处理
- **Checked Exception**（受检异常）：如 `IOException`、`SQLException`，必须在代码中显式处理（catch 或 throws）

---

### 序列化与 serialVersionUID

Java 对象序列化将对象状态（成员变量）转换为字节流，支持持久化存储和网络传输。**静态变量不参与序列化**，因为它们属于类而非对象。

反序列化时，JVM 会比较字节流中的 `serialVersionUID` 与当前类的 `serialVersionUID`，不一致则抛出 `InvalidClassException`。因此建议显式定义：

```java
private static final long serialVersionUID = 1L;
```

序列化的应用场景包括：对象持久化、RMI 远程方法调用、网络传输等。

---

### Java 内存模型（JMM）

Java 内存模型定义了多线程访问 Java 内存的规范，是理解并发编程的理论基础。

#### 主内存与工作内存

JMM 将内存划分为**主内存**和**工作内存**：
- 主内存存储共享变量（类的实例字段、静态字段）
- 每个线程拥有自己的工作内存，保存共享变量的副本
- 线程操作变量时使用工作内存中的副本，执行完毕后将最新值更新到主内存

#### 8 种内存间操作

JMM 定义了 8 种原子操作来管理主内存和工作内存之间的数据交互：

| 操作 | 作用 |
|------|------|
| **lock** | 把主内存变量标识为一条线程独占 |
| **unlock** | 释放被锁定的变量 |
| **read** | 从主内存传输变量值到工作内存 |
| **load** | 将 read 得到的值放入工作内存的变量副本 |
| **use** | 将工作内存变量值传递给执行引擎 |
| **assign** | 将执行引擎的值传递给工作内存变量 |
| **store** | 将工作内存变量值传输到主内存 |
| **write** | 将 store 得到的值放入主内存变量 |

#### volatile 的语义

volatile 变量的读写遵循特殊规则：每次读取必须从主内存刷新，每次写入必须立即同步到主内存。这保证了可见性，但不保证复合操作的原子性。

#### happens-before 原则

happens-before 定义了操作之间的偏序关系，是判断线程安全的核心规则。常见的 happens-before 关系包括：
- 同一线程中，代码顺序靠前的操作 happens-before 靠后的操作
- `unlock` 操作 happens-before 后续对同一个锁的 `lock` 操作
- 对 volatile 变量的写 happens-before 后续对该变量的读

如果两个操作之间不满足任何 happens-before 关系，则它们之间的执行顺序不确定，可能存在线程安全问题。

---

### 线程间通信

Java 线程之间的通信必须通过主内存进行：

1. 线程 A 将本地工作内存中更新过的共享变量刷新到主内存
2. 线程 B 从主内存读取线程 A 已更新的共享变量

这也是 volatile 和 synchronized 能保证可见性的底层原因。

---

### Iterator 与 ListIterator

| 特性 | Iterator | ListIterator |
|------|----------|-------------|
| 适用集合 | Set 和 List | 仅 List |
| 遍历方向 | 仅向前 | 双向（前进和后退） |
| 额外功能 | 无 | 添加元素、替换元素、获取索引位置 |

ListIterator 继承自 Iterator 接口，专为 List 集合设计，提供了更丰富的遍历和修改能力。

---

### HashMap：为什么容量是 2 的幂？

HashMap 的容量始终保持为 2 的幂次方，核心原因是**位运算优化**：当容量 n 为 2 的幂时，`hash % n` 等价于 `hash & (n - 1)`，位运算比取模运算快得多。

#### JDK 1.8 相比 1.7 的优化

1. **resize 扩容优化**：扩容时无需重新计算 hash，通过高位判断直接确定新位置
2. **引入红黑树**：当链表长度超过 8 时转化为红黑树，将最坏情况的查询复杂度从 O(n) 降为 O(log n)
3. **解决多线程死循环**：1.7 中头插法扩容可能导致链表成环，1.8 改为尾插法。但 HashMap 仍是非线程安全的，多线程环境应使用 ConcurrentHashMap

---

### POJO

POJO（Plain Ordinary Java Object）即普通 Java 对象，指没有继承特定框架类、没有实现特定接口的简单 Java 对象。POJO 的理念是保持对象的纯粹性，避免与特定框架耦合。

---

### 总结

Java 的核心基础涵盖面广且深度不浅。锁的升级策略（偏向锁 → 轻量级锁 → 重量级锁）体现了 JVM 对性能的极致追求；JMM 的主内存/工作内存模型和 happens-before 原则是理解并发编程的理论根基；volatile 和 synchronized 的区别、ThreadLocal 的使用场景和注意事项是日常开发中的高频知识点。扎实掌握这些基础，才能在面对复杂的并发问题和性能优化时游刃有余。
