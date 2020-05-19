---
layout: post
title:  "NIO-BIO-AIO"
date:   2019-11-12 11:25:00 +0900
comments: true
tags:
- newSQL NoSQL 
categories:
- 技术
---
#### 写在前面
- 即便是NIO，本地文件IO依然是Block操作的，NIO主要是解决网络IO的问题。
- 本质都是需要操作系统层次的支持。

#### BIO、NIO、AIO区别
- BIO 就是传统的 java.io 包，它是基于流模型实现的，交互的方式是同步、阻塞方式，也就是说在读入输入流或者输出流时，在读写动作完成之前，线程会一直阻塞在那里，它们之间的调用时可靠的线性顺序。它的有点就是代码比较简单、直观；缺点就是 IO 的效率和扩展性很低，容易成为应用性能瓶颈。
- NIO 是 Java 1.4 引入的 java.nio 包，提供了 Channel、Selector、Buffer 等新的抽象，可以构建多路复用的、同步非阻塞 IO 程序，同时提供了更接近操作系统底层高性能的数据操作方式。
- AIO 是 Java 1.7 之后引入的包，是 NIO 的升级版本，提供了异步非堵塞的 IO 操作方式，所以人们叫它 AIO（Asynchronous IO），异步 IO 是基于事件和回调机制实现的，也就是应用操作之后会直接返回，不会堵塞在那里，当后台处理完成，操作系统会通知相应的线程进行后续的操作。
- 深入理解BIO、NIO、AIO <https://zhuanlan.zhihu.com/p/51453522>

#### 结合select/poll/epoll看NIO
<https://www.jianshu.com/p/ef418ccf2f7d>

#### Stream（BIO) 与 Channel (NIO)
- Stream不支持异步
- Channel同时支持读写
- NIO流是以数据块为单位来处理，缓冲区就是用于读写的数据块。缓冲区的IO操作是由底层操作系统实现的，效率很快。
- 各种Channel Demo <https://blog.csdn.net/dd864140130/article/details/50327649>
- Channel & Buffer的使用<https://www.cnblogs.com/fwnboke/p/8529604.html>
#### Buffer的读取与写入
- Buffer相当于，操作系统与程序之间共同开辟了一份缓冲区共同读写，效率更高
- 本质上Buffer支持读写，又共用同一个缓冲区，在读写切换时确实需要进行相关操作
- 3个重要的属性
 - position:读的时候表示可以从哪里开始读，写的时候表示现在可以从哪里开始写。
 - limit:读的时候表示可以最大可读位置，写的时候表示最大可写的位置。
 - capacity：容量
- flip() & clear()，不论读写position都要从0开始
```java
class Buffer{
public final Buffer flip() {
        limit = position;
        position = 0;
        mark = -1;
        return this;
}
public final Buffer clear() {
        position = 0;
        limit = capacity;
        mark = -1;
        return this;
    }
}
```
- 参考
    - <https://www.cnblogs.com/yaowen/p/9173443.html>
    - <https://blog.csdn.net/u013096088/article/details/78638245>
    
#### Java NIO：Scatter 与 Gather
- Scatter 是指允许将一个channel中的数据分散的依次写入多个buffer中存储
- Gather 是指允许将多个buffer中的数据按某种顺序写入一个channel中
- <https://blog.csdn.net/lemon89/article/details/47152635>




https://www.jianshu.com/p/c0e7462f9e1d

https://blog.csdn.net/QuinnNorris/article/details/81129852

Reactor