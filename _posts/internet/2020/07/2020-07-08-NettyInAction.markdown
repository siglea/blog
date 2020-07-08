---
layout: post
title:  "Netty In Action"
date:   2020-07-08 19:18:00 +0900
comments: true
tags:
- java
- 网络
categories:
- 技术
---
#### Netty的组件
- Channel -> Socket
    - ChannelPipeline
        - ChannelHandler
    - ChannelConfig
- EventLoop -> 控制流、多线程处理、并发
  - 一个 EventLoopGroup 包含一个或者多个 EventLoop;
  - 一个 EventLoop 在它的生命周期内只和一个 Thread 绑定;
  - 所有由 EventLoop 处理的 I/O 事件都将在它专有的 Thread 上被处理;
  - 一个 Channel 在它的生命周期内只注册于一个 EventLoop，一个Channel可以理解为一个用户;
  - 一个 EventLoop 可能会被分配给一个或多个 Channel。 注意，在这种设计中，一个给定 Channel 的 I/O 操作都是由相同的 Thread 执行的，实际上消除了对于同步的需要。
  - EventLoop本身只由一个线程驱动，其处理了一个Channel的所有I/O事件，并且在该EventLoop的整个生命周期内都不会改变。
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

#### Netty的池化技术PooledByteBufAllocator
- 通过引用计数的方式实现 ReferenceCounted
- Unpooled.copiedBuffer("Netty rocks!",CharsetUtil.UTF-8);

#### ChannelHandler ChannelPipeline ChannelHandlerContext
- 每个ChannelHandler都会分配一个ChannelHandlerContext
- 通过Channel、Handler的write会传递整个pipe，但是通过context的write只能传递对应Handler之后的handlers
- SimpleChannelInboundHandler<T>，最常见的情况是，你的应用程序会利用一个 ChannelHandler 来接收解码消息，并对该数据应用业务逻辑。要创建一个这样的 ChannelHandler，
    你只需要扩展基类 SimpleChannel- InboundHandler<T>，其中 T 是你要处理的消息的 Java 类型 。
    在这个 ChannelHandler 中， 你将需要重写基类的一个或者多个方法，并且获取一个到 ChannelHandlerContext 的引用， 
    这个引用将作为输入参数传递给 ChannelHandler 的所有方法。在这种类型的 ChannelHandler 中，最重要的方法是 channelRead0(Channel- HandlerContext,T)。除了要求不要阻塞当前的 I/O 线程之外，其具体实现完全取决于你。

#### Netty 设计
- 从高层次的角度来看，Netty 解决了两个相应的关注领域，我们可将其大致标记为技术的和 体系结构的。
    - 首先，它的基于 Java NIO 的异步的和事件驱动的实现，保证了高负载下应用程序 性能的最大化和可伸缩性。
    - 其次，Netty 也包含了一组设计模式，将应用程序逻辑从网络层解耦， 简化了开发过程，同时也最大限度地提高了可测试性、模块化以及代码的可重用性。


#### 其他
- ChannelFuture 与 ChannelFutureListener相互结合，构成了Netty本身的关键构件之一
- 关于ServerBootStrap，因为服务器需要两组不同的 Channel。第一组将只包含一个 ServerChannel，代表服务 器自身的已绑定到某个本地端口的正在监听的套接字。而第二组将包含所有已创建的用来处理传 入客户端连接(对于每个服务器已经接受的连接都有一个)的 Channel。

####  不使用Netty的NIO
<img src="/img/nio-selector.jpg" width="600px" />