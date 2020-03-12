---
layout: post
title:  " Jvm内存模型、垃圾回收机制与调优 "
date:   2019-11-04 11:25:00
tags:
- JVM
categories:
- 互联网
---

#### GC的收集算法（实战中是集中算法组合使用）
- 标记-复制
    Serial New、Parallel New、Parallel Scavenge New、G1
- 标记-清除
    CMS
- 标记-整理
    Serial Old、Parallel Old、G1

#### 分代（为了更高效的区别回收，G1的分区region也是为了发挥多核并发优势）
- Young Generation
    Eden 伊甸园
    Survivor 幸存者（from/to，S0/S1)    
- Tenured/Old Generation
- Permanent Generation (Java8之前）
- Metaspace (Java8之后）

##### 参考
  JVM的4种垃圾回收算法、垃圾回收机制与总结 <https://zhuanlan.zhihu.com/p/54851319>

#### GC收集器
- Serial（串行）收集器
    新生代、老生代
- Parallel（并行）收集器
    新生代、老生代
- Parallel Scavenge New （GC自适应的调节策略GC Ergonomics）
    新生代、通过调整相关参数，比如新生代的大小，达到以合适的时间和耗时，达到高吞吐量
    吞吐量 = 运行用户代码时间 /（运行用户代码时间 + 垃圾收集时间）
- CMS（Concurrent Mark Sweep 并发）收集器 （并发低停顿收集器 Concurrent Low Pause Collector）
    老生代
- G1（并发）收集器（优先回收价值最大的Region（这也就是Garbage-First名称的来由）
    新生代、老生代
- JDK11的ZGC <https://mp.weixin.qq.com/s/KUCs_BJUNfMMCO1T3_WAjw>

##### 参考
- 7种JVM垃圾收集器特点，优劣势、及使用场景 <https://zhuanlan.zhihu.com/p/58896728>
- 深入理解JVM，7种垃圾收集器 <http://blog.itpub.net/69917606/viewspace-2656882>
- 深入详解JVM内存模型与JVM参数详细配置 <https://zhuanlan.zhihu.com/p/58896619>
    - 堆内存（Heap）此内存区域的唯一目的就是存放对象实例（new的对象），几乎所有的对象实例都在这里分配内存。
    - 方法区（Method Area）方法区也称”永久代“，它用于存储虚拟机加载的类信息、常量、静态变量、是各个线程共享的内存区域。
    - 虚拟机栈(JVM Stack) Java虚拟机栈是线程私有，生命周期与线程相同。创建线程的时候就会创建一个java虚拟机栈。
      虚拟机执行java程序的时候，每个方法都会创建一个栈帧，栈帧存放在java虚拟机栈中，通过压栈出栈的方式进行方法调用。
      栈帧又分为一下几个区域：局部变量表、操作数栈、动态连接、方法出口等。
    - 本地方法栈(Native Stack) 本地方法栈（Native Method Stacks）与虚拟机栈所发挥的作用是非常相似的，其区别不过是虚拟机栈为虚拟机执行Java方法（也就是字节码）服务，而本地方法栈则是为虚拟机使用到的Native方法服务。
    - 程序计数器（PC Register）
      程序计数器就是记录当前线程执行程序的位置，改变计数器的值来确定执行的下一条指令，比如循环、分支、方法跳转、异常处理，线程恢复都是依赖程序计数器来完成。
      Java虚拟机多线程是通过线程轮流切换并分配处理器执行时间的方式实现的。为了线程切换能恢复到正确的位置，每条线程都需要一个独立的程序计数器，所以它是线程私有的。
    - 直接内存
      直接内存并不是虚拟机内存的一部分，也不是Java虚拟机规范中定义的内存区域。jdk1.4中新加入的NIO，引入了通道与缓冲区的IO方式，它可以调用Native方法直接分配堆外内存，这个堆外内存就是本机内存，不会影响到堆内存的大小。
- JVM性能调优的6大步骤，及关键调优参数详解 <https://zhuanlan.zhihu.com/p/58897189>
- 深入剖析JVM：G1收集器+回收流程+推荐用例 <https://zhuanlan.zhihu.com/p/59861022>

#### java 参数
- 查看JVM使用的默认的垃圾收集器 <https://www.cnblogs.com/grey-wolf/p/9217497.html>
- JVM 参数 <https://blog.csdn.net/liyongbing1122/article/details/88716400>

逃逸分析
- <https://blog.csdn.net/w372426096/article/details/80333657>
- <https://blog.csdn.net/hollis_chuang/article/details/80922794>
