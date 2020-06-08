---
layout: post
title:  "DB-distributed-transacion"
date:   2019-11-12 11:25:00 +0900
comments: true
tags:
- 数据库
- 分布式
categories:
- 技术
---

### 数据库本地事务简述
- ACID原则
1. 原子性(Atomicity)
1. 一致性(Consistency)
1. 隔离性(Isolation)
1. 持久性(Durability)
- 以Mysql的InnoDB为例，事务的ACID是通过InnoDB日志和锁来保证
1. 事务的隔离性是通过数据库锁的机制实现的
1. 持久性通过Redo Log（重做日志）来实现，在事务提交前，只要将 Redo Log 持久化即可，不需要将数据持久化。
1. 原子性和一致性通过 Undo Log 来实现。（数据数据操作前的数据备份 Undo Log）
- 本质都是通过一个本地事务资源管理器来统一协调调度

### 分布式事务

#### 分布式事务产生的原因
- Service多节点部署（比如公司内的用户、账户等各种微服务)
- Resource 多节点 (每个人的数据部署再不同节点的数据库里)

#### 分布式系统之CAP定理
- CAP 定理，又被叫作布鲁尔定理。对于设计分布式系统(不仅仅是分布式事务)的架构师来说，CAP 就是你的入门理论。
- C (一致性)：对某个指定的客户端来说，读操作能返回一致的写操作。
对于数据分布在不同节点上的数据来说，如果在某个节点更新了数据，那么在其他节点如果都能读取到这个***的数据，那么就称为强一致，如果有某个节点没有读取到，那就是分布式不一致。
- A (可用性)：非故障的节点在合理的时间内返回合理的响应(不是错误和超时的响应)。可用性的两个关键一个是合理的时间，一个是合理的响应。
合理的时间指的是请求不能被阻塞，应该在合理的时间给出返回。合理的响应指的是系统应该明确返回结果并且结果是正确的，这里的正确指的是比如应该返回 50，而不是返回 40。
- P (分区容错性)：当出现网络分区后，系统能够继续工作。打个比方，这里集群有多台机器，有台机器网络出现了问题，但是这个集群仍然可以正常工作。

- 熟悉 CAP 的人都知道，三者不能共有，如果感兴趣可以搜索 CAP 的证明，在分布式系统中，网络无法 100% 可靠，分区其实是一个必然现象
    如果我们选择了 CA 而放弃了 P，那么当发生分区现象时，为了保证一致性，这个时候必须拒绝请求，但是 A 又不允许，所以分布式系统理论上不可能选择 CA 架构，只能选择 CP 或者 AP 架构。
    对于 CP 来说，放弃可用性，追求一致性和分区容错性，我们的 ZooKeeper 其实就是追求的强一致。
    对于 AP 来说，放弃一致性(这里说的一致性是强一致性)，追求分区容错性和可用性，这是很多分布式系统设计时的选择，后面的 BASE 也是根据 AP 来扩展。
    顺便一提，CAP 理论中是忽略网络延迟，也就是当事务提交时，从节点 A 复制到节点 B 没有延迟，但是在现实中这个是明显不可能的，所以总会有一定的时间是不一致。
    同时 CAP 中选择两个，比如你选择了 CP，并不是叫你放弃 A。因为 P 出现的概率实在是太小了，大部分的时间你仍然需要保证 CA。
    就算分区出现了你也要为后来的 A 做准备，比如通过一些日志的手段，是其他机器回复至可用。

#### 分布式系统之BASE定理
- BASE 是 Basically Available(基本可用)、Soft state(软状态)和 Eventually consistent (最终一致性)三个短语的缩写，是对 CAP 中 AP 的一个扩展。
- 基本可用：分布式系统在出现故障时，允许损失部分可用功能，保证核心功能可用。
- 软状态：允许系统中存在中间状态，这个状态不影响系统可用性，这里指的是 CAP 中的不一致。
- 最终一致：最终一致是指经过一段时间后，所有节点数据都将会达到一致。
- BASE 解决了 CAP 中理论没有网络延迟，在 BASE 中用软状态和最终一致，保证了延迟后的一致性。
- BASE 和 ACID 是相反的，它完全不同于 ACID 的强一致性模型，而是通过牺牲强一致性来获得可用性，并允许数据在一段时间内是不一致的，但最终达到一致状态

#### 常用分布式事务框架
- 基于XA的 2PC、3PC
     本质相当于本地事务的加强版，强一致性，引入中间事务协调者，依赖数据库，属于数据库资源层方案
- Saga
    引入补偿机制（最终一致性）
- TCC
    Try、Commit、Cancel
- 本地消息表
- RocketMQ(阿里开源)
- Seata

##### 参考资料
- [分布式事务概述](https://developer.51cto.com/art/201808/581174.htm)
- [由Seata看分布式事务取舍](https://www.jianshu.com/p/917cb4bdaa03)
- [常用分布式事务框架](https://cloud.tencent.com/developer/article/1401904)
- [蚂蚁金服分布式事务实战](https://zhuanlan.zhihu.com/p/75843832)
- [分布式事务选型的取舍infoq](https://www.infoq.cn/article/8bu33kuSyJ6P-wAAoELT)
- [分布式事务](http://www.tianshouzhi.com/api/tutorials/distributed_transaction/383)
- [Spring的分布式事务实现(JTA+XA/2PC)](https://www.jdon.com/48829)
- [Seata官网](http://seata.io/zh-cn/)
- [FLP不可能原理](https://www.cnblogs.com/firstdream/p/6585923.html) 
- [分布式事务：深入理解什么是2PC、3PC及TCC协议 ](http://www.sohu.com/a/290897501_684445)
- [如何基于RocketMQ的事务消息特性实现分布式系统的最终一致性？](https://juejin.im/post/5dd0ff1af265da0c075d0af7)
- [CAP定理](http://www.ruanyifeng.com/blog/2018/07/cap.html)
- [分布式事务的解决方案CSDN](https://blog.csdn.net/m0_38110132/article/details/76994165)
- [Atomikos和GTS-Fescar和TCC-Transaction和TX-LCN分布式事物的比较](https://www.bbsmax.com/A/obzb24Y0zE/)
- [分布式CSDN博客](https://blog.csdn.net/qq_27384769/category_7453176_1.html)
- [基于RocketMQ的最终一致性](https://www.itcodemonkey.com/article/13548.html)