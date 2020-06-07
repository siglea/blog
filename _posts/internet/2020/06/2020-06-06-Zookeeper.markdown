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

<https://mp.weixin.qq.com/s/ouayPydKCWc0FfGlaSnCrg>