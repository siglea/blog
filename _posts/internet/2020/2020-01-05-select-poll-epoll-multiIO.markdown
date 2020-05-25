---
layout: post
title:  "多路复用select poll epoll"
date:   2019-11-12 11:25:00 +0900
comments: true
tags:
- 网络
- 分布式
categories:
- 技术
---
#### 简单总结三者区别
- 一切都与历史有关，都是历史发展造成差异
- select最早出现（1983年在BSD里实现），由以下几个特点
  1. 无论效率如何确实实现了多路复用
  1. 原理也就是内核态监听最多1024个链接，任意一个链接有数据了，通知用户态去遍历所有链接获取数据
  1. 由于编程的原因把1024写在了linux的头文件FD_SETSIZE中
  1. 由于编程的原因数据直接写到了参数的地址上，导致需要每次需要重置参数
- poll 在1997年推出，修复select的两个问题（也是历史原因，当时机器硬件性能不高没有必要修复）
  1. 最大监听连接数修改为在 /proc/sys/fs/file-max 获取
  1. 内核通过修改pollfd.revents反馈其中的就绪时间
  1. 仍然需要遍历，效率仍然低，时间复杂度O(n)
- epoll，革新以上两种方式，内核只返回就绪的那一个链接，不需要遍历，所以效率提升了
  1. epoll其实也需要调用epoll_wait不断轮询就绪链表，期间也可能多次睡眠和唤醒交替，但是它是设备就绪时，调用回调函数，把就绪fd放入就绪链表中，并唤醒在epoll_wait中进入睡眠的进程。
  1. epoll对文件描述符的操作有两种模式：LT（level trigger）和ET（edge trigger）。LT模式是默认模式，LT模式与ET模式的区别如下：
    - LT模式：当epoll_wait检测到描述符事件发生并将此事件通知应用程序，应用程序可以不立即处理该事件。下次调用epoll_wait时，会再次响应应用程序并通知此事件。
    - ET模式：当epoll_wait检测到描述符事件发生并将此事件通知应用程序，应用程序必须立即处理该事件。如果不处理，下次调用epoll_wait时，不会再次响应应用程序并通知此事件。
    - LT模式，LT(level triggered)是缺省的工作方式，并且同时支持block和no-block socket。在这种做法中，内核告诉你一个文件描述符是否就绪了，然后你可以对这个就绪的fd进行IO操作。如果你不作任何操作，内核还是会继续通知你的。
    - ET模式，ET(edge-triggered)是高速工作方式，只支持no-block socket。在这种模式下，当描述符从未就绪变为就绪时，内核通过epoll告诉你。然后它会假设你知道文件描述符已经就绪，并且不会再为那个文件描述符发送更多的就绪通知，直到你做了某些操作导致那个文件描述符不再为就绪状态了(比如，你在发送，接收或者接收请求，或者发送接收的数据少于一定量时导致了一个EWOULDBLOCK 错误）。但是请注意，如果一直不对这个fd作IO操作(从而导致它再次变成未就绪)，内核不会发送更多的通知(only once)。ET模式在很大程度上减少了epoll事件被重复触发的次数，因此效率要比LT模式高。epoll工作在ET模式的时候，必须使用非阻塞套接口，以避免由于一个文件句柄的阻塞读/阻塞写操作把处理多个文件描述符的任务饿死。
    - 在select/poll中，进程只有在调用一定的方法后，内核才对所有监视的文件描述符进行扫描，而epoll事先通过epoll_ctl()来注册一个文件描述符，一旦基于某个文件描述符就绪时，内核会采用类似callback的回调机制，迅速激活这个文件描述符，当进程调用epoll_wait()时便得到通知。(此处去掉了遍历文件描述符，而是通过监听回调的的机制。这正是epoll的魅力所在。)

#### 参考资料
- <https://mp.weixin.qq.com/s/AXJW0Q77yYfld0cFEsLu1A>
- <https://mp.weixin.qq.com/s/71-X1urvqgFG08cxS4TNvA>
- <https://mp.weixin.qq.com/s/zg7Ty_aF-IO0A4w4b5UVjA>
- <https://mp.weixin.qq.com/s/R8cA0_1dNujVORionyg_4A>