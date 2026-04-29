---
layout: post
title:  "Rails 应用集成 Mailgun 邮件服务：从配置到踩坑全记录"
date:   2017-03-29 20:15:09 +0800
comments: true
tags:
- Ruby
- Rails
categories:
- 技术
---

在 Web 应用开发中，发送邮件是一个基础但不可或缺的功能——用户注册激活、密码重置、通知推送都离不开它。对于中小项目来说，自建邮件服务器成本高且维护复杂，使用第三方邮件服务是更务实的选择。本文记录了在 Rails 5 API 应用中集成 Mailgun 邮件服务的完整过程，包括配置步骤和实际遇到的坑。

## 为什么选择 Mailgun

在 SendGrid、Amazon SES、Mailgun 等主流邮件服务中，Mailgun 有几个优势：

- **Heroku 免费插件**：在 Heroku 上可以直接添加 Mailgun add-on，无需额外注册
- **免费额度**：每小时 100 封邮件的免费额度，对开发和小项目足够
- **API 和 SMTP 双模式**：既可以通过 RESTful API 发送，也支持传统 SMTP 协议
- **文档完善**：官方文档质量较高，各语言 SDK 齐全

## 配置步骤

### 第一步：创建 Mailgun 账号

注册 Mailgun 账号后，有一个容易忽略的关键点：**必须绑定信用卡**。否则你只能向"已授权收件人"发送邮件（即测试模式），无法向真实用户发送。

### 第二步：验证发送域名

Mailgun 默认提供一个沙箱域名（`sandbox*.mailgun.org`），建议先用它来测试流程是否跑通。

**使用沙箱域名测试的意义**：排除域名 DNS 配置问题的干扰，确认 Mailgun 本身能正常工作，以及目标邮箱是否会拦截 Mailgun 的邮件。

确认沙箱域名可用后，配置自定义域名：

1. 在 Mailgun 控制台添加你的域名
2. 到域名服务商（如 Namecheap、Cloudflare）配置 DNS 记录：
   - **TXT 记录**：SPF 和 DKIM 验证，证明你有权从该域名发送邮件
   - **MX 记录**：如果需要接收邮件
   - **CNAME 记录**：用于邮件追踪
3. 等待 Mailgun 验证（通常几分钟到几小时不等）

### 第三步：配置 Rails Action Mailer

在 Rails 中，邮件发送通过 Action Mailer 处理。以 SMTP 方式为例，在对应环境配置文件中添加：

**开发环境** `config/environments/development.rb`：

```ruby
config.action_mailer.delivery_method = :smtp
config.action_mailer.smtp_settings = {
  address:              'smtp.mailgun.org',
  port:                 587,
  domain:               'mydomain.club',
  user_name:            'postmaster@mydomain.club',
  password:             ENV['MAILGUN_SMTP_PASSWORD'],
  authentication:       'plain',
  enable_starttls_auto: true
}
```

几个注意事项：

- **密码不要硬编码**：使用环境变量（`ENV['MAILGUN_SMTP_PASSWORD']`）存储敏感信息
- **端口选择**：587 是推荐端口（STARTTLS），也可以使用 465（SSL）
- **domain**：填写你在 Mailgun 验证过的域名

**生产环境** `config/environments/production.rb` 使用相同配置，只需确保环境变量在服务器上正确设置。

### 第四步：创建 Mailer

```ruby
class UserMailer < ApplicationMailer
  def activation_email(user)
    @user = user
    @activation_url = "https://mydomain.club/activate?token=#{user.activation_token}"
    mail(to: @user.email, subject: '请激活您的账号')
  end
end
```

在用户注册后调用：

```ruby
UserMailer.activation_email(@user).deliver_later
```

使用 `deliver_later` 而非 `deliver_now`，将邮件发送任务放入后台队列（如 Sidekiq），避免阻塞请求。

## 踩坑记录

### 坑 1：ISP/ESP 拦截

这是最耗时的问题。在测试过程中，邮件发送日志显示 Mailgun 已接受（Accepted），但收件人始终收不到。一分钟后 Mailgun 日志中出现 **ESP throttling** 警告。

**原因**：某些邮件服务商（如 QQ 邮箱）会拦截来自 Mailgun 等第三方邮件平台的流量，将其识别为潜在垃圾邮件。

**解决方案**：
- 换用 Gmail、Outlook 等对第三方邮件服务更友好的邮箱测试
- 确保 SPF 和 DKIM DNS 记录配置正确
- 对于必须发送到 QQ 邮箱的场景，可能需要额外的邮件中转服务

### 坑 2：沙箱域名的收件人限制

使用沙箱域名时，只能向在 Mailgun 控制台中"Authorized Recipients"列表中的邮箱发送。这不是 bug，而是 Mailgun 防止滥用的机制。

### 坑 3：DNS 验证延迟

配置 DNS 记录后，Mailgun 验证可能不会立即通过。Namecheap 的 DNS 传播可能需要 5-30 分钟，某些情况下更久。耐心等待即可。

## SMTP vs API 模式对比

Mailgun 支持两种发送方式，选择取决于你的需求：

| 特性 | SMTP | API |
|------|------|-----|
| 集成难度 | 低（Rails 内置 SMTP 支持） | 需要安装 SDK 或手写 HTTP 请求 |
| 性能 | 较低（需要建立 SMTP 连接） | 较高（HTTP 请求更轻量） |
| 灵活性 | 受限于 SMTP 协议 | 支持模板、批量发送、标签等高级功能 |
| 适用场景 | 小规模、快速集成 | 大规模、需要高级功能 |

对于生产环境的大规模发送，推荐使用 API 模式配合 `mailgun-ruby` gem。

## 总结

在 Rails 应用中集成 Mailgun 的核心步骤：

1. 注册账号并绑定信用卡
2. 先用沙箱域名验证流程，再配置自定义域名
3. 配置 DNS（SPF、DKIM）并等待验证
4. 在 Rails 中配置 Action Mailer 的 SMTP 设置
5. 使用 `deliver_later` 异步发送邮件

最大的坑在于邮件可达性——ISP 拦截、DNS 配置不当、发件人信誉度不足都可能导致邮件无法送达。建议开发阶段使用 `letter_opener` gem 在浏览器中预览邮件，确认内容无误后再进行实际发送测试。
