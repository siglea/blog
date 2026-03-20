---
layout: post
title:  "深入理解 AWS IAM：身份与访问管理核心概念及实践"
date:   2019-01-11 23:30:09 +0900
comments: true
tags:
- 云服务
categories:
- 技术
---

在云计算时代，安全是一切架构的基础。AWS Identity and Access Management（IAM）作为 AWS 安全体系的基石，控制着"谁可以在什么条件下对哪些资源执行什么操作"。无论你是准备 AWS Developer Associate 认证考试，还是在实际项目中需要配置权限管理，深入理解 IAM 都是必修课。

## IAM 是什么

IAM 是 AWS 提供的免费服务，用于安全地管理对 AWS 资源的访问。它的核心能力包括：

- **身份认证（Authentication）**：确认"你是谁"
- **授权（Authorization）**：决定"你能做什么"
- **全局服务**：IAM 是全球性的，不绑定到任何特定 Region

## IAM 四大核心组件

IAM 的权限模型围绕四个关键概念构建：

### 1. User（用户）

User 代表一个具体的人或应用程序。每个 User 拥有独立的凭证，用于访问 AWS 资源。

创建用户时有两种访问方式：

**控制台访问（Console Access）**
- 需要设置用户名和密码
- 可以要求用户首次登录时重置密码
- 适用于需要通过 Web 管理界面操作 AWS 的场景

**编程访问（Programmatic Access）**
- 生成 Access Key ID 和 Secret Access Key
- **Secret Access Key 仅在创建时显示一次**，必须立即下载 CSV 文件妥善保存
- 适用于 CLI、SDK、API 调用等自动化场景

### 2. Group（组）

Group 是 User 的集合，用于批量管理权限。例如：

- `Developers` 组：赋予 EC2、S3、CodeDeploy 等开发相关权限
- `DBAdmins` 组：赋予 RDS、DynamoDB 管理权限
- `ReadOnly` 组：仅赋予只读权限

一个 User 可以属于多个 Group，Group 不能嵌套（即 Group 不能包含其他 Group）。

### 3. Role（角色）

Role 是为 AWS 资源或外部身份定义的临时权限集合。与 User 不同，Role 没有长期凭证，而是通过 STS（Security Token Service）签发临时凭证。

典型使用场景：

- **EC2 实例角色**：为 EC2 实例附加 Role，使其能够访问 S3 存储桶，而无需在实例中硬编码 Access Key
- **跨账号访问**：允许另一个 AWS 账号的用户临时访问你的资源
- **联合身份**：允许企业 AD 用户通过 SAML 登录 AWS

```
例如：创建一个 EC2-S3-ReadOnly 角色
→ 受信实体：EC2 服务
→ 附加策略：AmazonS3ReadOnlyAccess
→ 任何附加了此角色的 EC2 实例都可以读取 S3 数据
```

### 4. Policy（策略）

Policy 是一个 JSON 文档，精确定义了允许或拒绝的操作。策略可以附加到 User、Group 或 Role 上。

一个典型的 Policy 文档结构：

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::my-bucket",
        "arn:aws:s3:::my-bucket/*"
      ]
    }
  ]
}
```

关键字段说明：

| 字段 | 含义 |
|------|------|
| `Effect` | Allow 或 Deny |
| `Action` | 允许/拒绝的具体 API 操作 |
| `Resource` | 策略适用的 AWS 资源 ARN |
| `Condition` | 可选，限制策略生效的条件（如 IP 范围、时间等） |

## IAM 最佳实践

在实际项目和考试中，以下最佳实践都是高频考点：

1. **永远不要使用 Root 账号进行日常操作**：Root 账号是创建 AWS 账号时的初始账号，拥有不可限制的完整权限
2. **为 Root 账号启用 MFA（多因素认证）**：即使密码泄露，攻击者也无法登录
3. **遵循最小权限原则（Least Privilege）**：只赋予完成任务所需的最小权限
4. **使用 Group 管理权限**：避免直接为单个 User 附加策略
5. **定期轮换凭证**：Access Key 应定期更换
6. **使用 Role 而非 Access Key**：在 AWS 资源之间交互时，优先使用 Role

## IAM 权限评估逻辑

当一个请求到达 AWS 时，IAM 按以下逻辑评估权限：

1. 默认所有请求被**隐式拒绝**（Implicit Deny）
2. 检查所有适用的策略，如果有 **Allow**，则进入下一步
3. 如果有任何 **Explicit Deny**，则最终拒绝（Deny 始终优先于 Allow）

简单记忆：**Deny > Allow > Default Deny**

## 考试要点总结

- IAM 是**全局服务**，不关联任何特定 Region
- Root 账号不应用于日常操作，务必开启 MFA
- Access Key Secret 仅在创建时可见，丢失只能重新生成
- Policy 是 JSON 格式，可附加到 User、Group、Role
- Role 用于 AWS 资源间授权，优先于硬编码凭证
- 权限评估遵循 Explicit Deny > Allow > Implicit Deny

掌握 IAM 不仅是通过认证考试的关键，更是在实际 AWS 项目中构建安全架构的基础。建议在理解概念后，亲自在 AWS 控制台动手操作，加深理解。
