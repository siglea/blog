# encoding: utf-8
# frozen_string_literal: true

require 'cgi'
require 'json'
require 'kramdown'
require 'kramdown-parser-gfm'

ROOT = File.expand_path('..', __dir__)
md_path = File.join(ROOT, '_posts/tech/2026-03-24-black-apple-open-core.md')
raw = File.read(md_path, encoding: 'UTF-8')
raw = raw.sub(/\A---\r?\n.*?\r?\n---\r?\n/m, '')
body_md = raw.gsub('{{ site.baseurl }}', '/blog')
body = Kramdown::Document.new(body_md, input: 'GFM').to_html

title = '用OpenCore安装黑苹果万能步骤'
plain = body.gsub(/<[^>]+>/, ' ').gsub(/\s+/, ' ').strip
desc_short = plain[0, 280]
meta_desc = CGI.escapeHTML(desc_short[0, 160])
pub = '2026-03-24T23:02:56+08:00'
date_zh = '2026年03月24日'
rel_enc = '%E6%8A%80%E6%9C%AF/2026/03/24/black-apple-open-core.html'
canon = "https://siglea.github.io/blog/#{rel_enc}"

ld = {
  '@context' => 'https://schema.org',
  '@type' => 'BlogPosting',
  'author' => { '@type' => 'Person', 'name' => 'siglea' },
  'dateModified' => pub,
  'datePublished' => pub,
  'description' => desc_short,
  'headline' => title,
  'mainEntityOfPage' => { '@type' => 'WebPage', '@id' => canon },
  'publisher' => {
    '@type' => 'Organization',
    'name' => 'siglea',
    'logo' => { '@type' => 'ImageObject', 'url' => 'https://siglea.github.io/blog/assets/images/logo.png' }
  },
  'url' => canon
}
ld_json = JSON.generate(ld)

html = <<~HTML
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>#{CGI.escapeHTML(title)} - Code & Coffee</title>
  <meta name="description" content="#{meta_desc}">
  <link rel="stylesheet" href="/blog/css/main.css">
  <link rel="alternate" type="application/rss+xml" title="Code & Coffee" href="/blog/feed.xml">
  <!-- Begin Jekyll SEO tag v2.8.0 -->
<title>#{CGI.escapeHTML(title)} | Code &amp; Coffee</title>
<meta name="generator" content="Jekyll v4.4.1" />
<meta property="og:title" content="#{CGI.escapeHTML(title)}" />
<meta name="author" content="siglea" />
<meta property="og:locale" content="en_US" />
<meta name="description" content="#{meta_desc}" />
<meta property="og:description" content="#{meta_desc}" />
<link rel="canonical" href="#{canon}" />
<meta property="og:url" content="#{canon}" />
<meta property="og:site_name" content="Code &amp; Coffee" />
<meta property="og:type" content="article" />
<meta property="article:published_time" content="#{pub}" />
<meta name="twitter:card" content="summary" />
<meta property="twitter:title" content="#{CGI.escapeHTML(title)}" />
<script type="application/ld+json">
#{ld_json}
</script>
<!-- End Jekyll SEO tag -->

</head>
<body class="one-column">

  <div id="container">

    <div id="header">
      <div id="header-left">
        <span id="header-name"><a href="/blog/">Code & Coffee</a></span>
        <span class="header-nav">
          &raquo; <a href="/blog/">首页</a>
          &raquo; <a href="/blog/archive/">档案</a>
        </span>
      </div>

      <div id="header-right">
        <div id="google_search">
          <form action="https://www.google.com/search" target="_blank" method="get">
            <input type="text" name="q" class="searchbox" placeholder="Google..." />
            <input type="hidden" name="sitesearch" value="https://siglea.github.io/blog" />
            <input type="submit" class="searchbox_submit" value="&#x1F50D;" />
          </form>
        </div>

        <div id="feed_icon">
          <a href="/blog/feed.xml" title="RSS Feed">
            <img src="https://cdn.beekka.com/blogimg/asset/202107/bg2021072117.png" alt="RSS" style="height:18px;width:auto;border:none;" />
          </a>
        </div>
      </div>
    </div>

    <div id="content">

      <div id="alpha">
        <div id="alpha-inner">
          <div class="entry-asset asset hentry">

  <div class="asset-nav">
    <div class="entry-categories">
      分类<span class="delimiter">：</span>
      <a href="/blog/category/技术/" rel="tag">技术</a>
    </div>
    <div class="entry-location">
      <span class="nav-prev"><a href="/blog/%E6%8A%80%E6%9C%AF/2020/07/28/DotDot3.html">&laquo; Redis 并发竞争、MongoDB 架构对比...</a></span>
    </div>
  </div>

  <div class="asset-header">
    <h1 class="asset-name entry-title">#{CGI.escapeHTML(title)}</h1>
  </div>

  <div class="asset-meta">
    <p>
      日期：
      <a href="/blog/archive/">
        <abbr class="published" title="#{pub}">
          #{date_zh}
        </abbr>
      </a>
    </p>
  </div>

  <div class="asset-content entry-content">
    <div class="asset-body">
#{body}
    </div>
  </div>

  <div class="asset-footer">
    <h3>文档信息</h3>
    <ul>
      <li>发表日期：#{date_zh}</li>
      <li>版权声明：自由转载-非商用-非衍生-保持署名</li>
    </ul>
  </div>

</div>

        </div>
      </div>

    </div>

    <div id="footer">
      <div id="footer-content">
        <section>
          <h2>关于</h2>
          <p>探索技术深度，分享架构智慧。从后端架构到前端设计，从系统设计到产品思维， 在代码与咖啡的交织中，记录技术人的成长之旅。</p>
          <p>
            文章：<a href="/blog/archive/">78</a>
            &middot;
            <a href="/blog/feed.xml">RSS</a>
          </p>
        </section>

        <section>
          <h2>联系</h2>
          <p>
            <a href="https://github.com/siglea">GitHub</a>
            &middot; <a href="mailto:siglea@sina.com">Email</a>
          </p>
        </section>

        <section>
          <h2>版权</h2>
          <p>&copy; 2026 Code & Coffee</p>
          <p>自由转载-非商用-非衍生-保持署名</p>
        </section>
      </div>
    </div>

  </div>

  <script>
  if (/mobile/i.test(navigator.userAgent) || /android/i.test(navigator.userAgent))
    document.body.classList.add('mobile');
  </script>
</body>
</html>
HTML

out = File.join(ROOT, 'docs/技术/2026/03/24/black-apple-open-core.html')
File.write(out, html, encoding: 'UTF-8')
puts "Wrote #{out}"
