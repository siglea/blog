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
- 需要反复看看 <https://www.cnblogs.com/itxiaok/p/10357825.html>
- 相比 select ，poll 有这些优点：
    由于 poll 在 pollfd 里用 int fd 来表示文件描述符而不像 select 里用的 fd_set 来分别表示描述符，所以没有必须小于 1024 的限制，也没有数量限制；
    由于 poll 用 events 表示期待的事件，通过修改 revents 来表示发生的事件，所以不需要像 select 在每次调用前重新设置描述符和期待的事件。
    除此之外，poll 和 select 几乎相同。在 poll 返回后，需要遍历 fdarray 来检查各个 pollfd 里的 revents 是否发生了期待的事件；每次调用 poll 时，
    把 fdarray 复制到内核空间。在描述符太多而每次准备好的较少时，poll 有同样的性能问题。
- epoll 解决了 poll 和 select 的问题：
    - 只在 epoll_ctl 的时候把数据复制到内核空间，这保证了每个描述符和事件一定只会被复制到内核空间一次；每次调用 epoll_wait 都不会复制新数据到内核空间。相比之下，select 每次调用都会把三个 fd_set 复制一遍；poll 每次调用都会把 fdarray 复制一遍。
    - epoll_wait 返回 n ，那么只需要做 n 次循环，可以保证遍历的每一次都是有意义的。相比之下，select 需要做至少 n 次至多 maxfdp1 次循环；poll 需要遍历完 fdarray 即做 nfds 次循环。
    - 在内部实现上，epoll 使用了回调的方法。调用 epoll_ctl 时，就是注册了一个事件：在集合中放入文件描述符以及事件数据，并且加上一个回调函数。一旦文件描述符上的对应事件发生，就会调用回调函数，这个函数会把这个文件描述符加入到就绪队列上。当你调用 epoll_wait 时，它只是在查看就绪队列上是否有内容，有的话就返回给你的程序。select() poll() epoll_wait() 三个函数在操作系统看来，都是睡眠一会儿然后判断一会儿的循环，但是 select 和 poll 在醒着的时候要遍历整个文件描述符集合，而 epoll_wait 只是看看就绪队列是否为空而已。这是 epoll 高性能的理由，使得其 I/O 的效率不会像使用轮询的 select/poll 随着描述符增加而大大降低。
- Epoll的机理，我们便能很容易掌握epoll的用法了。一句话描述就是：三步曲。
  1. epoll_create()系统调用。此调用返回一个句柄，之后所有的使用都依靠这个句柄来标识。
    11. struct rb_root  rbr; 红黑树的根节点，这颗树中存储着所有添加到epoll中的需要监控的事件
    12. struct list_head rdlist; 双链表中则存放着将要通过epoll_wait返回给用户的满足条件的事件
  2. epoll_ctl()系统调用。通过此调用向epoll对象中添加、删除、修改感兴趣的事件，返回0标识成功，返回-1表示失败。
    21. 调用epoll_ctl向epoll对象中添加这100万个连接的套接字
    22. 而所有添加到epoll中的事件都会与设备(网卡)驱动程序建立回调关系，也就是说，当相应的事件发生时会调用这个回调方法。这个回调方法在内核中叫ep_poll_callback,它会将发生的事件添加到rdlist双链表中。
  3. epoll_wait()系统调用。通过此调用收集在epoll监控中已经发生的事件。

### 再次总结
#### 历史
 - select出现是1984年在BSD里面实现的(为了减少数据拷贝带来的性能损坏，内核对被监控的fd_set集合大小做了限制，并且这个是通过宏控制的，大小不可改变(限制为1024))
 - 14年之后也就是1997年才实现了poll，其实拖那么久也不是效率问题， 而是那个时代的硬件实在太弱，一台服务器处理1千多个链接简直就是神一样的存在了，select很长段时间已经满足需求
 - 2002, 大神 Davide Libenzi 实现了epoll
 
#### 区别
- 操作方式：select/poll依靠遍历，而epll靠回调
- IO效率：由于操作方式，select/poll时间复杂度是O(n)，epoll是O(1)
- 数据结构：select(数组)、poll(链表)、epoll(哈希表)
- 最大连接数：由于数据结构的原因，poll/epoll突破了数量的限制，而select只支持1024(2048)
- fd拷贝：select/poll都需要把fd集合从用户态拷贝到内核态，epoll没有描述符个数限制，使用一个文件描述符管理多个描述符，将用户关心的文件描述符的事件存放到内核的一个事件表中，这样在用户空间和内核空间的copy只需一次。
- epoll是通过内核于用户空间mmap同一块内存实现了节省拷贝的动作。

#### 源代码
```java
// select
int select(int maxfdp1,fd_set *readset,fd_set *writeset,fd_set *exceptset,const struct timeval *timeout);
// 主要问题在于在用户态创建fd_set然后拷贝到内核态，再由内核态装配数据后，在用户态中进行遍历
// 并且每次都需要重新初始化fd_set

// poll
int poll(struct pollfd *fds, nfds_t nfds, int timeout);
typedef struct pollfd {        
int fd;                         // 需要被检测或选择的文件描述符        
short events;                   // 对文件描述符fd上感兴趣的事件        
short revents;                  // 文件描述符fd上当前实际发生的事件
} 


// epoll
int epoll_create(int size); //  函数创建一个epoll句柄，参数size表明内核要监听的描述符数量。调用成功时返回一个epoll句柄描述符，失败时返回-1。
int epoll_ctl(int epfd, int op, int fd, struct epoll_event *event);
    // epfd 表示epoll句柄
    // op 表示fd操作类型，有如下3种
        // EPOLL_CTL_ADD   注册新的fd到epfd中
        // EPOLL_CTL_MOD 修改已注册的fd的监听事件
        // EPOLL_CTL_DEL 从epfd中删除一个fd
    // fd 是要监听的描述符
    // event 表示要监听的事件
struct epoll_event {
    __uint32_t events;  /* Epoll events */    
   epoll_data_t data;  /* User data variable */
};
typedef union epoll_data {
    void *ptr;    int fd;
    __uint32_t u32;
    __uint64_t u64;
} epoll_data_t;
int epoll_wait(int epfd, struct epoll_event * events, int maxevents, int timeout);
    // epfd 是epoll句柄
    // events 表示从内核得到的就绪事件集合
    // maxevents 告诉内核events的大小
    // timeout 表示等待的超时事件
```

#### 参考
- IO多路复用的三种机制Select，Poll，Epoll <https://mp.weixin.qq.com/s/UWdZsvPsV46VLpr7qHjgjA>
- IO模型及select、poll、epoll和kqueue的区别 <https://mp.weixin.qq.com/s/R8cA0_1dNujVORionyg_4A>
- Select，Poll，Epoll详解 <https://mp.weixin.qq.com/s/49yzOWWCoo1V1UG7iiJEVg>
- 大量代码 深入分析select&poll&epoll原理 <https://mp.weixin.qq.com/s/HC-xEavwXTypDIRvX0Tu3g>

### 简单总结三者区别
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
- C10K到C10M <http://www.52im.net/thread-561-1-1.html>