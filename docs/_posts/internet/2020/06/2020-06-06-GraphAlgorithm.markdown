---
layout: post
title:  "'图'相关算法"
date:   2020-06-06 10:17:00 +0900
comments: true
tags:
- 数据结构与算法
categories:
- 技术
---

#### 什么时"图"
- 可以简单理解我存储关系的数据结构，比如好友关系
- 分为有向图、无向图
- 存储结构
    - 邻接矩阵（类似多维数组）
    - 邻接表  （类似"正"索引）
    - 逆邻接表 （类似倒排索引）
    - 十字链表  （正倒索引联合）

#### 深度优先遍历 和 广度优先遍历
- 深度优先遍历，沿着当前分支，直到最后一个节点，然后遍历相邻节点（二叉树的前中后序遍历就是深度优先遍历），重点在回溯
- 广度优先遍历，遍历完当前节点的所有子节点，然后切换到下级节点（类似二叉树的层级遍历），重点在重放

#### 图的 “最短路径”
- 迪杰斯特拉算法 Dijkstra，解决带权重的A->G最短路径 <https://mp.weixin.qq.com/s/ALQntqQJkdWf4RbPaGOOhg>
- 多源最短路径，解决多个带权重节点间的最短路径，弗洛伊德算法 Floyd-Warshall <https://mp.weixin.qq.com/s/qnPSzv_xWSZN0VpdUgwvMg>
- 路径规划之 A* 算法 <https://mp.weixin.qq.com/s/FYKR_1yBKR4GJTn0fFIuAA>

##### 最小生成树
- 把所有点在没有回路的情况下，连接起来，并且权重相加最小（权重可以理解为城市见的距离）
- Kruskal算法，克鲁斯卡尔算法的基本思想是以边为主导地位，始终选择当前可用的最小边权的边（可以直接快排或者algorithm的sort）。每次选择边权最小的边链接两个端点是kruskal的规则，并实时判断两个点之间有没有间接联通。
  （也算是贪心算法思想）<https://blog.csdn.net/qq_41754350/article/details/81460643>
- prim算法，这个算法是以图的顶点为基础，从一个初始顶点开始，寻找触达其他顶点权值最小的边，并把该顶点加入到已触达顶点的集合中。当全部顶点都加入到集合时，算法的工作就完成了。Prim算法的本质，是基于贪心算法。
  <https://mp.weixin.qq.com/s/x7JT7re7W7IgNCgMf1kJTA>

#### Ford-Fulkerson 最大流算法
- 解决的问题：在一个流里，有着每条边的运载能力限制，我最多能从源头运输多少数量到目的地。
- <https://www.cnblogs.com/DarrenChan/p/9563511.html>
- <https://blog.csdn.net/sinat_41613352/article/details/84481115>

