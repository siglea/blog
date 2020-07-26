---
layout: post
title:  "高可用高并发"
date:   2020-07-26 14:36:00 +0900
comments: true
tags:
- 分布式
categories:
- 技术
---
#### 高可用
- 负载均衡
    - Consul + Consul-template 动态配置 Nginx upstream
    - Nginx + lua 动态负载均衡
- 限流，限制总并发数（池化）、排队或等待、降级
    - 接入层限流：
        - ngx_http_limit_conn_mode(连接数限制)
        - ngx_http_limit_req_module(漏桶算法)
        - openResty提供的Lua动态限流模块(lua-resty-limit-traffic)
    - 应用层限流：Redis+Lua 、Nginx+Lua
    - 节流，相同的事件特定窗口内只处理一次
- 降级，主要是当服务出问题或影响到核心流程的性能，需要暂时屏蔽掉一些非核心流程
    - 缓存是离用户越近越高效，而降级是离用户越近对系统的保护越好
    - 超时降级、故障降级
- 隔离
    - 线程隔离，通过不同线程池实现
    - 进程隔离，拆分子系统单独部署
    - 爬虫隔离，区分正常请求与Spider请求
    - 热点隔离，热点活动等
    - 集群隔离、机房隔离、读写隔离、动静隔离、资源隔离（CPU绑定等）
    - Hystrix隔离
    - Servlet3，基于NIO的线程池及异步化
```shell
HystrixComand.Setter.
    .withGroupKey(groupKey) # 全局服务分组
    .andCommandKey(commandKey) # 全局服务
    .andThreadPoolKey(threadPookKey) # 全局线程名称
    .andThreadPoolPropertiesDefaults(threadPoolPropDefaults)
    .andCommandPropertiesDefaults();

```
    
- 超时与重试 
- 回滚
- 压测与预案
    - JMeter/Apache ab/TCPCopy

#### 高并发
- 缓存，缓存主要是提高系统吞吐量
    - 分层缓存
        - 本地缓存(GuavaCache、Ehcache堆内外、MapDB堆内外)、应用将缓存、分布式缓存
        - 客户端缓存、浏览器缓存
        - Nginx代理层缓存
    - 缓存回收策略：基于时间、基于容量、基于Java对象应用
    - Java缓存类型：堆内缓存、堆外缓存、磁盘缓存
    - 缓存使用的模式
        - Cache-Aside：业务直接维护缓存
        - Cache-As-SoR(system of record)：面向缓存，不CareDB  
            - read-through、write-through、write-behind
    - HTTP缓存
        - Age/Vary/Via一般用于代理层CDN，比如代理层是否命中、使用什么协议
        - Etag/Last-Modified，服务器用于判断本次请求与上次请求资源是否修改了
- 池化
    - 数据库连接池
    - HTTPClient连接池
    - 线程池
- 异步并发
    - 微服务情况下，请求合并
- 扩容
    - 系统拆分
    - 数据拆分
        - JIMDB，京东内存KV
    - 任务拆分
        - Quartz
        - 当当开源 Elastic-Job-Lite
    - 数据异构
        - Canal是阿里开源的一款基于MySQL数据库binlog的增量订阅和消费组件
- 队列

#### openresty
https://www.jianshu.com/p/09c17230e1ae
<https://zhuanlan.zhihu.com/p/37102791>