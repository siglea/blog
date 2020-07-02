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
 ### MOM(Message Oriented Middleware)
<img src="/img/mq.jpg" width="600px"> 

17 个方面，综合对比 Kafka、RabbitMQ、RocketMQ、ActiveMQ 
<https://mp.weixin.qq.com/s/u7pyzEQgqmux9qUI_SPaNw>

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

### ActiveMQ

#### ActiveMQ 服务器宕机怎么办？
这得从 ActiveMQ 的储存机制说起。在通常的情况下，非持久化消息是存储在内存中的，持久化消息是存储在文件中的，它们的最大限制在配置文件的节点中配置。但是，在非持久化消息堆积到一定程度，内存告急的时候，ActiveMQ 会将内存中的非持久化消息写入临时文件中，以腾出内存。虽然都保存到了文件里，但它和持久化消息的区别是，重启后持久化消息会从文件中恢复，非持久化的临时文件会直接删除。
那如果文件增大到达了配置中的最大限制的时候会发生什么？我做了以下实验：
设置 2G 左右的持久化文件限制，大量生产持久化消息直到文件达到最大限制，此时生产者阻塞，但消费者可正常连接并消费消息，等消息消费掉一部分，文件删除又腾出空间之后，生产者又可继续发送消息， 服务自动恢复正常。
设置 2G 左右的临时文件限制，大量生产非持久化消息并写入临时文件，在达到最大限制时，生产者阻塞，消费者可正常连接但不能消费消息，或者原本慢速消费的消费者，消费突然停止。整个系统可连接， 但是无法提供服务，就这样挂了。

#### ActiveMQ 消息的不均匀消费。
有时在发送一些消息之后，开启 2 个消费者去处理消息。会发现一个消费者处理了所有的消息，另一个消费者根本没收到消息。原因在于 ActiveMQ 的 prefetch 机制。当消费者去获取消息时，不会一条一条去获取，而是一次性获取一批，默认是 1000 条。这些预获取的消息，在还没确认消费之前，在管理控制台还是可以看见这些消息的，但是不会再分配给其他消费者，此时这些消息的状态应该算作“已分配未消 费”，如果消息最后被消费，则会在服务器端被删除，如果消费者崩溃，则这些消息会被重新分配给新的消费者。但是如果消费者既不消费确认，又不崩溃，那这些消息就永远躺在消费者的缓存区里无法处理。更通常的情况是，消费这些消息非常耗时，你开了 10 个消费者去处理，结果发现只有一台机器吭哧吭哧处理，另外 9 台啥事不干。
解决方案：将 prefetch 设为 1，每次处理 1 条消息，处理完再去取，这样也慢不了多少。

#### ActiveMQ 死信队列。
如果你想在消息处理失败后，不被服务器删除，还能被其他消费者处理或重试，可以关闭AUTO_ACKNOWLEDGE，将 ack 交由程序自己处理。那如果使用了 AUTO_ACKNOWLEDGE，消息是什么时候被确认的，还有没有阻止消息确认的方法？有！
消费消息有 2 种方法：
- 一种是调用 consumer.receive()方法，该方法将阻塞直到获得并返回一条消息。这种情况下，消息返回给方法调用者之后就自动被确认了。
- 一种方法是采用 listener 回调函数，在有消息到达时，会调用 listener 接口的 onMessage 方法。在这种情况下，在 onMessage 方法执行完毕后， 消息才会被确认，此时只要在方法中抛出异常，该消息就不会被确认。
那么问题来了，如果一条消息不能被处理，会被退回服务器重新分配，如果只有一个消费者，该消息又会重新被获取，重新抛异常。就算有多个消费者，往往在一个服务器上不能处理的消息，在另外的服务器上依然不能被处理。难道就这么退回–获取–报错死循环了吗？
- 在重试 6 次后，ActiveMQ 认为这条消息是“有毒”的，将会把消息丢到死信队列里。如果你的消息不见了，去 ActiveMQ.DLQ 里找找，说不定就躺在那里。

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

#### Master是最终读写保存的地方，Slave中转     
除发送消息（Basic.Publish）外的所有动作都只会向 master 发送，然后再由master 将命令执行的结果广播给各个 slave。
如果消费者与 slave 建立连接并进行订阅消费，其实质都是从 master 上获取消息，只不过看似是从 slave 上消费而已。比如消费者与 slave 建立了 TCP 连接之后执行一个 Basic.Get 操作，那么首先是由 slave 将Basic.Get 请求发往 master，再由 master 准备好数据返回给 slave，最后由 slave 投递给消费者。


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
#### 写操作都发生在leader broker，其他broker会告诉client，leader在哪里
producer是否直接将数据发送到broker的leader(主节点
producer直接将数据发送到broker的leader(主节点)，不需要在多个节点
逬行分发，为了帮助producer做到这点，所有的Kafka节点都可以及时
的告知:哪些节点是活动的，目标topic目标分区的leader在哪。这样
producer就可以直接将消息发送到目的地了

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

<img src="/img/RocketMq.jpg" width="600px"> 

#### RocketMQ的部署结构有以下特点：
- Name Server是一个几乎无状态节点，可集群部署，节点之间无任何信息同步。
- Broker部署相对复杂，Broker分为Master与Slave，一个Master可以对应多个Slave，但是一个Slave只能对应一个Master，Master与Slave的对应关系通过指定相同的BrokerName，不同的BrokerId来定义，BrokerId为0表示Master，非0表示Slave。Master也可以部署多个。每个Broker与Name Server集群中的所有节点建立长连接，定时注册Topic信息到所有Name Server。
- Producer与Name Server集群中的其中一个节点（随机选择）建立长连接，定期从Name Server取Topic路由信息，并向提供Topic服务的Master建立长连接，且定时向Master发送心跳。Producer完全无状态，可集群部署。
- Consumer与Name Server集群中的其中一个节点（随机选择）建立长连接，定期从Name Server取Topic路由信息，并向提供Topic服务的Master、Slave建立长连接，且定时向Master、Slave发送心跳。Consumer既可以从Master订阅消息，也可以从Slave订阅消息，订阅规则由Broker配置决定。

#### RocketMq核心点
- Broker上存Topic信息，Topic由多个队列组成，队列会平均分散在多个Broker上。Producer的发送机制保证消息尽量平均分布到 所有队列中，最终效果就是所有消息都平均落在每个Broker上。
- RocketMQ的消息的存储是由ConsumeQueue和CommitLog配合来完成的，ConsumeQueue中只存储很少的数据，消息主体都是通过CommitLog来进行读写。 如果某个消息只在CommitLog中有数据，而ConsumeQueue中没有，则消费者无法消费，RocketMQ的事务消息实现就利用了这一点。
    - CommitLog：是消息主体以及元数据的存储主体，对CommitLog建立一个ConsumeQueue，每个ConsumeQueue对应一个（概念模型中的）MessageQueue，所以只要有 CommitLog在，ConsumeQueue即使数据丢失，仍然可以恢复出来。
    - ConsumeQueue：是一个消息的逻辑队列，存储了这个Queue在CommitLog中的起始offset，log大小和MessageTag的hashCode。每个Topic下的每个Queue都有一个对应的 ConsumeQueue文件，例如Topic中有三个队列，每个队列中的消息索引都会有一个编号，编号从0开始，往上递增。并由此一个位点offset的概念，有了这个概念，就可以对 Consumer端的消费情况进行队列定义。
- RocketMQ的高性能在于顺序写盘(CommitLog)、零拷贝和跳跃读(尽量命中PageCache)，高可靠性在于刷盘和Master/Slave，另外NameServer 全部挂掉不影响已经运行的Broker,Producer,Consumer。
- 发送消息负载均衡，且发送消息线程安全(可满足多个实例死循环发消息)，集群消费模式下消费者端负载均衡，这些特性加上上述的高性能读写， 共同造就了RocketMQ的高并发读写能力。
- 刷盘和主从同步均为异步(默认)时，broker进程挂掉(例如重启)，消息依然不会丢失，因为broker shutdown时会执行persist。 当物理机器宕机时，才有消息丢失的风险。另外，master挂掉后，消费者从slave消费消息，但slave不能写消息。
- RocketMQ具有很好动态伸缩能力(非顺序消息)，伸缩性体现在Topic和Broker两个维度。
    - Topic维度：假如一个Topic的消息量特别大，但集群水位压力还是很低，就可以扩大该Topic的队列数，Topic的队列数跟发送、消费速度成正比。
    - Broker维度：如果集群水位很高了，需要扩容，直接加机器部署Broker就可以。Broker起来后向Namesrv注册，Producer、Consumer通过Namesrv 发现新Broker，立即跟该Broker直连，收发消息。
- Producer: 失败默认重试2次；sync/async；ProducerGroup，在事务消息机制中，如果发送消息的producer在还未commit/rollback前挂掉了，broker会在一段时间后回查ProducerGroup里的其他实例，确认消息应该commit/rollback
- Consumer: DefaultPushConsumer/DefaultPullConsumer，push也是用pull实现的，采用的是长轮询方式；CLUSTERING模式下，一条消息只会被ConsumerGroup里的一个实例消费，但可以被多个不同的ConsumerGroup消费，BROADCASTING模式下，一条消息会被ConsumerGroup里的所有实例消费。
- DefaultPushConsumer: Broker收到新消息请求后，如果队列里没有新消息，并不急于返回，通过一个循环不断查看状态，每次waitForRunning一段时间(5s)，然后在check。当一直没有新消息，第三次check时，等待时间超过suspendMaxTimeMills(15s)，就返回空结果。在等待的过程中，Broker收到了新的消息后会直接调用notifyMessageArriving返回请求结果。“长轮询”的核心是，Broker端Hold住(挂起)客户端客户端过来的请求一小段时间，在这个时间内有新消息到达，就利用现有的连接立刻返回消息给Consumer。“长轮询”的主动权还是掌握在Consumer手中，Broker即使有大量消息积压，也不会主动推送给Consumer。长轮询方式的局限性，是在Hold住Consumer请求的时候需要占用资源，它适合用在消息队列这种客户端连接数可控的场景中。
- DefaultPullConsumer: 需要用户自己处理遍历MessageQueue、保存Offset，所以PullConsumer有更多的自主性和灵活性。
- 对于集群模式的非顺序消息，消费失败默认重试16次，延迟等级为3~18。(messageDelayLevel = "1s 5s 10s 30s 1m 2m 3m 4m 5m 6m 7m 8m 9m 10m 20m 30m 1h 2h")
- MQClientInstance是客户端各种类型的Consumer和Producer的底层类，由它与NameServer和Broker打交道。如果创建Consumer或Producer 类型的时候不手动指定instanceName，进程中只会有一个MQClientInstance对象，即当一个Java程序需要连接多个MQ集群时，必须手动指定不同的instanceName。需要一提的是，当消费者(不同jvm实例)都在同一台物理机上时，若指定instanceName，消费负载均衡将失效(每个实例都将消费所有消息)。另外，在一个jvm里模拟集群消费时，必须指定不同的instanceName，否则启动时会提示ConsumerGroup已存在。

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
- RocketMQ吐血总结 <https://blog.csdn.net/javahongxi/article/details/84931747>
- 从Mq到RocketMq <http://jm.taobao.org/2017/01/12/rocketmq-quick-start-in-10-minutes/>
- Rocketmq、Kafka、RabbitMq对比<https://www.jianshu.com/p/2838890f3284>
- RocketMq事务消息 <https://www.jianshu.com/p/cc5c10221aa1>
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