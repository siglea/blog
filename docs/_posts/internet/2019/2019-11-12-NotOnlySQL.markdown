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
### 存储精华
- 说到存储，其实效率才是最主要的，容量不是我们关心的，但是说到存储，不只是mq，所有需要高效率的存储其实最后利用的核心都是一样的。
    1. 随机写转换成顺序写：现在主流的硬盘是机械硬盘，
        机械硬盘的机械结构一次读写时间 = 寻道时间 + 旋转延迟 + 读取数据时间，
        那么寻道时间比较长，如果是顺序写，只需要一次寻道时间，关于机械硬盘整个过程，读者可自行google。
    2. 集中刷盘：
        因为每次刷盘都会进行系统调用，第二还是跟硬盘的本身属性有关，无论是机械硬盘还是ssd按照一定块刷盘会比小数据刷盘效率更好
- 对于存储系统而言，原本存储在一台机器上的数据，现在要存放在多台机器上。此时必须解决两个问题：分片，复制。
    - 数据分片(sharding)，又称分区(partition)，将数据集“合理的”拆分成多个分片，每台机器负责其中若干个分片。以此来突破单机容量的限制，同时也提升了整体的访问能力。另外，分片也降低了单个分片故障的影响范围。
    - 数据复制(replica)，也叫“副本”。分片无法解决单机故障丢数据的问题，所以，必然要通过冗余来解决系统高可用的问题。同时，副本机制也是提升系统吞吐、解决热点问题的重要手段。
    - 分片和副本是正交的，这意味着我们可以只使用其中一种或都使用，但通常都是同时使用的。因为分片解决的是规模和扩展性的问题，副本解决可靠、可用性的问题。对于一个生产可用的系统，二者必须同时具备。
    - 从使用者/客户端的角度看，分片和副本可以归结为同一个问题：请求路由，即请求应该发送给哪台机器来处理。
    - 读数据时，能通过某种机制来确保有一个合适的分片/副本来提供服务
    - 写数据时，能通过同样的机制来确保写到一个合适的地方，并确保副本的一致性        

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
- 主要使用跳表这种数据结构
- Redis持久化：RDB（快照）和AOF（写命令）
    - RDB相当于全量数据的备份
    - AOF相当于WAL类似的命令日志
    - <https://www.jianshu.com/p/cbe1238f592a>
- Redis淘汰策略
```shell
volatile-lru #从设置了过期时间的数据集中，选择最近最久未使用的数据释放；
allkeys-lru #从数据集中(包括设置过期时间以及未设置过期时间的数据集中)，选择最近最久未使用的数据释放；
volatile-random #从设置了过期时间的数据集中，随机选择一个数据进行释放；
allkeys-random #从数据集中(包括了设置过期时间以及未设置过期时间)随机选择一个数据进行入释放；
volatile-ttl #从设置了过期时间的数据集中，选择马上就要过期的数据进行释放操作；
noeviction #默认值，不删除任意数据(但redis还会根据引用计数器进行释放),这时如果内存不够时，会直接返回错误。
```
- 常用Redis的client，Redisson、Jedis、lettuce
- Redis事务
```shell
watch key1 key2 ... #监视一或多个key,如果在事务执行之前，被监视的key被其他命令改动，则事务被打断 （ 类似乐观锁 ）
multi #标记一个事务块的开始（ queued ）
exec #执行所有事务块的命令 （ 一旦执行exec后，之前加的监控锁都会被取消掉 ）　
discard #取消事务，放弃事务块中的所有命令
unwatch #取消watch对所有key的监控
```
- Redis Sentinel模式，传统的主从高可用模式 <https://www.cnblogs.com/duanxz/p/4701831.html>
    - 多个Sentinel，监控集群
    - Master故障后，Sentinel向其他Sentinel提议选举自己做主Sentinel
    - 选举主Sentinel后，根据规则从Slave中选出一个Slave晋升为Master
    - Sentinel通知客户端节点变更
- Twemproxy/nutcraker ,Redis的"分库分表方案"
    - 能自动分片，方便水平扩展
    - 虽然可以动态移除节点，但该移除节点的数据就丢失了。
      redis集群动态增加节点的时候,twemproxy不会对已有数据做重分布.maillist里面作者说这个需要自己写个脚本实现
- Codis是由豌豆荚开源的产品，涉及组件众多，其中 ZooKeeper 存放路由表和代理节点元数据、分发 Codis-Config 的命令；Codis-Config 是集成管理工具，有 Web 界面供使用；Codis-Proxy 是一个兼容 Redis 协议的无状态代理；Codis-Redis 基于 Redis 2.8 版本二次开发，加入 slot 支持，方便迁移数据。
- Redis Cluster，现代的分布式集群 
- 为什么 Redis 单线程能达到百万+QPS？<https://mp.weixin.qq.com/s/QrvUl6Ul9DxYoRZwSsMQZw>
- Redis 到底是单线程还是多线程？
  - Redis基于Reactor模式开发了网络事件处理器，这个处理器被称为文件事件处理器。它的组成结构为4部分：多个套接字、IO多路复用程序、文件事件分派器、事件处理器。因为文件事件分派器队列的消费是单线程的，所以Redis才叫单线程模型。
  - 其实，Redis 4.0 开始就有多线程的概念了，比如 Redis 通过多线程方式在后台删除对象、以及通过 Redis 模块实现的阻塞命令等。
  - Redis 6.0 加入了 Theaded IO 指的是在网络 IO 处理方面上了多线程，如网络数据的读写和协议解析等，需要注意的是，执行命令的核心模块还是单线程的。估计是乐观锁+悲观锁组合
  <https://mp.weixin.qq.com/s/X3e68ci6O9YPXbCAVaQc_w>

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
- 高可用模式：主从架构（Master-Slave）、副本集架构（Replica Set）、数据分片架构（Sharding）
    <https://www.jianshu.com/p/2825a66d6aed>
    
```sql
show collections -- 类似mysql的table
db.dropDatabase() -- 删除当前数据库
db.create Collection("user") -- 创建user表
use user 
db.user.drop()
db.user.insert({'name':'Mikie Hara','gender':'female','age':26,'salary':7000})  
db.user.save({'name':'Wentworth Earl Miller','gender':'male','age':41,'salary':33000}) 
db.user.find() -- 查看所有
db.user.find({"age":26}) -- 查看 age = 26
db.user.find({salary:{$gt:7000}}) -- 查看 salary > 7000
db.user.find({$or:[{salary:{$gt:10000}},{age:{$lt:25}}]}) -- 查看 OR
db.user.find({age:{$lt:30},salary:{$gt:6000}}) -- 查看 AND
db.user.find({name:/a/}) -- 正则匹配
db.user.find({name:/^W/})
db.user.findOne({$or:[{salary:{$gt:10000}},{age:{$lt:25}}]}) -- 查询一条
db.user.find({},{name:1,age:1,salary:1,sex_orientation:true}) -- 查询指定列
db.user.distinct('gender') -- 去重
db.user.find().pretty() -- 精简显示
db.user.find().limit(2) -- 显示前两条
db.user.find().skip(1) -- 调过第一条
db.user.find().sort({salary:1}) -- 升序
db.user.find().sort({salary:-1}) -- 降序
db.user.find().count() -- 查数
db.user.update({name:'Gal Gadot'},{$set:{age:23}},false,true)  -- 更新 （条件，更新值，不存在是否插入，是否全部更新）
db.user.update({name:'Mikie Hara'},{$set:{interest:"CBA"}},false,true) -- 新加字段
db.user.update({gender:'female'},{$inc:{salary:50}},false,true) -- 自增
db.test.remove() -- 删除
db.users.find({}, {"username": 1}).skip(2).limit(2) -- 分页
db.col.createIndex({"title":1}) -- 升序
db.col.getIndexes()
db.col.totalIndexSize() -- 查看集合索引大小
db.mycol.aggregate([{$group : {_id : "$by_user", num_tutorial : {$sum : 1}}}]) 
--  select by_user, count(*) from mycol group by by_user
db.users.find({gender:"M"},{user_name:1,_id:0}).explain()
db.user.find({"geo": {$near: [118.10388605,24.48923061], $maxDistance:0.1}},{id:1, name:1, state:1, geo:1}).limit(1).pretty()
```

<https://www.jianshu.com/p/fffb581bb1a9>
<https://www.jianshu.com/p/4ecde929b17d>

#### MongoDB的Map/Reduce
- Mongodb 中的 Map/reduce 主要是用来对数据进行批量处理和聚合操作。
- Map 和 Reduce。Map 函数调用 emit(key,value)遍历集合中所有的记录，将 key 与 value 传 给 Reduce 函数进行处理。
- Map 函数和 Reduce 函数是使用 Javascript 编写的，并可以通过 db.runCommand 或 mapre duce 命令来执行 MapReduce 操作。

#### Cassandra
- 我们不能希望cassandra完全适用于我们的逻辑，而是应该将我们的逻辑设计的更适合于cassandra
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

```sql
cqlsh
describe cluster; -- 集群

describe keyspaces; -- 查看已有DataBase
CREATE KEYSPACE tutorialspoint
WITH replication = {'class':'SimpleStrategy', 'replication_factor' : 3};

ALTER KEYSPACE KeySpaceName
WITH replication = {'class': 'Strategy name', 'replication_factor' : 'No.Of  replicas'};

DROP KEYSPACE tutorialspoint;

describe tables; -- 查看已有表
describe table table_name -- 查看表结构
CREATE TABLE users (
  user_id text PRIMARY KEY,
  first_name text,
  last_name text,
  emails set<text> -- 集合 Cassandra特有处理方式
);
INSERT INTO users (user_id, first_name, last_name, emails) VALUES('frodo', 'Frodo', 'Baggins', {'f@baggins.com', 'baggins@gmail.com'});
UPDATE users SET emails = emails + {'fb@friendsofmordor.org'} WHERE user_id = 'frodo';
SELECT user_id, emails FROM users WHERE user_id = 'frodo';
UPDATE users SET emails = emails - {'fb@friendsofmordor.org'} WHERE user_id = 'frodo';

-- 删除所有元素
UPDATE users SET emails = {} WHERE user_id = 'frodo';
DELETE emails FROM users WHERE user_id = 'frodo';

ALTER TABLE users ADD top_places list<text>; -- 向users表添加一个list列
UPDATE users SET top_places = [ 'rivendell', 'rohan' ] WHERE user_id = 'frodo'; -- 使用UPDATA命令向list插入值
UPDATE users SET top_places = [ 'the shire' ] + top_places WHERE user_id = 'frodo'; -- 在list前面插入值 
UPDATE users SET top_places = top_places + [ 'mordor' ] WHERE user_id = 'frodo'; -- 在list后面插入值 

ALTER TABLE users ADD todo map<timestamp, text>;
UPDATE users SET todo = { '2012-9-24' : 'enter mordor', '2014-10-2 12:00' : 'throw ring into mount doom' } WHERE user_id = 'frodo';

-- 使用TTL
UPDATE users USING TTL 86400 SET todo['2012-10-1'] = 'find water' WHERE user_id = 'frodo';
INSERT INTO users (user_name, password) VALUES ('cbrown', 'ch@ngem4a') USING TTL 86400;

-- 给集合添加索引
CREATE INDEX ON users(emails);
SELECT user_id FROM users WHERE emails CONTAINS 'baggins@gmail.com'

-- 分页查询
select * from test where token(a)>token(a10) limit 4;

select * from teacher limit 2;
select * from teacher where token(id)=token(1) and (address,name)>('guangxi','lihao') limit 2 ALLOW FILTERING;
select * from teacher where token(id)>token(1) limit 1; 

COPY users (user_id, first_name, last_name, emails) TO 'kevinfile'; -- 将名为emp的表复制到文件myfile
```

- 使用集合类型要注意：
    1. 集合的每一项最大是64K。
    2. 保持集合内的数据不要太大，免得Cassandra 查询延时过长，只因Cassandra 查询时会读出整个集合内的数据，集合在内部不会进行分页，集合的目的是存储小量数据。
    3. 不要向集合插入大于64K的数据，否则只有查询到前64K数据，其它部分会丢失。
- cassandra高级操作之索引、排序以及分页 <https://www.cnblogs.com/youzhibing/p/6617986.html>
    - Cassandra支持排序，但也是限制重重
        - 必须有第一主键的=号查询；cassandra的第一主键是决定记录分布在哪台机器上，也就是说cassandra只支持单台机器上的记录排序。
        - 只能根据第二、三、四…主键进行有序的，相同的排序。
  　　　　　有序：order by后面只能是先二、再三、再四…这样的顺序，有四，前面必须有三；有三，前面必须有二，以此类推。
  　　　　　相同的顺序：参与排序的主键要么与建表时指定的顺序一致，要么全部相反，具体会体现在下面的示例中
        - 不能有索引查询
    - cassandra的where查询约束
        - 第一主键 只能用=号查询
        - 第二主键 支持= > < >= <=
        - 索引列 只支持=号

### HBase Cassandra MongoDB
- 与RDBMS的区别
    - 关系数据库，磁盘存储是一行接一行，而列式存储是一列接一列
- 存储结构
    - MongoDB：GridFS、JSON/BSON
    - HBase：HRegionServer：【HLog、HRegion：【Store MemStore、StoreFile、HFile】】、HDFS。
        - HBase的数据分片按表进行，以行为粒度，基于rowkey范围进行拆分，每个分片称为一个region。一个集群有多张表，每张表划分为多个region，每台服务器服务很多region。所以，HBase的服务器称为RegionServer，简称RS。RS与表是正交的，即一张表的region会分布到多台RS上，一台RS也会调度多张表的region
        - HBase是水平拆分,意思是行是region划分的最小单位，即一行数据要么属于A region，要么属于Bregion，不会被拆到两个region中去。
        - 浅谈HBase的数据分布 <https://zhuanlan.zhihu.com/p/47074785>
        - hbase.regionserver.global.memstore.upperLimit、hbase.regionserver.global.memstore.lowerLimit、hbase.hregion.memstore.flush.size
        - HLog限制，hase.regionserver.max.logs
    - Cassandra：LSM、HashNode（一致性Hash的虚拟节点）、CommitLog、memtable、SSTable
        - Durable_writes，默认情况下，表的durable_writes属性设置为true，但可以将其设置为false。durable_writes参数用于设置写数据时是否写入commit log,如果设置为false,则写请求不会写commit log，会有丢失数据的风险。此参数默认为true,即要写commit log,生产系统应该将该参数设置为true。
    - HBase、Cassandra都是基于类似的LSM机制
- 存储形式
    - MongoDB：Collection JSON
    - Cassandra：Column family ，Row，Name/Value/Timestamp
    - HBase：put 't_user','1001','st1:age','18'
- 范围分页查询
    - MongoDB：利用skip().limit()实现
    - HBase：scan  'stu2',{COLUMNS => 'cf1:age', LIMMIT 10, STARTROW => 'xx'}
    - Cassandra：select * from teacher where token(id)>token(1) limit 1;
- 数据类型
    - MongoDB丰富，类似SQL
    - HBase只支持字符串
    - Cassandra多种
- 索引、二级索引、辅助索引
    - MongoDB：支持全索引，实现高性能。单一索引、复合、哈希、地址位置、文本等索引。BTree
    - HBase：主要是设计二级索引。二级索引的本质就是建立各列值与行键之间的映射关系。简单的可以借助RowKey
        1. RowKey也是基于B+树
        1. MapReduce方案 
        1. ITHBASE（Indexed-Transanctional HBase）方案 
        1. IHBASE（Index HBase）方案 
        1. Hbase Coprocessor(协处理器)方案 
        1. Solr+HBase方案
        1. CCIndex（complemental clustering index）方案
        1. Phoenix
        1. HBase RowKey与索引设计 <https://www.cnblogs.com/swordfall/p/10597802.html>
    - Cassandra
        - 第一主键 只能用=号查询
        - 第二主键 支持= > < >= <= 但是必须后面加 ALLOW FILTERING
        - 索引列 只支持=号    
        - 索引列 支持 like，只有主键支持 group by
        - PRIMARY KEY (user_id, uploaded_date, article_id)，第一列仍然是数据的partition key。其后所跟的所有的列都称为clustering column
        - CQL查询语句的特殊规则 <https://blog.csdn.net/ZZQHELLO2018/article/details/106302161>
- 事务
    - HBase的事务是行级事务，可以保证行级数据的原子性、一致性、隔离性以及持久性
    - MongoDB不支持事务
    - Cassandra支持行一级的原子性和隔离性，但与之交换的是高度的可用性和快速的读写性能。Cassandra写入具有持久性。
- 一致性和CAP
    - MongoDB、HBase强一致性，CP，0 数据丢失
    - Cassandra最终一致性（可调一致性），数据可能丢失，AP
        - Consistency，此命令显示当前的一致性级别，或设置新的一致性级别。Consistency可以理解读和写操作的Consistency Level。
          写操作的consistency level指定了写操作在通知客户端请求成功之前，必须确保已经成功完成写操作的replica的数量。
- Join支持
    - MongoDB不支持多表连接
    - Cassandra不支持多表连接，用数据冗余解决问题hotels_by_poi
    - HBase不支持Join，需要借助其他工具或者算法实现 
- 读写
    - HBase快速读取和写入，具有可扩展性。读写性能数据读写定位可能要通过最多 6 次的网络RPC，性能较低。
    - Cassandra快速随机性读取/写入，写多读少。数据读写定位非常快。
    
- MongoDB、HBase、Cassandra比较<https://www.cnblogs.com/yanduanduan/p/10563678.html>    
- Hbase和Cassandra <https://blog.csdn.net/aa5305123/article/details/83142514>    

<pre>
1.强一致性的读写：HBase不是一个最终一致性的存储。
2.自动sharding：HBase的table在集群种被分布在各个region，region可以做自动切分。
3.regionserver的failover；
4.Hadoop/HDFS的集成；
5.MapReduce：支持大数据的并行处理；
6.JAVA Client 以及Thrift/RESR API 访问；
7.Block Cache 以及Bloom filter；
8.操作管理。

1.C*借鉴Dynamo的架构思想，把自己叫做一个最终一致性的系统，如果使用至少是QUORUM 读写，还算是一个强一致的系统。
2.C*的sharding方式：一致性hash，有2种：
（1）人为配置好initial_token；
2.使用vnode，集群初始化以及节点bootstrap的时候会计算token，基于这些token做数据sharding。
3.可以容忍：replicator_number - (read/write level sufficient nodes)个节点挂了，比如3个副本，读写级别QUORUM（sufficient nodes是2），能容忍1节点挂；
4.支持MapReduce;
5.Thrift、CQL访问;
6.大数据处理的bloom filter 必备；
7.自己有jmx等常见管理，且datastax 公司有提供ops center；
</pre>
        
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

#### 常见 TSDB 时间序列数据库 Time Series Database ：influxdb、opentsdb、timeScaladb、Druid 、tablestore、ClickHouse等
- 持续高并发写入、无更新；数据压缩存储；低查询延时。
- 一种集时序数据高效读写，压缩存储，实时计算能力为一体的数据库服务，可广泛应用于物联网和互联网领域，实现对设备及业务服务的实时监控，实时预测告警。
<https://www.jianshu.com/p/31afb8492eff>
- 阿里巴巴双11千万级实时监控系统技术揭秘  <https://www.sohu.com/a/300572910_465959>

#### 其他
- 分布式系统之Quorum机制 <https://blog.csdn.net/tb3039450/article/details/80249664>
- NoSQL漫谈 <http://www.nosqlnotes.com/>
- NoSQL简介 <https://www.runoob.com/mongodb/nosql.html>
- NoSQL 还是 SQL ? <https://www.jianshu.com/p/296bacba3510>
- OLAP、OLTP <https://www.jianshu.com/p/b1d7ca178691>
- BeafQPS方法论 <https://mp.weixin.qq.com/s/DsdB7IuWoHnhNNJY1YUSMg>