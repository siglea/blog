---
layout: post
title:  "ZooKeeper"
date:   2020-06-06 13:17:00 +0900
comments: true
tags:
- 微服务
- 分布式
categories:
- 技术
---
#### 数据与存储
- 内存数据，Zookeeper的数据模型是树结构，在内存数据库中，存储了整棵树的内容，包括所有的节点路径、节点数据、ACL信息，Zookeeper会定时将这个数据存储到磁盘上。
　　1. DataTree，DataTree是内存数据存储的核心，是一个树结构，代表了内存中一份完整的数据。DataTree不包含任何与网络、客户端连接及请求处理相关的业务逻辑，是一个独立的组件。
　　2. DataNode，DataNode是数据存储的最小单元，其内部除了保存了结点的数据内容、ACL列表、节点状态之外，还记录了父节点的引用和子节点列表两个属性，其也提供了对子节点列表进行操作的接口。
　　3. ZKDatabase，Zookeeper的内存数据库，管理Zookeeper的所有会话、DataTree存储和事务日志。ZKDatabase会定时向磁盘dump快照数据，同时在Zookeeper启动时，会通过磁盘的事务日志和快照文件恢复成一个完整的内存数据库。
- 事务日志，FileTxnLog
<https://www.cnblogs.com/leesf456/p/6179118.html>

#### 散点
- 临时节点不允许有子节点，Ephemeral Node
- 每个节点大小不超过1MB

#### 使用场景
- 注册中心
- 配置中心
- HBase之MetaData存储
- 分布式锁

#### 常用命令
```shell
./zkServer.sh start | stop 
./zkServer.sh status
./zkCli.sh 

ls /
stat /
ls2 /

create /node1 /node1-content
create -e /node1-temp /node1-content-temp
```
<https://blog.csdn.net/dandandeshangni/article/details/80558383>

#### 阿里为什么不用 ZooKeeper 做服务发现？
- 基于CP而非AP
- 自身仅仅是主从的集群，而非分布式集群
- The King Of Coordination for Big Data

#### ZooKeeper的observer
当ZooKeeper集群中follower的数量很多时，投票过程会成为一个性能瓶颈，为了解决投票造成的压力，于是出现了observer角色。
observer角色不参与投票，它只是投票结果的"听众"，除此之外，它和follower完全一样，例如能接受读、写请求。就这一个特点，让整个ZooKeeper集群性能大大改善。
和follower一样，当observer收到客户端的读请求时，会直接从内存数据库中取出数据返回给客户端。
对于写请求，当写请求发送到某server上后，无论这个节点是follower还是observer，都会将它发送给leader。然后leader组织投票过程，所有server都收到这个proposal(包括observer，因为proposal是广播出去的)，但是leader和follower以及observer通过配置文件，都知道自己是不是observer以及谁是observer。自己是observer的server不参与投票。当leader收集完投票后，将那些observer的server去掉，在剩下的server中计算大多数，如果投票结果达到了大多数，这次写事务就成功，于是leader通知所有的节点(包括observer)，让它们将事务写入事务日志，并提交。

#### 使用 redis 如何设计分布式锁?说一下实现思路?使用 zk 可以吗?如何实现?这两种有什 么区别?
- redis:
    1. 线程 A setnx(上锁的对象,超时时的时间戳 t1)，如果返回 true，获得锁。
    2. 线程 B 用 get 获取 t1,与当前时间戳比较,判断是是否超时,没超时 false,若超时执行第 3 步; 
    3. 计算新的超时时间 t2,使用 getset 命令返回 t3(该值可能其他线程已经修改过),如果 t1==t3，获得锁，如果 t1!=t3 说明锁被其他线程获取了。 
    4. 获取锁后，处理完业务逻辑，再去判断锁是否超时，如果没超时删除锁，如果已超时， 不用处理(防止删除其他线程的锁)。
- zk:
    1. 客户端对某个方法加锁时，在 zk 上的与该方法对应的指定节点的目录下，生成一个唯一 的瞬时有序节点 node1; 
    2. 客户端获取该路径下所有已经创建的子节点，如果发现自己创建的 node1 的序号是最小 的，就认为这个客户端获得了锁。
    3. 如果发现 node1 不是最小的，则监听比自己创建节点序号小的最大的节点，进入等待。
    4. 获取锁后，处理完逻辑，删除自己创建的 node1 即可。 区别:zk 性能差一些，开销大，实现简单。
- redis分布式锁的缺点
    - 比如分布式环境下，A获取到了锁之后，因为线程A的业务代码耗时过长，导致锁的超时时间，锁自动失效。
      后续线程B就意外的持有了锁，之后线程A再次恢复执行，直接用del命令释放锁，这样就错误的将线程B同样Key的锁误删除了。代码耗时过长还是比较常见的场景，假如你的代码中有外部通讯接口调用，就容易产生这样的场景。

<https://mp.weixin.qq.com/s/ouayPydKCWc0FfGlaSnCrg>

#### Zookeeper队列管理(文件系统、通知机制)
- 两种类型的队列:
    - 同步队列，当一个队列的成员都聚⻬时，这个队列才可用，否则一直等待所有成员到达。 
    - 队列按照 FIFO 方式进行入队和出队操作。
- 第一类，在约定目录下创建临时目录节点，监听节点数目是否是我们要求的数目。
- 第二类，和分布式锁服务中的控制时序场景基本原理一致，入列有编号，出列按编号。在特定的目录下创建 PERSISTENT_SEQUENTIAL节点，创建成功时Watcher通知等待的队列，队列删除序列号最小的节点用以消费。
- 此场景下Zookeeper的znode用于消息存储，znode存储的数据就是消息队列中的消息内容，SEQUENTIAL序列号就是消息的编 号，按序取出即可。由于创建的节点是持久化的，所以不必担心队列消息的丢失问题。