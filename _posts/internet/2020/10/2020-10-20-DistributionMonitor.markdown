---
layout: post
title:  "分布式监控"
date:   2019-11-12 11:25:00 +0900
comments: true
tags:
- Java
- 分布式
categories:
- 技术
---
#### 微服务中的监控分根据作用领域分为三大类，Logging，Tracing，Metrics。
- Logging - 用于记录离散的事件。例如，应用程序的调试信息或错误信息。它是我们诊断问题的依据。比如我们说的ELK就是基于Logging。
- Metrics - 用于记录可聚合的数据。例如，队列的当前深度可被定义为一个度量值，在元素入队或出队时被更新；HTTP 请求个数可被定义为一个计数器，新请求到来时进行累。prometheus专注于Metrics领域。
- Tracing - 用于记录请求范围内的信息。例如，一次远程方法调用的执行过程和耗时。它是我们排查系统性能问题的利器。最常用的有Skywalking，ping-point，zipkin。

#### 参考
 - 一些好用的开源监控工具汇总 
 <https://mp.weixin.qq.com/s/3eDrbITbi66e3dzwYJPmeQ>
 
 - 基于SkyWalking的分布式跟踪系统
 <https://mp.weixin.qq.com/s?__biz=MzAwMTk4NjM1MA==&mid=2247484337&amp;idx=1&amp;sn=e9d5ce0423b70f73279fc86011085d44&source=41>