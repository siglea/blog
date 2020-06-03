---
layout: post
title:  "Not Only SQL"
date:   2019-11-12 11:25:00 +0900
comments: true
tags:
- NoSQL
- 数据库 
- 数据结构与算法
categories:
- 技术
---
#### SQL-CAP
<div align="left">
<img src="/img/nosql-cap.jpg" width="500px">
</div>

#### NoSQL由来
- 高可用 ！= 分布式，传统的关系型数据库RDB，并没有实现真正意义上的分布式，即便是分库分表也仅仅是"伪分布式"，不具备诸如数据多分区备份等特性
- 传统的关系型数据库RDB，主从同步的集群，本质上是全量数据的备份，也不是分布式真正要求的可伸缩
- 传统的关系型数据库RDB，数据表结构或Meta或schema固定，扩展成本高
- RDB以行位核心的数据存储，NoSQl以列为核心(HBase/Cassandra)或KV(Redis)为核心
- 1946年，第一台通用计算机诞生。但一直到1970年RDMBS的出现，大家才找到通用的数据存储方案。到21世纪，DT时代让数据容量成为最棘手的问题，对此谷歌和亚马逊分别提出了自己的NoSQL解决方案，比如谷歌于2006年提出了Bigtable。2009年的一次技术大会上，NoSQL一词被正式提出，到现在共有225种解决方案。
NoSQL与RDMBS的区别主要在两点：第一，它提供了无模式的灵活性，支持很灵活的模式变更；第二，可伸缩性，原生的RDBMS只适用于单机和小集群。而NoSQL一开始就是分布式的，解决了读写和容量扩展性问题。以上两点，也是NoSQL产生的根本原因。

#### NoSQL分类
这些NoSQL数据库分为Graph，Document，Column Family以及Key-Value Store等四种。这四种类型的数据库分别使用了不同的数据结构来记录数据。因此它们所适用的场景也不尽相同。

#### 关系型数据库和非关系型数据库的应用场景对比
- 关系型数据库适合存储结构化数据，如用户的帐号、地址：
    1. 这些数据通常需要做结构化查询，比如join，这时候，关系型数据库就要胜出一筹
    1. 这些数据的规模、增长的速度通常是可以预期的
    1. 事务性、一致性
　　
- NoSQL适合存储非结构化数据，如文章、评论：
    1. 这些数据通常用于模糊处理，如全文搜索、机器学习
    1. 这些数据是海量的，而且增长的速度是难以预期的，
    1. 根据数据的特点，NoSQL数据库通常具有无限（至少接近）伸缩性
    1. 按key获取数据效率很高，但是对join或其他结构化查询的支持就比较差

#### BST（二叉搜索树）、AVL树、红黑树、2-3树、B树、B+树、LSM树
- <https://www.jianshu.com/p/bb929dc75007>
- AVL树
    - 特性
        - 要求每个节点的左右子树高度差不超过1
        - 树的高度差越小，查找效率越高，但是调整成本高
- 红黑树
    - 特性（保存自平衡，从根到叶子的最长路径不会超过最短路径的2倍）
        1. 结点是红色或黑色。
        2. 根结点是黑色。
        3. 每个叶子结点都是黑色的空结点（NIL结点）。
        4. 每个红色结点的两个子结点都是黑色。(从每个叶子到根的所有路径上不能有两个连续的红色结点)
        5. 从任一结点到其每个叶子的所有路径都包含相同数目的黑色结点。
- 2-3树，2-3个节点
- B树，M个节点（操作系统文件目录）
- B+树，B+树内部节点不保存数据，所以能在内存中存放更多索引，增加缓存命中率。另外因为叶子节点相连遍历操作很方便，而且数据也具有顺序性，便于区间查找。
- LSM
    - 原理上类似JVM的复制算法/压缩整理算法，也就是插入的新的数据不去找之前的位置插入，而是用新空间存放然后与旧数据合并，合并完成之后，最老的数据直接就清除掉了，这样磁盘上相邻的数据都是顺序的。
    - LSM在内存中有memtable（接受实时写） 、immutable memtable(写满了等待向磁盘flush或合并），磁盘内有分层的SSTable
    - LSM之所以快，就是因为写入在内容，之后是异步的去合并写入磁盘。（B/B树，写入操作都是同步的在磁盘进行）
    - LSM-tree 基本原理及应用 <https://cloud.tencent.com/developer/news/340271>
    - Cassandra、HBase、LevelDB、RocksDB、BigTable
    - 算法细节 <https://www.cnblogs.com/siegfang/archive/2013/01/12/lsm-tree.html>

#### 二级索引？
- 二级索引，其实就是倒排索引的一种变种

#### Redis 

#### MongoDB
- 典型应用场景
    - 使用MongoDB做了O2O快递应用，·将送快递骑手、快递商家的信息（包含位置信息）存储在 MongoDB，然后通过 MongoDB 的地理位置查询，这样很方便的实现了查找附近的商家、骑手等功能，使得快递骑手能就近接单
    - 什么场景应该用 MongoDB ？ <https://yq.aliyun.com/articles/64352>
    - MongoDB 应用场景?（知乎）<https://www.zhihu.com/question/32071167?sort=created>
    - 一般来讲，我会将MySQL中的部分表迁移到MongoDB中，主要是涉及到车辆历史轨迹以及温湿度数据等机器采集到的数据，而订单数据、客户数据等信息，仍然放到MySQL数据库中，主要是因为这两类数据实时采集，实时更新，会随着时间的推移，项目的扩大（PAAS服务），造成非常巨大的数据量，而一般MySQL在单表数据量超过500万后，性能就会下降的比较快，虽然可以通过分表的方式进行处理，但是随着时间的增长，仍然会给我带来比较大的麻烦（如查询等），这样，就不如将其放到MongoDB中存储，查询什么的都会比较方便，不过需要注意根据片键分片哦。
    - 在主流的计算机语言如Java、Python中对JSON都有很好的支持，数据从MongoDB中读取出来后，可无需转换直接使用；MongoDB文档另一个特点是Key-Value键值对支持丰富的数据结构，Value可以是普通的整型、字符串，可以是数组，也可以是嵌套的子文档，使用嵌套的好处是在MongoDB中仅需一次简单的查询就能够获取到你所需的数据。举电商领域为例，网易严选上卖的上衣和裤子两种商品，除了有共同属性，如产地、价格、材质、颜色等外，还有各自有不同的属性集，如上衣的独有属性是肩宽、胸围、袖长等，裤子的独有属性是臀围、脚口和裤长等。
- 支持的引擎，mmapv1、wiredtiger、mongorocks（rocksdb）、in-memory
- 强大的索引，地理位置索引可用于构建 各种 O2O 应用、文本索引解决搜索的需求、TTL索引解决历史数据自动过期的需求
- MongoDB与Mysql/Hadoop/Redis的优缺点比较 <https://blog.csdn.net/tanqian351/article/details/81744970>

#### Cassandra
- Cassandra数据建模 <https://www.cnblogs.com/cjsblog/p/12878330.html>
- 详解Cassandra数据模型中的primary key <https://blog.csdn.net/Yaokai_AssultMaster/article/details/77439897>
    - 一致性哈希算法的特点是可以接受任何输入，但总会输出位于固定范围内的（当前集群的结点有对应的）值。简而言之，某一特定的partition key总会对应集群中的某一特定的结点，而这个partition key对应的数据也总是应当在这个结点上被找到。
      对于分布式系统而言，这一点极其重要。其原因是如果对某一特定数据，我们无法确定其所对应的结点位置的话，我们就总是需要遍历集群中的每一个结点才能找到需要的数据。对于小规模的集群，这样的操作可能还可以接受。但对于大规模的分布式数据库而言，这将会严重影响整个系统的效率。
    - Room表是"静态表"，RoomMember就是"动态表"；User表是"静态表"，UserArticle就是"动态表"
    - Partition Key (col1, col2)为了确定数据的位置，Clustering Key (col3, col4)，主要是为了排序。例如：PRIMARY KEY((col1, col2), col3, col4))
- 一切设计都是为了查询
- Cassandra更加AP,可调一致性（HBase是CP)
- 属于宽表的一种（HBase、Alibaba TableStore、Google BigTable)
- 应该把 Cassandra 看做是一个有索引的、面向列的存储系统。
    - Cassandra 经常被看做是一种面向列（Column-Oriented）的数据库，这也并不算错。它的数据结构不是关系型的，而是一个多维稀疏哈希表。稀疏（Sparse）意味着任何一行都可能会有一列或者几列，但每行都不一定（像关系模型那样）和其他行有一样的列。每行都有一个唯一的键值，用于进行数据访问。所以，更确切地说，应该把 Cassandra 看做是一个有索引的、面向行的存储系统。
    - Cassandra 的数据存储结构基本可以看做是一个多维哈希表。这意味着你不必事先精确地决定你的具体数据结构或是你的记录应该包含哪些具体字段。这特别适合处于草创阶段，还在不断增加或修改服务特性的应用。而且也特别适合应用在敏捷开发项目中，不必进行长达数月的预先分析。对于使用 Cassandra 的应用，如果业务发生变化了，只需要在运行中增加或删除某些字段就行了，不会造成服务中断。
    - 当然， 这不是说你不需要考虑数据。相反，Cassandra 需要你换个角度看数据。在 RDBMS 里， 你得首先设计一个完整的数据模型， 然后考虑查询方式， 而在 Cassandra 里，你可以首先思考如何查询数据，然后提供这些数据就可以了。
- cassandra的难点在于建模，不同于RDB的一种建模思路（KeySpaces<->DataBase,ColumnFamily<->Table)仅仅是概念的类似，实际上设计思想完全不同
    - Keyspaces：键空间是 Cassandra 的数据容器，可以理解为关系型数据库中的数据库（Database）。对于一个 Keyspace 来说，包括定义每行数据的复制节点数目、定义在一致性哈希环中某个节点的替换策略、列族（Column Families）等多个概念。
    - 列族：列的容器，它的结构像是一个四维哈希表，[Keyspace][ColumnFamily][Key][Column]。
    - 列：一组键值对。
- cassandra以列为核心，相当于把RDB中的宽表，细化为随时可以扩展的动态列
- 就Cassandra而言，最关键的地方在于Key的设计。Cassandra之中一共包含下面5种Key:
    - Primary Key
    - Partition Key
    - Composite Key
    - Compound Key
    - Clustering Key
- Cassandra 是为优异的写吞吐量而特别优化的。
- 应用场景
    - 根据项目的 wiki，Cassandra 已经被用于开发了多种不同的应用，包括窗口化的时间序列数据库，用于文档搜索的反向索引，以及分布式任务优先级队列。
    - 产品目录和零售应用程序Cassandra被许多零售商用于购物车数据保持和快速的产品目录输入和输出。
    - 社交媒体分析和推荐引擎Cassandra是许多在线公司和社交媒体提供商的良好数据库，用于分析和推荐给客户。
    - Yelp的广告分析系统，Spotify的所有用户信息存储
    - Feeds场景、滴滴或物联网订单轨迹场景 <https://mp.weixin.qq.com/s/DaspXFLPASYE7N0WHllcYQ>
    - cassandra在饿了么的应用 <https://zhuanlan.zhihu.com/p/42175864>
    <div align="left">
    <img src="/img/cassandra.jpg" width="500px">
    </div>
- cassandra与mysql使用对比 <https://www.ibm.com/developerworks/cn/opensource/os-apache-cassandra/>
- cassandra使用场景判断：何时使用及何时不用 <https://developer.aliyun.com/article/713847>
- Discord 公司如何使用 Cassandra 存储上亿条线上数据(消息系统) <https://segmentfault.com/a/1190000019111842>
- Spotify如何使用Cassandra实现个性化推荐 <https://segmentfault.com/a/1190000020976455>
- CQL语法 <https://www.w3cschool.cn/cassandra/cassandra_alter_keyspace.html>

#### "图"数据库 Graph Database Neo4J
<https://www.cnblogs.com/loveis715/p/5277051.html>

#### 其他KV的NoSQL： Leveldb、Rocksdb、Tair
<https://mp.weixin.qq.com/s/JSPvpnKMzbehP7urdDOlbA>

#### 列式存储：ClickHouse(OLAP)、Cassandra、HBase(OLAP)、Vertica

#### NewSQL(分布式RDB)：oceanDB、TiDB
- 初识TiDB <https://mp.weixin.qq.com/s/_KS4AAfynvn-sYl-7nJSkg>
- 从NoSQL到NewSQL，谈交易型分布式数据库建设要点 <https://mp.weixin.qq.com/s/HPuiCn9oyB8itsqMcXB_1w>
- 从架构特点到功能缺陷，重新认识分析型分布式数据库 <https://mp.weixin.qq.com/s/ZOelW__ON_86YgXmVeDEwA>
- 简单比较SQL、NoSQL、NewSQL <https://mp.weixin.qq.com/s/AHYaFT9Du2UlufVQjb47bg>
- NewSQL概述 <https://mp.weixin.qq.com/s/AcuFiHgRJg2OcNGtfjRxYA>
- 滴滴放弃TiDB <https://mp.weixin.qq.com/s/_h4UE1LMrO-UjE-TaGH20g>
- 分库分表 or NewSQL数据库 ? <https://mp.weixin.qq.com/s/ymVxSe8nueuG7knKwcIAMw>

#### 常见 TSDB 时间序列数据库 Time Series Database ：influxdb、opentsdb、timeScaladb、Druid 、tablestore等
一种集时序数据高效读写，压缩存储，实时计算能力为一体的数据库服务，可广泛应用于物联网和互联网领域，实现对设备及业务服务的实时监控，实时预测告警。
<https://www.jianshu.com/p/31afb8492eff>

#### 其他
- 分布式系统之Quorum机制 <https://blog.csdn.net/tb3039450/article/details/80249664>
- NoSQL漫谈 <http://www.nosqlnotes.com/>
- NoSQL简介 <https://www.runoob.com/mongodb/nosql.html>
- NoSQL 还是 SQL ? <https://www.jianshu.com/p/296bacba3510>
- OLAP、OLTP <https://www.jianshu.com/p/b1d7ca178691>
- BeafQPS方法论 <https://mp.weixin.qq.com/s/DsdB7IuWoHnhNNJY1YUSMg>