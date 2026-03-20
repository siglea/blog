---
layout: post
title:  "Jekyll 静态博客搭建指南：从零开始打造个人技术博客"
date:   2019-05-14 17:46:56 +0800
tags: 
- 工具
categories:
- 技术
---

对于技术人来说，拥有一个个人博客是梳理知识、建立影响力的有效途径。相比 WordPress 等动态博客系统，Jekyll 以其简洁、免费托管（GitHub Pages）和对 Markdown 的原生支持，成为了程序员群体中最受欢迎的静态博客方案之一。

### 为什么选择 Jekyll

| 特性 | 说明 |
|------|------|
| 静态网站 | 无需数据库和服务器端语言，纯 HTML/CSS/JS |
| Markdown 写作 | 用 Markdown 专注内容，不用操心排版 |
| GitHub Pages 免费托管 | 推送到 GitHub 即自动部署，零运维成本 |
| 丰富的主题生态 | 大量开源主题可选，也可以完全自定义 |
| Liquid 模板引擎 | 灵活的模板语法，支持变量、循环、条件判断 |
| SEO 友好 | 生成纯静态页面，加载快，搜索引擎友好 |

### 环境准备

Jekyll 基于 Ruby 构建，安装前需要准备 Ruby 环境：

```bash
# macOS（使用 Homebrew）
brew install ruby
gem install bundler jekyll

# Ubuntu / Debian
sudo apt-get install ruby-full build-essential
gem install bundler jekyll

# 验证安装
jekyll -v
```

### 快速开始

#### 创建新站点

```bash
# 创建新的 Jekyll 项目
jekyll new my-blog

# 进入项目目录
cd my-blog

# 启动本地开发服务器
bundle exec jekyll serve
```

执行 `jekyll serve` 后，访问 `http://localhost:4000` 即可看到博客。Jekyll 会监听文件变化并自动重新生成站点，修改后刷新浏览器即可看到效果。

#### 项目结构

```
my-blog/
├── _config.yml          # 站点配置文件
├── _posts/              # 博客文章目录
│   └── 2019-05-14-welcome.md
├── _layouts/            # 页面布局模板
│   ├── default.html
│   └── post.html
├── _includes/           # 可复用的页面片段
│   ├── header.html
│   └── footer.html
├── _sass/               # Sass 样式文件
├── assets/              # 静态资源（图片、CSS、JS）
├── _site/               # 生成的静态站点（不要手动修改）
├── Gemfile              # Ruby 依赖管理
└── index.html           # 首页
```

### 撰写文章

#### 文件命名规范

文章放在 `_posts` 目录下，文件名必须遵循以下格式：

```
YYYY-MM-DD-title.md
```

例如：`2019-05-14-welcome-to-jekyll.md`

#### Front Matter（前置元数据）

每篇文章开头需要用 YAML 格式声明元数据：

```yaml
---
layout: post
title:  "文章标题"
date:   2019-05-14 17:46:56 +0800
tags:
- Ruby
- Jekyll
categories:
- 技术
---
```

| 字段 | 说明 |
|------|------|
| layout | 使用的布局模板，通常为 `post` |
| title | 文章标题 |
| date | 发布日期和时区 |
| tags | 标签列表，用于分类检索 |
| categories | 分类，会影响生成的 URL 路径 |

#### Markdown 写作

Front Matter 之后就是正文，使用标准 Markdown 语法。Jekyll 默认使用 kramdown 作为 Markdown 解析器，支持表格、脚注、代码高亮等扩展语法。

### 代码高亮

Jekyll 内置了对代码片段的强力支持。可以使用 Liquid 标签或标准 Markdown 语法：

**方式一：Liquid 标签**

{% highlight ruby %}
def print_hi(name)
  puts "Hi, #{name}"
end
print_hi('Tom')
#=> prints 'Hi, Tom' to STDOUT.
{% endhighlight %}

**方式二：Markdown 围栏代码块**

````markdown
```ruby
def print_hi(name)
  puts "Hi, #{name}"
end
```
````

两种方式效果相同，推荐使用 Markdown 围栏代码块，更简洁通用。

### 站点配置（_config.yml）

`_config.yml` 是 Jekyll 的核心配置文件：

```yaml
title: My Tech Blog
description: 分享技术，记录成长
url: "https://username.github.io"
baseurl: ""

# 构建设置
markdown: kramdown
permalink: /:categories/:year/:month/:day/:title.html

# 分页
paginate: 10
paginate_path: "/page:num/"

# 排除不需要生成的文件
exclude:
  - Gemfile
  - Gemfile.lock
  - node_modules
  - README.md
```

注意：修改 `_config.yml` 后需要重启 `jekyll serve` 才能生效，不会自动重新加载。

### 部署到 GitHub Pages

GitHub Pages 原生支持 Jekyll，部署流程极为简单：

```bash
# 1. 在 GitHub 创建仓库：username.github.io

# 2. 初始化 Git 并推送
cd my-blog
git init
git add .
git commit -m "Initial blog setup"
git remote add origin https://github.com/username/username.github.io.git
git push -u origin master

# 3. 访问 https://username.github.io 查看博客
```

如果使用项目仓库（非 `username.github.io`），需要在仓库 Settings → Pages 中配置发布分支。

### 常用技巧

#### 草稿功能

将未完成的文章放在 `_drafts` 目录下（无需日期前缀），本地预览时加 `--drafts` 参数：

```bash
bundle exec jekyll serve --drafts
```

#### 自定义域名

在仓库根目录创建 `CNAME` 文件，写入自定义域名：

```
blog.example.com
```

然后在域名 DNS 中添加 CNAME 记录指向 `username.github.io`。

#### 评论系统

Jekyll 是静态站点，不自带评论功能。常见的第三方评论方案：

- **Disqus**：国际主流，但国内访问较慢
- **Gitalk**：基于 GitHub Issues，适合技术博客
- **Utterances**：同样基于 GitHub Issues，更轻量
- **Valine**：基于 LeanCloud，无需登录即可评论

#### 搜索功能

可以使用 `jekyll-search` 插件或基于 `lunr.js` 实现客户端全文搜索，无需后端支持。

### 常见问题

| 问题 | 解决方案 |
|------|----------|
| 中文文件名导致构建失败 | 避免使用中文文件名，用拼音或英文替代 |
| 本地预览正常但 GitHub Pages 报错 | 检查是否使用了 GitHub Pages 不支持的插件 |
| 样式错乱 | 检查 `_config.yml` 中的 `baseurl` 配置 |
| 文章不显示 | 确认文件名日期格式正确且日期不是未来日期 |
| 构建缓慢 | 使用 `--incremental` 参数开启增量构建 |

### 推荐资源

- [Jekyll 官方文档](https://jekyllrb.com/docs/home)
- [Jekyll GitHub 仓库](https://github.com/jekyll/jekyll)
- [Jekyll Talk 社区](https://talk.jekyllrb.com/)
- [Jekyll Themes](http://jekyllthemes.org/) - 免费主题集合

### 总结

Jekyll 是一个"刚刚好"的博客方案——足够简单让你专注于写作，又足够灵活支持各种自定义需求。配合 GitHub Pages 的免费托管，你可以零成本拥有一个专业的技术博客。如果你一直在犹豫要不要开始写博客，不妨就从 `jekyll new` 开始吧。
