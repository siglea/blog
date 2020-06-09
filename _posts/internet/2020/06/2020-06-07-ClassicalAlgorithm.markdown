---
layout: post
title:  "经典算法思想"
date:   2020-06-07 14:25:00 +0900
comments: true
tags:
- 数据结构与算法
categories:
- 技术
---
数据结构算法，问题TOP10 <https://mp.weixin.qq.com/s/rqzCvFWira204eJ1HA22yg>

#### 贪心算法
- 贪心的意思在于在作出选择时，每次都要选择对自身最为有利的结果，保证自身利益的最大化。贪心算法就是利用这种贪心思想而得出一种算法。
- 例：小明手中有 1，5，10，50，100 五种面额的纸币，每种纸币对应张数分别为 5，2，2，3，5 张。若小明需要支付 456 元，则需要多少张纸币？
- 最小生成树 Kruskal算法
- 最小生成树 prim算法
- 分发饼干、跳跃游戏、无重叠区间、摆动序列 <https://mp.weixin.qq.com/s/4GKIwV34Zp4W1VFTwhx-uw>
- 分糖果、无重叠区间 <https://mp.weixin.qq.com/s/YhFGBAXhv8c-Rfs6Fuciow>

#### 分治算法
- 快速排序算法、大整数乘法、残缺棋盘游戏 <https://mp.weixin.qq.com/s/2rnEhHcJEGSEmlAK18B2VQ>
- 汉诺塔、快速排序、归并排序 <https://mp.weixin.qq.com/s/paOrlfpdMwvCUDywda0EvQ>

#### 动态规划算法 Dynamic Programming
```shell
F(1) = 1;
F(2) = 2; 
F(n) = F(n-1)+F(n-2);（n>=3）

F(10) = F(9) + F(8) #最优子结构
F(1) F(2) #边界
F(n) = F(n-1) + F(n-2) #状态转移方程
```
- 斐波那契 <https://mp.weixin.qq.com/s/3LR-iVC4zgj0tGhZ780PcQ>
- 上台阶与挖黄金 <https://mp.weixin.qq.com/s/3h9iqU4rdH3EIy5m6AzXsg>
- 高楼扔鸡蛋 <https://mp.weixin.qq.com/s/ncrvbpiZauXAGnUZTh5qtA>

#### 回溯法
- 深度优先遍历 <https://mp.weixin.qq.com/s/UCTjKA7olFb00C6CLlqHAA>
- 八皇后问题 <https://mp.weixin.qq.com/s/puk7IAZkSe6FCkZnt0jnSA>
- 八皇后问题与数独 <https://mp.weixin.qq.com/s/vfItwB2GpXCy-s2dQJnkIg>
- A*寻路算法 <https://mp.weixin.qq.com/s/FYKR_1yBKR4GJTn0fFIuAA>
- 多源最短路径，弗洛伊德算法 Floyd-Warshall <https://mp.weixin.qq.com/s/qnPSzv_xWSZN0VpdUgwvMg>

#### 分支定界法
- 广度优先遍历 <https://mp.weixin.qq.com/s/Rdg14IPL4Czx4J5obgbqEQ>

#### 字符串匹配算法
- BF算法，是Brute Force（暴力算法，按位比较 O(m*n)）
- RK算法，是Rabin-Karp (计算hash值进行比较 O(n)) <https://mp.weixin.qq.com/s/EVkV1AQC9GBI29zNiWDH6g>
- Knuth-Morris-Pratt算法（简称KMP）是最常用的之一 <https://mp.weixin.qq.com/s/xr5rgSF3dOV9XH0gC5oO0w>
- 字符串匹配算法综述:BF、RK、KMP、BM、Sunday <https://mp.weixin.qq.com/s/RSnFzrmitwCCgDuB73I2QA>

#### 参考
- 小灰算法2017 <https://mp.weixin.qq.com/s/4kTtn_gLYQrX7JFlEJdsZg>
- 小灰算法2018 <https://mp.weixin.qq.com/s/oFQHrCZvItgc8McrZSaovw>
- 小灰算法2019 <https://mp.weixin.qq.com/s/Ok5SjqhiQkG5sLUPNY02Mw>
- 小灰算法2020 <https://mp.weixin.qq.com/s/dpWZ6qOvU1T9sdOzMNVyAA>
- 二十世纪最伟大的10大算法 <https://blog.csdn.net/v_JULY_v/article/details/6127953>