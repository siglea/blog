---
layout: post
title:  "一致性（Consistency）与 共识（Consensus）"
date:   2019-11-12 11:25:00 +0900
comments: true
tags:
- 算法 
- 分布式
categories:
- 技术
---
#### Byzantine Fault Tolerance 分类
在分布式系统中，这种不听指挥的坏节点，就被称为“拜占庭错误节点”。一般来说，按照对“拜占庭错误节点”的容忍程度（简称BFT，Byzantine Fault Tolerance），分布式系统可以分为以下三类：
- 非BFT类：完全无法容忍“拜占庭错误节点”，但可以容忍其他错误的系统。（包括Pasox、SOLO、RAFT等。）
- BFT类：可以容忍“拜占庭错误节点”的系统。（包括PBFT、SBFT、VBFT、DBFT等。）
- 区块链类：不仅可以容忍“拜占庭错误节点”，还可以容忍节点的自由进出，这才是我们真正意义上的、狭义上的“区块链”。
   （包括我们熟悉的POW、POS、DPOS等等。）
- 其实与git的版本分支管理思想是一致的

<https://www.cnblogs.com/X-knight/p/9157814.html>

#### “一致性（Consistency）”和“共识（Consensus）”
Paxos、Raft等通常被误称为“一致性算法”。但是“一致性（Consistency）”和“共识（Consensus）”并不是同一个概念。Paxos、Raft等其实都是共识（Consensus）算法。
从专业的角度来讲，我们通常所说的一致性（Consistency）在分布式系统中指的是对于同一个数据的多个副本，其对外表现的数据一致性，如强一致性、顺序一致性、最终一致性等，都是用来描述副本问题中的一致性的。而共识（Consensus）则不同，简单来说，共识问题是要经过某种算法使多个节点达成相同状态的一个过程。一致性强调结果，共识强调过程。
<https://mp.weixin.qq.com/s/2v2E3Ls8BO1tZhv9qz5vPg>

#### 一致性分类
- 弱一致性（最终一致性）
  1. DNS（Domain Name System）
  1. Gossip（Cassandra、Redis的通信协议）<https://www.jianshu.com/p/54eab117e6ae>
- 强一致性
  - 主从同步
  - 多数一致，每次写都保证写入大于N/2个节点，每次读保证从大于N/2个节点中读。
    Paxos、Raft（multi-paxos）、ZAB（multi-paxos，Zookeeper atomic broadcast protocol，是Zookeeper内部用到的一致性协议。基本与Raft相同）

#### Pasox
Paxos算法是莱斯利·兰伯特(Leslie Lamport)1990年提出的一种基于消息传递的一致性算法。
Paxos的发展分类：Basic Paxos、Multi Paxos、Fast Paxos

#### Basic Paxos
1. 多个Proposer，都可以拿最新的编号N，进行prepare()，
1. 每个Acceptor会响应大于本地编号的所有prepare()，并且只会promise()最大的那个编号的提案
1. 最大编号的Proposer，收集够过半的票数之后，立即发送accept()给对应的Acceptor
1. 接受到accept()的Acceptor就有了最新的确认提案结果
    - 如果此时有新的大于N的prepare()就会进入下次选举循环，否则Acceptor会返回最新的提议结果给调用方
    - 如果此时收到不大于N的accept()则拒绝回应或者回应error；                   
1. 活锁，可能会存在一种情况：假定有2个proposer先后向acceptor发送请求，acceptor在接收到proposer1的prepare请求后更新编号为proposer1的编号；此时，proposer2接着向acceptor发送比proposer1编号更大的prepare请求，acceptor会立刻更新成proposer2的编号，那么当proposer1发送accept请求时由于编号不满足要求就会被accept给拒绝掉，则重新获取编号再次回到第一阶段发送prepare请求；从此2个proposer之间不断重复发送prepare请求，导致系统出现活锁
<https://mp.weixin.qq.com/s/j_08HupjHGHHwdyM8fsmfg>

#### Multi Paxos之Raft (Reliable, Replicated, Redundant, And Fault-Tolerant)
- 多个follower变身为candidate，同时term++，投票给自己同时向其他节点发送RequestVote RPC
- 节点(N)会投票给term是最新的，log至少和自身(N)一样新的candidate
- candidate收到多数投票，然后发送自己已经是leader的HeartBeat，接受者转变为follower，选举结束
- 一段时间后依然没有胜者。该种情况下会开启新一轮的选举。（Raft中使用随机选举超时时间来解决当票数相同无法确定leader的问题。）
- 日志复制（Log Replication）主要作用是用于保证节点的一致性，这阶段所做的操作也是为了保证一致性与高可用性。
  当Leader选举出来后便开始负责客户端的请求，所有事务（更新操作）请求都必须先经过Leader处理，日志复制（Log Replication）就是为了保证执行相同的操作序列所做的工作。
  在Raft中当接收到客户端的日志（事务请求）后先把该日志追加到本地的Log中，然后通过heartbeat把该Entry同步给其他Follower，Follower接收到日志后记录日志然后向Leader发送ACK，当Leader收到大多数（n/2+1）Follower的ACK信息后将该日志设置为已提交并追加到本地磁盘中，通知客户端并在下个heartbeat中Leader将通知所有的Follower将该日志存储在自己的本地磁盘中。
<https://www.cnblogs.com/binyue/p/8647733.html>

#### 如何解决split brain问题
- 分布式协议一个著名问题就是 split brain 问题。
简单说，就是比如当你的 cluster 里面有两个结点，它们都知道在这个 cluster 里需要选举出一个 master。那么当它们两之间的通信完全没有问题的时候，就会达成共识，选出其中一个作为 master。但是如果它们之间的通信出了问题，那么两个结点都会觉得现在没有 master，所以每个都把自己选举成 master。于是 cluster 里面就会有两个 master。
区块链的分叉其实类似分布式系统的split brain。
一般来说，Zookeeper会默认设置：
    - zookeeper cluster的节点数目必须是奇数。
    - zookeeper 集群中必须超过半数节点(Majority)可用，整个集群才能对外可用。
- Majority 就是一种 Qunroms 的方式来支持Leader选举，可以防止 split brain出现。奇数个节点可以在相同容错能力的情况下节省资源。

#### ZAB算法 Zookeeper atomic broadcast protocol
- 基本与Raft相同，在一些名词叫起来是有区别的
- ZAB将Leader的一个生命周期叫做epoch，而Raft称之为term
- 实现上也有些许不同，如raft保证日志的连续性，心跳是Leader向Follower发送，而ZAB方向与之相反

#### 一致性算法的实践
- 使用Paxos的组件，Chubby(Google首次运用Multi Paxos算法到工程领域)
- 使用Raft的组件，Redis-Cluster、etcd
- 使用ZAB的组件，Zookeeper（Yahoo开源）

<https://www.cnblogs.com/think90/p/11443428.html>
