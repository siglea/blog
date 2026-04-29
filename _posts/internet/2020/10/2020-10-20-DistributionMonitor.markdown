---
layout: post
title:  "微服务可观测性三大支柱：Logging、Tracing 与 Metrics 全解析"
date:   2019-11-12 11:25:00 +0900
comments: true
tags:
- 微服务
- 分布式
categories:
- 技术
---

当系统从单体架构演进到微服务架构后，一个请求可能需要经过十几个服务的协作才能完成。一旦出现问题，传统的"看日志、查数据库"的排查方式变得力不从心。这时候，构建完善的可观测性（Observability）体系就成为微服务治理的核心课题。

### 什么是可观测性

可观测性（Observability）源自控制论，指的是通过系统的外部输出来推断其内部状态的能力。在微服务语境下，可观测性意味着我们能够回答以下问题：

- 系统现在的状态是什么？（健康还是异常？）
- 某个请求经历了哪些服务？每一步耗时多少？
- 为什么这个请求失败了？根因在哪个环节？

可观测性由三大支柱构成：**Logging（日志）**、**Tracing（链路追踪）**、**Metrics（指标）**。

### 三大支柱详解

#### 一、Logging（日志）

日志用于记录**离散的事件**，是最传统也最基础的观测手段。

**记录内容**：应用程序运行时的调试信息、错误信息、业务事件等。

**典型方案：ELK Stack**

ELK 是 Elasticsearch + Logstash + Kibana 的组合，是目前最流行的日志收集与分析方案：

```
应用日志 → Filebeat(采集) → Logstash(清洗/转换) → Elasticsearch(存储/索引) → Kibana(可视化)
```

| 组件 | 职责 |
|------|------|
| Filebeat | 轻量级日志采集器，安装在应用服务器上 |
| Logstash | 日志清洗和转换，支持丰富的 filter 插件 |
| Elasticsearch | 分布式搜索引擎，提供全文检索和聚合分析 |
| Kibana | 可视化面板，支持日志查询和仪表盘制作 |

**日志最佳实践**：

1. **结构化日志**：使用 JSON 格式输出日志，便于机器解析

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "ERROR",
  "service": "order-service",
  "traceId": "abc123",
  "message": "Failed to create order",
  "userId": "user_456",
  "errorCode": "INVENTORY_INSUFFICIENT"
}
```

2. **统一 TraceId**：在日志中携带链路追踪 ID，实现日志与 Trace 的关联
3. **合理的日志级别**：避免在循环中打 INFO 日志，ERROR 日志应包含足够的上下文
4. **日志脱敏**：敏感信息（手机号、身份证号等）不应明文出现在日志中

#### 二、Metrics（指标）

Metrics 用于记录**可聚合的数据**，关注的是系统运行的趋势和状态。

**核心特点**：
- 数值型，可以做数学运算（求和、平均、百分位等）
- 时间序列数据，天然适合做趋势分析和告警

**典型方案：Prometheus + Grafana**

Prometheus 是 CNCF 项目，专注于 Metrics 领域，采用 Pull 模型主动拉取指标数据。

```
应用(暴露/metrics端点) ← Prometheus(定期拉取) → Grafana(可视化) 
                                              → AlertManager(告警)
```

**四种指标类型**：

| 类型 | 说明 | 示例 |
|------|------|------|
| Counter | 只增不减的计数器 | HTTP 请求总数、错误总数 |
| Gauge | 可增可减的仪表盘 | 当前连接数、队列深度、CPU 使用率 |
| Histogram | 数据分布统计 | 请求延迟分布（P50/P95/P99） |
| Summary | 类似 Histogram，客户端计算分位数 | 响应时间百分位 |

**监控的黄金指标（Google SRE 四个黄金信号）**：

1. **延迟（Latency）**：请求处理时间
2. **流量（Traffic）**：系统负载量，如 QPS
3. **错误率（Errors）**：失败请求占比
4. **饱和度（Saturation）**：资源使用程度，如 CPU、内存、磁盘

#### 三、Tracing（链路追踪）

Tracing 用于记录**请求范围内的完整调用链路**，是排查分布式系统性能问题的利器。

**核心概念**：
- **Trace**：一次完整的请求链路，由多个 Span 组成
- **Span**：一个工作单元，代表一次 RPC 调用或本地方法调用
- **SpanContext**：在服务间传递的上下文，包含 TraceId 和 SpanId

**典型方案对比**：

| 工具 | 特点 | 侵入性 | 存储 |
|------|------|--------|------|
| SkyWalking | 基于 Java Agent，无侵入 | 低 | ES / H2 / MySQL |
| Zipkin | Twitter 开源，轻量级 | 中（需埋点） | ES / MySQL / Cassandra |
| Pinpoint | 韩国 Naver 开源，UI 美观 | 低（Java Agent） | HBase |
| Jaeger | Uber 开源，CNCF 项目 | 中 | ES / Cassandra |

**SkyWalking 架构**：

```
应用(Java Agent自动埋点)
        ↓ gRPC
SkyWalking OAP Server(分析和聚合)
        ↓
Storage(Elasticsearch)
        ↓
SkyWalking UI(拓扑图/调用链/指标)
```

SkyWalking 的最大优势在于基于 Java Agent 的**字节码增强技术**，无需修改业务代码即可实现自动埋点，支持 HTTP、RPC、数据库、MQ 等多种调用的追踪。

### 三大支柱的协作

三大支柱不是孤立存在的，而是通过 **TraceId** 实现串联：

1. 用户报告请求失败 → 从 **Metrics** 大盘发现错误率上升
2. 通过 **Tracing** 找到失败请求的完整调用链，定位到某个下游服务超时
3. 通过 TraceId 在 **Logging** 中检索具体的错误日志，查看详细的异常堆栈

这种从宏观到微观的排查路径：**Metrics → Tracing → Logging**，是微服务故障排查的标准范式。

### 实际落地建议

1. **从 Metrics 开始**：如果团队刚开始建设可观测性，优先接入 Prometheus + Grafana，成本低、见效快
2. **按需引入 Tracing**：当服务调用链超过 3 层时，就应该考虑引入链路追踪
3. **统一日志规范**：在团队层面制定日志格式标准和级别规范，避免日志混乱
4. **合理采样**：Tracing 全量采集对存储和性能有较大影响，建议使用采样策略（如 1% 采样 + 错误请求全采）
5. **告警收敛**：避免告警风暴，设置合理的告警阈值和收敛规则

### 开源监控工具全景

| 领域 | 工具 |
|------|------|
| Metrics | Prometheus、InfluxDB、OpenTSDB |
| Logging | ELK、Loki（Grafana）、Fluentd |
| Tracing | SkyWalking、Jaeger、Zipkin |
| 综合平台 | Datadog、New Relic、阿里云 ARMS |
| 基础监控 | Zabbix、Nagios、Open-Falcon |

### 总结

可观测性不是锦上添花，而是微服务架构下的必需品。Logging 提供事件级的详细信息，Metrics 提供系统级的趋势数据，Tracing 提供请求级的链路视图——三者相辅相成，缺一不可。在技术选型时，根据团队规模和业务复杂度选择合适的工具组合，从简单开始逐步完善，远比追求一步到位更加务实。
