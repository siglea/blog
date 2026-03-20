---
layout: post
title:  "Keepalived 高可用方案：原理、架构与容错机制详解"
date:   2019-12-08 11:25:00 +0900
comments: true
tags:
- 分布式
categories:
- 技术
---

### 引言

在分布式系统中，**高可用（High Availability）** 是一个永恒的主题。无论是 Web 服务器、数据库还是负载均衡器，单点故障（SPOF）都可能导致整个服务不可用。Keepalived 作为一个轻量级的高可用解决方案，通过 VRRP 协议实现服务的自动故障转移，被广泛应用于 Nginx、LVS、MySQL 等关键组件的高可用部署中。

### Keepalived 是什么

Keepalived 最初是专为 LVS（Linux Virtual Server）负载均衡软件设计的，用来管理并监控 LVS 集群中各个服务节点的状态。后来加入了 VRRP（Virtual Router Redundancy Protocol）功能，使其成为一个通用的高可用解决方案。

Keepalived 的核心能力包括：

- **LVS 管理**：自动配置和管理 LVS 的转发规则
- **健康检查**：对后端服务节点进行多种方式的健康检测（TCP、HTTP、脚本等）
- **故障转移**：通过 VRRP 协议实现 VIP（虚拟 IP）的自动漂移，保证服务不间断

它让管理员不再需要手动处理故障切换，极大地降低了运维复杂度。

### VRRP 协议与工作原理

VRRP（Virtual Router Redundancy Protocol，虚拟路由冗余协议）是 Keepalived 实现高可用的基石。其核心思想是：

将 N 台提供相同功能的服务器组成一个**路由器组**，组内有一个 **Master** 和多个 **Backup**。Master 持有一个对外提供服务的 **VIP（Virtual IP）**，客户端只需要连接 VIP 即可，无需关心背后是哪台实际服务器。

#### 工作流程

```
                    VIP: 192.168.1.100
                          │
            ┌─────────────┼─────────────┐
            │             │             │
       ┌────┴────┐  ┌────┴────┐  ┌────┴────┐
       │ Master  │  │ Backup1 │  │ Backup2 │
       │ Pri:100 │  │ Pri:90  │  │ Pri:80  │
       └─────────┘  └─────────┘  └─────────┘
```

1. **Master 选举**：启动时，优先级最高的节点成为 Master，持有 VIP
2. **心跳广播**：Master 周期性地向组内发送 VRRP 通告报文（默认每秒一次）
3. **故障检测**：Backup 如果在指定时间内未收到 Master 的通告，则判定 Master 故障
4. **自动切换**：优先级最高的 Backup 升级为新的 Master，接管 VIP

整个切换过程通常在秒级完成，对客户端几乎透明。

### Keepalived 的三大核心模块

Keepalived 的内部架构由三个模块组成：

| 模块 | 职责 |
|------|------|
| **Core** | 核心模块，负责主进程启动、维护以及全局配置文件的加载和解析 |
| **Check** | 健康检查模块，支持 TCP_CHECK、HTTP_GET、SSL_GET、MISC_CHECK 等多种检查方式 |
| **VRRP** | VRRP 协议实现模块，负责 VIP 的管理和故障转移 |

### 典型配置示例

以 Nginx + Keepalived 实现双机热备为例：

**Master 节点配置** (`/etc/keepalived/keepalived.conf`)：

```bash
global_defs {
    router_id nginx_master
}

vrrp_script check_nginx {
    script "/etc/keepalived/check_nginx.sh"
    interval 2
    weight -20
}

vrrp_instance VI_1 {
    state MASTER
    interface eth0
    virtual_router_id 51
    priority 100
    advert_int 1

    authentication {
        auth_type PASS
        auth_pass 1111
    }

    virtual_ipaddress {
        192.168.1.100
    }

    track_script {
        check_nginx
    }
}
```

**Backup 节点配置**只需将 `state` 改为 `BACKUP`，`priority` 设置为较低的值（如 90）。

**Nginx 健康检查脚本** (`check_nginx.sh`)：

```bash
#!/bin/bash
if [ $(ps -C nginx --no-header | wc -l) -eq 0 ]; then
    systemctl start nginx
    sleep 2
    if [ $(ps -C nginx --no-header | wc -l) -eq 0 ]; then
        systemctl stop keepalived
    fi
fi
```

这个脚本的逻辑是：检测 Nginx 是否存活，如果挂了先尝试重启，重启失败则停止 Keepalived，触发 VIP 漂移到 Backup 节点。

### 常见容错机制

在分布式系统设计中，除了 Keepalived 提供的故障转移能力，还有几种经典的容错机制值得了解：

#### 1. Failover — 失效转移

当主要组件异常时，其功能自动转移到备份组件。要点是**有主有备，主故障时备自动启用**。

典型场景：
- MySQL 双 Master 模式，主库故障时自动切换到备库
- Redis Sentinel 哨兵模式，自动将 Slave 提升为 Master
- Keepalived 的 VIP 漂移就是 Failover 的经典实现

#### 2. Failfast — 快速失败

**尽可能早地发现并暴露错误**，按照预设的错误流程处理，而不是尝试掩盖问题。

Java 中的典型例子：当多个线程并发修改同一个集合时，迭代器会立即抛出 `ConcurrentModificationException`，而不是返回不确定的结果。

```java
List<String> list = new ArrayList<>(Arrays.asList("a", "b", "c"));
for (String item : list) {
    if ("b".equals(item)) {
        list.remove(item);  // 触发 ConcurrentModificationException
    }
}
```

这种设计理念在微服务架构中也很常见：当依赖服务不可用时，快速返回错误而不是长时间等待超时。

#### 3. Failback — 失效自动恢复

Failover 之后的自动恢复过程。当故障节点修复后，将网络资源和服务恢复到原始主机上提供。

需要注意的是，Failback 在某些场景下可能引发**脑裂问题**——原 Master 恢复后与新 Master 争抢 VIP。Keepalived 通过 VRRP 优先级机制来解决这个问题：可以配置 `nopreempt`（非抢占模式），让原 Master 恢复后不自动抢回 VIP。

#### 4. Failsafe — 失效安全

即使在故障情况下也不会造成伤害，或尽量减少伤害。

一个经典的例子是交通信号灯：当控制系统检测到信号冲突时，不会让所有方向都显示绿灯，而是切换到闪烁警示模式。在软件系统中，限流、降级、熔断都是 Failsafe 思想的体现。

### 生产环境中的注意事项

1. **脑裂防护**：确保 Master 和 Backup 之间的网络通信稳定，必要时使用多条心跳线路
2. **非抢占模式**：在某些场景下配置 `nopreempt`，避免 VIP 频繁漂移
3. **健康检查间隔**：检查间隔不宜过长（影响故障发现速度），也不宜过短（增加系统开销）
4. **日志监控**：配置 Keepalived 日志并接入监控系统，及时发现状态变化

### 参考资料

- [Keepalived 官网](http://www.keepalived.org)
- [Keepalived 权威指南](https://www.cnblogs.com/clsn/p/8052649.html)

### 总结

Keepalived 通过 VRRP 协议提供了一种简洁高效的高可用方案。理解其背后的 Master-Backup 选举机制、健康检查策略和 VIP 漂移原理，能帮助我们在生产环境中构建更可靠的服务架构。同时，Failover、Failfast、Failback、Failsafe 这四种容错机制是分布式系统设计的基本功，在架构设计中需要灵活运用。
