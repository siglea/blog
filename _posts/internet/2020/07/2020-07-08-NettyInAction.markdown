---
layout: post
title:  "Netty 实战：从核心组件到高性能网络编程"
date:   2020-07-08 19:18:00 +0900
comments: true
tags:
- Java
- 网络
categories:
- 技术
---

Netty 是 Java 生态中最流行的异步事件驱动网络框架，被广泛应用于 RPC 框架（如 Dubbo、gRPC）、消息中间件（如 RocketMQ）、大数据组件（如 Spark、Flink）等基础设施中。本文基于《Netty 实战》一书的核心内容，从内存管理、零拷贝、NIO Selector、核心组件、ChannelPipeline 到 WebSocket 等多个维度，系统梳理 Netty 的设计哲学与关键技术。

**延伸阅读：**
- Netty 实战 <https://mp.weixin.qq.com/s/OFG6tD9YRbII3BgjF4IKRg>
- Java 网络编程与 NIO <https://www.cnblogs.com/itxiaok/category/1395489.html>

---

### 一、Netty 的内存管理：Arena、Chunk、Page、SubPage

Netty 的内存分配器借鉴了 jemalloc 的设计思想，通过多层级的内存管理结构实现了高效的内存分配与回收。

- **Arena**：简单来说，Arena 就是一个内存分配器，所有分配的内存都由 Arena 维护。一般会有多个 Arena 实例，目的是减少锁竞争。Netty 对 jemalloc 的 Arena 进行了更具体的实现，即 `PoolArena`。

- **Chunk**：Chunk 是 Netty 向操作系统申请内存的最小调度单位。Chunk 大小固定为 **16MB**，即 Netty 每次向操作系统申请内存最小为 16MB。

- **Page**：一个 Chunk 被划分为 **2048 个 Page**，每个 Page 大小为 **8KB**。Page 是给 ByteBuf 分配内存的最小调度单位（尽管还有更小的 SubPage 级别，但分配 SubPage 时仍需先获取一个 Page）。当 ByteBuf 需要申请的内存大小（必定是 2 的幂次方）≥ 8KB 时，会先取一个 Chunk，然后以 Page 级别分配内存，最后将当前 Chunk 标记为"使用了一部分"并放进对应占用率的 ChunkList。

- **SubPage**：当 ByteBuf 需要申请的内存大小（必定是 2 的幂次方）< 8KB 时，例如需要 2KB，则会先取一个 Chunk，再取一个 Page，然后将 Page 分成 4 份（pageSize / size），每份 2KB，取其中一份给 ByteBuf 初始化。之后是一个自底向上标记的过程：将当前使用的 SubPage 标记为"已使用"，上一层 Page 标记为"部分使用"，再上一级 Chunk 标记为"部分使用"，最终将 Chunk 放进对应占用率的 ChunkList。

**延伸阅读：**
- jemalloc 之 Arena、Chunk、Page、SubPage <https://www.jianshu.com/p/f1988cc08dfd>
- 内存规格、缓存结构等概念介绍 <https://blog.csdn.net/qq_33347239/article/details/104270629>
- 关于 OS Page Cache 与 Kafka 零拷贝 <https://www.cnblogs.com/leadership/p/12349486.html>

---

### 二、Netty 的零拷贝

Netty 的零拷贝体现在多个层面，综合运用了操作系统和应用层的优化手段：

1. **NIO 的 DirectMemory**：基于 mmap 的直接内存映射，避免了堆内外内存之间的数据拷贝。
2. **FileRegion 的 transferTo**：基于 sendFile 系统调用，实现文件到网络的零拷贝传输。
3. **CompositeByteBuf**：通过 `wrap` 将多个 ByteBuf 逻辑合并，以及通过 `slice` 对单个 ByteBuf 进行逻辑分拆，避免了内存层面的实际拷贝。

---

### 三、NIO Selector 与 epoll

#### 3.1 Selector 的创建

在 Linux 系统下，`sun.nio.ch.DefaultSelectorProvider.create()` 会生成一个 `EPollSelectorProvider` 类型的 SelectorProvider。也可以在 `META-INF/services` 下配置 `java.nio.channels.spi.SelectorProvider` 来指定自定义实现。

```shell
public static SelectorProvider provider() {
    synchronized (lock) {
        if (provider != null)
            return provider;
        return AccessController.doPrivileged(
            new PrivilegedAction<>() {
                public SelectorProvider run() {
                        if (loadProviderFromProperty())
                            return provider;
                        if (loadProviderAsService())
                            return provider;
                        provider = sun.nio.ch.DefaultSelectorProvider.create();
                        return provider;
                    }
                });
    }
}
```

#### 3.2 EPollSelectorImpl 的初始化

EPollSelectorImpl 在构造时会初始化 epoll 相关的底层资源：

```shell
EPollSelectorImpl(SelectorProvider sp) throws IOException {
        super(sp);
        long pipeFds = IOUtil.makePipe(false);
        fd0 = (int) (pipeFds >>> 32);
        fd1 = (int) pipeFds;
        try {
            pollWrapper = new EPollArrayWrapper();
            pollWrapper.initInterrupt(fd0, fd1);
            fdToKey = new HashMap<>();
        } catch (Throwable t) {}
}
// EPollArrayWrapper
void initInterrupt(int fd0, int fd1) {
    outgoingInterruptFD = fd1;
    incomingInterruptFD = fd0;
    epollCtl(epfd, EPOLL_CTL_ADD, fd0, EPOLLIN);
}

private native int epollCreate();
private native void epollCtl(int epfd, int opcode, int fd, int events);
private native int epollWait(long pollAddress, int numfds, long timeout,
                             int epfd) throws IOException;
```

#### 3.3 Selector 的三个 SelectionKey 集合

Selector 中维护了 3 个至关重要的 SelectionKey 集合：

- **keys**：所有注册到 Selector 的 Channel 所表示的 SelectionKey 都会存在于该集合中。元素的添加发生在 Channel 注册到 Selector 时。
- **selectedKeys**：该集合中的每个 SelectionKey 都是其对应的 Channel 在上一次 selection 操作期间被检测到至少有一种感兴趣的操作已准备好被处理。它是 keys 的子集。
- **cancelledKeys**：执行了取消操作的 SelectionKey 会被放入该集合中。它也是 keys 的子集。

**参考：** <https://www.cnblogs.com/itxiaok/p/10357828.html>

---

### 四、深入理解 epoll

epoll 相关系统调用在 Linux 2.5 后引入，针对传统 select/poll 的不足做了重大改进。

**select/poll 的缺点：**
- 每次调用时要重复地从用户模式读入参数，并重复地扫描文件描述符。
- 每次调用开始时要把当前进程放入各个文件描述符的等待队列，调用结束后再从各个等待队列中删除。

**epoll 的改进：**
- 将 select/poll 单个操作拆分为 `epoll_create`、多个 `epoll_ctl` 和一个 `epoll_wait`。
- 操作系统内核针对 epoll 操作添加了一个文件系统，每个被监视的文件描述符都有对应的 inode 节点，主要信息保存在 `eventpoll` 结构中，被监视文件的信息则保存在 `epitem` 结构中（一对多关系）。
- 由于在执行 `epoll_create` 和 `epoll_ctl` 时已经把用户模式的信息保存到内核了，所以之后即便反复调用 `epoll_wait`，也不会重复拷贝参数、扫描文件描述符、频繁操作等待队列。

**epoll 的性能优势核心在于回调机制：**
- select/poll 在"醒着"的时候要遍历整个 fd 集合，而 epoll 在"醒着"的时候只需判断就绪链表是否为空。设备就绪时通过回调函数将就绪 fd 放入就绪链表并唤醒 epoll_wait 中睡眠的进程，节省了大量 CPU 时间。
- select/poll 每次调用都要把 fd 集合从用户态往内核态拷贝一次，而 epoll 只需要一次拷贝，将 current 往等待队列上也只挂一次。

---

### 五、Netty 的核心组件

#### 5.1 EventLoop 与 EventLoopGroup

`EventLoop` 是 Netty 处理 I/O 事件的核心抽象，负责控制流、多线程处理与并发：

- 一个 `EventLoopGroup` 包含一个或多个 `EventLoop`
- 一个 `EventLoop` 在其生命周期内只和一个 Thread 绑定
- 所有由 `EventLoop` 处理的 I/O 事件都将在它专有的 Thread 上被处理
- 一个 `Channel` 在其生命周期内只注册于一个 `EventLoop`（一个 Channel 可理解为一个连接）
- 一个 `EventLoop` 可能被分配给多个 `Channel`——在这种设计中，给定 Channel 的 I/O 操作都由相同的 Thread 执行，实际上消除了对于同步的需要
- `EventLoop` 本身只由一个线程驱动，处理一个 Channel 的所有 I/O 事件，且在整个生命周期内不会改变

#### 5.2 Channel 与 ChannelPipeline

- **Channel** 对应网络 Socket，每个 Channel 关联一个 `ChannelPipeline` 和 `ChannelConfig`。
- **ChannelPipeline** 是 ChannelHandler 的容器，消息在 Pipeline 中流经一系列 Handler 进行处理。
- **ChannelFuture** 提供异步通知机制，与 `ChannelFutureListener` 结合构成了 Netty 的关键构件之一。

---

### 六、ByteBuf：Netty 的数据容器

Netty 的 `ByteBuf` 相比 JDK 原生的 `ByteBuffer` 有诸多优势：

- 可以被用户自定义的缓冲区类型扩展
- 通过内置的复合缓冲区类型实现了透明的零拷贝
- 容量可以按需增长（类似 JDK 的 StringBuilder）
- 在读和写两种模式之间切换不需要调用 `ByteBuffer.flip()` 方法
- 读和写使用了不同的索引
- 支持方法的链式调用
- 支持引用计数
- 支持池化

---

### 七、对象池化技术 PooledByteBufAllocator

Netty 通过引用计数（`ReferenceCounted` 接口）实现对象的池化管理：

- 非池化场景可使用 `Unpooled.copiedBuffer("Netty rocks!", CharsetUtil.UTF_8)`
- 由于采用引用计数，需要在消费完消息之后调用 `ReferenceCountUtil.release(msg)`
- 可通过 `java -Dio.netty.leakDetectionLevel=ADVANCED` 设置泄露检测级别

<img src="{{ site.baseurl }}/img/leak_level.jpg" width="600px" />

---

### 八、ChannelHandler、ChannelPipeline 与 ChannelHandlerContext

Netty 的 Handler 体系是理解其消息处理模型的关键：

- 每个 `ChannelHandler` 都会被分配一个 `ChannelHandlerContext`
- 通过 Channel 或 Handler 调用 `write` 会将消息传递给整个 Pipeline；但通过 `ChannelHandlerContext` 的 `write` 只会传递给对应 Handler 之后的 Handler
- **SimpleChannelInboundHandler\<T\>** 是最常用的入站 Handler 基类。继承它后只需重写 `channelRead0(ChannelHandlerContext, T)` 方法即可，除了不要阻塞当前 I/O 线程之外，具体实现完全取决于业务需求
- **ChannelOutboundHandlerAdapter** 中几乎所有方法都会传入 `ChannelPromise` 实例。作为 `ChannelFuture` 的子类，`ChannelPromise` 也可以被分配用于异步通知的监听器：

```shell
promise.addListener(new ChannelFutureListener() {
@Override
public void operationComplete(ChannelFuture f) {
if (!f.isSuccess()) { f.cause().printStackTrace();
                        f.channel().close();
                    }
}); 
```

---

### 九、EventLoop 与线程模型

Netty 的线程模型本质上是创建包含少量线程的 `EventLoop` 线程池 `EventLoopGroup`，一个 `EventLoop` 管理多个 Channel，实际上就是 I/O 多路复用的体现。

<img src="{{ site.baseurl }}/img/eventLoop.jpg" width="600px" />

---

### 十、Bootstrap 引导类

**为什么引导类是 Cloneable 的？** 有时需要创建多个具有相似或相同配置的 Channel。为支持这种模式而不需要为每个 Channel 都创建并配置一个新的引导类实例，`AbstractBootstrap` 被标记为 `Cloneable`。在一个已配置完成的引导类实例上调用 `clone()` 将返回另一个可立即使用的引导类实例。

需要注意的是，这种方式只会创建引导类实例的 EventLoopGroup 的一个**浅拷贝**，后者将在所有克隆的 Channel 实例之间共享。这是可以接受的，因为通常这些克隆的 Channel 的生命周期都很短暂，典型场景是创建一个 Channel 以进行一次 HTTP 请求。

关于 **ServerBootstrap**：服务器需要两组不同的 Channel。第一组只包含一个 `ServerChannel`，代表服务器自身的已绑定到某个本地端口的正在监听的套接字。第二组包含所有已创建的用来处理传入客户端连接的 Channel（每个服务器已接受的连接都有一个对应的 Channel）。

---

### 十一、Netty 的设计哲学

从高层次角度来看，Netty 解决了两个相应的关注领域：

- **技术层面**：基于 Java NIO 的异步和事件驱动实现，保证了高负载下应用程序性能的最大化和可伸缩性。
- **架构层面**：包含了一组设计模式，将应用程序逻辑从网络层解耦，简化了开发过程，同时最大限度地提高了可测试性、模块化以及代码的可重用性。

#### 不使用 Netty 的原生 NIO

<img src="{{ site.baseurl }}/img/nio-selector.jpg" width="600px" />

---

### 十二、SSL/TLS 支持

Netty 提供了使用 OpenSSL 工具包的 SSLEngine 实现（`OpenSslEngine`），相比 JDK 提供的 SSLEngine 实现有更好的性能。如果 OpenSSL 库可用，可以将 Netty 应用程序配置为默认使用 `OpenSslEngine`；如果不可用，Netty 会回退到 JDK 实现。无论使用哪种实现，SSL API 和数据流都是一致的。

<img src="{{ site.baseurl }}/img/ssl_tls.jpg" width="600px" />

```shell
SelfSignedCertificate cert = new SelfSignedCertificate();
SslContext context = SslContext.newServerContext(cert.certificate(), cert.privateKey());

SSLEngine engine = context.newEngine(ch.alloc());
engine.setUseClientMode(false);
ch.pipeline().addFirst(new SslHandler(engine));
```

---

### 十三、空闲连接检测与超时处理

及时检测空闲连接并释放资源是保证服务稳定性的重要手段。Netty 内置了以下 Handler：

- `IdleStateHandler(0, 0, 60, TimeUnit.SECONDS)` —— 检测读写空闲
- `ReadTimeoutHandler` —— 读超时时触发 `exceptionCaught()`
- `WriteTimeoutHandler` —— 写超时时触发 `exceptionCaught()`

---

### 十四、写大数据

当需要传输大文件或大量数据流时，Netty 提供了分块传输的支持：

- **ChunkedFile**：从文件中逐块获取数据，适用于平台不支持零拷贝或需要转换数据的场景
- **ChunkedNioFile**：类似 ChunkedFile，但使用 FileChannel
- **ChunkedStream**：从 InputStream 中逐块传输内容
- **ChunkedNioStream**：从 ReadableByteChannel 中逐块传输内容

```shell 
public final class WriteStreamHandler extends ChannelInboundHandlerAdapter {
    @Override
    public void channelActive(ChannelHandlerContext ctx)throws Exception {
        super.channelActive(ctx);
        ctx.writeAndFlush(
        new ChunkedStream(new FileInputStream(file)));
    } 
}
```

---

### 十五、WebSocket 支持

#### 15.1 WebSocketFrame 类型

- **BinaryWebSocketFrame**：包含二进制数据
- **TextWebSocketFrame**：包含文本数据
- **ContinuationWebSocketFrame**：包含属于上一个 BinaryWebSocketFrame 或 TextWebSocketFrame 的后续数据
- **CloseWebSocketFrame**：表示 CLOSE 请求，包含关闭状态码和原因
- **PingWebSocketFrame**：请求传输一个 PongWebSocketFrame
- **PongWebSocketFrame**：作为 PingWebSocketFrame 的响应被发送

#### 15.2 WebSocket 示例

下面展示了一个完整的 WebSocket 服务端 Pipeline 配置：

```shell
ChannelPipeline pipeline = ch.pipeline();
# http编解码
pipeline.addLast(new HttpServerCodec());
# 写入一个文件的内容
pipeline.addLast(new ChunkedWriteHandler());
# 将一个 HttpMessage 和跟随它的多个 HttpContent 聚合
# 为单个 FullHttpRequest 或者 FullHttpResponse(取决于它是被用来处理请求还是响应)。
# 安装了这个之后， ChannelPipeline 中的下一个 ChannelHandler 将只会 收到完整的 HTTP 请求或响应
pipeline.addLast(new HttpObjectAggregator(64 * 1024));
# 如果是/ws请求就交个下个handler，否则HTTP handler来处理
pipeline.addLast(new HttpRequestHandler("/ws"));
# 按照 WebSocket 规范的要求，处理 WebSocket 升级握手、 PingWebSocketFrame 、 PongWebSocketFrame 和 CloseWebSocketFrame
pipeline.addLast(new WebSocketServerProtocolHandler("/ws"));
# 处理 TextWebSocketFrame 和握手完成事件
pipeline.addLast(new TextWebSocketFrameHandler(group));
```

在从标准 HTTP/HTTPS 协议切换到 WebSocket 时，使用一种称为**升级握手**的机制。因此，使用 WebSocket 的应用程序始终以 HTTP/S 作为开始，然后再执行升级。

#### 15.3 HTTP 协议中的 Expect: 100-continue

HTTP/1.1 协议中设计 `100 (Continue)` 状态码的目的是：在客户端发送 Request Message 之前，允许客户端先判定服务器是否愿意接受其消息主体（基于 Request Headers）。即客户端在 POST 较大数据到服务端之前，允许双方先"握手"——如果匹配上了，客户端才开始发送较大数据。这样做是因为如果客户端直接发送请求数据而服务器又拒绝该请求，会带来很大的资源开销。

**参考：** <https://blog.csdn.net/skh2015java/article/details/88723028>

#### 15.4 WebSocket 升级过程

```shell
# req
GET /chat HTTP/1.1
Host: server.example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: x3JJHMbDL1EzLkh9GBhXDw==
Sec-WebSocket-Protocol: chat, superchat
Sec-WebSocket-Version: 13
Origin: http://example.com

# resp
Sec-WebSocket-Key: x3JJHMbDL1EzLkh9GBhXDw==
Sec-WebSocket-Protocol: chat, superchat
Sec-WebSocket-Version: 13
```

**参考：** <http://www.xiaosongit.com/index/detail/id/645.html>

---

### 十六、总结

Netty 之所以能成为 Java 网络编程的事实标准，在于它在多个层面做到了极致：

- **内存管理**：借鉴 jemalloc 的 Arena/Chunk/Page/SubPage 分层设计，配合池化与引用计数，大幅降低了 GC 压力
- **I/O 模型**：封装了 epoll 等高性能 I/O 多路复用机制，通过 EventLoop 消除了线程同步的复杂性
- **零拷贝**：从操作系统到应用层多维度的零拷贝优化
- **协议支持**：内置 HTTP、WebSocket、SSL/TLS 等主流协议的编解码器
- **架构设计**：通过 ChannelPipeline 的责任链模式实现了高度模块化和可扩展性

理解 Netty 的这些设计，不仅有助于高效使用该框架，更能深化对高性能网络编程本质的理解。

**PCB**（Process Control Block）—— 操作系统中进程的核心数据结构，每个网络连接在 OS 层面都对应着进程/线程资源的管理。
