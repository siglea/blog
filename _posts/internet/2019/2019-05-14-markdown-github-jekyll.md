---
layout: post
title:  "从零搭建个人技术博客：Jekyll + GitHub Pages + Markdown 完全指南"
date:   2019-05-27 19:00:00 +0900
comments: true
tags:
- 工具
categories:
- 技术
---

如果你是一名技术人员，拥有一个自己的技术博客几乎是标配。相比 WordPress 等动态博客系统，Jekyll + GitHub Pages 的组合以其轻量、免费、版本控制友好等特性，成为了技术圈最受欢迎的博客方案之一。本文将带你从环境搭建到日常写作，完整走通这条路径。

## 为什么选择 Jekyll + GitHub Pages

在众多静态网站生成器（Hugo、Hexo、Gatsby 等）中，Jekyll 有几个独特优势：

- **GitHub 原生支持**：GitHub Pages 内置 Jekyll 构建，推送 Markdown 文件即可自动部署，无需额外 CI/CD 配置
- **Ruby 生态成熟**：丰富的插件体系，主题选择多样
- **Markdown 原生**：所有文章用 Markdown 编写，专注内容而非排版
- **免费托管**：GitHub Pages 提供免费的 HTTPS 域名和托管服务

## Jekyll 安装与环境配置

### 前置条件

Jekyll 基于 Ruby，因此需要先安装 Ruby 运行环境。推荐使用 rbenv 来管理 Ruby 版本，避免系统 Ruby 版本冲突。

macOS 用户可以通过 Homebrew 安装：

```shell
brew install rbenv ruby-build
rbenv install 3.1.0
rbenv global 3.1.0
```

### 安装 Jekyll 及常用插件

环境就绪后，通过 gem 安装 Jekyll 及博客常用插件：

```shell
gem install jekyll
gem install jekyll-archives
gem install jekyll-paginate
gem install jekyll-sitemap
gem install jekyll-seo
```

各插件的作用：

| 插件 | 功能 |
|------|------|
| `jekyll-archives` | 按日期、标签、分类自动生成归档页面 |
| `jekyll-paginate` | 文章列表分页 |
| `jekyll-sitemap` | 自动生成 `sitemap.xml`，利于搜索引擎收录 |
| `jekyll-seo` | 自动注入 SEO 相关的 meta 标签 |

也可以在项目根目录创建 `Gemfile`，统一管理依赖：

```ruby
source "https://rubygems.org"

gem "jekyll", "~> 4.3"
gem "jekyll-archives"
gem "jekyll-paginate"
gem "jekyll-sitemap"
gem "jekyll-seo-tag"
```

然后执行 `bundle install` 一次性安装。

## Jekyll 常用命令

日常开发中，最常用的两个命令：

```shell
jekyll s    # 编译并启动本地开发服务器，默认 http://localhost:4000
jekyll b    # 仅编译，输出到 _site 目录
```

`jekyll s` 支持实时监听文件变化并自动重新编译（`_config.yml` 修改除外，需要重启）。开发时推荐加上 `--drafts` 参数来预览草稿：

```shell
jekyll s --drafts
```

### rbenv 环境管理

如果项目需要特定 Ruby 版本，可以使用 rbenv 的本地版本管理：

```shell
rbenv local          # 查看当前目录的 Ruby 版本
rbenv local 3.1.0    # 设置当前目录使用 3.1.0 版本
rbenv versions       # 查看所有已安装的 Ruby 版本
```

## Jekyll 项目结构概览

一个典型的 Jekyll 博客项目结构如下：

```
myblog/
├── _config.yml      # 站点配置文件
├── _posts/          # 博客文章目录
│   └── 2019-05-27-my-first-post.md
├── _drafts/         # 草稿目录
├── _layouts/        # 页面布局模板
├── _includes/       # 可复用的页面片段
├── _sass/           # Sass 样式源文件
├── assets/          # 静态资源（图片、CSS、JS）
├── index.html       # 首页
└── Gemfile          # Ruby 依赖管理
```

文章文件名必须遵循 `YYYY-MM-DD-title.md` 格式，Jekyll 通过文件名解析日期和 URL。

## Markdown 写作基础

Jekyll 文章使用 Markdown 语法编写。每篇文章开头需要包含 YAML Front Matter：

```markdown
---
layout: post
title: "文章标题"
date: 2019-05-27 19:00:00 +0900
tags:
- 标签1
- 标签2
categories:
- 分类
---

正文内容从这里开始...
```

### 常用 Markdown 语法速查

| 语法 | 效果 |
|------|------|
| `# 标题` | 一级标题 |
| `**粗体**` | **粗体** |
| `` `代码` `` | `行内代码` |
| `[链接](url)` | 超链接 |
| `![图片](url)` | 图片 |
| `> 引用` | 引用块 |

代码块使用三个反引号包裹，并指定语言以获得语法高亮：

````markdown
```python
print("Hello Jekyll!")
```
````

更完整的 Markdown 语法参考：
- [Markdown 官方教程](https://www.markdownguide.org/)
- [菜鸟教程 - Markdown](https://www.runoob.com/markdown/md-lists.html)

## 部署到 GitHub Pages

1. 在 GitHub 创建名为 `username.github.io` 的仓库
2. 将 Jekyll 项目推送到该仓库的 `main` 分支
3. 在仓库 Settings → Pages 中确认构建源为正确的分支
4. 访问 `https://username.github.io` 即可看到博客

如果需要自定义域名，在项目根目录添加 `CNAME` 文件，写入你的域名，然后在域名服务商配置 DNS 解析指向 GitHub Pages 的 IP。

## 总结

Jekyll + GitHub Pages + Markdown 的组合为技术人员提供了一套高效、免费、可控的博客方案。虽然初始配置需要一点时间，但一旦搭建完成，写作体验非常流畅——你只需要专注于 Markdown 内容，其余交给工具链处理。如果你还没有自己的技术博客，不妨从今天开始。

[jekyll-website]: https://jekyllrb.com
[jekyll-gh]:    https://github.com/jekyll/jekyll
[github-website]: https://github.com/
