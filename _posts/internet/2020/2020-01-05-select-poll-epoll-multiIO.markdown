---
layout: post
title:  "IO 多路复用深入解析：select、poll 与 epoll 的演进之路"
date:   2019-11-12 11:25:00 +0900
comments: true
tags:
- 网络
- 分布式
categories:
- 技术
---

IO 多路复用是高性能网络编程的核心技术，它允许单个线程同时监视多个文件描述符（socket），在任何一个就绪时及时响应。从 1984 年的 select 到 2002 年的 epoll，IO 多路复用机制经历了近 20 年的演进。本文将深入剖析 select、poll、epoll 三种机制的原理、区别与实现细节。

---

## 一、历史背景

理解三者的差异，首先要了解它们诞生的历史背景：

- **1984 年**：select 在 BSD 中实现。当时的硬件性能有限，一台服务器能处理 1000 多个连接就已经是"神一样的存在"，select 完全能满足需求。
- **1997 年**：时隔 14 年，poll 问世。拖了这么久并非效率问题，而是当时的硬件水平使得 select 的限制并不构成瓶颈。
- **2002 年**：大神 Davide Libenzi 实现了 epoll，彻底革新了 IO 多路复用的性能表现。

---

## 二、select 机制

select 是最早的 IO 多路复用实现，其核心思想是：内核监听一组文件描述符，当其中任意一个就绪时，通知用户态程序去遍历检查。

### 2.1 函数签名

```java
int select(int maxfdp1, fd_set *readset, fd_set *writeset, fd_set *exceptset, const struct timeval *timeout);
```

### 2.2 工作原理

1. 用户态创建 fd_set，设置需要监听的文件描述符
2. 将 fd_set 拷贝到内核态
3. 内核遍历所有 fd，检查是否有事件就绪
4. 如果有就绪事件，内核将结果写入 fd_set 并返回
5. 用户态遍历 fd_set，找出就绪的文件描述符

### 2.3 select 的局限

1. **数量限制**：由于 fd_set 的实现方式（位图数组），最多只能监听 1024 个文件描述符（该值在 Linux 头文件 `FD_SETSIZE` 中写死，不可运行时修改）
2. **每次重置**：由于内核直接修改了 fd_set 参数的内存地址，每次调用前都需要重新初始化 fd_set
3. **遍历开销**：返回后需要遍历所有 fd（至少 n 次，至多 maxfdp1 次），而不仅仅是就绪的那些
4. **拷贝开销**：每次调用都会将三个 fd_set 完整地从用户态拷贝到内核态

---

## 三、poll 机制

poll 在 1997 年推出，修复了 select 的两个历史遗留问题。

### 3.1 函数签名

```java
int poll(struct pollfd *fds, nfds_t nfds, int timeout);

typedef struct pollfd {        
    int fd;           // 需要被检测或选择的文件描述符        
    short events;     // 对文件描述符 fd 上感兴趣的事件        
    short revents;    // 文件描述符 fd 上当前实际发生的事件
};
```

### 3.2 相比 select 的改进

- **突破数量限制**：poll 使用 `int fd` 代替 fd_set 来表示文件描述符，没有 1024 的硬编码限制。最大连接数可在 `/proc/sys/fs/file-max` 获取。
- **无需重置参数**：poll 用 events 表示期待的事件，通过修改 revents 来反馈发生的事件，两个字段分离，无需每次重新设置。

### 3.3 poll 的不足

除了上述两点改进外，poll 和 select 几乎相同：

- 返回后仍然需要遍历整个 pollfd 数组（nfds 次循环），时间复杂度仍为 O(n)
- 每次调用仍需将整个 fdarray 从用户态拷贝到内核态
- 在描述符很多但每次就绪的很少时，存在同样的性能问题

---

## 四、epoll 机制

epoll 是 Linux 2.6 内核引入的革命性 IO 多路复用方案，从根本上解决了 select 和 poll 的性能瓶颈。

### 4.1 三步曲 API

epoll 的使用分为三个系统调用：

**1. epoll_create()** —— 创建 epoll 实例

```java
int epoll_create(int size);
```

返回一个 epoll 句柄，后续操作都依赖这个句柄。其内部维护两个关键数据结构：
- `struct rb_root rbr`：红黑树的根节点，存储所有添加到 epoll 中的需要监控的事件
- `struct list_head rdlist`：双链表，存放将要通过 epoll_wait 返回给用户的就绪事件

**2. epoll_ctl()** —— 管理事件

```java
int epoll_ctl(int epfd, int op, int fd, struct epoll_event *event);
```

通过此调用向 epoll 对象中添加、删除、修改感兴趣的事件。参数说明：
- `epfd`：epoll 句柄
- `op`：操作类型（EPOLL_CTL_ADD 注册 / EPOLL_CTL_MOD 修改 / EPOLL_CTL_DEL 删除）
- `fd`：要监听的描述符
- `event`：要监听的事件

```java
struct epoll_event {
    __uint32_t events;  /* Epoll events */    
    epoll_data_t data;  /* User data variable */
};
typedef union epoll_data {
    void *ptr;
    int fd;
    __uint32_t u32;
    __uint64_t u64;
} epoll_data_t;
```

调用 epoll_ctl 时，会为每个文件描述符注册一个回调函数（内核中叫 `ep_poll_callback`）。一旦对应事件发生，回调函数会将该文件描述符加入到就绪链表（rdlist）中。

**3. epoll_wait()** —— 等待就绪事件

```java
int epoll_wait(int epfd, struct epoll_event *events, int maxevents, int timeout);
```

只需检查就绪队列是否为空。如果返回值为 n，则只需做 n 次循环，保证每一次遍历都是有意义的。

### 4.2 epoll 为什么高性能

epoll 的性能优势来自三个关键设计：

1. **减少数据拷贝**：只在 epoll_ctl 时将数据拷贝到内核空间，保证每个描述符只被拷贝一次。epoll_wait 调用时不需要复制新数据。而 select 和 poll 每次调用都要重新拷贝。
2. **避免无效遍历**：epoll_wait 返回 n 就只遍历 n 个就绪事件，而不是像 select/poll 那样遍历所有注册的描述符。
3. **回调机制**：select/poll 醒来时要遍历整个文件描述符集合，而 epoll_wait 只需查看就绪队列是否为空。epoll 通过内核与用户空间 mmap 同一块内存，进一步减少了拷贝开销。

### 4.3 LT 模式与 ET 模式

epoll 对文件描述符的操作有两种触发模式：

**LT（Level Trigger，水平触发）**—— 默认模式
- 当 epoll_wait 检测到事件发生并通知应用程序后，应用程序**可以不立即处理**
- 下次调用 epoll_wait 时，会**再次通知**该事件
- 同时支持阻塞和非阻塞 socket

**ET（Edge Trigger，边沿触发）**—— 高速模式
- 当 epoll_wait 检测到事件发生并通知应用程序后，应用程序**必须立即处理**
- 如果不处理，下次调用 epoll_wait 时**不会再次通知**
- 只支持非阻塞 socket（必须使用非阻塞套接口，避免阻塞读/写操作饿死其他文件描述符）

ET 模式在很大程度上减少了 epoll 事件被重复触发的次数，因此效率比 LT 模式更高。但使用门槛也更高——必须确保每次通知时都将数据读取/写入完毕。

---

## 五、三者对比总结

| 维度 | select | poll | epoll |
|------|--------|------|-------|
| 诞生时间 | 1984 | 1997 | 2002 |
| 操作方式 | 遍历 | 遍历 | 回调 |
| IO 效率 | O(n) | O(n) | O(1) |
| 底层数据结构 | 数组（位图） | 链表 | 红黑树 + 就绪链表 |
| 最大连接数 | 1024（FD_SETSIZE 硬编码） | 无限制（取决于系统 file-max） | 无限制 |
| fd 拷贝 | 每次调用全量拷贝 | 每次调用全量拷贝 | epoll_ctl 时一次性注册，mmap 共享内存 |
| 参数重置 | 需要每次重新设置 | 不需要（events/revents 分离） | 不需要 |

一切差异都与历史发展有关。select 在 1984 年实现了多路复用的基本能力；poll 在 1997 年修复了数量限制和参数重置的问题；epoll 在 2002 年通过回调机制和 mmap 共享内存，将 IO 多路复用的性能推向了新的高度。

---

## 参考资料

- IO多路复用的三种机制Select，Poll，Epoll <https://mp.weixin.qq.com/s/UWdZsvPsV46VLpr7qHjgjA>
- IO模型及select、poll、epoll和kqueue的区别 <https://mp.weixin.qq.com/s/R8cA0_1dNujVORionyg_4A>
- Select，Poll，Epoll详解 <https://mp.weixin.qq.com/s/49yzOWWCoo1V1UG7iiJEVg>
- 大量代码 深入分析select&poll&epoll原理 <https://mp.weixin.qq.com/s/HC-xEavwXTypDIRvX0Tu3g>
- <https://mp.weixin.qq.com/s/AXJW0Q77yYfld0cFEsLu1A>
- <https://mp.weixin.qq.com/s/71-X1urvqgFG08cxS4TNvA>
- <https://mp.weixin.qq.com/s/zg7Ty_aF-IO0A4w4b5UVjA>
- C10K到C10M <http://www.52im.net/thread-561-1-1.html>
- <https://www.cnblogs.com/itxiaok/p/10357825.html>
