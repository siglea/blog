---
layout: post
title:  "Netty-Mina"
date:   2020-05-18 23:25:00 +0900
comments: true
tags:
- 网络编程 
categories:
- 技术
---
#### 从零开发一个IM服务端  
- 通俗易懂 <http://www.52im.net/forum.php?mod=viewthread&tid=2768&highlight=netty>
- 基于Netty实现海量接入的推送服务技术要点 <http://www.52im.net/forum.php?mod=viewthread&tid=166&highlight=netty>

#### 必读有关“为何选择Netty”的11个疑问及解答
- <http://www.52im.net/forum.php?mod=viewthread&tid=163&highlight=netty>

#### TCP网关
HAProxy nginx LVS
- 生产环境大部分还是采用通过rest方式获取IpList，然后有客户端直接发起长连接的方式
- 京东京麦的生产级TCP网关技术实践总结 <http://www.52im.net/forum.php?mod=viewthread&tid=1243&highlight=netty>
- 一套海量在线用户的移动端IM架构设计实践 <http://www.52im.net/thread-812-1-1.html>

#### Reactor 线程模型
- Reactor 是反应堆的意思，Reactor 模型是指通过一个或多个输入同时传递给服务处理器的服务请求的事件驱动处理模式。
服务端程序处理传入多路请求，并将它们同步分派给请求对应的处理线程，Reactor 模式也叫 Dispatcher 模式，即 I/O 多了复用统一监听事件，收到事件后分发(Dispatch 给某进程)，是编写高性能网络服务器的必备技术之一。
<http://www.52im.net/forum.php?mod=viewthread&tid=2043&highlight=netty>

#### Why Netty?JDK 原生 NIO 程序的问题
- JDK 原生也有一套网络应用程序 API，但是存在一系列问题，主要如下：
    1. NIO 的类库和 API 繁杂，使用麻烦：你需要熟练掌握 Selector、ServerSocketChannel、SocketChannel、ByteBuffer 等。
    1. 需要具备其他的额外技能做铺垫：例如熟悉 Java 多线程编程，因为 NIO 编程涉及到 Reactor 模式，你必须对多线程和网路编程非常熟悉，才能编写出高质量的 NIO 程序。
    1. 可靠性能力补齐，开发工作量和难度都非常大：例如客户端面临断连重连、网络闪断、半包读写、失败缓存、网络拥塞和异常码流的处理等等。NIO 编程的特点是功能开发相对容易，但是可靠性能力补齐工作量和难度都非常大。
    1. JDK NIO 的 Bug：例如臭名昭著的 Epoll Bug，它会导致 Selector 空轮询，最终导致 CPU 100%。官方声称在 JDK 1.6 版本的 update 18 修复了该问题，但是直到 JDK 1.7 版本该问题仍旧存在，只不过该 Bug 发生概率降低了一些而已，它并没有被根本解决。
    
#### Java NIO epoll bug 以及 Netty 的解决之道
- epoll 空轮询导致 CPU 利用率 100% <http://songkun.me/2019/07/26/2019-07-26-java-nio-epoll-bug-and-netty-solution/>
 
#### netty中的epoll实现
- 在java中，IO多路复用的功能通过nio中的Selector提供，在不同的操作系统下jdk会通过spi的方式加载不同的实现，
比如在macos下是KQueueSelectorProvider，KQueueSelectorProvider底层使用了kqueue来进行IO多路复用；
在linux 2.6以后的版本则是EPollSelectorProvider，EPollSelectorProvider底层使用的是epoll。
虽然jdk自身提供了selector的epoll实现，netty仍实现了自己的epoll版本，根据netty开发者在StackOverflow的回答，主要原因有两个：
    - 支持更多socket option，比如TCP_CORK和SO_REUSEPORT
    - 使用了边缘触发（ET）模式
- <https://juejin.im/post/5d46ce64f265da03e05af722>
- ET和LT的区别在于触发事件的条件不同，LT比较符合编程思维（有满足条件的就触发），ET触发的条件更苛刻一些（仅在发生变化时才触发），对使用者的要求也更高，理论效率更高
- 边缘触发和水平触发<https://juejin.im/post/5cdaa67f518825691b4a5cc0>
