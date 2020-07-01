---
layout: post
title:  " SpringCloud "
date:   2020-04-04 11:25:00
tags:
- 微服务
- 分布式
- Spring
categories:
- 技术
---
#### Spring
- Eureka：服务治理组件，包括服务端的注册中心和客户端的服务发现机制；
- Ribbon：负载均衡的服务调用组件，具有多种负载均衡调用策略；
- Hystrix：服务容错组件，实现了断路器模式，为依赖服务的出错和延迟提供了容错能力；
- Feign：基于Ribbon和Hystrix的声明式服务调用组件；
- Zuul：API网关组件，对请求提供路由及过滤功能。
- Spring Cloud Bus
用于传播集群状态变化的消息总线，使用轻量级消息代理链接分布式系统中的节点，可以用来动态刷新集群中的服务配置。
Spring Cloud Bus 提供了跨多个实例刷新配置的功能。因此，在上面的示例中，如果我们刷新 Employee Producer1，则会自动刷新所有其他必需的模块。如果我们有多个微服务启动并运行，这特别有用。这是通过将所有微服务连接到单个消息代理来实现的。无论何时刷新实例，此事件都会订阅到侦听此代理的所有微服务，并且它们也会刷新。可以通过使用端点/总线/刷新来实现对任何单个实例的刷新。
- Spring Cloud Consul
基于Hashicorp Consul的服务治理组件。
- Spring Cloud Security
安全工具包，对Zuul代理中的负载均衡OAuth2客户端及登录认证进行支持。
- Spring Cloud Sleuth
Spring Cloud应用程序的分布式请求链路跟踪，支持使用Zipkin、HTrace和基于日志（例如ELK）的跟踪。
- Spring Cloud Stream
轻量级事件驱动微服务框架，可以使用简单的声明式模型来发送及接收消息，主要实现为Apache Kafka及RabbitMQ。
- Spring Cloud Task
用于快速构建短暂、有限数据处理任务的微服务框架，用于向应用中添加功能性和非功能性的特性。
- Spring Cloud Zookeeper
基于Apache Zookeeper的服务治理组件。
- Spring Cloud Gateway
API网关组件，对请求提供路由及过滤功能。Spring Cloud Gateway是Spring Cloud官方推出的第二代网关框架，取代Zuul网关。网关作为流量的，在微服务系统中有着非常作用，网关常见的功能有路由转发、权限校验、限流控制等作用。
使用了一个RouteLocatorBuilder的bean去创建路由，除了创建路由RouteLocatorBuilder可以让你添加各种predicates和filters，predicates断言的意思，顾名思义就是根据具体的请求的规则，由具体的route去处理，filters是各种过滤器，用来对请求做各种判断和修改。
- Spring Cloud OpenFeign
基于Ribbon和Hystrix的声明式服务调用组件，可以动态创建基于Spring MVC注解的接口实现用于服务调用，在Spring Cloud 2.0中已经取代Feign成为了一等公民。
- 什么是Spring Cloud Config?
在分布式系统中，由于服务数量巨多，为了方便服务配置文件统一管理，实时更新，所以需要分布式配置中心组件。在Spring Cloud中，有分布式配置中心组件spring cloud config ，它支持配置服务放在配置服务的内存中（即本地），也支持放在远程Git仓库中。在spring cloud config 组件中，分两个角色，一是config server，二是config client。
使用：（1）添加pom依赖（2）配置文件添加相关配置（3）启动类添加注解@EnableConfigServer
- Spring中使用@Autowired注解静态实例对象 <https://blog.csdn.net/RogueFist/article/details/79575665>
- 多个ApplicationRunner，可以用@Order指定优先级串行执行的，如果优先级高的block了，后面的需要等着


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
- hessian / sofa
    
### Just Do SpringCloud
- 首选 <https://windmt.com/tags/Spring-Cloud/>
- [springcloud.cc][springcloud.cc]
- [springcloud.fun][springcloud.fun]
- [大话SpringCloud][763040709]
- <https://www.geekdigging.com>

### 常见组件
- 服务配置中心（注册发现）：Netflix的Eureka、Apache的zookeeper、Spring家族的Spring Cloud Consul、携程apollo
    - [Zookeeper保证的是CP，Eureka保证的是AP][5c5753d2aeb0]  
- 客户端负载均衡：Netflix Ribbon (提供云端负载均衡，有多种负载均衡策略可供选择，可配合服务发现和断路器使用。)
    - 客户端负载均衡(Ribbon)服务实例的清单在客户端，客户端进行负载均衡算法分配。(从上面的知识我们已经知道了：客户端可以从Eureka Server中得到一份服务清单，在发送请求时通过负载均衡算法，在多个服务器之间选择一个进行访问)
      Zuul路由的业务，对业务进行了归类，并交给了对应的微服务。
    - 服务端负载均衡(Nginx)服务实例的清单在服务端，服务器进行负载均衡算法分配,
      Nginx路由请求的压力，对请求进行平均后，交给了服务器处理。
    - [撸一撸Spring Cloud Ribbon的原理-负载均衡策略][8477781]
    - 可以使用Ribbon + resetTemplate 或者直接使用 Feign（已经内置Ribbon）来实现客户端侧的负载均衡
- 熔断器：Netflix Hystrix（Envoy)
- Spring Cloud Feign：它基于 Netflix Feign 实现，整合了 Spring Cloud Ribbon 与 Spring Cloud Hystrix, 除了整合这两者的强大功能之外，它还提 供了声明式的服务调用(不再通过RestTemplate)。
    生产环境一般使用restTemplate + ribbon
- 服务网关: Netflix Zuul  、 Spring Cloud GateWay
    - Zuul相当于一个分布式的大Servlet+Filter入口可进行路由及过滤等
    - Zuul也可以近似的理解为是SOA里的ESB，统一入口调用
    - Zuul也默认集成了Hystrix与Ribbon
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

### 基于SpringCloud的开源项目

[5c5753d2aeb0]: https://www.jianshu.com/p/5c5753d2aeb0
[springcloud.cc]: https://www.springcloud.cc/
[springcloud.fun]: http://springcloud.fun
[763040709]: https://www.zhihu.com/question/283286745/answer/763040709
[dubbo-update-again]: http://www.ityouknow.com/springcloud/2017/11/20/dubbo-update-again.html
[8477781]: https://www.cnblogs.com/kongxianghai/p/8477781.html


