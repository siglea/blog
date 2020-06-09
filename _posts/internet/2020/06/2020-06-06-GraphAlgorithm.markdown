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

#### 图的 “最短路径”（
- 迪杰斯特拉算法 Dijkstra，解决带权重的A->G最短路径 <https://mp.weixin.qq.com/s/ALQntqQJkdWf4RbPaGOOhg>
- 多源最短路径，解决多个带权重节点间的最短路径，弗洛伊德算法 Floyd-Warshall <https://mp.weixin.qq.com/s/qnPSzv_xWSZN0VpdUgwvMg>
- 路径规划之 A* 算法 <https://mp.weixin.qq.com/s/FYKR_1yBKR4GJTn0fFIuAA>

#### Ford-Fulkerson 最大流算法

#### 最小生成树
- Kruskal算法 <https://blog.csdn.net/qq_41754350/article/details/81460643>
- prim算法 <https://mp.weixin.qq.com/s/x7JT7re7W7IgNCgMf1kJTA>