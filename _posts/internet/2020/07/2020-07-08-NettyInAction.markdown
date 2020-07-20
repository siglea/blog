---
layout: post
title:  "Netty In Action"
date:   2020-07-08 19:18:00 +0900
comments: true
tags:
- Java
- 网络
categories:
- 技术
---
#### 其他
- Netty实战 <https://mp.weixin.qq.com/s/OFG6tD9YRbII3BgjF4IKRg>
- Java网络编程与NIO，多看几遍 <https://www.cnblogs.com/itxiaok/category/1395489.html>
- jemalloc之arena、chunk、page、subpage <https://www.jianshu.com/p/f1988cc08dfd>
- 内存规格、缓存&结构、chunk、arena、page、subpage等概念介绍 <https://blog.csdn.net/qq_33347239/article/details/104270629>
    - Arena
      - 简单来说，Arena就是一个内存分配器，所有分配的内存都是由Arena维护的，并且一般会有多个，目的是减少锁竞争。
        而netty则是对jemalloc的Arena进行能更加具体的实现，也就是netty中的PoolArena。
    - Chunk
      - chunk是Netty向操作系统申请内存的最小调度单位，根据上图，chunk大小固定为16mB，也就是说，Netty每次向操作系统申请内存最小为16mB。
    - Page
      - 上面说了一个chunk大小是16mb，如果Netty每次分配一个ByteBuf，都用掉一个chunk的大小，那显然太浪费了。
      - 于是设计者们就决定将一个chunk划分为2048个Page，每个Page大小为8kb，Page是给ByteBuf分配内存的最小调度单位，尽管还有更小的subpage级别，但是分配subpage时，仍然需要先拿到一个page。
      - 当ByteBuf需要申请的内存大小（必定是2的幂次方） >= 8kb时，会先取一个chunk，然后会以page级别分配内存，最后将当前chunk标记为“使用了一个部分”，然后放进对应占用率的chunkList。
    - SubPage
      - 当ByteBuf需要申请的内存大小（必定是2的幂次方）< 8kb时，比如现在需要size=2kb，则会先取一个chunk，然后再取一个page，然后将page分成4份（pageSize/size），每一份为2kb，然后取其中一份给ByteBuf初始化。
      - 之后就是一个自底向上标记的过程了，将当前使用的一份subpage标记为“已使用”，上一层page标记为“部分使用”，再上一级chunk标记为“部分使用”，最终也是将chunk放进对应占用率的chunkList。
- 关于OS Page Cache的简单介绍，同时再一次介绍了kafka的零拷贝 <https://www.cnblogs.com/leadership/p/12349486.html>

#### Netty的零拷贝体现在多个方面
1. NIO 的基于mmap的DirectMemory
2. FileRegion 的基于sendFile的transferTo
3. CompositeByteBuf的wrap数组合并与slice数组分拆

#### NIO Selector
- linux系统下sun.nio.ch.DefaultSelectorProvider.create(); 会生成一个sun.nio.ch.EPollSelectorProvider类型的SelectorProvider。
  或者在META-INF/services包含有一个java.nio.channels.spi.SelectorProvider提供类配置文件
  
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

- EPollSelectorImpl中初始化epoll相关方法

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
- Selector中维护3个特别重要的SelectionKey集合，分别是
    - keys：所有注册到Selector的Channel所表示的SelectionKey都会存在于该集合中。keys元素的添加会在Channel注册到Selector时发生。
    - selectedKeys：该集合中的每个SelectionKey都是其对应的Channel在上一次操作selection期间被检查到至少有一种SelectionKey中所感兴趣的操作已经准备好被处理。该集合是keys的一个子集。
    - cancelledKeys：执行了取消操作的SelectionKey会被放入到该集合中。该集合是keys的一个子集。
- 参考 <https://www.cnblogs.com/itxiaok/p/10357828.html>

#### 再说epoll
- epoll相关系统调用是在Linux 2.5 后的某个版本开始引入的。该系统调用针对传统的select/poll不足，设计上作了很大的改动。select/poll 的缺点在于:
    - 每次调用时要重复地从用户模式读入参数，并重复地扫描文件描述符。
    - 每次在调用开始时，要把当前进程放入各个文件描述符的等待队列。在调用结束后，又把进程从各个等待队列中删除。
- epoll 是把 select/poll 单个的操作拆分为 1 个 epollcreate，多个 epollctrl和一个 wait。
    此外，操作系统内核针对 epoll 操作添加了一个文件系统，每一个或者多个要监视的文件描述符都有一个对应的inode 节点，
    主要信息保存在 eventpoll 结构中。而被监视的文件的重要信息则保存在 epitem 结构中，是一对多的关系。
    由于在执行 epollcreate 和 epollctrl 时，已经把用户模式的信息保存到内核了， 所以之后即便反复地调用 epoll_wait，
    也不会重复地拷贝参数，不会重复扫描文件描述符，也不反复地把当前进程放入/拿出等待队列。
- select，poll实现需要自己不断轮询所有fd集合，直到设备就绪，期间可能要睡眠和唤醒多次交替。而epoll其实也需要调用epoll_wait不断轮询就绪链表，
    期间也可能多次睡眠和唤醒交替，但是它是设备就绪时，调用回调函数，把就绪fd放入就绪链表中，并唤醒在epoll_wait中进入睡眠的进程。虽然都要睡眠和交替，
    但是select和poll在“醒着”的时候要遍历整个fd集合，而epoll在“醒着”的时候只要判断一下就绪链表是否为空就行了，这节省了大量的CPU时间。这就是回调机制带来的性能提升。
- select，poll每次调用都要把fd集合从用户态往内核态拷贝一次，并且要把current往设备等待队列中挂一次，而epoll只要一次拷贝，而且把current往等待队列上挂也只挂一次
    （在epoll_wait的开始，注意这里的等待队列并不是设备等待队列，只是一个epoll内部定义的等待队列）。这也能节省不少的开销。

#### Netty的组件
- group() EventLoop -> 控制流、多线程处理、并发
  - 一个 EventLoopGroup 包含一个或者多个 EventLoop;
  - 一个 EventLoop 在它的生命周期内只和一个 Thread 绑定;
  - 所有由 EventLoop 处理的 I/O 事件都将在它专有的 Thread 上被处理;
  - 一个 Channel 在它的生命周期内只注册于一个 EventLoop，一个Channel可以理解为一个用户;
  - 一个 EventLoop 可能会被分配给一个或多个 Channel。 注意，在这种设计中，一个给定 Channel 的 I/O 操作都是由相同的 Thread 执行的，实际上消除了对于同步的需要。
  - EventLoop本身只由一个线程驱动，其处理了一个Channel的所有I/O事件，并且在该EventLoop的整个生命周期内都不会改变。
- channel() Channel -> Socket
    - ChannelPipeline
        - handler() ChannelHandler
    - ChannelConfig
- ChannelFuture -> 异步通知

#### Netty的数据容器ByteBuf
- 它可以被用户自定义的缓冲区类型扩展;
- 通过内置的复合缓冲区类型实现了透明的零拷贝; 
- 容量可以按需增长(类似于 JDK 的 StringBuilder); 
- 在读和写这两种模式之间切换不需要调用 ByteBuffer 的 flip()方法; 
- 读和写使用了不同的索引;
- 支持方法的链式调用;
- 支持引用计数;
- 支持池化。

#### Netty的对象池化技术PooledByteBufAllocator
- 通过引用计数的方式实现 ReferenceCounted
- Unpooled.copiedBuffer("Netty rocks!",CharsetUtil.UTF-8);
- 由于采用引用计数，需要在消费完消息之后调用ReferenceCountUtil.release(msg);
- 可以通过 java -Dio.netty.leakDetectionLevel=ADVANCED 这个参数设置泄露检测级别
<img src="/img/leak_level.jpg" width="600px" />

#### ChannelHandler ChannelPipeline ChannelHandlerContext
- 每个ChannelHandler都会分配一个ChannelHandlerContext
- 通过Channel、Handler的write会传递整个pipe，但是通过context的write只能传递对应Handler之后的handlers
- SimpleChannelInboundHandler<T>，最常见的情况是，你的应用程序会利用一个 ChannelHandler 来接收解码消息，并对该数据应用业务逻辑。要创建一个这样的 ChannelHandler，
    你只需要扩展基类 SimpleChannel- InboundHandler<T>，其中 T 是你要处理的消息的 Java 类型 。
    在这个 ChannelHandler 中， 你将需要重写基类的一个或者多个方法，并且获取一个到 ChannelHandlerContext 的引用， 
    这个引用将作为输入参数传递给 ChannelHandler 的所有方法。在这种类型的 ChannelHandler 中，最重要的方法是 channelRead0(Channel- HandlerContext,T)。除了要求不要阻塞当前的 I/O 线程之外，其具体实现完全取决于你。
- ChannelOutboundHandlerAdapter，几乎所有的 ChannelOutboundHandler 上的方法都会传入一个 ChannelPromise 的实例。
    作为 ChannelFuture 的子类，ChannelPromise 也可以被分配用于异步通知的监听器。
```shell
promise.addListener(new ChannelFutureListener() {
@Override
public void operationComplete(ChannelFuture f) {
if (!f.isSuccess()) { f.cause().printStackTrace();
                        f.channel().close();
                    }
}); 
```
#### EventLoop和线程池
- 本质是创建包含少量的线程EventLoop的线程池EventLoopGroup，一个EventLoop管理多个Channel，
    实际上就是IO多路复用
<img src="/img/eventLoop.jpg" width="600px" />

#### Bootstrap
- 为什么引导类是 Cloneable 的 你有时可能会需要创建多个具有类似配置或者完全相同配置的Channel。为了支持这种模式而又不
    - 需要为每个Channel都创建并配置一个新的引导类实例，AbstractBootstrap被标记为了 Cloneable1。在一个已经配置完成的引导类实例上调用clone()方法将返回另一个可以立即使用的引 导类实例。
    - 注意，这种方式只会创建引导类实例的EventLoopGroup的一个浅拷贝，所以，后者 2将在所有克 隆的Channel实例之间共享。这是可以接受的，因为通常这些克隆的Channel的生命周期都很短暂，一 个典型的场景是——创建一个Channel以进行一次HTTP请求。

#### Netty 设计
- 从高层次的角度来看，Netty 解决了两个相应的关注领域，我们可将其大致标记为技术的和 体系结构的。
    - 首先，它的基于 Java NIO 的异步的和事件驱动的实现，保证了高负载下应用程序 性能的最大化和可伸缩性。
    - 其次，Netty 也包含了一组设计模式，将应用程序逻辑从网络层解耦， 简化了开发过程，同时也最大限度地提高了可测试性、模块化以及代码的可重用性。

####  不使用Netty的NIO
<img src="/img/nio-selector.jpg" width="600px" />

####  Netty 的 OpenSSL/SSLEngine 实现
- Netty 还提供了使用 OpenSSL 工具包(www.openssl.org)的 SSLEngine 实现。这个 OpenSsl-Engine 类提供了比 JDK 提供的 SSLEngine 实现更好的性能。
- 如果 OpenSSL 库可用，可以将 Netty 应用程序(客户端和服务器)配置为默认使用 OpenSslEngine。如果不可用，Netty 将会回退到 JDK 实现。有关配置 OpenSSL 支持的详细说明，参见 Netty 文档: http://netty.io/wiki/forked-tomcat-native.html#wikih2-1。
- 注意，无论你使用 JDK 的 SSLEngine 还是使用 Netty 的 OpenSslEngine，SSL API 和数据流都 是一致的。

<img src="/img/ssl_tls.jpg" width="600px" />

```shell
SelfSignedCertificate cert = new SelfSignedCertificate();
SslContext context = SslContext.newServerContext(cert.certificate(), cert.privateKey());

SSLEngine engine = context.newEngine(ch.alloc());
engine.setUseClientMode(false);
ch.pipeline().addFirst(new SslHandler(engine));
```

#### 检测空闲连接以及超时对于及时释放资源 
- new IdleStateHandler(0, 0, 60, TimeUnit.SECONDS)
- ReadTimeoutHandler exceptionCaught()
- WriteTimeoutHandler exceptionCaught()

#### 写大数据
- ChunkedFile 从文件中逐块获取数据，当你的平台不支持零拷贝或者你需要转换数据时使用
- ChunkedNioFile 和 ChunkedFile 类似，只是它使用了 FileChannel 
- ChunkedStream 从 InputStream 中逐块传输内容 
- ChunkedNioStream 从ReadableByteChannel中逐块传输内容
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
#### WebSocketFrame
- BinaryWebSocketFrame 包含了二进制数据
- TextWebSocketFrame 包含了文本数据
- ContinuationWebSocketFrame 包含属于上一个BinaryWebSocketFrame或TextWebSocket-Frame 的文本数据或者二进制数据
- CloseWebSocketFrame 表示一个 CLOSE 请求，包含一个关闭的状态码和关闭的原因
- PingWebSocketFrame 作为一个对于 PingWebSocketFrame 的响应被发送
- PongWebSocketFrame 请求传输一个 PongWebSocketFrame

#### WebSocket示例
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
在从标准的HTTP或者HTTPS协议切换到WebSocket时，将会使用一种称为升级握手的机制。因此 ，使用WebSocket的应用程序将始终以HTTP/S作为开始，然后再执行升级。这个升级动 作发生的确切时刻特定于应用程序;它可能会发生在启动时，也可能会发生在请求了某个特定的 URL之后。

#### 理解HTTP协议中的 Expect: 100-continue
- HTTP/1.1 协议里设计 100 (Continue) HTTP 状态码的的目的是，在客户端发送 Request Message 之前，HTTP/1.1 协议允许客户端先判定服务器是否愿意接受客户端发来的消息主体（基于 Request Headers）。
- 即， 客户端 在 Post（较大）数据到服务端之前，允许双方“握手”，如果匹配上了，Client 才开始发送（较大）数据。
- 这么做的原因是，如果客户端直接发送请求数据，但是服务器又将该请求拒绝的话，这种行为将带来很大的资源开销。
<https://blog.csdn.net/skh2015java/article/details/88723028>

#### http协议与websocket协议升级过程
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
<http://www.xiaosongit.com/index/detail/id/645.html>

#### 其他
- ChannelFuture 与 ChannelFutureListener相互结合，构成了Netty本身的关键构件之一
- 关于ServerBootStrap，因为服务器需要两组不同的 Channel。第一组将只包含一个 ServerChannel，代表服务 器自身的已绑定到某个本地端口的正在监听的套接字。而第二组将包含所有已创建的用来处理传 入客户端连接(对于每个服务器已经接受的连接都有一个)的 Channel。
- PCB Process Control Block
