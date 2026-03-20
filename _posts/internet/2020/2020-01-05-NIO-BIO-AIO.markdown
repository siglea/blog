---
layout: post
title:  "Java IO 模型详解：BIO、NIO 与 AIO 的原理、区别与实战"
date:   2019-11-12 11:25:00 +0900
comments: true
tags:
- 网络
- Java
categories:
- 技术
---

Java 的 IO 模型经历了从 BIO 到 NIO 再到 AIO 的演进，每一次升级都是为了更高效地处理网络通信和文件操作。理解这三种 IO 模型的原理和适用场景，是构建高性能 Java 网络应用的基础。本文将从概念对比出发，深入讲解 NIO 的核心组件（Channel、Buffer、Selector），并通过完整的代码示例展示 AIO 和 NIO 多路复用的实现方式。

---

### 一、BIO、NIO、AIO 概念对比

在开始之前需要明确一点：**即便是 NIO，本地文件 IO 依然是 Block 操作的，NIO 主要是解决网络 IO 的问题。** 而且本质都需要操作系统层次的支持。

#### 1.1 三种模型的区别

- **BIO（Blocking IO）**：传统的 `java.io` 包，基于流模型实现，交互方式是同步阻塞的。在读入输入流或写出输出流时，线程会一直阻塞在那里，直到读写动作完成。优点是代码简单直观；缺点是 IO 效率和扩展性很低，容易成为应用性能瓶颈。

- **NIO（Non-blocking IO）**：Java 1.4 引入的 `java.nio` 包，提供了 Channel、Selector、Buffer 等新的抽象，可以构建多路复用的、同步非阻塞 IO 程序，同时提供了更接近操作系统底层高性能的数据操作方式。

- **AIO（Asynchronous IO）**：Java 1.7 引入，是 NIO 的升级版本，提供了异步非阻塞的 IO 操作方式。异步 IO 是基于事件和回调机制实现的，应用操作之后会直接返回，不会阻塞在那里，当后台处理完成后操作系统会通知相应的线程进行后续操作。

- 深入理解 BIO、NIO、AIO：<https://zhuanlan.zhihu.com/p/51453522>

#### 1.2 结合 select/poll/epoll 理解 NIO

NIO 的多路复用能力在底层依赖操作系统提供的 select/poll/epoll 等系统调用。Selector 本质上就是对这些系统调用的 Java 封装。

参考：<https://www.jianshu.com/p/ef418ccf2f7d>

---

### 二、Stream（BIO）vs Channel（NIO）

从编程模型上看，BIO 和 NIO 的核心区别体现在 Stream 和 Channel 的差异上：

| 特性 | Stream（BIO） | Channel（NIO） |
|------|--------------|----------------|
| 方向 | 单向（InputStream / OutputStream） | 双向（同时支持读写） |
| 阻塞 | 阻塞式 | 支持非阻塞 |
| 数据单位 | 字节/字符流 | 数据块（Buffer） |
| 异步支持 | 不支持 | 支持 |

NIO 流是以数据块为单位来处理的，缓冲区就是用于读写的数据块。缓冲区的 IO 操作由底层操作系统实现，效率很高。

参考：
- 各种 Channel Demo：<https://blog.csdn.net/dd864140130/article/details/50327649>
- Channel & Buffer 的使用：<https://www.cnblogs.com/fwnboke/p/8529604.html>

---

### 三、Buffer 的读写机制

Buffer 是 NIO 中最核心的概念之一。它相当于在操作系统与程序之间开辟了一片共享的缓冲区进行读写，效率远高于传统的流式操作。

由于 Buffer 支持读写两种操作且共用同一块缓冲区，在读写模式切换时需要进行相应的状态转换。

#### 3.1 三个关键属性

- **position**：读的时候表示可以从哪里开始读，写的时候表示现在可以从哪里开始写
- **limit**：读的时候表示最大可读位置，写的时候表示最大可写位置
- **capacity**：缓冲区的总容量，创建后不可改变

#### 3.2 flip() 与 clear()

这两个方法是 Buffer 读写模式切换的关键。无论读写，position 都要从 0 开始：

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

- `flip()`：从写模式切换到读模式。将 limit 设为当前 position（即已写入数据的末尾），将 position 重置为 0（从头开始读）
- `clear()`：从读模式切换到写模式。将 position 重置为 0，将 limit 设为 capacity（可以写满整个缓冲区）

参考：
- <https://www.cnblogs.com/yaowen/p/9173443.html>
- <https://blog.csdn.net/u013096088/article/details/78638245>

---

### 四、Scatter 与 Gather

NIO 还提供了分散读取和聚集写入的能力：

- **Scatter（分散读取）**：允许将一个 Channel 中的数据分散地依次写入多个 Buffer 中存储
- **Gather（聚集写入）**：允许将多个 Buffer 中的数据按某种顺序写入一个 Channel 中

这在处理具有固定格式的协议数据时非常有用，可以将消息头和消息体分别读入不同的 Buffer。

参考：<https://blog.csdn.net/lemon89/article/details/47152635>

#### allocateDirect 直接缓冲区

`ByteBuffer.allocateDirect()` 创建的是直接缓冲区，它使用的是堆外内存（Native Memory），避免了 JVM 堆和操作系统之间的数据拷贝，适合大量 IO 操作的场景。但分配和回收的成本较高，适合长期使用的缓冲区。

参考：<https://www.jianshu.com/p/c0e7462f9e1d>

---

### 五、AIO 实战：AsynchronousServerSocketChannel

AIO 是真正的异步 IO，`accept()` 和 `read()/write()` 都不会阻塞当前线程。以下是一个简单的 AIO 服务端示例：

```java
import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.AsynchronousServerSocketChannel;
import java.nio.channels.AsynchronousSocketChannel;
import java.util.concurrent.Future;
 
public class Server {
	public static void main(String[] args) {
		try {
			Server server = new Server();
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
 
	public Server() throws Exception {
		AsynchronousServerSocketChannel serverSocketChannel = AsynchronousServerSocketChannel.open();
		InetSocketAddress inetSocketAddress = new InetSocketAddress("localhost", 80);
		serverSocketChannel.bind(inetSocketAddress);
 
		Future<AsynchronousSocketChannel> accept;
 
		while (true) {
			// accept()不会阻塞。
			accept = serverSocketChannel.accept();
 
			System.out.println("=================");
			System.out.println("服务器等待连接...");
			AsynchronousSocketChannel socketChannel = accept.get();// get()方法将阻塞。
 
			System.out.println("服务器接受连接");
			System.out.println("服务器与" + socketChannel.getRemoteAddress() + "建立连接");
 
			ByteBuffer buffer = ByteBuffer.wrap("demo".getBytes());
			Future<Integer> write=socketChannel.write(buffer);
			
			while(!write.isDone()) {
				Thread.sleep(10);
			}
			
			System.out.println("服务器发送数据完毕.");
			socketChannel.close();
		}
	}
}
```

这个示例中，`serverSocketChannel.accept()` 返回一个 `Future` 对象而不会阻塞，真正的阻塞发生在 `accept.get()` 调用处。这种模式允许在等待连接的同时做其他事情（虽然本例中没有展示）。在实际项目中，通常会使用 `CompletionHandler` 回调模式来替代 Future 轮询。

---

### 六、NIO 多路复用实战：ServerSocketChannel + Selector

以下是一个完整的 NIO 多路复用服务端示例，展示了如何用一个线程处理多个客户端连接：

```java
import java.io.IOException;
import java.net.Inet4Address;
import java.net.InetSocketAddress;
import java.net.ServerSocket;
import java.net.SocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.*;
import java.util.Iterator;
import java.util.Set;

public class SelectorServer {
    private static int LISTEN_PORT = 5300;
    public static void main(String[] args) {
         /*
        ServerSocketChannel
        ServerSocket
        SocketChannel
        Selector
        SelectionKey
         */
        try {
            ServerSocketChannel ssc = buildServerSocketChannel();
 
            Selector selector = Selector.open();
            SelectionKey skey = ssc.register( selector, SelectionKey.OP_ACCEPT );
 
            ByteBuffer echoBuffer = ByteBuffer.allocate(128);
            printSelectorKeys(selector);
            System.out.println("channel 准备就绪！");
            while(true) {
                int num = selector.select();//获取通道内是否有选择器的关心事件
                if (num < 1) {
                    continue;
                }
                Set<SelectionKey> selectedKeys = selector.selectedKeys();//获取通道内关心事件的集合
                Iterator<SelectionKey> it = selectedKeys.iterator();
                while (it.hasNext()) {
                    //遍历每个key
                    SelectionKey key = it.next();
                    it.remove();
                    System.out.println("key hashCode=" + key.hashCode());
                    if (key.isAcceptable()) {
                        // 有新的socket链接进来
                        ServerSocketChannel serverChanel = (ServerSocketChannel)key.channel();
                        SocketChannel sc = serverChanel.accept();
                        sc.configureBlocking( false );
                        SelectionKey newKey = sc.register( selector, SelectionKey.OP_READ );
                        System.out.println( "Got connection from "+sc );
                        printSelectorKeys(selector);
                    }
                    if (key.isReadable()) {
                        // 有请求进来
                        SocketChannel sc = (SocketChannel)key.channel();
                        System.out.println("address:" + sc.socket().getPort());
                        int bytesEchoed = 0;
                        while((bytesEchoed = sc.read(echoBuffer))> 0){
                            System.out.println("bytesEchoed:"+bytesEchoed);
                        }
                        echoBuffer.flip();
                        if (bytesEchoed == -1) {
                            System.out.println("connect finish!over!");
                            sc.close();
                            printSelectorKeys(selector);
                            break;
                        }
                        byte [] content = new byte[echoBuffer.limit()];
                        echoBuffer.get(content);
                        String result=new String(content, "utf-8");
                        doPost(result,sc);
                        echoBuffer.clear();
                    }
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
 
    }
 
    private static void printSelectorKeys(Selector selector) {
        Set<SelectionKey> keys = selector.keys();
        Iterator<SelectionKey> iterator = keys.iterator();
        while (iterator.hasNext()) {
            SelectionKey key = iterator.next();
            System.out.println("all:selectKey hashCode=" + key.hashCode());
        }
    }
 
    private static void doPost(String result, SocketChannel sc) {
        System.out.println(result);
    }
 
    private static ServerSocketChannel buildServerSocketChannel() throws IOException {
        ServerSocketChannel channel = ServerSocketChannel.open();
        channel.configureBlocking( false );//使通道为非阻塞
        ServerSocket ss = channel.socket();//创建基于NIO通道的socket连接
        ss.bind(new InetSocketAddress(LISTEN_PORT));//新建socket通道的端口
        //将NIO通道选绑定到择器,当然绑定后分配的主键为skey
        return channel;
    }
    private static void register(ServerSocketChannel ssc, Selector selector, int ops) throws ClosedChannelException {
        SelectionKey key = ssc.register(selector, ops);
        System.out.println("selectKey hashCode=" + key.hashCode());
    }
}
```

这段代码的核心工作流程：

1. **创建 ServerSocketChannel** 并设置为非阻塞模式
2. **创建 Selector** 并将 ServerSocketChannel 注册到 Selector 上，关注 `OP_ACCEPT` 事件
3. **事件循环**：调用 `selector.select()` 阻塞等待事件到达
4. **处理 Accept 事件**：接受新连接，将新的 SocketChannel 注册到 Selector 上，关注 `OP_READ` 事件
5. **处理 Read 事件**：读取客户端发送的数据，通过 Buffer 进行数据交换

这就是 NIO 多路复用的核心——**一个 Selector 线程可以同时监听多个 Channel 的 IO 事件**，避免了为每个连接创建一个线程的开销，是构建高并发网络服务的基础模式。

---

### 七、总结

| 模型 | 同步/异步 | 阻塞/非阻塞 | 适用场景 |
|------|----------|------------|---------|
| BIO | 同步 | 阻塞 | 连接数少、对延迟不敏感的场景 |
| NIO | 同步 | 非阻塞 | 连接数多、但每个连接传输数据量不大的场景（如聊天服务器） |
| AIO | 异步 | 非阻塞 | 连接数多且每个连接传输数据量大的场景（如文件服务器） |

在实际项目中，直接使用 NIO 编程较为复杂（需要处理半包/粘包、连接管理等问题），因此通常会使用 Netty 这样的网络框架来屏蔽底层细节。但理解 BIO/NIO/AIO 的原理，是深入理解 Netty 等框架设计思想的前提。
