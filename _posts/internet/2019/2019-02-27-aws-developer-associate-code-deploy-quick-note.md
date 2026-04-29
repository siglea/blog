---
layout: post
title:  "AWS CodeDeploy 部署服务核心概念与实践指南"
date:   2019-02-27 19:00:00 +0900
comments: true
tags:
- AWS
- 云服务
categories:
- 技术
---

AWS CodeDeploy 是亚马逊云服务提供的一项全托管部署服务，能够自动将应用程序部署到 EC2 实例、本地服务器（On-Premises）以及 Lambda 函数。它是 AWS CI/CD 工具链中的重要一环，可以与 Jenkins、GitHub Actions 等 CI 工具以及 Ansible、Chef、Puppet 等配置管理工具无缝集成。

本文整理了 CodeDeploy 的核心概念，包括部署流程、部署方式和 AppSpec 配置文件，帮助你快速建立对这项服务的整体认知。

---

## 部署流程概览

CodeDeploy 的部署流程可以用下图概括：

<img src="{{ site.baseurl }}/img/aws-code-deploy/code_deploy.png">

整个流程的核心步骤包括：

1. **打包应用**：将代码和 AppSpec 配置文件一起打包为部署包（Revision）
2. **上传到存储**：将部署包上传到 S3 或 GitHub
3. **创建部署**：通过 AWS 控制台、CLI 或 API 触发部署
4. **CodeDeploy Agent 执行**：目标实例上预装的 Agent 从存储位置拉取部署包，按 AppSpec 文件定义的生命周期钩子（Hooks）依次执行部署动作

---

## 部署方式

CodeDeploy 支持两种主要的部署方式，适用于不同的业务场景和风险偏好。

### 1. In-Place 部署（就地部署）

也被称为 **Rolling Update（滚动更新）**，是最直接的部署方式。

**工作原理**：
- 逐批停止实例上正在运行的应用，部署新版本后重新启动
- 部署期间被更新的实例暂时不可用，请求由其他实例处理（整体容量会暂时减小）
- 部署完成后实例重新加入负载均衡

**适用范围**：
- EC2 实例、On-Premises 服务器
- **不支持** Lambda 函数

**回滚策略**：
- 需要重新部署上一个版本（即再次执行一次完整的部署流程）
- 无法做到即时回滚

**适用场景**：对可用性要求不是极端苛刻的内部系统、测试环境，或者实例数量较多、滚动更新影响面可控的场景。

### 2. Blue/Green 部署（蓝绿部署）

蓝绿部署是一种零停机的部署策略，通过准备一套全新的环境来避免部署过程中的服务中断。

**工作原理**：
- 在新的实例集合（Green 环境）上部署新版本
- 部署验证通过后，将流量从旧环境（Blue）切换到新环境（Green）
- Blue 环境保留一段时间，便于快速回滚

**命名约定**：
- **Blue**：当前正在运行的活跃部署环境
- **Green**：即将上线的新版本环境

**适用范围**：
- EC2 实例、On-Premises 服务器
- Lambda 函数（通过流量权重切换实现）

**优势**：
- 零停机部署
- 回滚极快，只需将流量切回 Blue 环境
- Green 环境可以在切换前进行充分的验收测试

---

## AppSpec 文件配置

AppSpec（Application Specification）文件是 CodeDeploy 的核心配置文件，定义了部署的具体行为。不同的部署目标对应不同的配置结构。

### Lambda 部署的 AppSpec 配置

```yaml
version: 0.0
resources:
  - myLambdaFunction:
      Type: AWS::Lambda::Function
      Properties:
        Name: "myFunction"
        Alias: "myAlias"
        CurrentVersion: "1"
        TargetVersion: "2"
hooks:
  - BeforeAllowTraffic: "LambdaFunctionToValidateBeforeTrafficShift"
  - AfterAllowTraffic: "LambdaFunctionToValidateAfterTrafficShift"
```

主要配置项：

| 字段 | 说明 |
|------|------|
| **version** | AppSpec 文件版本 |
| **resources** | Lambda 函数的名称和属性 |
| **hooks** | 指定在流量切换前后执行的验证函数 |

Lambda 部署的 Hooks 只有两个时机：
- **BeforeAllowTraffic**：流量切换前执行，用于预热或前置验证
- **AfterAllowTraffic**：流量切换后执行，用于后置验证

### EC2 / On-Premises 部署的 AppSpec 配置

```yaml
version: 0.0
os: linux
files:
  - source: /index.html
    destination: /var/www/html/
hooks:
  ApplicationStop:
    - location: scripts/stop_server.sh
      timeout: 300
  BeforeInstall:
    - location: scripts/before_install.sh
  AfterInstall:
    - location: scripts/after_install.sh
  ApplicationStart:
    - location: scripts/start_server.sh
  ValidateService:
    - location: scripts/validate.sh
      timeout: 300
```

主要配置项：

| 字段 | 说明 |
|------|------|
| **version** | AppSpec 文件版本 |
| **os** | 操作系统类型（linux / windows） |
| **files** | 源文件和目标路径的映射 |
| **hooks** | 各生命周期阶段执行的脚本 |

EC2 / On-Premises 部署的生命周期 Hooks 更加丰富，完整的执行顺序如下：

| 阶段 | 说明 |
|------|------|
| **ApplicationStop** | 优雅停止当前版本的应用 |
| **DownloadBundle** | CodeDeploy Agent 将部署包下载到临时目录（系统自动执行） |
| **BeforeInstall** | 安装前的准备工作，如备份当前版本、解密文件等 |
| **Install** | 将文件从临时目录复制到目标位置（系统自动执行） |
| **AfterInstall** | 安装后的配置工作，如修改文件权限、更新配置文件等 |
| **ApplicationStart** | 启动新版本的应用 |
| **ValidateService** | 执行验证测试，确认部署成功 |
| **BeforeBlockTraffic** | 从负载均衡器注销实例前的准备工作 |
| **BlockTraffic** | 将实例从负载均衡器中注销（系统自动执行） |
| **AfterBlockTraffic** | 实例从负载均衡器注销后的清理工作 |

需要注意的是，`DownloadBundle`、`Install`、`BlockTraffic` 这三个阶段由 CodeDeploy Agent 自动执行，不支持自定义脚本。

---

## 实践建议

1. **AppSpec 文件必须放在部署包的根目录**，文件名为 `appspec.yml`
2. **优先选择 Blue/Green 部署**用于生产环境，In-Place 部署更适合开发测试环境
3. **在 ValidateService 阶段编写充分的健康检查脚本**，确保部署后服务真正可用
4. **配合 CloudWatch 告警和 Auto Scaling**，在部署异常时自动触发回滚
5. **合理设置 Hooks 的 timeout**，避免脚本执行超时导致部署失败

---

## 总结

AWS CodeDeploy 通过标准化的部署流程和灵活的 AppSpec 配置，降低了应用部署的复杂度和风险。In-Place 部署适合快速迭代的场景，Blue/Green 部署则提供了更高的安全性和可回滚性。理解 AppSpec 文件的生命周期 Hooks 是用好 CodeDeploy 的关键——它们定义了部署过程中每个阶段的行为，是实现自动化部署的基础。
