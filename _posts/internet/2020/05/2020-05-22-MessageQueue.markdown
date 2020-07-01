---
layout: post
title:  " kafka activeMQ RabbitMq RocketMQ "
date:   2020-05-22 11:25:00
tags:
- MQ
- 分布式
categories:
- 技术
---
### AMQP，即Advanced Message Queuing Protocol（ActiveMQ、RabbitMQ都支持）
- 高级消息队列协议，是应用层协议的一个开放标准，为面向消息的中间件设计。消息中间件主要用于组件之间的解耦，消息的发送者无需知道消息使用者的存在，反之亦然。
- AMQP的主要特征是面向消息、队列、路由（包括点对点和发布/订阅）、可靠性、安全。RabbitMQ是一个开源的AMQP实现，服务器端用Erlang语言编写，支持多种客户端，如：Python、Ruby、.NET、Java、JMS、C、PHP、ActionScript、XMPP、STOMP等，支持AJAX。用于在分布式系统中存储转发消息，在易用性、扩展性、高可用性等方面表现不俗。

#### 两种消息模型：
- 点对点（单播），当采用点对点模型时，消息将发送到一个队列，该队列的消息只能被一个消费者消费。   
- publish-subscribe（发布订阅、广播）模型。而采用发布订阅模型时，消息可以被多个消费者消费。
  在发布订阅模型中，生产者和消费者完全独立，不需要感知对方的存在。
  例如，在用户登录后，各个其他模板更加登录进行不同的处理

#### 如何保证可用性
- 主从架构（ActiveMQ、RabbitMQ）
- 分布式架构（kafka、RocketMQ）  

#### 推拉模式
消费模式分为推（push）模式和拉（pull）模式。推模式是指由 Broker 主动推送消息至消费端，实时性较好，不过需要一定的流制机制来确保服务端推送过来的消息不会压垮消费端。而拉模式是指消费端主动向 Broker 端请求拉取（一般是定时或者定量）消息，实时性较推模式差，但是可以根据自身的处理能力而控制拉取的消息量。

### RabbitMq
- Exchange：消息交换机，生产者不是直接将消息投递到Queue中的，实际上是生产者将消息发送到Exchange（交换器，下图中的X），由Exchange将消息路由到一个或多个Queue中（或者丢弃）。
- Exchange Types RabbitMQ常用的Exchange Type有fanout、direct、topic、headers这四种（AMQP规范里还提到两种Exchange Type，分别为system与自定义，这里不予以描述），之后会分别进行介绍。
- Queue：消息队列载体，每个消息都会被投入到一个或多个队列。
- Binding：绑定，它的作用就是把exchange和queue按照路由规则绑定起来，这样RabbitMQ就知道如何正确地将消息路由到指定的Queue了。
- Routing Key：路由关键字，生产者在将消息发送给Exchange的时候，一般会指定一个routing key，来指定这个消息的路由规则，而这个routing key需要与Exchange Type及binding key联合使用才能最终生效。

```shell 
rabbitmq-server start
service rabbitmq-server restart
rabbitmqctl status
rabbitmq-plugins enable rabbitmq_management
rabbitmqctl add_user rabbitmq 123456
rabbitmqctl set_user_tags rabbitmq administrator
rabbitmqctl set_permissions -p / rabbitmq ".*" ".*" ".*"
```

#### RabbitMQ可以通过三种方法来部署分布式集群系统
- cluster:不支持跨网段，用于同一个网段内的局域网。可以随意的动态增加或者减少。节点之间需要运行相同版本的RabbitMQ和Erlang。
    - 普通模式：默认的集群模式，slave只保存Queue相关的元数据。
    - 镜像模式：把需要的队列做成镜像队列，存在于多个节点（至少1个镜像节点、多个Slave节点），属于RabbitMQ的HA方案
- federation:应用于广域网，允许单台服务器上的交换机或队列接收发布到另一台服务器上交换机或队列的消息，可以是单独机器或集群。federation队列类似于单向点对点连接，消息会在联盟队列之间转发任意次，直到被消费者接受。通常使用federation来连接internet上的中间服务器，用作订阅分发消息或工作队列。
- shovel:连接方式与federation的连接方式类似，但它工作在更低层次。可以应用于广域网

#### RabbitMQ 节点类型
- RAM node:内存节点将所有的队列、交换机、绑定、用户、权限和vhost的元数据定义存储在内存中，好处是可以使得像交换机和队列声明等操作更加的快速。
    - RabbitMQ要求在集群中至少有一个磁盘节点，所有其他节点可以是内存节点，当节点加入或者离开集群时，必须要将该变更通知到至少一个磁盘节点。
    - 如果集群中唯一的一个磁盘节点崩溃的话，集群仍然可以保持运行，但是无法进行其他操作(包括创建队列、交换器、绑定，添加用户、更改权限、添加和删除集群结点)，直到节点恢复。
    - 解决方案：设置两个磁盘节点，至少有一个是可用的，可以保存元数据的更改。
- Disk node:将元数据存储在磁盘中，单节点系统只允许磁盘类型的节点，防止重启RabbitMQ的时候，丢失系统的配置信息。

#### Consumer Cancellation Notification 机制用于什么场景？
- 用于保证当镜像 queue 中 master 挂掉时，连接到 slave 上的 consumer 可以收到自身 consume 被取消的通知，进而可以重新执行 consume 动作从新选出的 master 出获得消息。若不采用该机制，连接到 slave 上的 consumer 将不会感知 master 挂掉这个事情，导致后续无法再收到新 master 广播出来的 message 。另外，因为在镜像 queue 模式下，存在将 message 进行 requeue 的可能，所以实现 consumer 的逻辑时需要能够正确处理出现重复 message 的情况。

#### “dead letter”queue 的用途？
- 当消息被 RabbitMQ server 投递到 consumer 后，但 consumer 却通过 Basic.Reject 进行了拒绝时（同时设置 requeue=false），那么该消息会被放入“dead letter”queue 中。该 queue 可用于排查 message 被 reject 或 undeliver 的原因。

#### 什么情况下会出现 blackholed 问题？
- blackholed 问题是指，向 exchange 投递了 message ，而由于各种原因导致该message 丢失，但发送者却不知道。可导致 blackholed 的情况：1.向未绑定 queue 的exchange 发送 message；2.exchange 以 binding_key key_A 绑定了 queue queue_A，但向该 exchange 发送 message 使用的 routing_key 却是 key_B。

#### 如何防止出现 blackholed 问题？
- 没有特别好的办法，只能在具体实践中通过各种方式保证相关 fabric 的存在。另外， 如果在执行 Basic.Publish 时设置 mandatory=true ，则在遇到可能出现 blackholed 情况时，服务器会通过返回 Basic.Return 告之当前 message 无法被正确投递（内含原因 312 NO_ROUTE）。

#### RabbitMQ之Qos prefetchCount
- 实际使用RabbitMQ过程中，如果完全不配置QoS，这样Rabbit会尽可能快速地发送队列中的所有消息到client端。
    因为consumer在本地缓存所有的message，从而极有可能导致OOM或者导致服务器内存不足影响其它进程的正常运行。
    所以我们需要通过设置Qos的prefetch count来控制consumer的流量。同时设置得当也会提高consumer的吞吐量。

#### RabbitMq参考
- RabbitMQ <https://www.jianshu.com/p/78847c203b76>
- RabbitMQ镜像队列 <https://www.jianshu.com/p/fcc35573567c>
- RabbitMQ原理、集群、基本操作及常见故障处理 <https://mp.weixin.qq.com/s/J-4INNmU_vM_Xs__KFEqIQ>

#### 如何保证消息不被重复消费？
- 分析:这个问题其实换一种问法就是，如何保证消息队列的幂等性?这个问题可以认为是消息队列领域的基本问题。换句话来说，是在考察你的设计能力，这个问题的回答可以根据具体的业务场景来答，没有固定的答案。
- 回答:先来说一下为什么会造成重复消费?其实无论是那种消息队列，造成重复消费原因其实都是类似的。
    - 正常情况下，消费者在消费消息时候，消费完毕后，会发送一个确认信息给消息队列，消息队列就知道该消息被消费了，就会将该消息从消息队列中删除。只是不同的消息队列发送的确认信息形式不同,例如RabbitMQ是发送一个ACK确认消息，RocketMQ是返回一个CONSUME_SUCCESS成功标志，kafka实际上有个offset的概念，简单说一下(如果还不懂，出门找一个kafka入门到精通教程),就是每一个消息都有一个offset，kafka消费过消息后，需要提交offset，让消息队列知道自己已经消费过了。那造成重复消费的原因?，就是因为网络传输等等故障，确认信息没有传送到消息队列，导致消息队列不知道自己已经消费过该消息了，再次将该消息分发给其他的消费者。如何解决?这个问题针对业务场景来答分以下几点
    - 比如，你拿到这个消息做数据库的insert操作。那就容易了，给这个消息做一个唯一主键，那么就算出现重复消费的情况，就会导致主键冲突，避免数据库出现脏数据。
    - 再比如，你拿到这个消息做redis的set的操作，那就容易了，不用解决，因为你无论set几次结果都是一样的，set操作本来就算幂等操作。
    - 如果上面两种情况还不行，上大招。准备一个第三方介质,来做消费记录。以redis为例，给消息分配一个全局id，只要消费过该消息，将<id,message>以K-V形式写入redis。那消费者开始消费前，先去redis中查询有没消费记录即可。

#### 消费者消费失败，如何处理？
- 消费成功时，手动ack，这样队列会再次推送或者再次pull
- 用redis对立的"伪消费队列"最大的问题就是在于消费后没有ACK，发生意外会有很多脏数据
- 也可以用幂等的方式消费者保存业务的进展，用单独程序做补偿消费
- 如果消费者处理一个消息失败了，消息系统一般会把这个消息放回队列，这样其他消费者可以继续处理

#### 如何保证消费的可靠性传输?
- RabbitMQ
    - 生产者丢数据，可以用事务方式来保证发送成功或回滚，也可以队列接受后异步返回ack或nack来实现
    - 消息队列丢数据，可以持久化队列并且配置自动重复参数
    - 消费者丢数据，手动ack
    
- kafka
    - (1)生产者丢数据
      在kafka生产中，基本都有一个leader和多个follwer。follwer会去同步leader的信息。因此，为了避免生产者丢数据，做如下两点配置
      1. 第一个配置要在producer端设置acks=all。这个配置保证了，follwer同步完成后，才认为消息发送成功。
      1. 在producer端设置retries=MAX，一旦写入失败，这无限重试
    - 消息队列丢数据
      针对消息队列丢数据的情况，无外乎就是，数据还没同步，leader就挂了，这时zookpeer会将其他的follwer切换为leader,那数据就丢失了。针对这种情况，应该做两个配置。
      1. replication.factor参数，这个值必须大于1，即要求每个partition必须有至少2个副本
      1. min.insync.replicas参数，这个值必须大于1，这个是要求一个leader至少感知到有至少一个follower还跟自己保持联系
      这两个配置加上上面生产者的配置联合起来用，基本可确保kafka不丢数据
    - 消费者丢数据
      这种情况一般是自动提交了offset，然后你处理程序过程中挂了。kafka以为你处理好了。再强调一次offset是干嘛的
      offset：指的是kafka的topic中的每个消费组消费的下标。简单的来说就是一条消息对应一个offset下标，每次消费数据的时候如果提交offset，那么下次消费就会从提交的offset加一那里开始消费。

### Kafka

#### Kafka 数据传输的事物定义有哪三种?
数据传输的事务定义通常有以下三种级别:
1. 最多一次: 消息不会被重复发送，最多被传输一次，但也有可能一次不传输 
1. 最少一次: 消息不会被漏发送，最少被传输一次，但也有可能被重复传输. 
1. 精确的一次(Exactly once): 不会漏传输也不会重复传输,每个消息都传输被一次而且 仅仅被传输一次，这是大家所期望的

#### kafka 收到消息的 ack 机制
- request.required.acks 有三个值 0 1 -1
- 0:生产者不会等待 broker 的 ack，这个延迟最低但是存储的保证最弱当 server 挂掉的时候就 会丢数据
- 1:服务端会等待 ack 值 leader 副本确认接收到消息后发送 ack 但是如果 leader 挂掉后他不 确保是否复制完成新 leader 也会导致数据丢失
- -1:同样在 1 的基础上 服务端会等所有的 follower 的副本受到数据后才会受到 leader 发出 的 ack，这样数据不会丢失

#### Kafka More
15.消费者负载均衡策略 ，一个消费者组中的一个分片对应一个消费者成员，他能保证每个消费者成员都能访问，如果 组中成员太多会有空闲的成员
16.数据有序 ，一个消费者组里它的内部是有序的 消费者组与消费者组之间是无序的
17.kafaka ，生产数据时数据的分组策略 生产者决定数据产生到集群的哪个 partition 中 每一条消息都是以(key，value)格式Key 是由生产者发送数据传入

#### 关于kafka
- Apache Kafka不是消息中间件的一种实现。相反，它只是一种分布式流式系统。
不同于基于队列和交换器的RabbitMQ，Kafka的存储层是使用分区事务日志来实现的。
- 过期日志会根据时间或大小，进行清除 
- 极好的总结 <https://segmentfault.com/a/1190000021138998>
- zookeeper在kafka中的作用 <https://www.jianshu.com/p/a036405f989c>
- 一次事故 <https://www.jianshu.com/p/72a54f835b6b>
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

#### kafka数据存储
- Kafka和RocketMQ存储区别 <https://mp.weixin.qq.com/s/_hJcEqTMASpeDkavcdtDsw>
    - partition升级为ConsumerQueue，并且只存储消息的地址，由单独的commitLog记录消息文件
    - consumerQueue消息格式大小固定（20字节），写入pagecache之后被触发刷盘频率相对较低。就是因为每次写入的消息小，造成他占用的pagecache少，主要占用方一旦被清理，那么他就可以不用清理了。
    - kafka中多partition会存在随机写的可能性，partition之间刷盘的冲撞率会高，但是rocketmq中commitLog都是顺序写。

- partition：topic 的分区，一个 topic 可以包含多个 partition，topic 消息保存在各个partition 上
    - 每个partition是一个有序的队列也是一个目录。
    - partition 内消息是有序的，Consumer 通过 pull 方式消费消息。Kafka 不删除已消费的消息.。对于 partition，顺序读写磁盘数据，以时间复杂度 O(1)方式提供消息持久化能力。
    - 每个partition(目录)相当于一个巨型文件被平均分配到多个大小相等segment(段)数据文件中。但每个段segment file消息数量不一定相等，这种特性方便old segment file快速被删除。
- segment：partition物理上由多个segment文件组成，每个segment大小相等，顺序读写。
    - 每个 segment 数据文件以该段中最小的 offset 命名，文件扩展名为.log。这样在查找指定 offset 的 Message 的 时候，用二分查找就可以定位到该 Message 在哪个 segment 数据文件中。
    - segment file组成：由2大部分组成，分别为index file和data file，此2个文件一一对应，成对出现，后缀".index"和“.log”分别表示为segment索引文件、数据文件。
- Kafka 为每个分段后的数据文件建立了索引文件，文件名与数据文件的名字是一样的，只是文件扩 展名为.index。index 文件中并没有为数据文件中的每条 Message 建立索引，而是采用了稀疏存 储的方式，每隔一定字节的数据建立一条索引。这样避免了索引文件占用过多的空间，从而可以 将索引文件保留在内存中。
- 由于消息 topic 由多个 partition 组成，且 partition 会均衡分布到不同 broker 上，因此，为了有 效利用 broker 集群的性能，提高消息的吞吐量，producer 可以通过随机或者 hash 等方式，将消 息平均发送到多个 partition 上，以实现负载均衡。
- 是提高消息吞吐量重要的方式，Producer 端可以在内存中合并多条消息后，以一次请求的方式发 送了批量的消息给 broker，从而大大减少 broker 存储消息的 IO 操作次数。但也一定程度上影响 了消息的实时性，相当于以时延代价，换取更好的吞吐量。
- Producer 端可以通过 GZIP 或 Snappy 格式对消息集合进行压缩。Producer 端进行压缩之后，在 Consumer 端需进行解压。压缩的好处就是减少传输的数据量，减轻对网络传输的压力，在对大 数据处理上，瓶颈往往体现在网络上而不是 CPU(压缩和解压会耗掉部分 CPU 资源)。
- Current Offset是针对Consumer的poll过程的，它可以保证每次poll都返回不重复的消息；而Committed Offset是用于Consumer Rebalance过程的，它能够保证新的Consumer能够从正确的位置开始消费一个partition，从而避免重复消费。
- Zookeeper：保存着集群 broker、topic、partition 等 meta 数据;另外，还负责 broker 故障发现，partition leader 选举，负载均衡等功能。
- auto.offset.reset表示如果Kafka中没有存储对应的offset信息的话（有可能offset信息被删除），消费者从何处开始消费消息。它拥有三个可选值：earliest：从最早的offset开始消费、latest：从最后的offset开始消费、none：直接抛出exception给consumer
  
  
### rocketmq

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
- rocketmq为什么使用nameserver而不使用ZooKeeper？<https://blog.csdn.net/earthhour/article/details/78718064>
- 点赞削峰 <https://mp.weixin.qq.com/s/w6aCc-ueYHjkNeEZYcmAhw>

#### 参考
- 消息队列常见问题 
    - <https://www.cnblogs.com/williamjie/p/9481780.html>
- 优知学院消息队列
    - <https://zhuanlan.zhihu.com/p/60288173>
    - <https://zhuanlan.zhihu.com/p/60288391>
- IM系统的MQ消息中间件选型：Kafka还是RabbitMQ？
    - <https://zhuanlan.zhihu.com/p/37993013>
- MQ消息队列的12点核心原理总结
    - <https://zhuanlan.zhihu.com/p/60289322>