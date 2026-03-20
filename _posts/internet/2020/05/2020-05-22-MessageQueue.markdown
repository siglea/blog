---
layout: post
title:  "消息队列全面解析：Kafka、RabbitMQ、RocketMQ与ActiveMQ对比实战"
date:   2020-05-22 11:25:00
tags:
- MQ
- 分布式
categories:
- 技术
---

在分布式系统架构中，消息队列（Message Queue）扮演着至关重要的角色。它不仅实现了系统间的解耦，还提供了异步通信、流量削峰、最终一致性等核心能力。当前主流的消息中间件包括 ActiveMQ、RabbitMQ、RocketMQ 和 Kafka，它们各有所长，适用于不同的业务场景。本文将从协议模型、可靠性、高可用架构、数据存储等维度，对这四款消息中间件进行全面解析。

## MOM（Message Oriented Middleware）概览

<img src="{{ site.baseurl }}/img/mq.jpg" width="600px"> 

消息中间件（MOM，Message Oriented Middleware）是一类以消息传递为核心机制的基础设施软件。它的核心价值在于将消息的发送者与接收者解耦——生产者无需知道消费者的存在，反之亦然。这种松耦合的设计使得系统具备更好的可扩展性和容错能力。

关于四大消息中间件的综合对比，可参考：
- 17 个方面，综合对比 Kafka、RabbitMQ、RocketMQ、ActiveMQ 
<https://mp.weixin.qq.com/s/u7pyzEQgqmux9qUI_SPaNw>

## AMQP 协议：高级消息队列协议

AMQP（Advanced Message Queuing Protocol）是应用层协议的一个开放标准，为面向消息的中间件设计，ActiveMQ 和 RabbitMQ 都支持该协议。AMQP 的主要特征是面向消息、队列、路由（包括点对点和发布/订阅）、可靠性和安全。

RabbitMQ 是 AMQP 的一个经典开源实现，服务器端用 Erlang 语言编写，支持多种客户端，如 Python、Ruby、.NET、Java、JMS、C、PHP、ActionScript、XMPP、STOMP 等，也支持 AJAX。它在分布式系统中用于存储和转发消息，在易用性、扩展性、高可用性等方面表现不俗。

### 两种消息模型

消息队列通常支持两种核心模型，几乎所有的 MQ 产品都围绕这两种模型构建：

- **点对点（Point-to-Point，单播）**：消息发送到一个队列，该队列的消息只能被一个消费者消费。这种模型适合任务分发场景，确保每条消息只被处理一次。
- **发布订阅（Publish-Subscribe，广播）**：消息可以被多个消费者消费。生产者和消费者完全独立，不需要感知对方的存在。典型场景如用户登录后，各个业务模块根据登录事件进行不同的处理（发送欢迎邮件、更新用户画像、记录登录日志等）。

### 如何保证高可用

不同消息中间件在高可用方面采取了不同的架构策略：

- **主从架构**：ActiveMQ、RabbitMQ 采用这种方式。通过主节点负责读写、从节点负责数据备份来实现高可用，当主节点故障时从节点可以接管服务。
- **分布式架构**：Kafka、RocketMQ 采用原生分布式设计。数据天然分布在多个节点上，每个分区都有多个副本，具备更强的水平扩展能力。

### 推拉模式

消息的消费模式分为推（Push）模式和拉（Pull）模式，二者各有优劣：

- **推模式**：由 Broker 主动推送消息至消费端，实时性较好。但需要流控机制来确保服务端推送的消息不会压垮消费端。
- **拉模式**：消费端主动向 Broker 请求拉取消息（一般是定时或定量），实时性较差，但消费者可以根据自身处理能力控制拉取的消息量，更加灵活可控。

---

## ActiveMQ

ActiveMQ 是 Apache 旗下的老牌消息中间件，基于 JMS 规范实现，功能完善、文档丰富，适合中小规模的消息处理场景。

### ActiveMQ 服务器宕机怎么办？

这个问题需要从 ActiveMQ 的存储机制说起。在通常情况下，非持久化消息存储在内存中，持久化消息存储在文件中，它们的最大限制在配置文件中配置。当非持久化消息堆积到一定程度、内存告急时，ActiveMQ 会将内存中的非持久化消息写入临时文件以腾出内存。虽然都保存到了文件里，但与持久化消息的区别是：重启后持久化消息会从文件中恢复，而非持久化的临时文件会直接删除。

当文件增大到达配置的最大限制时会发生什么？以下是两组实验结果：

- **持久化消息实验**：设置约 2G 的持久化文件限制，大量生产持久化消息直到达到上限。此时生产者阻塞，但消费者可正常连接并消费消息。等消息消费掉一部分、文件删除腾出空间后，生产者可继续发送消息，服务自动恢复正常。
- **非持久化消息实验**：设置约 2G 的临时文件限制，大量生产非持久化消息写入临时文件。达到上限时，生产者阻塞，消费者可正常连接但不能消费消息，或者原本慢速消费的消费者突然停止消费。整个系统可连接但无法提供服务。

### ActiveMQ 消息的不均匀消费

有时发送一些消息后，开启 2 个消费者处理消息，会发现一个消费者处理了所有消息，另一个根本没收到。原因在于 ActiveMQ 的 **prefetch 机制**：消费者获取消息时不是逐条获取，而是一次性预获取一批，默认是 1000 条。这些预获取的消息在未确认消费前不会再分配给其他消费者，状态为"已分配未消费"。

如果消费者既不消费确认又不崩溃，这些消息就永远滞留在消费者缓存区里。更常见的是处理这些消息非常耗时，开了 10 个消费者，结果只有一台在工作，其余 9 台空闲。

**解决方案**：将 prefetch 设为 1，每次处理 1 条消息、处理完再取，这样也慢不了多少。

### ActiveMQ 死信队列

如果希望消息处理失败后不被服务器删除、还能被其他消费者处理或重试，可以关闭 AUTO_ACKNOWLEDGE，将 ACK 交由程序自己处理。

消费消息有两种方法：

- **调用 consumer.receive()**：该方法将阻塞直到获得并返回一条消息。消息返回给方法调用者后就自动被确认了。
- **采用 listener 回调函数**：当有消息到达时，会调用 listener 接口的 onMessage 方法。在 onMessage 方法执行完毕后消息才会被确认，只要在方法中抛出异常，该消息就不会被确认。

如果一条消息不能被处理，会被退回服务器重新分配。如果只有一个消费者，该消息又会被重新获取再次抛异常，进入"退回-获取-报错"的死循环。ActiveMQ 的处理策略是：**在重试 6 次后，认为这条消息是"有毒"的，将其丢到死信队列（ActiveMQ.DLQ）里**。

---

## RabbitMQ

RabbitMQ 是基于 AMQP 协议实现的消息中间件，以其灵活的路由机制和成熟的管理界面著称。

### 核心概念

理解 RabbitMQ 的架构需要掌握以下核心概念：

- **Exchange（交换机）**：生产者并非直接将消息投递到 Queue 中，而是发送到 Exchange，由 Exchange 将消息路由到一个或多个 Queue（或丢弃）。
- **Exchange Types**：常用的有 fanout（广播）、direct（直连）、topic（主题匹配）、headers 四种类型。
- **Queue（队列）**：消息队列载体，每个消息都会被投入到一个或多个队列。
- **Binding（绑定）**：将 Exchange 和 Queue 按照路由规则绑定起来，让 RabbitMQ 知道如何正确路由消息到指定 Queue。
- **Routing Key（路由键）**：生产者发送消息给 Exchange 时指定的路由关键字，需与 Exchange Type 及 Binding Key 联合使用才能生效。

### 常用管理命令

```shell 
rabbitmq-server start
service rabbitmq-server restart
rabbitmqctl status
rabbitmq-plugins enable rabbitmq_management
rabbitmqctl add_user rabbitmq 123456
rabbitmqctl set_user_tags rabbitmq administrator
rabbitmqctl set_permissions -p / rabbitmq ".*" ".*" ".*"
```

### 分布式集群部署

RabbitMQ 支持三种分布式集群部署方式：

- **Cluster 模式**：不支持跨网段，用于同一网段内的局域网，可动态增减节点。节点间需要运行相同版本的 RabbitMQ 和 Erlang。
    - **普通模式**：默认集群模式，Slave 只保存 Queue 相关的元数据。
    - **镜像模式**：将需要的队列做成镜像队列，存在于多个节点（至少 1 个镜像节点、多个 Slave 节点），属于 RabbitMQ 的 HA 方案。
- **Federation 模式**：应用于广域网，允许单台服务器上的交换机或队列接收发布到另一台服务器上的消息。消息会在联盟队列之间转发任意次直到被消费者接受，通常用于连接 Internet 上的中间服务器做订阅分发或工作队列。
- **Shovel 模式**：连接方式与 Federation 类似，但工作在更低层次，同样可应用于广域网。

### 节点类型

- **RAM Node（内存节点）**：将所有队列、交换机、绑定、用户、权限和 vhost 的元数据定义存储在内存中，操作更快速。集群中至少需要一个磁盘节点，建议设置两个磁盘节点以保证高可用。
- **Disk Node（磁盘节点）**：将元数据存储在磁盘中，防止重启时丢失系统配置信息。

### Consumer Cancellation Notification 机制

该机制用于保证当镜像 Queue 中 Master 挂掉时，连接到 Slave 上的 Consumer 可以收到自身 consume 被取消的通知，进而重新执行 consume 动作从新选出的 Master 获取消息。若不采用该机制，连接到 Slave 上的 Consumer 将无法感知 Master 挂掉，导致后续无法再收到新 Master 广播的消息。在镜像 Queue 模式下存在消息 requeue 的可能，所以 Consumer 的逻辑需要能正确处理重复消息。

### Dead Letter Queue 的用途

当消息被 RabbitMQ 投递到 Consumer 后，Consumer 通过 Basic.Reject 拒绝（同时设置 requeue=false），该消息会被放入 Dead Letter Queue。该队列可用于排查消息被 reject 或 undeliver 的原因。

### Blackholed 问题

Blackholed 是指向 Exchange 投递了消息，但由于各种原因消息丢失而发送者不知道。常见原因包括：向未绑定 Queue 的 Exchange 发送消息；Exchange 以 binding_key A 绑定了 Queue，但发送消息使用的 routing_key 却是 B。

**防止措施**：在执行 Basic.Publish 时设置 mandatory=true，遇到可能出现 Blackholed 的情况时，服务器会通过 Basic.Return 告知当前消息无法被正确投递（内含原因 312 NO_ROUTE）。

### Qos prefetchCount 流量控制

如果完全不配置 QoS，RabbitMQ 会尽可能快速地发送队列中的所有消息到客户端。因为 Consumer 在本地缓存所有消息，极有可能导致 OOM 或影响其他进程的正常运行。通过设置 Qos 的 prefetch count 来控制 Consumer 的流量，设置得当也会提高 Consumer 的吞吐量。

### Master 与 Slave 的读写关系

除发送消息（Basic.Publish）外的所有动作都只会向 Master 发送，然后再由 Master 将命令执行结果广播给各个 Slave。即使消费者与 Slave 建立连接并进行订阅消费，其实质都是从 Master 上获取消息——Slave 将请求发往 Master，Master 准备好数据返回给 Slave，最后由 Slave 投递给消费者。

### 参考资料
- RabbitMQ <https://www.jianshu.com/p/78847c203b76>
- RabbitMQ镜像队列 <https://www.jianshu.com/p/fcc35573567c>
- RabbitMQ原理、集群、基本操作及常见故障处理 <https://mp.weixin.qq.com/s/J-4INNmU_vM_Xs__KFEqIQ>

---

## 消息队列通用问题

### 如何保证消息不被重复消费？

这个问题本质上是如何保证消息队列的幂等性。无论是哪种消息队列，造成重复消费的原因都是类似的：消费者消费完消息后，确认信息（ACK/offset 提交等）因网络故障没有传送到消息队列，导致消息队列不知道该消息已被消费，再次分发给其他消费者。

解决方案需根据业务场景选择：

- **数据库 Insert 场景**：给消息设置一个唯一主键，重复消费时会产生主键冲突，避免脏数据。
- **Redis Set 场景**：Set 操作本身是幂等的，无论执行几次结果都一样，无需特殊处理。
- **通用方案**：使用第三方介质做消费记录。以 Redis 为例，给消息分配全局 ID，消费过的消息以 `<id, message>` 的 KV 形式写入 Redis。消费前先查询 Redis 中是否存在消费记录。

### 消费者消费失败如何处理？

- 消费成功时手动 ACK，失败时队列会再次推送或等待再次 Pull
- 避免使用 Redis 做"伪消费队列"，最大问题是消费后没有 ACK，发生意外会产生脏数据
- 可以用幂等方式让消费者保存业务进展，用单独程序做补偿消费
- 消费者处理消息失败时，消息系统一般会把消息放回队列，让其他消费者继续处理

### 如何保证消息的可靠性传输？

**RabbitMQ 的三个环节**：
- **生产者丢数据**：使用事务方式保证发送成功或回滚，也可以让队列接收后异步返回 ACK/NACK
- **消息队列丢数据**：持久化队列并配置自动重复参数
- **消费者丢数据**：手动 ACK

**Kafka 的三个环节**：
- **生产者丢数据**：在 Producer 端设置 `acks=all`（Follower 同步完成后才认为消息发送成功），设置 `retries=MAX`（写入失败无限重试）
- **消息队列丢数据**：设置 `replication.factor > 1`（每个 Partition 至少 2 个副本），设置 `min.insync.replicas > 1`（至少一个 Follower 保持联系）。配合生产者配置可基本确保 Kafka 不丢数据。
- **消费者丢数据**：避免自动提交 offset，改为手动提交。自动提交可能在处理过程中崩溃，Kafka 误以为已处理完成。offset 是 Kafka Topic 中每个消费组消费的下标，每次消费数据时提交 offset，下次就从 offset+1 开始消费。

---

## Kafka

Kafka 严格来说不是传统意义上的消息中间件，而是一种分布式流式平台。不同于基于队列和交换器的 RabbitMQ，Kafka 的存储层使用分区事务日志来实现，过期日志会根据时间或大小进行清除。

### 写操作与 Leader 路由

Producer 直接将数据发送到 Broker 的 Leader（主节点），不需要在多个节点间分发。所有 Kafka 节点都可以及时告知哪些节点是活动的、目标 Topic 目标分区的 Leader 在哪，这样 Producer 就可以直接将消息发送到目的地。

### 数据传输的事务级别

Kafka 支持三种数据传输的事务语义：

1. **最多一次（At Most Once）**：消息不会被重复发送，最多被传输一次，但也有可能不传输
2. **最少一次（At Least Once）**：消息不会被漏发送，最少被传输一次，但也有可能被重复传输
3. **精确一次（Exactly Once）**：不会漏传输也不会重复传输，每个消息传输且仅传输一次

### ACK 机制

`request.required.acks` 有三个值：

- **0**：生产者不等待 Broker 的 ACK，延迟最低但保证最弱，Server 挂掉会丢数据
- **1**：服务端等待 Leader 副本确认接收到消息后发送 ACK，但 Leader 挂掉后不确保复制是否完成，可能导致数据丢失
- **-1**：在 1 的基础上，服务端等所有 Follower 副本都收到数据后才发送 ACK，数据不会丢失

### 消费者与数据组织

- 消费者负载均衡策略：一个消费者组中的一个分片对应一个消费者成员，确保每个消费者都能访问。如果组中成员太多，会有空闲成员。
- 数据有序性：一个消费者组内部是有序的，消费者组之间是无序的。
- 数据分组策略：生产者决定数据产生到集群的哪个 Partition 中，每条消息以 (key, value) 格式传输，Key 由生产者发送数据时传入。

### Kafka 数据存储架构

Kafka 的存储架构设计精巧，层次分明：

- **Partition**：Topic 的分区，一个 Topic 可包含多个 Partition。每个 Partition 是一个有序队列，也是一个目录。Partition 内消息有序，Consumer 通过 Pull 方式消费。Kafka 不删除已消费的消息，以时间复杂度 O(1) 方式提供消息持久化能力。
- **Segment**：Partition 物理上由多个 Segment 文件组成，每个 Segment 大小相等，顺序读写。每个 Segment 以该段中最小的 offset 命名（扩展名 .log），查找指定 offset 的消息时可用二分查找定位。Segment 由 index 文件和 data 文件组成，一一对应、成对出现（.index 和 .log）。
- **稀疏索引**：index 文件中并没有为每条消息建立索引，而是采用稀疏存储方式，每隔一定字节建立一条索引，避免索引文件占用过多空间，从而可以将索引文件保留在内存中。

**性能优化手段**：

- **负载均衡**：Producer 可以通过随机或 Hash 方式将消息平均发送到多个 Partition 上
- **批量发送**：Producer 在内存中合并多条消息后一次请求发送，大大减少 Broker 的 IO 操作次数，以时延换取吞吐量
- **压缩传输**：Producer 端可通过 GZIP 或 Snappy 格式压缩消息集合，在大数据处理上瓶颈往往在网络而非 CPU
- **Offset 管理**：Current Offset 保证每次 poll 返回不重复的消息；Committed Offset 用于 Consumer Rebalance，保证新 Consumer 从正确位置开始消费
- **Zookeeper**：保存集群 Broker、Topic、Partition 等元数据，负责 Broker 故障发现、Partition Leader 选举和负载均衡
- **auto.offset.reset**：earliest（从最早的 offset 开始消费）、latest（从最后的 offset 开始消费）、none（直接抛出异常）

### Kafka 与 RocketMQ 存储区别

<https://mp.weixin.qq.com/s/_hJcEqTMASpeDkavcdtDsw>

RocketMQ 对 Kafka 的存储做了改进：
- Partition 升级为 ConsumerQueue，只存储消息的地址，由单独的 CommitLog 记录消息文件
- ConsumerQueue 消息格式大小固定（20 字节），写入 PageCache 后刷盘频率较低
- Kafka 中多 Partition 会存在随机写的可能性，Partition 之间刷盘冲撞率高；RocketMQ 中 CommitLog 都是顺序写

### 常用启动命令

```shell 
#启动zk
bin/zookeeper-server-start.sh config/zookeeper.properties &
#启动kafka
bin/kafka-server-start.sh config/server.properties
# kafka默认只支持本地访问，如果需要外网访问，需要用hostname.com的方式配置
# hostname.com可以是任意自定义的，不需要备案，只是起到"代名词"作用
#1、
config/server.properties
listeners=PLAINTEXT://hostname.com:9092
#2、
#kafka broker机器配置hosts
broker机器的内网ip  hostname.com
#3、
#调用端也是是kafka的Client端 的机器配置hosts
broker机器的外网ip  hostname.com
```

### 相关资料
- 极好的总结 <https://segmentfault.com/a/1190000021138998>
- zookeeper在kafka中的作用 <https://www.jianshu.com/p/a036405f989c>
- 一次事故 <https://www.jianshu.com/p/72a54f835b6b>

---

## RocketMQ

RocketMQ 是阿里巴巴开源的分布式消息中间件，在高吞吐、低延迟、海量消息堆积等方面表现突出。它吸收了 Kafka 的优点，同时针对电商等复杂业务场景做了大量增强。

<img src="{{ site.baseurl }}/img/RocketMq.jpg" width="600px"> 

### RocketMQ 核心优势

- **原生分布式支持**：ActiveMQ 原生存在单点问题，RocketMQ 天然支持分布式
- **严格的消息顺序**：ActiveMQ 无法保证，RocketMQ 可以保证
- **海量消息低延迟**：支持亿级消息堆积能力，亿级消息写入时仍可保持低延迟
- **消息拉取模式**：
    1. PUSH：消费者端设置 Listener
    2. PULL：应用可主动从 Broker 获取消息，主动拉取需注意消费记录位置问题
- **轻量级分布式协调**：从 ZooKeeper 演进为自研 NameServer，更轻量、更贴近框架需求、性能更好
- **分布式事务机制**：生产者预提交事务，RocketMQ 在收到明确事务或查询到明确事务后，发送下游事务流程
- **消费重试、高效订阅者水平扩展、多语言 API** 等

### 顺序消息

- 发送时同个 orderId 路由到相同分区
- 消费时由同一个消费者消费同一个订单
- 参考：<https://www.cnblogs.com/hzmark/p/orderly_message.html>

### 部署架构

RocketMQ 的部署结构具有以下特点（可理解为带有协调服务的主从架构）：

- **NameServer**：几乎无状态节点，可集群部署，节点之间无任何信息同步
- **Broker**：分为 Master 与 Slave，一个 Master 对应多个 Slave，通过相同 BrokerName 和不同 BrokerId 定义对应关系（BrokerId=0 为 Master）。每个 Broker 与 NameServer 集群中的所有节点建立长连接，定时注册 Topic 信息
- **Producer**：与 NameServer 集群中的一个节点（随机选择）建立长连接，定期取 Topic 路由信息，向提供 Topic 服务的 Master 建立长连接并定时发送心跳。Producer 完全无状态，可集群部署
- **Consumer**：与 NameServer 集群中的一个节点建立长连接，定期取 Topic 路由信息，向 Master、Slave 建立长连接并定时发心跳。Consumer 既可从 Master 也可从 Slave 订阅消息

### RocketMQ 核心机制详解

**存储与性能**：

- Broker 上存 Topic 信息，Topic 由多个队列组成，队列平均分散在多个 Broker 上。Producer 的发送机制保证消息尽量平均分布到所有队列
- 消息存储由 MessageQueue 和 CommitLog 配合完成。MessageQueue 中只存储少量数据，消息主体通过 CommitLog 进行读写。如果消息只在 CommitLog 中有数据而 MessageQueue 中没有，消费者无法消费——RocketMQ 的事务消息就利用了这一点
    - **CommitLog**：消息主体及元数据的存储主体，只要 CommitLog 在，即使 MessageQueue 数据丢失仍可恢复
    - **MessageQueue**：消息的逻辑队列，存储该 Queue 在 CommitLog 中的起始 offset、大小和 MessageTag 的 hashCode

**高性能与高可靠**：

- 高性能源于顺序写盘（CommitLog）、零拷贝和跳跃读（尽量命中 PageCache）
- 高可靠在于刷盘和 Master/Slave 机制。NameServer 全部挂掉不影响已运行的 Broker、Producer、Consumer
- 发送消息负载均衡且线程安全，集群消费模式下消费者端也做负载均衡

**容错机制**：

- 刷盘和主从同步均为异步（默认）时，Broker 进程挂掉（如重启）消息不会丢失（shutdown 时会执行 persist）。只有物理机器宕机时才有消息丢失风险
- Master 挂掉后，消费者从 Slave 消费消息，但 Slave 不能写消息
- Producer 失败默认重试 2 次，支持 sync/async 模式
- Consumer 支持 CLUSTERING（一条消息只被同组一个实例消费）和 BROADCASTING（同组所有实例都消费）模式

**长轮询机制（DefaultPushConsumer）**：

Broker 收到新消息请求后，如果队列里没有新消息，并不急于返回，而是通过循环不断查看状态，每次 waitForRunning 一段时间（5s），然后 check。当一直没有新消息，第三次 check 时等待时间超过 suspendMaxTimeMills（15s），就返回空结果。在等待过程中 Broker 收到新消息会直接调用 notifyMessageArriving 返回结果。"长轮询"的核心是 Broker 端 Hold 住客户端请求一小段时间，有新消息到达就利用现有连接立刻返回。

**动态伸缩能力**（非顺序消息）：

- **Topic 维度**：消息量大但集群水位低时，可扩大 Topic 队列数
- **Broker 维度**：集群水位高时，直接加机器部署 Broker，自动注册到 NameServer

**消费重试**：集群模式的非顺序消息，消费失败默认重试 16 次，延迟等级为 3~18（"1s 5s 10s 30s 1m 2m 3m 4m 5m 6m 7m 8m 9m 10m 20m 30m 1h 2h"）。

<https://www.cnblogs.com/javazhiyin/p/13327925.html>

### 安装与启动

```shell
# install rocketmq
unzip rocketmq-all-4.7.0-source-release.zip
cd rocketmq-all-4.7.0/
mvn -Prelease-all -DskipTests clean install -U
cd distribution/target/rocketmq-4.7.0/rocketmq-4.7.0

# config JAVA_HOME
vim ~/.bashrc
export JAVA_HOME=/usr/lib/jvm/jdk-13
export JRE_HOME=${JAVA_HOME}/jre
export CLASSPATH=.:${JAVA_HOME}/lib:${JRE_HOME}/lib
export PATH=${JAVA_HOME}/bin:$PATH

#Start Name Server
nohup sh bin/mqnamesrv &
tail -f ~/logs/rocketmqlogs/namesrv.log
#The Name Server boot success...

#Start Broker
nohup sh bin/mqbroker -n localhost:9876 &
#The broker[%s, 172.30.30.233:10911] boot success...

# 外网访问 配置 /etc/hosts
# 相关报错 RemotingTooMuchRequestException: sendDefaultImpl call timeout；
broker机器的内网ip  hostname.com
# 配置conf/broker.conf 
brokerIP1=hostname.com
./mqbroker -n localhost:9876 -c ../conf/broker.conf &

# 相关报错 No route info of this topic
# 保持客户端rocketmq版本号与服务器一致
# 设置该属性 autoCreateTopicEnable=true 
./mqadmin topicList -n localhost:9876

```

### 相关资料
- rocketmq为什么使用nameserver而不使用ZooKeeper？<https://blog.csdn.net/earthhour/article/details/78718064>
- 点赞削峰 <https://mp.weixin.qq.com/s/w6aCc-ueYHjkNeEZYcmAhw>
- RocketMQ吐血总结 <https://blog.csdn.net/javahongxi/article/details/84931747>
- 从Mq到RocketMq <http://jm.taobao.org/2017/01/12/rocketmq-quick-start-in-10-minutes/>
- Rocketmq、Kafka、RabbitMq对比<https://www.jianshu.com/p/2838890f3284>
- RocketMq事务消息 <https://www.jianshu.com/p/cc5c10221aa1>

---

## 总结

选择消息队列时，需要根据业务场景权衡各方面因素：

| 特性 | ActiveMQ | RabbitMQ | RocketMQ | Kafka |
|------|----------|----------|----------|-------|
| 定位 | 传统 MQ | 企业级 MQ | 分布式 MQ | 流处理平台 |
| 吞吐量 | 万级 | 万级 | 十万级 | 十万级 |
| 可用性 | 主从 | 主从/镜像 | 分布式 | 分布式 |
| 消息顺序 | 不保证 | 不保证 | 保证 | 分区有序 |
| 适用场景 | 中小规模 | 中小规模/路由复杂 | 电商/金融 | 大数据/日志 |

总的来说，如果业务规模不大且对路由灵活性有要求，RabbitMQ 是不错的选择；如果追求高吞吐量和分布式能力，且面向电商、金融等场景，RocketMQ 更为合适；如果是大数据流处理和日志收集场景，Kafka 几乎是标准答案。

#### 参考资料
- 消息队列常见问题 <https://www.cnblogs.com/williamjie/p/9481780.html>
- 优知学院消息队列
    - <https://zhuanlan.zhihu.com/p/60288173>
    - <https://zhuanlan.zhihu.com/p/60288391>
- IM系统的MQ消息中间件选型：Kafka还是RabbitMQ？
    - <https://zhuanlan.zhihu.com/p/37993013>
- MQ消息队列的12点核心原理总结
    - <https://zhuanlan.zhihu.com/p/60289322>
