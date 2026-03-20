---
layout: post
title:  "Elasticsearch实战指南：从核心概念到亿级数据性能优化"
date:   2019-11-04 11:25:00 +0900
comments: true
tags:
- 数据库
- 分布式
categories:
- 技术
---

Elasticsearch（简称 ES）是当前最流行的分布式搜索和分析引擎，广泛应用于全文搜索、日志分析、业务监控等场景。它基于 Apache Lucene 构建，提供了简洁的 RESTful API 和强大的分布式能力。本文将从 ES 的核心概念入手，深入剖析其索引结构、集群选举、查询优化等关键技术，并结合实际案例探讨亿级数据量下的性能调优策略。

---

## 推荐资源

- Elasticsearch 专栏 <https://mp.weixin.qq.com/mp/appmsgalbum?action=getalbum&album_id=1340073242396114944&__biz=MzI2NDY1MTA3OQ==&scene=21#wechat_redirect>
- 腾讯 Elasticsearch 海量规模背后的内核优化剖析 <https://mp.weixin.qq.com/s/OGY2FB1FfyPBHeG-kKX_Xw>
- 腾讯万亿级 Elasticsearch 内存效率提升技术解密 <https://mp.weixin.qq.com/s/ipuIq_E5rOPPF7_XdS5PGQ>
- Elasticsearch 在各大互联网公司的真实应用案例 <https://mp.weixin.qq.com/s/Sntf8JoHYFSqkqRtcvVReQ>

---

## 基础入门

如果你是 ES 新手，建议从以下资源开始：

- 全文搜索引擎 Elasticsearch 入门教程 <http://www.ruanyifeng.com/blog/2017/08/elasticsearch.html>
- Elasticsearch 之基础概念 <https://www.jianshu.com/p/d68197bc7def>
- [ES 官网](https://www.elastic.co/cn/products/elasticsearch)

---

## 性能优化高级技巧

在生产环境中，ES 的性能调优直接影响搜索体验和系统稳定性。以下是经过实践验证的优化策略：

1. **合理分配节点角色**：`node.master: false` 和 `node.data: true`，优先确定好 Master 节点和 Data 节点的比例
2. **锁定内存**：`bootstrap.mlockall: true`，ES 主要依赖内存提高效率，需要锁定内存防止 Swapping，同时要预留充足的 HeapSize
3. **优化集群重启恢复**：通过设置 `gateway.recover_after_nodes`、`gateway.expected_nodes`、`gateway.recover_after_time`，可以在集群重启时避免过多的分片交换，将数据恢复时间从数小时缩短为几秒
4. **不要随意修改 GC 和线程池配置**：默认的 CMS 垃圾回收器和线程池大小经过精心调优
5. **使用单播发现**：ES 默认配置为单播发现，防止节点无意加入集群。最好使用单播代替组播

```shell
discovery.zen.ping.multicast.enabled:false
discovery.zen.ping.unicast.hosts:["esmaster01","esmaster02","esmaster03"]
```

6. **防止误删**：`action.disable_delete_all_indices: true`
7. **定期合并 Segment**：调整 force_merge 参数，闲时合并小的 Segment 到大的。参考 <https://blog.csdn.net/jiankunking/article/details/84667437>
8. **冷数据收缩**：定期进行 shrink 操作以缩减存储。参考 <https://my.oschina.net/5icode/blog/2872151>
9. **索引生命周期管理**：采取 curator 进行管理。参考 <https://blog.csdn.net/laoyang360/article/details/85882832>
10. **索引重建使用别名**：参考 <https://blog.csdn.net/u010454030/article/details/84918103>
11. **精细化 Mapping 设计**：充分结合各字段属性，明确是否需要检索、是否需要存储

参考：
- <https://blog.csdn.net/xshy3412/article/details/51841270>
- <https://blog.csdn.net/u014646662/article/details/99293604/>

---

## Filter 与 Query 的区别

ES 的搜索分为过滤（Filter）和查询（Query）两大类，理解二者的区别对于写出高效的搜索语句至关重要。

### Filter（结构化检索）

类似 SQL 的 WHERE 子句，用于精确匹配和范围筛选，不计算相关性评分，且结果可以被缓存：

- `term`：完全匹配，不分词
- `range` / `exists` / `prefix` / `wildcard` / `regexp` / `type` / `ids` / `fuzzy`：模糊匹配

### Query（全文检索）

使用倒排索引进行搜索，计算相关性评分：

- `match query`：分词全文检索
- `match_phrase query`：短语检索
- `match_phrase_prefix`：短语前缀检索
- `multi_match`：多字段匹配检索

### 复合检索

- 固定得分、Bool 组合、改变评分检索
- 特定检索：父子文档检索、Geo 检索

参考：<https://mp.weixin.qq.com/s/tiiveCW3W-oDIgxvlwsmXA>

---

## Lucene 索引文件结构

理解 Lucene 的索引结构有助于深入理解 ES 的底层工作原理：

- **索引（Index）**：Lucene 的索引由许多文件组成，放在同一个目录下
- **段（Segment）**：一个索引由多个段组成，段与段之间独立。添加新文档时生成新段，达到阈值时不同段可以合并。`segments.gen` 和 `segments_N` 是段的元数据文件
- **文档（Document）**：建索引的基本单位，一个段中可以包含多篇文档
- **域（Field）**：一个文档由多个域组成（如标题、作者、正文等），不同域可指定不同的索引方式
- **词（Term）**：索引的最小单位，是经过词法分词和语言处理后的字符串

---

## Master 选举机制

ES 的 Master 选举是其分布式协调的核心机制。相比于其他一致性方案，ES 的方案没有 term 的概念，因此在同一个选举周期内可能出现 NodeA 投票给多个 Node 的情况，这种情况会在广播时由其中一个 Master 自动降级。

ES 使用 quorum（多数派）思想避免 Split-brain：只有获得超过半数选票的节点才能成为 Master，通过 `discovery.zen.minimum_master_nodes` 设置（一般为 `eligibleNodesNum / 2 + 1`）。

### 选举触发条件

- 当前 Master Eligible 节点不是 Master
- 当前 Master Eligible 节点与其它节点通信无法发现 Master
- 集群中无法连接到 Master 的 Master Eligible 节点数量已达到 `minimum_master_nodes` 设定值

### 选举过程

1. 寻找 clusterStateVersion 比自己高的 Master Eligible 节点，向其发送选票
2. 如果 clusterStateVersion 一样，则选节点 ID 最小的节点，向该节点投票
3. 如果一个节点收到足够多的投票（>= minimum_master_nodes），并且也向自己投票了，则成为 Master 开始发布集群状态
4. 超时则进入下一轮

**ZenDiscovery** 是 ES 的节点发现组件，类似于 Hadoop 的 ZooKeeper 或 RocketMQ 的 NameServer。

参考：
- <https://blog.csdn.net/ailiandeziwei/article/details/87856210>
- <https://www.cnblogs.com/dogs/p/11511458.html>

---

## ES 核心概念

ES 的数据组织层次与关系型数据库有相似之处，但也有本质区别：

- **Index（索引，类比数据库）**：包含一堆有相似结构的文档数据，比如客户索引、商品分类索引、订单索引
- **Type（类型，类比表）**：每个索引里可以有一个或多个 Type。**注意**：ES 6.x 版只允许每个 Index 包含一个 Type，7.x 版已彻底移除 Type
- **Document（文档，类比行）**：ES 中的最小数据单元，通常用 JSON 结构表示
- **Field（字段，类比列）**：一个 Document 里面有多个 Field
- **Mapping（映射，类比约束）**：定义 Document 中每个字段的类型、使用的分析器、是否索引等属性
- **Shard（分片）**：解决节点容量上限问题，通过将 Index 分为多个分片实现水平扩展，默认通过 `hash(文档id)` 决定数据归属
- **Replicas（副本）**：提供数据冗余保护和搜索性能提升。如 replicas=2，则每条数据共有三份（1 个 Primary Shard + 2 个 Replica Shard），统称 Replicas Group

底层存储采用 **LSM（Log Structured Merge Trees）** 思想，通过 Translog 和 In-memory Buffer 实现高性能写入。参考 <https://www.cnblogs.com/luxiaoxun/p/13025019.html>

为了解决磁盘 IO 问题，Lucene 引入了倒排索引的二级索引 **FST（Finite State Transducer）**，原理类似前缀树，加速查询。

---

## 常用命令

以下是 ES 日常操作中最常用的 RESTful API 命令：

```shell
$ curl localhost:9200 # 默认来一下
{
  "name" : "atntrTf",
  "cluster_name" : "elasticsearch",
  "cluster_uuid" : "tf9250XhQ6ee4h7YI11anA",
  "version" : {
    "number" : "5.5.1",
    "build_hash" : "19c13d0",
    "build_date" : "2017-07-18T20:44:24.823Z",
    "build_snapshot" : false,
    "lucene_version" : "6.6.0"
  },
  "tagline" : "You Know, for Search"
}

#查看节点所有的Index
curl -X GET 'http://localhost:9200/_cat/indices?v'

#查看所有Type
curl 'localhost:9200/_mapping?pretty=true'

#新建Index
curl -X PUT 'localhost:9200/weather'
{
  "acknowledged":true,
  "shards_acknowledged":true
}

#删除Index
curl -X DELETE 'localhost:9200/weather'

# 新建Index附件结构 Index:accounts Type:person
# 新建一个名称为accounts的 Index，里面有一个名称为person的 Type。person有三个字段。
curl -X PUT 'localhost:9200/accounts' -d '
{
  "mappings": {
    "person": {
      "properties": {
        "user": {
          "type": "text",
          "analyzer": "ik_max_word",
          "search_analyzer": "ik_max_word"
        },
        "title": {
          "type": "text",
          "analyzer": "ik_max_word",
          "search_analyzer": "ik_max_word"
        },
        "desc": {
          "type": "text",
          "analyzer": "ik_max_word",
          "search_analyzer": "ik_max_word"
        }
      }
    }
  }
}'

#给指定Index指定的type增加Document
$ curl -X PUT 'localhost:9200/accounts/person/1' -d '
{
  "user": "张三",
  "title": "工程师",
  "desc": "数据库管理"
}'
{
  "_index":"accounts",
  "_type":"person",
  "_id":"1",
  "_version":1,
  "result":"created",
  "_shards":{"total":2,"successful":1,"failed":0},
  "created":true
}

$ curl -X POST 'localhost:9200/accounts/person' -d '
{
  "user": "李四",
  "title": "工程师",
  "desc": "系统管理"
}'
{
  "_index":"accounts",
  "_type":"person",
  "_id":"AV3qGfrC6jMbsbXb6k1p",
  "_version":1,
  "result":"created",
  "_shards":{"total":2,"successful":1,"failed":0},
  "created":true
}


#查看指定Index指定的type的指定Document
curl 'localhost:9200/accounts/person/1?pretty=true'
{
  "_index" : "accounts",
  "_type" : "person",
  "_id" : "1",
  "_version" : 1,
  "found" : true,
  "_source" : {
    "user" : "张三",
    "title" : "工程师",
    "desc" : "数据库管理"
  }
}

#查看指定Index指定的type的所有记录
$ curl 'localhost:9200/accounts/person/_search'
{
  "took":2,
  "timed_out":false,
  "_shards":{"total":5,"successful":5,"failed":0},
  "hits":{
    "total":2,
    "max_score":1.0,
    "hits":[
      {
        "_index":"accounts",
        "_type":"person",
        "_id":"AV3qGfrC6jMbsbXb6k1p",
        "_score":1.0,
        "_source": {
          "user": "李四",
          "title": "工程师",
          "desc": "系统管理"
        }
      },
      {
        "_index":"accounts",
        "_type":"person",
        "_id":"1",
        "_score":1.0,
        "_source": {
          "user" : "张三",
          "title" : "工程师",
          "desc" : "数据库管理，软件开发"
        }
      }
    ]
  }
}

# Elastic 默认一次返回10条结果，可以通过size字段改变这个设置
$ curl 'localhost:9200/accounts/person/_search'  -d '
{
  "query" : { "match" : { "desc" : "管理" }},
  "size": 1
}'

#搜索指定Index指定的type的复合搜索条件的记录 from:偏移量 size:数据量
#该分页方式是假分页，会读取整体数据只显示size，数据量超过1万性能急剧下降
curl 'localhost:9200/accounts/person/_search'  -d '
{
  "query" : { "match" : { "desc" : "管理" }},
  "from": 1,
  "size": 1
}'

#逻辑搜索 OR 关系
curl 'localhost:9200/accounts/person/_search'  -d '
{
  "query" : { "match" : { "desc" : "软件 系统" }}
}'

#逻辑搜索 AND 关系
curl 'localhost:9200/accounts/person/_search'  -d '
{
  "query": {
    "bool": {
      "must": [
        { "match": { "desc": "软件" } },
        { "match": { "desc": "系统" } }
      ]
    }
  }
}'

#scroll分页查询
#区别于from size的方式的本质是采用类似Oracle的游标
curl -XGET 'localhost:9200/twitter/tweet/_search?scroll=1m' -d '
{
    "query": {
        "match" : {
            "title" : "elasticsearch"
        }
    }
}
'

curl -X GET  'localhost:9200/_search/scroll?scroll=1m&scroll_id=c2Nhbjs2OzM0NDg1ODpzRlBLc0FXNlNyNm5JWUc1'

```

---

## 分布式原理

### 倒排索引

倒排索引是 ES 搜索能力的核心：
1. 建立 `key => value-index => value` 的映射关系
2. 对文本进行分词、过滤停用词、相似词合并
3. 构建索引

### 分布式机制

1. ES 会对数据进行切分，每个分片保存多个副本
2. 数据写入和索引建立都是先在 Master 完成再同步到 Slave
3. 选举策略和 ZooKeeper/Redis 集群类似（拜占庭将军问题）：
    - Master 节点宕机：重新选举
    - 非 Master 节点宕机：Master 将该节点上的 Primary Shard 身份转移到其他 Replica Shard。修复后 Master 控制分配缺失的 Replica Shard 并同步数据
4. 分布式查询类似 Map/Reduce
5. **NRT（Near RealTime）**：默认每秒 refresh 一次，写入的数据 1 秒后才能被看到
    - 数据路径：buffer → segment file → os cache → 磁盘
    - 日志路径：trans_log → os cache → 磁盘
    - 关键操作：refresh、flush、translog、merge
6. 默认 primary shard=5，replica=1，共计 10 个 shard

### 写数据过程

1. 客户端选择一个 Node 发送请求，该 Node 成为 Coordinating Node（协调节点）
2. Coordinating Node 对 Document 进行路由，将请求转发给对应的 Primary Shard 所在 Node
3. Primary Shard 处理请求，然后将数据同步到 Replica Node
4. Coordinating Node 确认 Primary 和所有 Replica 都完成后，返回响应

### 读数据过程

1. 客户端发送请求到任意 Node，成为 Coordinating Node
2. Coordinating Node 对 Document 路由，使用 Round-Robin 随机轮询算法在 Primary Shard 及其所有 Replica 中选择一个，实现读请求负载均衡
3. 接收请求的 Node 返回 Document 给 Coordinating Node
4. Coordinating Node 返回 Document 给客户端

---

## 亿级数据性能优化实战

在处理亿级数据时，ES 的性能优化需要从多个维度入手：

- **用内存换速度**：ES 严重依赖底层的 Filesystem Cache。给 Filesystem Cache 更多内存，让内存可以容纳所有 Index Segment File，搜索基本走内存，性能极高。最佳情况是机器内存至少能容纳总数据量的一半。
- **减少 ES 中无用字段的数据量**：采用 ES + HBase 的架构，ES 只存索引字段，全量数据放 HBase
- **数据预热，冷热分离，冗余数据**：将热点数据提前加载到缓存
- **由应用服务器完成部分逻辑运算**：减轻 ES 的计算压力
- **使用 Scroll API 优化分页性能**：避免 from+size 深分页带来的性能问题

### 实战案例

- 5 台机器，每台 6 核 64G，集群总内存 320G
- 日增量数据约 2000 万条（约 500MB），每月增量约 6 亿条（15G），数据总量约 100G
- Index 数据量预估和 Shard 个数预估（不支持后续增加 Shard，需要重建），建议每个 Shard 小于 30G

---

## ES 高并发线程安全

在读数据与写数据之间如果有其他线程进行写操作就会出问题。ES 使用**版本控制**来避免这种问题——在修改数据时指定版本号，操作一次版本号加 1。

---

## Bulk API 数据量限制

Bulk 会将处理的数据载入内存，最佳数据量不是固定值，取决于硬件、文档大小和复杂性、索引和搜索负载。一般建议 1000-5000 个文档，大小建议 5-15MB。默认不能超过 100M，可通过 `http.max_content_length: 100mb` 修改。

---

## 客户端连接策略

TransportClient 利用 Transport 模块远程连接 ES 集群，它并不加入集群，只是获得一个或多个初始化的 Transport 地址，并以轮询方式与这些地址通信。

---

## 大数据量聚合

ES 提供的首个近似聚合是 Cardinality 度量，基于 **HLL（HyperLogLog）算法**。它先对输入做哈希运算，然后根据结果中的 bits 做概率估算得到基数。特点是：可配置精度以控制内存使用；小数据集精度非常高；无论数千还是数十亿唯一值，内存使用量只与配置的精确度相关。

---

## Lucene 生态：Nutch、Solr 与 Elasticsearch

- **Lucene**：提供全文搜索的函数库，不是一个应用软件
- **Nutch**：Lucene + 爬虫，分布式爬虫系统
- **Solr**：基于 Lucene 的完整搜索服务，属于 Apache 开源项目
- **Elasticsearch**：同样基于 Lucene，专注分布式搜索和实时分析

### Solr vs Elasticsearch

- Solr 利用 ZooKeeper 进行分布式管理，ES 自带分布式协调
- Solr 支持更多格式，ES 仅支持 JSON
- Solr 官方功能更多，ES 注重核心功能，高级功能多由第三方插件提供
- Solr 在传统搜索中表现更好，但处理**实时搜索**时效率明显低于 ES

### 关于 Nutch

Nutch 诞生于 2002 年 8 月，自 1.2 版本后从搜索引擎演化为网络爬虫。1.x 基于 Hadoop/HDFS，2.x 通过 Apache Gora 支持 HBase、Cassandra、MySQL 等多种存储。

参考：
- <https://www.cnblogs.com/yinhaiming/articles/1542921.html>
- <https://www.cnblogs.com/fosilzhou/articles/4629220.html>
- <https://blog.csdn.net/xiaoyu714543065/article/details/10374191>

---

## 管理工具

- BigDesk Plugin
- Elasticsearch Head Plugin
- Kibana

---

## ELK 与其他搭配

- **ELK 系统**：E（Elasticsearch）+ L（Logstash，日志收集系统）+ K（Kibana，数据可视化平台），是最经典的日志分析架构
- **ElasticSearch + HBase**：ES 做索引，HBase 存全量数据
- 其他相关项目：Katta、Hadoop contrib/index、Lucandra、HBasene

---

## 总结

Elasticsearch 的强大在于其分布式架构和近实时的搜索能力。在实际应用中，合理的 Mapping 设计、恰当的分片策略、充足的内存配置是保障性能的三大基石。对于大规模数据场景，建议采用 ES + HBase 的混合架构，让 ES 专注于搜索索引，将全量数据存储交给更适合的系统。

#### 参考资料
- Elasticsearch 在各大互联网公司的真实应用案例 <https://mp.weixin.qq.com/s/Sntf8JoHYFSqkqRtcvVReQ>
- 漫画讲原理 <http://developer.51cto.com/art/201904/594615.htm>
- 搜索引擎之倒排索引解读 <https://www.jianshu.com/p/b3f987b0fbf1>
- [Java实战教程大数据技术之Elasticsearch](https://www.jianshu.com/p/3fa27dda63ab)
- 腾讯 Elasticsearch 海量规模背后的内核优化剖析 <https://mp.weixin.qq.com/s/OGY2FB1FfyPBHeG-kKX_Xw>
- 腾讯万亿级 Elasticsearch 内存效率提升技术解密 <https://mp.weixin.qq.com/s/ipuIq_E5rOPPF7_XdS5PGQ>
