---
layout: default
title: 关于我
---

<div class="about-container" style="max-width: 900px; margin: 0 auto; padding: 40px 20px;">
  <!-- 个人简介卡片 -->
  <div class="profile-card" style="text-align: center; margin-bottom: 50px;">
    <div class="avatar-wrapper" style="position: relative; display: inline-block; margin-bottom: 25px;">
      <img src="{{ site.baseurl }}/img/me.jpg" alt="{{ site.author }}" 
           style="width: 150px; height: 150px; border-radius: 50%; object-fit: cover; 
                  border: 4px solid var(--primary-color); box-shadow: 0 8px 32px rgba(99, 102, 241, 0.3);">
      <div class="status-badge" style="position: absolute; bottom: 10px; right: 10px; 
                                        width: 20px; height: 20px; background: #10b981; 
                                        border-radius: 50%; border: 3px solid white;"></div>
    </div>
    
    <h1 style="font-size: 2.5rem; margin-bottom: 10px; background: linear-gradient(135deg, var(--primary-color), var(--accent-color)); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
      {{ site.author }}
    </h1>
    <p style="font-size: 1.2rem; color: var(--text-secondary); margin-bottom: 20px;">
      全栈架构师
    </p>
    
    <div class="location" style="color: var(--text-muted); margin-bottom: 25px;">
      <i class="fas fa-map-marker-alt"></i> 北京
    </div>
    
    <div class="social-links" style="display: flex; justify-content: center; gap: 15px;">
      {% if site.github_username %}
      <a href="https://github.com/{{ site.github_username }}" target="_blank" rel="noopener"
         style="width: 45px; height: 45px; border-radius: 50%; background: var(--bg-card); 
                display: flex; align-items: center; justify-content: center; 
                color: var(--text-secondary); text-decoration: none; transition: all 0.3s;
                border: 1px solid var(--border-color);"
         onmouseover="this.style.background='var(--primary-color)';this.style.color='white';this.style.transform='translateY(-3px)'"
         onmouseout="this.style.background='var(--bg-card)';this.style.color='var(--text-secondary)';this.style.transform='translateY(0)'">
        <i class="fab fa-github" style="font-size: 1.2rem;"></i>
      </a>
      {% endif %}
      {% if site.social.linkedin %}
      <a href="https://linkedin.com/in/{{ site.social.linkedin }}" target="_blank" rel="noopener"
         style="width: 45px; height: 45px; border-radius: 50%; background: var(--bg-card); 
                display: flex; align-items: center; justify-content: center; 
                color: var(--text-secondary); text-decoration: none; transition: all 0.3s;
                border: 1px solid var(--border-color);"
         onmouseover="this.style.background='#0077b5';this.style.color='white';this.style.transform='translateY(-3px)'"
         onmouseout="this.style.background='var(--bg-card)';this.style.color='var(--text-secondary)';this.style.transform='translateY(0)'">
        <i class="fab fa-linkedin-in" style="font-size: 1.2rem;"></i>
      </a>
      {% endif %}
      <a href="mailto:{{ site.email }}"
         style="width: 45px; height: 45px; border-radius: 50%; background: var(--bg-card); 
                display: flex; align-items: center; justify-content: center; 
                color: var(--text-secondary); text-decoration: none; transition: all 0.3s;
                border: 1px solid var(--border-color);"
         onmouseover="this.style.background='#ea4335';this.style.color='white';this.style.transform='translateY(-3px)'"
         onmouseout="this.style.background='var(--bg-card)';this.style.color='var(--text-secondary)';this.style.transform='translateY(0)'">
        <i class="fas fa-envelope" style="font-size: 1.2rem;"></i>
      </a>
      <a href="{{ site.baseurl }}/feed.xml" target="_blank"
         style="width: 45px; height: 45px; border-radius: 50%; background: var(--bg-card); 
                display: flex; align-items: center; justify-content: center; 
                color: var(--text-secondary); text-decoration: none; transition: all 0.3s;
                border: 1px solid var(--border-color);"
         onmouseover="this.style.background='#f60';this.style.color='white';this.style.transform='translateY(-3px)'"
         onmouseout="this.style.background='var(--bg-card)';this.style.color='var(--text-secondary)';this.style.transform='translateY(0)'">
        <i class="fas fa-rss" style="font-size: 1.2rem;"></i>
      </a>
    </div>
  </div>

  <!-- 统计数据 -->
  <div class="stats-grid" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 50px;">
    <div class="stat-card" style="text-align: center; padding: 25px; background: var(--bg-card); 
                                  border-radius: 16px; border: 1px solid var(--border-color);">
      <div style="font-size: 2.5rem; font-weight: 700; color: var(--primary-color); margin-bottom: 8px;">
        {{ site.posts | size }}
      </div>
      <div style="color: var(--text-secondary); font-size: 0.9rem;">篇文章</div>
    </div>
    <div class="stat-card" style="text-align: center; padding: 25px; background: var(--bg-card); 
                                  border-radius: 16px; border: 1px solid var(--border-color);">
      <div style="font-size: 2.5rem; font-weight: 700; color: var(--accent-color); margin-bottom: 8px;">
        {{ site.categories | size }}
      </div>
      <div style="color: var(--text-secondary); font-size: 0.9rem;">个分类</div>
    </div>
    <div class="stat-card" style="text-align: center; padding: 25px; background: var(--bg-card); 
                                  border-radius: 16px; border: 1px solid var(--border-color);">
      <div style="font-size: 2.5rem; font-weight: 700; color: #10b981; margin-bottom: 8px;">
        {{ site.tags | size }}
      </div>
      <div style="color: var(--text-secondary); font-size: 0.9rem;">个标签</div>
    </div>
  </div>

  <!-- 个人介绍 -->
  <div class="about-section" style="margin-bottom: 40px;">
    <h2 style="font-size: 1.5rem; margin-bottom: 20px; display: flex; align-items: center; gap: 10px;">
      <i class="fas fa-user-circle" style="color: var(--primary-color);"></i>
      关于我
    </h2>
    <div style="background: var(--bg-card); padding: 25px; border-radius: 12px; border: 1px solid var(--border-color); line-height: 1.8;">
      <p>{{ site.description }}</p>
      <p style="margin-top: 15px;">
        热爱技术，专注于后端架构与系统设计。在这里记录学习心得、技术实践和生活感悟。
        欢迎交流探讨，共同进步！
      </p>
    </div>
  </div>

  <!-- 技能标签 -->
  <div class="skills-section" style="margin-bottom: 40px;">
    <h2 style="font-size: 1.5rem; margin-bottom: 20px; display: flex; align-items: center; gap: 10px;">
      <i class="fas fa-code" style="color: var(--primary-color);"></i>
      技术领域
    </h2>
    <div class="skills-cloud" style="display: flex; flex-wrap: wrap; gap: 10px;">
      {% assign skills = "Java,Spring,微服务,分布式系统,高并发,架构设计,DevOps,容器化,数据库,缓存,消息队列,Linux,云原生" | split: "," %}
      {% for skill in skills %}
      <span style="padding: 8px 16px; background: linear-gradient(135deg, var(--primary-color), var(--accent-color)); 
                   color: white; border-radius: 20px; font-size: 0.9rem;">
        {{ skill }}
      </span>
      {% endfor %}
    </div>
  </div>

  <!-- 联系方式 -->
  <div class="contact-section">
    <h2 style="font-size: 1.5rem; margin-bottom: 20px; display: flex; align-items: center; gap: 10px;">
      <i class="fas fa-envelope" style="color: var(--primary-color);"></i>
      联系我
    </h2>
    <div style="background: var(--bg-card); padding: 25px; border-radius: 12px; border: 1px solid var(--border-color);">
      <p style="margin-bottom: 15px;">
        <i class="fas fa-envelope" style="color: var(--primary-color); width: 20px;"></i>
        邮箱: <a href="mailto:{{ site.email }}" style="color: var(--primary-color); text-decoration: none;">{{ site.email }}</a>
      </p>
      <p style="margin-bottom: 15px;">
        <i class="fab fa-github" style="color: var(--primary-color); width: 20px;"></i>
        GitHub: <a href="https://github.com/{{ site.github_username }}" target="_blank" rel="noopener" 
                   style="color: var(--primary-color); text-decoration: none;">@{{ site.github_username }}</a>
      </p>
      <p>
        <i class="fas fa-rss" style="color: var(--primary-color); width: 20px;"></i>
        RSS订阅: <a href="{{ site.baseurl }}/feed.xml" target="_blank" 
                   style="color: var(--primary-color); text-decoration: none;">{{ site.url }}{{ site.baseurl }}/feed.xml</a>
      </p>
    </div>
  </div>
</div>

<style>
:root {
  --primary-color: #6366f1;
  --accent-color: #8b5cf6;
  --bg-card: #f8fafc;
  --border-color: #e2e8f0;
  --text-secondary: #64748b;
  --text-muted: #94a3b8;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr !important;
  }
  
  .about-container {
    padding: 20px 15px !important;
  }
}
</style>
