---
layout: post
title:  "一致性（Consistency）与 共识（Consensus）"
date:   2019-11-12 11:25:00 +0900
comments: true
tags:
- 数据结构与算法 
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

#### Basic Paxos （忽然发现这个过程与3PC很相似，需要2次多数投票）
- 一阶段，Proposer发出prepare()，Acceptor给出承诺promise()
    - Proposer生成全局唯一且递增的Proposal ID (可使用时间戳加Server ID)，向所有Acceptors发送Prepare请求，这里无需携带提案内容，只携带Proposal ID即可。
    - Acceptor承诺一：不再接受Proposal ID小于等于（注意：这里是<= ）当前请求的Prepare请求。
    - Acceptor承诺二：不再接受Proposal ID小于（注意：这里是< ）当前请求的Propose请求。
    - Acceptor应答一：不违背以前作出的承诺下，回复已经Accept过的提案中Proposal ID最大的那个提案的Value和Proposal ID，没有则返回空值。
- 二阶段，Proposer发出提议propose()，Acceptor接受accept()
    - Proposer提案：Proposer收到多数Acceptors的Promise应答后，从应答中选择Proposal ID最大的提案的Value，作为本次要发起的提案。如果所有应答的提案Value均为空值，则可以自己随意决定提案Value。然后携带当前Proposal ID，向所有Acceptors发送Propose请求。
    - Acceptor接受：Acceptor收到Propose请求后，在不违背自己之前作出的承诺下，接受并持久化当前Proposal ID和提案Value。
- 三阶段，Proposer发送最终决议
    - Proposer收到多数Acceptors的Accept后，决议形成，将形成的决议发送给所有Learners。
1. <https://zhuanlan.zhihu.com/p/31780743>                 
1. <https://mp.weixin.qq.com/s/j_08HupjHGHHwdyM8fsmfg>

#### 活锁，可能会存在一种情况：假定有2个proposer先后向acceptor发送请求，acceptor在接收到proposer1的prepare请求后更新编号为proposer1的编号；
此时，proposer2接着向acceptor发送比proposer1编号更大的prepare请求，acceptor会立刻更新成proposer2的编号，那么当proposer1发送accept请求时由于编号不满足要求就会被accept给拒绝掉，则重新获取编号再次回到第一阶段发送prepare请求；
从此2个proposer之间不断重复发送prepare请求，导致系统出现活锁

#### 如何解决split brain问题
- 分布式协议一个著名问题就是 split brain 问题。
简单说，就是比如当你的 cluster 里面有两个结点，它们都知道在这个 cluster 里需要选举出一个 master。那么当它们两之间的通信完全没有问题的时候，就会达成共识，选出其中一个作为 master。
但是如果它们之间的通信出了问题，那么两个结点都会觉得现在没有 master，所以每个都把自己选举成 master。于是 cluster 里面就会有两个 master。
区块链的分叉其实类似分布式系统的split brain。
一般来说，Zookeeper会默认设置：
    - zookeeper cluster的节点数目必须是奇数。
    - zookeeper 集群中必须超过半数节点(Majority)可用，整个集群才能对外可用。
- Majority(大多数) 就是一种 Quorum(法定代表人) 的方式来支持Leader选举，可以防止 split brain出现。奇数个节点可以在相同容错能力的情况下节省资源。

#### Multi Paxos之Raft (Reliable, Replicated, Redundant, And Fault-Tolerant)
- 多个follower变身为candidate，同时term++，投票给自己同时向其他节点发送RequestVote RPC
- 节点(N)会投票给term是最新的，log至少和自身(N)一样新的candidate
- candidate收到多数投票，然后发送自己已经是leader的HeartBeat，接受者转变为follower，选举结束
- 一段时间后依然没有胜者。该种情况下会开启新一轮的选举。（Raft中使用随机选举超时时间来解决当票数相同无法确定leader的问题。）
- 日志复制（Log Replication）主要作用是用于保证节点的一致性，这阶段所做的操作也是为了保证一致性与高可用性。
  当Leader选举出来后便开始负责客户端的请求，所有事务（更新操作）请求都必须先经过Leader处理，日志复制（Log Replication）就是为了保证执行相同的操作序列所做的工作。
  在Raft中当接收到客户端的日志（事务请求）后先把该日志追加到本地的Log中，然后通过heartbeat把该Entry同步给其他Follower，Follower接收到日志后记录日志然后向Leader发送ACK，当Leader收到大多数（n/2+1）Follower的ACK信息后将该日志设置为已提交并追加到本地磁盘中，通知客户端并在下个heartbeat中Leader将通知所有的Follower将该日志存储在自己的本地磁盘中。
<https://www.cnblogs.com/binyue/p/8647733.html>

#### ZAB协议 2阶段
1. 消息广播阶段 （类似2PC）
    - leader写本地之后，同步给follower，大多数follower写成功并且ACK给leader，就表示写成功
    - 否则表示集群故障了，进入崩溃恢复阶段
2. 崩溃恢复阶段 （发现阶段、同步阶段zxid不是最大）
    - 自我投票，之后让其他follower投票给自己
    - 投票比较策略：当其他节点的纪元比自身高投它，如果纪元epoch相同比较自身的zxid的大小，选举zxid大的节点，这里的zxid代表节点所提交事务最大的id，zxid越大代表该节点的数据越完整。
        最后如果epoch和zxid都相等，则比较服务的serverId，这个Id是配置zookeeper集群所配置的，所以我们配置zookeeper集群的时候可以把服务性能更高的集群的serverId配置大些，让性能好的机器担任leader角色。
    - leader产生后，当 Follower 链接上 Leader 之后，Leader 服务器会根据自己服务器上最后被提交的 ZXID 和 Follower 上的 ZXID 进行比对，比对结果要么回滚，要么和 Leader 同步。

#### ZAB算法 Zookeeper atomic broadcast protocol
- 基本与Raft相同，在一些名词叫起来是有区别的
- ZAB将Leader的一个生命周期叫做epoch，而Raft称之为term
- 实现上也有些许不同，如raft保证日志的连续性，心跳是Leader向Follower发送，而ZAB方向与之相反
- ZAB选举阶段只接受比自己大的zxid，意味着经过多次之后，拥有最新数据的节点才有可能成为leader

#### raft 协议和 zab 协议区别
- 相同点
    - 都使用 timeout 来重新选择 leader
    - 采用quorum来确定整个系统的一致性,这个quorum一般实现是集群中半数以上的服务器, zookeeper里还提供了带权重的quorum实现.
    - 都由leader来发起写操作.
    - 都采用心跳检测存活性
    - leader election都采用先到先得的投票方式 
    - zookeeper 的 zab 实现里选主要求选出来的主拥有 quorum 里最新的历史，而 raft 的 follower 的选主投票根据 term 的大小+日志完成度来选择投票给谁，这点上来看是比较类似的
- 不同点
    - zab用的是epoch和count的组合来唯一表示一个值,而raft用的是term和index
    - zab的follower在投票给一个leader之前必须和leader的日志达成一致,而raft的follower则简单地说是谁的 term 高就投票给谁
    - raft协议的心跳是从leader到follower,而zab协议则相反
    - raft 协议数据只有单向地从 leader 到 follower（成为 leader 的条件之一就是拥有最新的 log），而 zab 的 zookeeper 实现中 ，一个 prospective leader (epoch最大但是zxid不是最大)需要将自己的 log 更新为 quorum 里面最新的 log，然后才好在 synchronization 阶段将 quorum 里的其他机器的 log 都同步到一致
<https://www.cnblogs.com/think90/p/11443428.html>

#### 一致性算法的实践
- 使用Paxos的组件，Chubby(Google首次运用Multi Paxos算法到工程领域)
- 使用Raft的组件，Redis-Cluster、etcd
- 使用ZAB的组件，Zookeeper（Yahoo开源）