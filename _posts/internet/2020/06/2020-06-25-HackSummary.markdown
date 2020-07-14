---
layout: post
title:  "各种攻击"
date:   2020-06-07 14:25:00 +0900
comments: true
tags:
- 网络
- 安全
categories:
- 技术
---

DDos Distributed Denial of Service
https://www.jianshu.com/p/e7a5fdc67b8f


攻击方式叫做crossing site scripting,跨站脚本，简称XSS
https://www.jianshu.com/p/38d61b0c0a17
这种攻击方式叫做cross site request forgery,跨站请求伪造CSRF
https://www.jianshu.com/p/2de97b609a44

SQL注入 https://www.cnblogs.com/myseries/p/10821372.html

常见六大Web安全攻防解析
https://www.cnblogs.com/fundebug/p/details-about-6-web-security.html

CSRF，跨站请求伪造，攻击方伪装用户身份发送请求从而窃取信息或者破坏系统。
讲述基本原理：用户访问A网站登陆并生成了cookie，再访问B网站，如果A网站存在CSRF漏洞，此时B网站给A网站的请求（此时相当于是用户访问），A网站会认为是用户发的请求，从而B网站就成功伪装了你的身份，因此叫跨站脚本攻击。


CSRF防范：
A、合理规范api请求方式，GET，POST
B、对POST请求加token令牌验证，生成一个随机码并存入session，表单中带上这个随机码，提交的时候服务端进行验证随机码是否相同。


XSS，跨站脚本攻击。

防范：不相信任何输入，过滤输入。 