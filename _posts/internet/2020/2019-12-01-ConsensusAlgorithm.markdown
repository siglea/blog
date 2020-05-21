---
layout: post
title:  "一致性算法"
date:   2019-11-12 11:25:00 +0900
comments: true
tags:
- 算法 
categories:
- 技术
---
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

#### 一致性算法的实践
- 使用Paxos的组件，Chubby(Google首次运用Multi Paxos算法到工程领域)
- 使用Raft的组件，Redis-Cluster、etcd
- 使用ZAB的组件，Zookeeper（Yahoo开源）

<https://www.cnblogs.com/think90/p/11443428.html>