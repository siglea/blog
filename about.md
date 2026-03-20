---
layout: default
title: 关于我
---

<div class="entry-asset asset hentry">
  <div class="asset-header">
    <h2 class="asset-name entry-title">关于我</h2>
  </div>
  <div class="asset-content entry-content">
    <div class="asset-body">
      <p>{{ site.description }}</p>
      <p>热爱技术，专注于后端架构与系统设计。在这里记录学习心得、技术实践和生活感悟。欢迎交流探讨，共同进步！</p>
      
      <h3>博客统计</h3>
      <ul>
        <li>文章数量：{{ site.posts | size }} 篇</li>
        <li>分类数量：{{ site.categories | size }} 个</li>
        <li>标签数量：{{ site.tags | size }} 个</li>
      </ul>
      
      <h3>技术领域</h3>
      <p>Java、Spring、微服务、分布式系统、高并发、架构设计、DevOps、容器化、数据库、缓存、消息队列、Linux、云原生</p>
      
      <h3>联系方式</h3>
      <ul>
        <li>邮箱：<a href="mailto:{{ site.email }}">{{ site.email }}</a></li>
        {% if site.github_username %}
        <li>GitHub：<a href="https://github.com/{{ site.github_username }}" target="_blank" rel="noopener">@{{ site.github_username }}</a></li>
        {% endif %}
        <li>RSS订阅：<a href="{{ site.baseurl }}/feed.xml" target="_blank">{{ site.url }}{{ site.baseurl }}/feed.xml</a></li>
      </ul>
    </div>
  </div>
</div>
