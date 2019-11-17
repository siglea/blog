---
layout: post
title:  "DB-distributed-transacion"
date:   2019-11-12 11:25:00 +0900
comments: true
tags:
- mysql DB 
categories:
- 互联网
---

[常用分布式事务框架](https://cloud.tencent.com/developer/article/1401904)
[蚂蚁金服分布式事务实战](https://zhuanlan.zhihu.com/p/75843832)
[分布式事务选型的取舍infoq](https://www.infoq.cn/article/8bu33kuSyJ6P-wAAoELT)
[分布式事务](http://www.tianshouzhi.com/api/tutorials/distributed_transaction/383)
[Spring的分布式事务实现(JTA+XA/2PC)](https://www.jdon.com/48829)
[Seata官网](http://seata.io/zh-cn/)
[FLP不可能原理](https://www.cnblogs.com/firstdream/p/6585923.html) 
[分布式事务：深入理解什么是2PC、3PC及TCC协议 ](http://www.sohu.com/a/290897501_684445)
[如何基于RocketMQ的事务消息特性实现分布式系统的最终一致性？](https://juejin.im/post/5dd0ff1af265da0c075d0af7)
[CAP定理](http://www.ruanyifeng.com/blog/2018/07/cap.html)
[分布式事务的解决方案CSDN](https://blog.csdn.net/m0_38110132/article/details/76994165)
[Atomikos和GTS-Fescar和TCC-Transaction和TX-LCN分布式事物的比较](https://www.bbsmax.com/A/obzb24Y0zE/)
[分布式CSDN博客](https://blog.csdn.net/qq_27384769/category_7453176_1.html)
https://www.itcodemonkey.com/article/13548.html

强一致性的2PC、3PC、Paxos、Raft、Zab；
最终一致性的Saga、TCC、Seata(AT和MT模式）以及MQ事务消息

面试官问到了MySQL 的Update操作执行过程，你提到了WAL技术，先写Redolog，防止机器Crash造成数据丢失，也能提高性能，
通过配置还可以减少磁盘IO的次数；紧接着又补充到，Kafka、Rocketmq等消息中间件以及Elasticsearch、HBase、Leveldb、Rocksdb、
TiDB、Tair等高性能存储组件都用到了这种技术，这同样也可以体现你的技术视野。