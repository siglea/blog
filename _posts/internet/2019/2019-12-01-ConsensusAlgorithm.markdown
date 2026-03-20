---
layout: post
title:  "分布式共识算法全解析：从 Paxos 到 Raft 与 ZAB"
date:   2019-11-12 11:25:00 +0900
comments: true
tags:
- 数据结构与算法 
- 分布式
categories:
- 技术
---

在分布式系统中，如何让多个节点对某个值达成一致，是最核心也是最困难的问题之一。本文将系统梳理一致性与共识的概念区别，介绍 BFT 容错分类，并深入讲解 Paxos、Raft、ZAB 三种主流共识算法的原理与差异。

---

## 一、一致性（Consistency）与共识（Consensus）的区别

Paxos、Raft 等算法经常被误称为"一致性算法"，但实际上它们是**共识（Consensus）算法**。

- **一致性（Consistency）**：指对于同一数据的多个副本，其对外表现的数据一致性。如强一致性、顺序一致性、最终一致性等，描述的是副本之间数据状态的统一程度。**一致性强调结果。**
- **共识（Consensus）**：指通过某种算法使多个节点达成相同状态的过程。**共识强调过程。**

简言之，一致性关注的是"数据看起来是否一样"，共识关注的是"节点如何协商出一个统一的决定"。

参考：<https://mp.weixin.qq.com/s/2v2E3Ls8BO1tZhv9qz5vPg>

---

## 二、拜占庭容错（BFT）分类

在分布式系统中，节点可能因为各种原因而表现异常——不仅仅是崩溃，还可能发送错误甚至恶意的消息。这种不听指挥的坏节点被称为"拜占庭错误节点"。按照对拜占庭错误的容忍程度，分布式系统可以分为三类：

| 类别 | 特点 | 代表算法 |
|------|------|----------|
| **非 BFT 类** | 完全无法容忍拜占庭错误，但可以容忍节点崩溃等故障 | Paxos、SOLO、Raft |
| **BFT 类** | 可以容忍拜占庭错误节点 | PBFT、SBFT、VBFT、DBFT |
| **区块链类** | 不仅容忍拜占庭错误，还能容忍节点的自由进出 | PoW、PoS、DPoS |

这个分类思想其实与 Git 的版本分支管理颇为相似——都需要在多个"分支"之间协调出一个统一的"主线"。

参考：<https://www.cnblogs.com/X-knight/p/9157814.html>

---

## 三、一致性的分类

### 3.1 弱一致性（最终一致性）

不要求所有节点在任意时刻都能读到最新数据，但保证在一定时间后所有副本最终会收敛到一致状态。

典型代表：
- **DNS（Domain Name System）**：域名解析的传播有延迟窗口
- **Gossip 协议**：Cassandra、Redis 集群的节点通信协议。参考：<https://www.jianshu.com/p/54eab117e6ae>

### 3.2 强一致性

每次读操作都能读到最近一次写操作的结果。实现方式包括：

- **主从同步**：写操作完成后等待所有从节点同步完毕再返回
- **多数一致（Quorum）**：每次写保证写入 > N/2 个节点，每次读保证从 > N/2 个节点中读取。代表算法：Paxos、Raft（Multi-Paxos）、ZAB（Multi-Paxos 变种）

---

## 四、Basic Paxos 算法

Paxos 算法是 Leslie Lamport 于 1990 年提出的基于消息传递的共识算法，是分布式共识领域的奠基之作。其发展分为 Basic Paxos、Multi Paxos 和 Fast Paxos。

Basic Paxos 的核心流程分为三个阶段（与 3PC 有相似之处，都需要两轮多数投票）：

### 4.1 第一阶段：Prepare / Promise

**Proposer 发出 Prepare 请求：**
- Proposer 生成全局唯一且递增的 Proposal ID（可使用时间戳 + Server ID），向所有 Acceptor 发送 Prepare 请求，此时只需携带 Proposal ID，无需提案内容。

**Acceptor 给出承诺：**
- 承诺一：不再接受 Proposal ID ≤ 当前请求的 Prepare 请求
- 承诺二：不再接受 Proposal ID < 当前请求的 Propose 请求
- 应答：在不违背已有承诺的前提下，回复已 Accept 过的提案中 Proposal ID 最大的那个提案的 Value 和 Proposal ID；如果没有，则返回空值

### 4.2 第二阶段：Propose / Accept

**Proposer 提案：**
- 收到多数 Acceptor 的 Promise 应答后，从应答中选择 Proposal ID 最大的提案的 Value 作为本次要发起的提案。如果所有应答的 Value 均为空，则可以自行决定提案 Value。然后携带当前 Proposal ID，向所有 Acceptor 发送 Propose 请求。

**Acceptor 接受：**
- 在不违背之前承诺的前提下，接受并持久化当前 Proposal ID 和提案 Value。

### 4.3 第三阶段：发送最终决议

Proposer 收到多数 Acceptor 的 Accept 后，决议形成，将最终决议发送给所有 Learner。

参考：
1. <https://zhuanlan.zhihu.com/p/31780743>
2. <https://mp.weixin.qq.com/s/j_08HupjHGHHwdyM8fsmfg>

### 4.4 活锁问题

Basic Paxos 可能出现活锁：假设 Proposer1 和 Proposer2 先后向 Acceptor 发送请求。Acceptor 接收到 Proposer1 的 Prepare 后更新编号为 Proposer1 的编号；此时 Proposer2 发送了更大编号的 Prepare，Acceptor 又更新为 Proposer2 的编号。当 Proposer1 发送 Accept 请求时编号不满足要求被拒绝，于是重新获取编号回到第一阶段……两个 Proposer 之间不断重复，导致系统出现活锁。

解决方案通常是引入**随机退避**或选举出一个**Leader Proposer**来避免多个 Proposer 竞争。

---

## 五、Split Brain（脑裂）问题

脑裂是分布式协议中一个经典问题。当集群中的节点之间通信中断时，每个分区都可能认为自己是唯一的"主"，从而产生多个 Master。区块链中的分叉本质上也是一种脑裂现象。

### 5.1 Zookeeper 的解决方案

Zookeeper 通过以下策略避免脑裂：

- 集群节点数目必须是**奇数**
- 集群中必须**超过半数节点（Majority）** 可用，整个集群才能对外提供服务

Majority 是一种 Quorum（法定人数）机制来支持 Leader 选举，可以有效防止脑裂。使用奇数个节点可以在相同容错能力的情况下节省资源——例如 3 个节点和 4 个节点都只能容忍 1 个节点故障，所以 3 个节点更经济。

---

## 六、Raft 算法

Raft（Reliable, Replicated, Redundant, And Fault-Tolerant）是 Multi-Paxos 的一种简化实现，通过将共识问题分解为 **Leader 选举** 和 **日志复制** 两个子问题来降低理解和实现难度。

### 6.1 Leader 选举

1. 多个 Follower 变身为 Candidate，同时 term++，投票给自己并向其他节点发送 RequestVote RPC
2. 节点 N 会投票给 term 最新的、log 至少和自身一样新的 Candidate
3. Candidate 收到多数投票后，发送 Leader 心跳，接收者转变为 Follower，选举结束
4. 如果一段时间后仍无胜者（票数相同），则开启新一轮选举。Raft 使用**随机选举超时时间**来解决票数相同的问题

### 6.2 日志复制（Log Replication）

日志复制是保证节点一致性的核心机制。Leader 选举出来后负责处理客户端请求，所有更新操作都必须先经过 Leader。

1. Leader 接收到客户端日志后，先追加到本地 Log
2. 通过心跳将该 Entry 同步给其他 Follower
3. Follower 记录日志后向 Leader 发送 ACK
4. 当 Leader 收到多数（n/2+1）Follower 的 ACK 后，将该日志设为已提交并追加到本地磁盘，通知客户端
5. 在下个心跳中，Leader 通知所有 Follower 将该日志存储到本地磁盘

参考：<https://www.cnblogs.com/binyue/p/8647733.html>

---

## 七、ZAB 协议

ZAB（Zookeeper Atomic Broadcast）协议是 Zookeeper 内部使用的一致性协议，基本与 Raft 相同，分为两个阶段。

### 7.1 消息广播阶段（类似 2PC）

- Leader 写本地后，同步给 Follower
- 大多数 Follower 写成功并 ACK 给 Leader，表示写成功
- 否则表示集群故障，进入崩溃恢复阶段

### 7.2 崩溃恢复阶段（发现 + 同步）

1. **自我投票**：节点先投票给自己，然后请求其他节点投票
2. **投票比较策略**：
   - 优先比较 epoch（纪元），epoch 大的优先
   - epoch 相同则比较 zxid（事务 ID），zxid 大的优先（zxid 越大表示数据越完整）
   - epoch 和 zxid 都相等，则比较 serverId，serverId 大的优先（可以将性能更好的机器配置更大的 serverId）
3. **数据同步**：Leader 产生后，根据自己和 Follower 的 ZXID 进行比对，比对结果要么回滚，要么与 Leader 同步

---

## 八、Raft 与 ZAB 的异同

### 8.1 相同点

- 都使用 timeout 来触发重新选举
- 都采用 Quorum 机制（通常是集群半数以上）确定一致性
- 都由 Leader 发起写操作
- 都采用心跳检测存活性
- Leader 选举都采用先到先得的投票方式
- 选主都要求候选者拥有最新的数据

### 8.2 不同点

| 维度 | Raft | ZAB |
|------|------|-----|
| 标识方式 | term + index | epoch + count（zxid） |
| 日志一致性要求 | Follower 投票时比较 term 和日志完成度 | Follower 投票前必须和 Leader 日志达成一致 |
| 心跳方向 | Leader → Follower | Follower → Leader |
| 数据流向 | 单向，Leader → Follower | 可能双向，新 Leader（epoch 最大但 zxid 不是最大）需要先从 Quorum 中同步最新日志 |

ZAB 的一些术语与 Raft 不同：ZAB 将 Leader 的一个生命周期叫做 epoch，而 Raft 称之为 term。ZAB 选举阶段只接受比自己大的 zxid，意味着经过多轮投票后，拥有最新数据的节点才有可能成为 Leader。

参考：<https://www.cnblogs.com/think90/p/11443428.html>

---

## 九、共识算法的工程实践

不同的共识算法在工业界有着广泛的应用：

| 算法 | 使用组件 |
|------|----------|
| **Paxos** | Chubby（Google 首次将 Multi-Paxos 应用于工程领域） |
| **Raft** | Redis Cluster、etcd |
| **ZAB** | Zookeeper（Yahoo 开源） |

---

## 总结

共识算法是分布式系统的基石。从理论上的 Paxos 到工程友好的 Raft 和 ZAB，共识算法不断在**正确性**、**可理解性**和**工程可实现性**之间寻找平衡。理解这些算法的核心思想——多数派投票、Leader 选举、日志复制——对于设计和运维分布式系统至关重要。在实际选型时，Raft 因其简洁的设计成为当前最流行的选择，而 ZAB 则在 Zookeeper 生态中发挥着不可替代的作用。
