---
layout: post
title:  "BitMap-BloomFilter"
date:   2020-06-07 14:25:00 +0900
comments: true
tags:
- 数据结构与算法
categories:
- 技术
---

#### BitMap
- 近似的理解为用一个大数组的索引来表示数字本身，用0或1表示该数字是否存在
- 一个32位的int，只用一个标志位来表示是否存在
- 但是数字如果重复只会保留一个，主要用于去重类似的场景

#### BloomFilter
- 判断短连接是否重复、垃圾邮件等场景
- 把url，3次不同hash，得到3个不同的hashcode，存入bitmap
- 多次hash是为了降低hash重复的概率
- 由于以上特性，bloomFilter算法计算出不存在的一定就是不存在，如果计算出来存在有一定几率重复（因为hash的特性）

#### 参考链接
- Bitmap算法 整合版 <https://mp.weixin.qq.com/s/xxauNrJY9HlVNvLrL5j2hg>
- 什么是布隆算法？<https://mp.weixin.qq.com/s/RmR5XmLeMvk35vgjwxANFQ>