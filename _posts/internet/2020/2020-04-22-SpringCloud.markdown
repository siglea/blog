---
layout: post
title:  "Spring Cloud 微服务生态全景：核心组件与架构实践"
date:   2020-04-04 11:25:00
tags:
- 微服务
- 分布式
- Spring
categories:
- 技术
---
<img src="{{ site.baseurl }}/img/springcloud.jpg" width="600px" />

在微服务架构逐渐成为后端系统主流选择的今天，Spring Cloud 凭借其与 Spring Boot 的深度整合、丰富的组件生态以及活跃的社区支持，成为了 Java 领域构建微服务系统的事实标准。本文将对 Spring Cloud 的核心组件进行系统性梳理，并结合微服务架构的演进背景，帮助读者建立一个完整的技术全景视图。

---

### 一、Spring Cloud 核心组件概览

Spring Cloud 并不是一个单一的框架，而是一系列子项目的集合，每个子项目解决微服务架构中的某一类问题。以下是最常用的核心组件及其职责。

#### 1.1 Eureka：服务注册与发现

Eureka 是 Netflix 开源的服务治理组件，包括服务端的注册中心（Eureka Server）和客户端的服务发现机制（Eureka Client）。

**高可用部署**：Eureka Server 的高可用实际上就是将自己作为服务向其他注册中心注册自己，这样就可以形成一组互相注册的服务注册中心，以实现服务清单的互相同步，达到高可用效果。

在实际配置中，可以调整服务续约和失效的时间参数：

```shell
# 定义服务续约任务的调用间隔时间，默认30秒
eureka.instance.lease-renewal-interval-in-seconds=30
# 定义服务失效的时间，默认90秒 eureka.instance.lease-expiration-duration-in-seconds=90
```

**自我保护机制**：Eureka Server 在运行期间，会统计心跳失败的比例在15分钟之内是否低于85%，如果出现低于的情况，Eureka Server 会将当前的实例注册信息保护起来，让这些实例不会过期，尽可能保护这些注册信息。但是，在这段保护期间内实例若出现问题，那么客户端很容易拿到实际已经不存在的服务实例，会出现调用失败的情况，所以客户端必须要有容错机制，比如可以使用请求重试、断路器等机制。

```shell
# 关闭保护机制，以确保注册中心可以将不用的实例正确剔除(本地调试可以使用，线上不推荐)
eureka.server.enable-self-preservation=false
```

#### 1.2 Ribbon：客户端负载均衡

Ribbon 是负载均衡的服务调用组件，具有多种负载均衡调用策略。与服务端负载均衡（如 Nginx）不同，Ribbon 将服务实例清单维护在客户端，由客户端根据负载均衡算法选择目标实例发起调用。

#### 1.3 Hystrix：服务容错与熔断

Hystrix 是服务容错组件，实现了断路器模式，为依赖服务的出错和延迟提供了容错能力。当某个服务出现故障或响应超时，Hystrix 能够快速失败并提供降级方案，防止故障在系统中蔓延。

#### 1.4 Feign：声明式服务调用

Feign 是基于 Ribbon 和 Hystrix 的声明式服务调用组件。开发者只需定义接口并添加注解，即可完成服务间的 HTTP 调用，极大地简化了开发工作。

#### 1.5 Zuul / Spring Cloud Gateway：API 网关

Zuul 是 Netflix 开源的 API 网关组件，对请求提供路由及过滤功能。

Spring Cloud Gateway 是 Spring Cloud 官方推出的第二代网关框架，取代 Zuul 网关。网关作为流量的入口，在微服务系统中承担路由转发、权限校验、限流控制等关键职责。Gateway 使用 `RouteLocatorBuilder` 来创建路由，支持添加各种 predicates（断言，根据具体的请求规则匹配对应的 route）和 filters（过滤器，用来对请求做各种判断和修改）。

---

### 二、Spring Cloud 扩展组件

除了上述核心组件，Spring Cloud 还提供了一系列扩展组件，覆盖配置管理、消息总线、链路追踪等场景。

| 组件 | 功能 |
|------|------|
| **Spring Cloud Bus** | 用于传播集群状态变化的消息总线，使用轻量级消息代理链接分布式系统中的节点，可以用来动态刷新集群中的服务配置。通过将所有微服务连接到单个消息代理，任何单个实例的刷新事件都会订阅到所有监听此代理的微服务，实现配置的自动同步。 |
| **Spring Cloud Consul** | 基于 Hashicorp Consul 的服务治理组件。 |
| **Spring Cloud Security** | 安全工具包，对 Zuul 代理中的负载均衡 OAuth2 客户端及登录认证进行支持。 |
| **Spring Cloud Sleuth** | 分布式请求链路跟踪，支持使用 Zipkin、HTrace 和基于日志（例如 ELK）的跟踪。 |
| **Spring Cloud Stream** | 轻量级事件驱动微服务框架，可以使用简单的声明式模型来发送及接收消息，主要实现为 Apache Kafka 及 RabbitMQ。 |
| **Spring Cloud Task** | 用于快速构建短暂、有限数据处理任务的微服务框架，用于向应用中添加功能性和非功能性的特性。 |
| **Spring Cloud Zookeeper** | 基于 Apache Zookeeper 的服务治理组件。 |
| **Spring Cloud OpenFeign** | 基于 Ribbon 和 Hystrix 的声明式服务调用组件，可以动态创建基于 Spring MVC 注解的接口实现用于服务调用，在 Spring Cloud 2.0 中已经取代 Feign 成为了一等公民。 |

#### Spring Cloud Config：分布式配置中心

在分布式系统中，由于服务数量巨多，为了方便服务配置文件统一管理、实时更新，需要分布式配置中心组件。Spring Cloud Config 支持将配置放在配置服务的内存中（即本地），也支持放在远程 Git 仓库中。其中分两个角色：Config Server 和 Config Client。

使用步骤：（1）添加 pom 依赖（2）配置文件添加相关配置（3）启动类添加注解 `@EnableConfigServer`。

<img src="{{ site.baseurl }}/img/springconfig.jpg" width="600px" />

#### 其他实用技巧

- Spring 中使用 `@Autowired` 注解静态实例对象：<https://blog.csdn.net/RogueFist/article/details/79575665>
- 多个 `ApplicationRunner` 可以用 `@Order` 指定优先级串行执行的，如果优先级高的 block 了，后面的需要等着

---

### 三、常见组件选型对比

在实际项目中，各组件往往有多种可选方案。以下是按功能分类的常见选型：

**服务配置中心（注册发现）**：Netflix Eureka、Apache Zookeeper、Spring Cloud Consul、携程 Apollo
- [Zookeeper 保证的是 CP，Eureka 保证的是 AP][5c5753d2aeb0]

**客户端负载均衡**：Netflix Ribbon，提供云端负载均衡，有多种负载均衡策略可供选择，可配合服务发现和断路器使用。
- 客户端负载均衡（Ribbon）：服务实例的清单在客户端，客户端进行负载均衡算法分配。从 Eureka Server 获取一份服务清单，在发送请求时通过负载均衡算法在多个服务器之间选择一个进行访问。Zuul 路由的是业务，对业务进行归类后交给对应的微服务。
- 服务端负载均衡（Nginx）：服务实例的清单在服务端，服务器进行负载均衡算法分配。Nginx 路由的是请求的压力，对请求进行平均后交给服务器处理。
- [撸一撸 Spring Cloud Ribbon 的原理 - 负载均衡策略][8477781]
- 可以使用 Ribbon + RestTemplate 或者直接使用 Feign（已经内置 Ribbon）来实现客户端侧的负载均衡

**熔断器**：Netflix Hystrix（Envoy）

**Spring Cloud Feign**：基于 Netflix Feign 实现，整合了 Spring Cloud Ribbon 与 Spring Cloud Hystrix，除了整合这两者的强大功能之外，它还提供了声明式的服务调用（不再通过 RestTemplate）。生产环境一般使用 RestTemplate + Ribbon。

**服务网关**：Netflix Zuul、Spring Cloud Gateway
- Zuul 相当于一个分布式的大 Servlet + Filter 入口，可进行路由及过滤等
- Zuul 也可以近似理解为 SOA 里的 ESB，统一入口调用
- Zuul 也默认集成了 Hystrix 与 Ribbon

**分布式配置**：Spring Cloud Config（Chef）

**事件消息总线**：Spring Cloud Bus

**链路追踪**：Spring Cloud Sleuth 与 Twitter Zipkin

**数据流**：Spring Cloud Stream（数据流操作开发包，封装了与 Redis、Rabbit、Kafka 等发送接收消息）

**服务监控**：Zabbix、Nagios、Metrics、Spectator

---

### 四、Zookeeper 补充说明

由于 Zookeeper 在微服务架构中扮演着重要角色（尤其在 Dubbo 体系中），这里做简要补充：

- 简单理解，ZK 就是一套简单的文件系统结构，目录（节点）可以设置 value 及 subNode，并且该节点可以设置不同的权限（默认/用户名+密码/IP/秘钥，共4种）
- ZK 集群简单理解就是，基于 ZAB 一致性算法的变种 keep alived 集群
- ZK 集群是 CP 模型，强一致性的，也就是说数据出现了不一致性（通常是节点挂了），整个服务集群就会 Hold 住等待数据一致。这个缺点导致 ZK 并不是最佳的注册中心，因为服务注册中心 AP 模型最好，部分服务有问题并不表示所有服务不可用。
- Zookeeper 命令参考：<https://blog.csdn.net/feixiang2039/article/details/79810102>
- Curator 实现的 ZK 分布式锁：<https://www.sohu.com/a/341386202_315839>

---

### 五、关于微服务架构的思考

#### SOA（ESB）与微服务

微服务并不是凭空产生的新概念，它是从 SOA（面向服务的架构）演进而来。SOA 通常依赖 ESB（企业服务总线）来实现服务间的通信和编排，而微服务则更强调去中心化、独立部署和轻量级通信。

- <https://zhuanlan.zhihu.com/p/30477325>
- <https://www.cnblogs.com/guanghe/p/10978349.html>
- <https://mp.weixin.qq.com/s/9YxdCkl98kZq_Bh_DqwCmA>

#### 微服务实践系列

- <https://windmt.com/2018/04/14/spring-cloud-0-microservices/>
- <https://windmt.com/2018/04/14/spring-cloud-1-services-governance/>

#### Spring Cloud vs Dubbo

Spring Cloud 和 Dubbo 是 Java 微服务领域的两大主流框架。Spring Cloud 提供了更完整的微服务解决方案（配置、网关、链路追踪等），而 Dubbo 在 RPC 调用性能上有显著优势。

- <https://mp.weixin.qq.com/s/qDiSn29uqSpA0yaM07nmbQ>
- <https://mp.weixin.qq.com/s/GSLXRnl0pg5ynVwbQcon7A>
- [阿里 Dubbo 与 Spring Cloud][dubbo-update-again]

#### RPC 技术：Thrift / gRPC

RPC（远程过程调用）是微服务间通信的另一种重要方式。相比 HTTP RESTful，RPC 通常具有更高的通信效率和更强的类型约束。

- <https://blog.csdn.net/kesonyk/article/details/50924489>
- <https://developer.51cto.com/art/201908/601617.htm>
- <https://segmentfault.com/a/1190000011478469>
- <https://zhuanlan.zhihu.com/p/136112210>
- RPC 与 HTTP 的关系：<https://mp.weixin.qq.com/s/0RXTUWHXDmMddsPVWej2Qg>
- 快速理解 RPC 技术——基本概念、原理和用途：<http://www.52im.net/forum.php?mod=viewthread&tid=2620>

#### WebService 与 RPC

WebService 某种程度上也是一种 RPC。2000年左右出现 XML，借此微软等联盟推出了基于 XML 的 SOAP 协议，实现各系统之间的通信。

- WebService 的历史：<https://www.iteye.com/blog/andot-662787>
- WebService 的 Demo：<https://blog.csdn.net/weixin_42672054/article/details/81708464>
- Thrift/WebService 等可以生成客户端代码，隐藏了底层通信细节，对象化了数据（否则需要自行解析）
- Thrift、Dubbo 等方式基于 TCP 实现，主要是性能方面的考虑

#### 其他 RPC 框架

Hessian / SOFA

---

### 六、学习资源

- 首选：<https://windmt.com/tags/Spring-Cloud/>
- [springcloud.cc][springcloud.cc]
- [springcloud.fun][springcloud.fun]
- [大话 SpringCloud][763040709]
- <https://www.geekdigging.com>

---

### 七、总结

Spring Cloud 为微服务架构提供了一站式的解决方案，从服务注册发现、负载均衡、熔断降级，到配置中心、消息总线、链路追踪，几乎覆盖了微服务治理的所有关键环节。在实际项目中，建议根据团队技术栈和业务场景灵活选型——如果追求开箱即用和生态完整性，Spring Cloud 是很好的选择；如果对 RPC 性能有更高要求，可以考虑 Dubbo 或 gRPC 体系，甚至将两者结合使用。

[5c5753d2aeb0]: https://www.jianshu.com/p/5c5753d2aeb0
[springcloud.cc]: https://www.springcloud.cc/
[springcloud.fun]: http://springcloud.fun
[763040709]: https://www.zhihu.com/question/283286745/answer/763040709
[dubbo-update-again]: http://www.ityouknow.com/springcloud/2017/11/20/dubbo-update-again.html
[8477781]: https://www.cnblogs.com/kongxianghai/p/8477781.html
