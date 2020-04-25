---
layout: post
title:  " SpringCloud "
date:   2020-04-04 11:25:00
tags:
- SpringCloud
categories:
- 技术
---
#### Just Do SpringCloud
- [springcloud.cc][springcloud.cc]
- [springcloud.fun][springcloud.fun]
- [大话SpringCloud][763040709]
- [阿里Dubbo与Spring Cloud][dubbo-update-again]

#### 常见组件
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



[5c5753d2aeb0]: https://www.jianshu.com/p/5c5753d2aeb0
[springcloud.cc]: https://www.springcloud.cc/
[springcloud.fun]: http://springcloud.fun
[763040709]: https://www.zhihu.com/question/283286745/answer/763040709
[dubbo-update-again]: http://www.ityouknow.com/springcloud/2017/11/20/dubbo-update-again.html
[8477781]: https://www.cnblogs.com/kongxianghai/p/8477781.html