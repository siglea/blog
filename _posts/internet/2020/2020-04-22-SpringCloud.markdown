---
layout: post
title:  " SpringCloud "
date:   2020-04-04 11:25:00
tags:
- SpringCloud
categories:
- 技术
---
### 关于微服务
- SOA(ESB)与微服务
    - <https://zhuanlan.zhihu.com/p/30477325>
    - <https://www.cnblogs.com/guanghe/p/10978349.html>
    - <https://mp.weixin.qq.com/s/9YxdCkl98kZq_Bh_DqwCmA>
- 微服务哪些事
    - <https://windmt.com/2018/04/14/spring-cloud-0-microservices/>
    - <https://windmt.com/2018/04/14/spring-cloud-1-services-governance/>
- SpringCloud & Dubbo
    - <https://mp.weixin.qq.com/s/qDiSn29uqSpA0yaM07nmbQ>
    - <https://mp.weixin.qq.com/s/GSLXRnl0pg5ynVwbQcon7A>
    - [阿里Dubbo与Spring Cloud][dubbo-update-again]
- RPC之thrift/gRPC
    - <https://blog.csdn.net/kesonyk/article/details/50924489>
    - <https://developer.51cto.com/art/201908/601617.htm>
    - <https://segmentfault.com/a/1190000011478469>
    - <https://zhuanlan.zhihu.com/p/136112210>
    - RPC与HTTP的关系 <https://mp.weixin.qq.com/s/0RXTUWHXDmMddsPVWej2Qg>
    - 快速理解RPC技术——基本概念、原理和用途 <http://www.52im.net/forum.php?mod=viewthread&tid=2620>
- WebService某种程度上也是一种RPC
    - WebService的历史 <https://www.iteye.com/blog/andot-662787>
    - WebService的demo<https://blog.csdn.net/weixin_42672054/article/details/81708464>
    - 2000年左右出现xml，借此微软等联盟推出了基于XML的SOAP协议，实现各系统之间的通信
    - thrift/webservice等可以生成客户端代码，隐藏了底层通信细节，对象化了数据（否则需要自行解析）
    - thrift、dobbo等方式基于TCP实现，主要是性能方面的考虑吧
    
### Just Do SpringCloud
- 首选 <https://windmt.com/tags/Spring-Cloud/>
- [springcloud.cc][springcloud.cc]
- [springcloud.fun][springcloud.fun]
- [大话SpringCloud][763040709]
- <https://www.geekdigging.com>

### 常见组件
- 服务配置中心（注册发现）：Netflix的Eureka、Apache的zookeeper、Spring家族的Spring Cloud Consul
    - [Zookeeper保证的是CP，Eureka保证的是AP][5c5753d2aeb0]  
- 客户端负载均衡：Netflix Ribbon (提供云端负载均衡，有多种负载均衡策略可供选择，可配合服务发现和断路器使用。)
    - 客户端负载均衡(Ribbon)服务实例的清单在客户端，客户端进行负载均衡算法分配。(从上面的知识我们已经知道了：客户端可以从Eureka Server中得到一份服务清单，在发送请求时通过负载均衡算法，在多个服务器之间选择一个进行访问)
      Zuul路由的业务，对业务进行了归类，并交给了对应的微服务。
    - 服务端负载均衡(Nginx)服务实例的清单在服务端，服务器进行负载均衡算法分配,
      Nginx路由请求的压力，对请求进行平均后，交给了服务器处理。
    - [撸一撸Spring Cloud Ribbon的原理-负载均衡策略][8477781]
- 熔断器：Netflix Hystrix（Envoy)
- Spring Cloud Feign：它基于 Netflix Feign 实现，整合了 Spring Cloud Ribbon 与 Spring Cloud Hystrix, 除了整合这两者的强大功能之外，它还提 供了声明式的服务调用(不再通过RestTemplate)。
- 服务网关: Netflix Zuul  、 Spring Cloud GateWay
- 分布式配置：Spring Cloud Config (Chef)
- 时间消息总线：Spring Cloud Bus
- 链路追踪：Spring Cloud Sleuth 与 Twitter Zipkin
- 数据流：Spring Cloud Stream (数据流操作开发包，封装了与Redis,Rabbit、Kafka等发送接收消息。)
- 服务监控：Zabbix、Nagios、Metrics、Spectator

### 相关组件
#### zookeeper
- 简单理解，zk就是一套简单的文件系统结构，本目录(节点)可以设置value及subNode,
  并且该节点可以设置不同的权限（默认/用户名+密码/ip/秘钥，这4种)
- zk集群简单理解就是，基于ZAB一致性算法的变种keep alived集群
- zk集群是CP模型，强一致性的，也就是说数据出现了不一致性（通常是节点挂了），整个服务集群就会Hold住等待数据一致，
  所以，这个缺点导致zk并不是最佳的注册中心，因为服务注册中心AP模型最好，部分服务有问题并不表示所有服务不可用。
- zookeeper 命令 <https://blog.csdn.net/feixiang2039/article/details/79810102>
- Curator实现的zk分布式锁 <https://www.sohu.com/a/341386202_315839>


[5c5753d2aeb0]: https://www.jianshu.com/p/5c5753d2aeb0
[springcloud.cc]: https://www.springcloud.cc/
[springcloud.fun]: http://springcloud.fun
[763040709]: https://www.zhihu.com/question/283286745/answer/763040709
[dubbo-update-again]: http://www.ityouknow.com/springcloud/2017/11/20/dubbo-update-again.html
[8477781]: https://www.cnblogs.com/kongxianghai/p/8477781.html


