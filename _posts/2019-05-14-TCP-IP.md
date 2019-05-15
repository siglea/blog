##### TCP建立连接的本质含义是？
1.确定通信整个链路的是否接通
2.确定双方信息处理服务准备完毕
3.告知彼此的第一个发送字节的初始序列号，建立连接后对每一个发送的字节都需要以初始序列号为原点进行编号。
4.TCP是双工的，所以建立连接后，两端都是互为客户端服务端

##### 心跳包的本质含义是？
keepalive只是表示网络连接正常
心跳包同时表示应用程序正常
既可以应用层实现，也可以通过KeepAlive参数来设置
应用层实现的优点是可控、可自定义、可方便处理异常、无论传输层协议是TCP还是UDP都可以用
KeepAlive并不是TCP协议规范的一部分，但在几乎所有的TCP/IP协议栈（不管是Linux还是Windows）中，都实现了KeepAlive功能
KeepAlive参数设置的方式缺点是各个底层操作系统对KeepAlive支持不同，
对有些复杂的网络情况不灵敏？实际都会发RST
“心跳除了说明应用程序还活着（进程还在，网络通畅），更重要的是表明应用程序还能正常工作。
而 TCP keepalive 有操作系统负责探查，即便进程死锁，或阻塞，操作系统也会如常收发 TCP keepalive 消息。对方无法得知这一异常。摘自《Linux 多线程服务端编程》”
https://yq.aliyun.com/articles/269571

##### TCP丢包及重试
https://monkeysayhi.github.io/2018/03/07/%E6%B5%85%E8%B0%88TCP%EF%BC%881%EF%BC%89%EF%BC%9A%E7%8A%B6%E6%80%81%E6%9C%BA%E4%B8%8E%E9%87%8D%E4%BC%A0%E6%9C%BA%E5%88%B6/
https://gafferongames.com/post/udp_vs_tcp/
https://zhuanlan.zhihu.com/p/41174248
