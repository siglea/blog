---
layout: post
title:  " Elasticsearch  Demo "
date:   2019-11-04 11:25:00 +0900
comments: true
tags:
- 分布式搜索引擎
- 全文搜索引擎
categories:
- 互联网
---
#### 基础入门
http://www.ruanyifeng.com/blog/2017/08/elasticsearch.html
https://www.jianshu.com/p/d68197bc7def
#### 常用命令
```shell
#查看节点左右的Index
curl -X GET 'http://localhost:9200/_cat/indices?v'

#查看所有Type
curl 'localhost:9200/_mapping?pretty=true'

#新建Index
curl -X PUT 'localhost:9200/weather'

#删除Index
curl -X DELETE 'localhost:9200/weather'

#新建Index附件结构 Index:accounts Type:person
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

#查看指定Index指定的type的指定Document
curl 'localhost:9200/accounts/person/1?pretty=true'

#查看指定Index指定的type的所有记录
$ curl 'localhost:9200/accounts/person/_search'

#搜索指定Index指定的type的复合搜索条件的记录 from:偏移量 size:数据量
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

```
#### java教程
https://www.jianshu.com/p/3fa27dda63ab
#### lucene & nutch（2002） 
https://www.cnblogs.com/yinhaiming/articles/1542921.html
#### Elasticsearch（2010） & Solr（2004）
https://www.cnblogs.com/fosilzhou/articles/4629220.html

#### 原理
http://developer.51cto.com/art/201904/594615.htm
https://www.jianshu.com/p/b3f987b0fbf1
https://blog.csdn.net/JENREY/article/details/81290535

#### 其他
https://www.aboutyun.com/thread-14986-1-1.html
https://www.aboutyun.com/forum.php?mod=viewthread&tid=17406&page=1
https://www.jianshu.com/p/366d9bd38d14

网络爬虫将抓取到的HTML页面解析完成之后，把解析出的数据加入缓冲区队列，由其他两个线程负责处理数据，一个线程负责将数据保存到分布式数据库，一个线程负责将数据提交到搜索引擎进行索引。
https://blog.csdn.net/xiaoyu714543065/article/details/10374191
https://www.ibm.com/developerworks/cn/opensource/os-cn-BigInsightsNutchSolr/
nutch是分布式爬虫系统，solr是搜索引擎。（1） Nutch诞生于2002年8月，是Apache旗下的一个用Java实现的开源搜索引擎项目，自Nutch1.2版本之后，Nutch已经从搜索引擎演化为网络爬虫，接着Nutch进一步演化为两大分支版本：1.X和2.X，这两大分支最大的区别在于2.X对底层的数据存储进行了抽象以支持各种底层存储技术。（2） 1.x版本是基于Hadoop架构的，底层存储使用的是HDFS，而2.x通过使用Apache Gora，使得Nutch可以访问HBase、Accumulo、Cassandra、MySQL、DataFileAvroStore、AvroStore等NoSQL。（3）nutch主要用于采集网页，solr可以作为搜索服务器。nutch+solr可以搭建一个简单的搜索引擎。（4）简单地讲，nutch就是用于分布式采集数据源，solr用于建索引和搜索服务。

#### 故事
