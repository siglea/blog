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
ChannelFuture 与 ChannelFutureListener相互结合，构成了Netty本身的关键构件之一
EventLoop本身只由一个线程驱动，其处理了一个Channel的所有I/O事件，并且在该EventLoop的整个生命周期内都不会改变。
Unpooled
