---
layout: post
title:  " Jvm垃圾回收与调优 "
date:   2019-11-04 11:25:00 +0900MMMMMMMMMMMMMMMMMMMMMMMMMMMMMJK M
tags:
- java
categories:
- 互联网
---

#### GC的收集算法
- 标记-复制，待回收对象较多，适用于新生代
- 标记-清除
- 标记-压缩

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
- Parallel（并行）收集器
- CMS（并发）收集器
- G1（并发）收集器
- JDK11的ZGC <https://mp.weixin.qq.com/s/KUCs_BJUNfMMCO1T3_WAjw>

##### 参考
- 7种JVM垃圾收集器特点，优劣势、及使用场景 <https://zhuanlan.zhihu.com/p/58896728>
    <http://blog.itpub.net/69917606/viewspace-2656882>
- 深入详解JVM内存模型与JVM参数详细配置 <https://zhuanlan.zhihu.com/p/58896619>
- JVM性能调优的6大步骤，及关键调优参数详解 <https://zhuanlan.zhihu.com/p/58897189>
- 深入剖析JVM：G1收集器+回收流程+推荐用例 <https://zhuanlan.zhihu.com/p/59861022>

#### java 参数

查看JVM使用的默认的垃圾收集器 https://www.cnblogs.com/grey-wolf/p/9217497.html

JVM 参数 https://blog.csdn.net/liyongbing1122/article/details/88716400

关于JVM收集器讲的不错
https://mp.weixin.qq.com/s/1uVK5qL1g1l9ybAB7mwQNw

逃逸分析
