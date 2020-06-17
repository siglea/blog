---
layout: post
title:  " Elasticsearch  Summary "
date:   2019-11-04 11:25:00 +0900
comments: true
tags:
- 数据库
- 分布式
categories:
- 技术
---
#### 前言
- 腾讯Elasticsearch海量规模背后的内核优化剖析 <https://mp.weixin.qq.com/s/OGY2FB1FfyPBHeG-kKX_Xw>
- 腾讯万亿级 Elasticsearch 内存效率提升技术解密 <https://mp.weixin.qq.com/s/ipuIq_E5rOPPF7_XdS5PGQ>
- Elasticsearch 在各大互联网公司大量真实的应用案例！ <https://mp.weixin.qq.com/s/Sntf8JoHYFSqkqRtcvVReQ>

#### 基础入门
- 全文搜索引擎 Elasticsearch 入门教程 <http://www.ruanyifeng.com/blog/2017/08/elasticsearch.html>
- Elasticsearch之基础概念 <https://www.jianshu.com/p/d68197bc7def>
- [ec官网](https://www.elastic.co/cn/products/elasticsearch)


#### es的核心概念
- Index（索引-数据库），
索引包含一堆有相似结构的文档数据，，比如可以有一个客户索引，商品分类索引，订单索引，索引有一个名称。一个index包含很多document，一个index就代表了一类类似的或者相同的document。比如说建立一个product index，商品索引，里面可能就存放了所有的商品数据，所有的商品document。
- Type（类型-表），
每个索引里都可以有一个或多个type，type是index中的一个逻辑数据分类，一个type下的document，都有相同的field。
根据规划，Elastic 6.x 版只允许每个 Index 包含一个 Type，7.x 版将会彻底移除 Type
- Document（文档-行），
文档是es中的最小数据单元，一个document可以是一条客户数据，一条商品分类数据，一条订单数据，通常用JSON数据结构表示，每个index下的type中，都可以去存储多个document。
- Field（字段-列），
Field是Elasticsearch的最小单位。一个document里面有多个field，每个field就是一个数据字段。
- mapping（映射-约束），
数据如何存放到索引对象上，需要有一个映射配置，包括：数据类型、是否存储、是否分词等。这样就创建了一个名为blog的Index。Type不用单独创建，在创建Mapping 时指定就可以。Mapping用来定义Document中每个字段的类型，即所使用的 analyzer、是否索引等属性，非常关键等。
- shard 分片，
es中的shard用来解决节点的容量上限问题,通过将index分为多个分片(默认为一个也就是不分片),一个或多个node共同存储该index的所有数据实现水平拓展(类似于关系型数据库中的分表)它们共同持有该索引的所有数据,默认通过hash(文档id)决定数据的归属
- replicas 副本，
    replicas主要为了以下两个目的，
    由于数据只有一份,如果一个node挂了,那存在上面的数据就都丢了,有了replicas,只要不是存储这条数据的node全挂了,数据就不会丢。
    通过在所有replicas上并行搜索提高搜索性能.由于replicas上的数据是近实时的(near realtime),因此所有replicas都能提供搜索功能,通过设置合理的replicas数量可以极高的提高搜索吞吐量。
    eg,如果指定了replicas=2,那么对于一条数据它共有三份,一份称为primary shard,另外两份称为 replicas shard. 这三个统称为replicas group(副本组)。
- ZenDiscovery，节点发现组件(类似于Hadoop的ZK，或者RocketMq的nameserver)
- LSM思想，Translog In-memory buffer
- 为了解磁盘 IO 问题，Lucene 引入排索引的二级索引 FST [Finite State Transducer] 。原理上可以理解为前缀树，加速查询。

#### 常用命令
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

#### 相关原理
- 倒排索引
    1. key => value-index => value
    2. 分词、过滤助动叹词、相似词合并
    3. 索引建立
- 分布式
    1. Elasticsearch也是会对数据进行切分，同时每一个分片会保存多个副本
    1. 数据写入和索引建立，都是先在master完成再同步到slave
    1. 选举策略和zk/redis集成都很类似(拜占庭将军问题)
        1. master节点宕机了，那么会重新选举一个节点为master节点。
        1. 如果是非master节点宕机了，那么会由master节点，让那个宕机节点上的primary shard的身份转移到其他机器上的replica shard。
           修复了那个宕机机器，重启了之后，master节点会控制将缺失的replica shard分配过去，同步后续修改的数据之类的，让集群恢复正常。
    1. 分布式查询操作类似Map/Reduce
    1. NRT(Near RealTime)
        - 默认是每隔1秒refresh一次的，所以es是准实时的，因为写入的数据1秒之后才能被看到。
        - -> buffer -> segment file -> os cache -> 磁盘 
        - -> trans_log -> os cache -> 磁盘
        - refresh、flush、translog、merge
    1. 默认primary shard=5，replica=1共计10shard
    1. es写数据过程
        1. 客户端选择一个node发送请求过去，这个node就是coordinating node（协调节点）
        2. coordinating node，对document进行路由，将请求转发给对应的node（有primary shard）
        3. 实际的node上的primary shard处理请求，然后将数据同步到replica node
        4. coordinating node，如果发现primary node和所有replica node都搞定之后，就返回响应结果给客户端
    1. es读取数据过程
        1. 客户端发送请求到任意一个node，成为coordinate node
        2. coordinate node对document进行路由，将请求转发到对应的node，此时会使用round-robin随机轮询算法，在primary shard以及其所有replica中随机选择一个，让读请求负载均衡
        3. 接收请求的node返回document给coordinate node
        4. coordinate node返回document给客户端

#### 实战总结亿级性能
- 用内存换速度
   es的搜索引擎严重依赖于底层的filesystem cache，你如果给filesystem cache更多的内存，尽量让内存可以容纳所有的indx segment file索引数据文件，
   那么你搜索的时候就基本都是走内存的，性能会非常高。归根结底，你要让es性能要好，最佳的情况下，就是你的机器的内存，至少可以容纳你的总数据量的一半.
- 减少es中的无用字段的数据量(es+hbase)
- 数据预热，冷热分离，冗余数据
- 由应用服务器完成某些逻辑及运算操作
- 使用sroll api优化分页性能

##### 实战案例
- 5台机器，每台机器是6核64G的，集群总内存是320G
- es集群的日增量数据大概是2000万条，每天日增量数据大概是500MB，每月增量数据大概是6亿，15G。（数据总量大概是100G左右）
- index数据量预估，shard个数预估（不支持后续增加shard需要重建),建议每个shard小于30G

#### 参考资料
-  Elasticsearch 在各大互联网公司大量真实的应用案例！ ☆☆☆<https://mp.weixin.qq.com/s/Sntf8JoHYFSqkqRtcvVReQ>
- 漫画讲原理 <http://developer.51cto.com/art/201904/594615.htm>
- 搜索引擎之倒排索引解读 <https://www.jianshu.com/p/b3f987b0fbf1>
- [java实战教程大数据技术之elasticsearch](https://www.jianshu.com/p/3fa27dda63ab)
-  腾讯Elasticsearch海量规模背后的内核优化剖析 <https://mp.weixin.qq.com/s/OGY2FB1FfyPBHeG-kKX_Xw>
-  腾讯万亿级 Elasticsearch 内存效率提升技术解密 <https://mp.weixin.qq.com/s/ipuIq_E5rOPPF7_XdS5PGQ>

#### lucene & nutch（2002） & Solr（2004）&  Elasticsearch（2010） 
- Lucene其实是一个提供全文文本搜索的函数库，它不是一个应用软件
- Nutch = Lucene + 爬虫
- Solr 是基于Lucene的一套完整的搜索服务属于Apache开源项目
- Nutch是分布式爬虫系统，solr是搜索引擎

##### Solr & Elasticsearch
- Solr 利用 Zookeeper 进行分布式管理，而 Elasticsearch 自身带有分布式协调管理功能;
- Solr 支持更多格式的数据，而 Elasticsearch 仅支持json文件格式；
- Solr 官方提供的功能更多，而 Elasticsearch 本身更注重于核心功能，高级功能多有第三方插件提供；
- Solr 在传统的搜索应用中表现好于 Elasticsearch，但在处理实时搜索应用时效率明显低于 Elasticsearch。

##### 关于Nutch
- Nutch诞生于2002年8月，是Apache旗下的一个用Java实现的开源搜索引擎项目，
自Nutch1.2版本之后，Nutch已经从搜索引擎演化为网络爬虫，接着Nutch进一步演化为两大分支版本：1.X和2.X，
这两大分支最大的区别在于2.X对底层的数据存储进行了抽象以支持各种底层存储技术。
- 1.x版本是基于Hadoop架构的，底层存储使用的是HDFS，而2.x通过使用Apache Gora，
使得Nutch可以访问HBase、Accumulo、Cassandra、MySQL、DataFileAvroStore、AvroStore等NoSQL。
- nutch主要用于采集网页，solr可以作为搜索服务器。nutch+solr可以搭建一个简单的搜索引擎。
- 简单地讲，nutch就是用于分布式采集数据源，solr用于建索引和搜索服务。

##### 参考资料
- <https://www.cnblogs.com/yinhaiming/articles/1542921.html>
- <https://www.cnblogs.com/fosilzhou/articles/4629220.html>
- <https://blog.csdn.net/xiaoyu714543065/article/details/10374191>
- <https://www.ibm.com/developerworks/cn/opensource/os-cn-BigInsightsNutchSolr/>
- <https://www.jianshu.com/p/366d9bd38d14>

#### 其他
- ELK 系统，也就是日志分析系统。其中 E 就是 Elasticsearch，L 是 Logstash，是一个日志收集系统，K 是 Kibana，是一个数据可视化平台。
- ElasticSearch + Hbase
- Katta Hadoop contrib/index Lucandra HBasene








