---
layout: post
title:  "NIO-BIO-AIO"
date:   2019-11-12 11:25:00 +0900
comments: true
tags:
- Java 
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

#### allocateDirect直接缓冲区
- “IO与NIO ”重点概念整理<https://www.jianshu.com/p/c0e7462f9e1d>

#### AsynchronousServerSocketChannel
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
#### ServerSocketChannel+Selector实现多路复用io
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