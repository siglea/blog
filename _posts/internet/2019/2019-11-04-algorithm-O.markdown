---
layout: post
title:  "算法时间复杂度"
date:   2019-11-04 11:25:00 +0900
comments: true
tags:
- 数据结构与算法
categories:
- 技术
---

#### 时间复杂度原则
- 如果运行时间是常数量级，用常数1表示
- 只保留时间函数中的最高阶项
```
T(n) = 0.5n^2 + 0.5n
T(n) = O(n^2)
```
- 如果最高阶项存在，则省去最高阶项前面的系数
```
T(n) = 3n
T(n) = O(n)
```

#### 时间复杂度排序
```
O(1) < O(logN) < O(n) < O(n^2)
```


