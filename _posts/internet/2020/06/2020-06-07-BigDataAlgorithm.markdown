---
layout: post
title:  "大数据常用算法概述"
date:   2020-06-07 13:25:00 +0900
comments: true
tags:
- 数据结构与算法
- BigData
categories:
- 技术
---
<https://www.jianshu.com/p/4427db9337d7>

十道海量数据处理面试题与十个方法大总结 
<https://blog.csdn.net/twlkyao/article/details/12037073>
从头到尾解析Hash表算法
<https://blog.csdn.net/v_JULY_v/article/details/6256463>

教你如何迅速秒杀掉：99%的海量数据处理面试题
<https://blog.csdn.net/v_july_v/article/details/7382693>


#### 决策树算法
#### 回归算法
#### 朴素贝叶斯分类算法
#### 聚类-KNN算法
#### SVM支持向量机分类
#### 推荐算法

#### TF-IDF
- TF-IDF（term frequency–inverse document frequency，词频-逆向文件频率）是一种用于信息检索（information retrieval）与文本挖掘（text mining）的常用加权技术。
- TF-IDF是一种统计方法，用以评估一字词对于一个文件集或一个语料库中的其中一份文件的重要程度。字词的重要性随着它在文件中出现的次数成正比增加，但同时会随着它在语料库中出现的频率成反比下降。
- TF-IDF的主要思想是：如果某个单词在一篇文章中出现的频率TF高，并且在其他文章中很少出现，则认为此词或者短语具有很好的类别区分能力，适合用来分类。

#### TF-IDF算法实现简单快速，但是仍有许多不足之处：
- 没有考虑特征词的位置因素对文本的区分度，词条出现在文档的不同位置时，对区分度的贡献大小是不一样的。
- 按照传统TF-IDF，往往一些生僻词的IDF(反文档频率)会比较高、因此这些生僻词常会被误认为是文档关键词。
- 传统TF-IDF中的IDF部分只考虑了特征词与它出现的文本数之间的关系，而忽略了特征项在一个类别中不同的类别间的分布情况。
- 对于文档中出现次数较少的重要人名、地名信息提取效果不佳。
