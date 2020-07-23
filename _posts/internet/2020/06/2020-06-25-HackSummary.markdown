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
#### DDos  Distributed Denial of Service 分布式拒绝服务
- 利用大量合法的分布式服务器对目标发送请求，从而导致正常合法用户无法获得服务。通俗点讲就是利用网络节点资源如：IDC服务器、个人PC、手机、智能设备、打印机、摄像头等对目标发起大量攻击请求，从而导致服务器拥塞而无法对外提供正常服务
- 分类
    - 资源消耗类攻击，Syn Flood、Ack Flood、UDP Flood(限流和唯一识别限制)
    - 服务消耗性攻击，它主要是针对服务的特点进行精确定点打击，如web的CC，数据服务的检索，文件服务的下载等。这类攻击往往不是为了拥塞流量通道或协议处理通道，它们是让服务端始终处理高消耗型的业务的忙碌状态
    - 反射类攻击，一般请求回应的流量远远大于请求本身流量的大小
    - CC(ChallengeCollapsar，挑战黑洞)，不准确的分类，CC攻击的原理是通过代理服务器或者大量肉鸡模拟多个用户访问目标网站的动态页面，制造大量的后台数据库查询动作，消耗目标CPU资源，造成拒绝服务。CC不像DDoS可以用硬件防火墙来过滤攻击，CC攻击本身的请求就是正常的请求。
- 防御手段
    - 资源隔离
    - 应用层用户规则
    - 数据分析
    - 资源对抗、流量清洗，比如，隐藏源站IP后将攻击流量引流到高防IP
- 参考 <https://www.jianshu.com/p/e7a5fdc67b8f>
- 流量清洗的原理和DDoS流量清洗的实践 <https://dun.163.com/news/p/4e52c024c7c94220b3f7201498a388c6>

#### XSS crossing site scripting,跨站脚本（数据被黑客窃取）
- 通过.src的方式，将本地数据提交到黑客后台，需要黑客通过其他手段把js代码注入到正常网站
- 防御手段：cookie上加HttpOnly，不允许js读取；服务端过滤script信息；前端展示安全过滤
- 参考 <https://www.jianshu.com/p/38d61b0c0a17>

#### CSRF cross site request forgery,跨站请求伪造 （伪造合法请求）
- A网站登录成功并保持了本地cookie，黑客的B网站读取A的cookie伪造向A的请求
- 原因：
  - 同源策略阻止了js读取其他网站的cookie等内容，但没有防止js向其他网站发出请求
  - 同源策略限制了ajax请求，但没有限制form表单提交，前文提过img标签不受同源策略限制
  - 黑客网站利用用户向目标网站发起请求的时候，请求会带上目标网站下发的cookie
- 防御
  - referer(在http请求头中)验证解决方案,浏览器会告诉服务器，哪个页面发送了请求
    不过由于 http 头在某些版本的浏览器上存在可被篡改的可能性，所以这个解决方案并不完善
  - 目标网站通过cookie生成hash值，提交请求时带上hash值，服务端对hash进行过滤
  - 表单提交加验证码，如图片上的随机字符串
  - 用户登录时服务端生成token，之后用户请求必须带上token
- 参考 <https://www.jianshu.com/p/2de97b609a44>

#### SQL注入 
- <https://www.cnblogs.com/myseries/p/10821372.html>

#### 其他
- 常见六大Web安全攻防解析 <https://www.cnblogs.com/fundebug/p/details-about-6-web-security.html>


