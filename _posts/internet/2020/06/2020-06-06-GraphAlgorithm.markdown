---
layout: post
title:  "图论算法全景：从基础遍历到最短路径与最大流"
date:   2020-06-06 10:17:00 +0900
comments: true
tags:
- 数据结构与算法
categories:
- 技术
---

在数据结构的世界里，线性表描述的是一对一的关系，树描述的是一对多的关系，而"图"则是最通用的结构——它描述的是多对多的关系。社交网络中的好友关系、地图中的路线规划、网络中的路由选择，这些问题的背后都是图论算法在发挥作用。本文将系统梳理图的基本概念、存储方式、遍历策略以及几个经典算法。

## 什么是"图"

图（Graph）是由顶点（Vertex）和边（Edge）组成的数据结构，用于表示实体之间的关系。简单来说，你可以把图理解为**存储关系的数据结构**。

根据边是否有方向，图分为两类：

- **无向图**：边没有方向，A-B 和 B-A 等价，例如微信好友关系
- **有向图**：边有方向，A→B 不等于 B→A，例如微博关注关系

根据边是否有权重，又可分为：

- **无权图**：边仅表示"是否连通"
- **带权图**：边附带权重值，例如城市间的距离、网络链路的带宽

## 图的存储结构

如何在计算机中高效存储图？有以下几种经典方案：

### 邻接矩阵（Adjacency Matrix）

使用二维数组 `matrix[i][j]` 表示顶点 i 到顶点 j 是否有边。

- **优点**：查询两个顶点是否相连是 O(1) 操作
- **缺点**：对于稀疏图浪费大量空间，空间复杂度 O(V²)

### 邻接表（Adjacency List）

每个顶点维护一个链表，存储所有与之相连的顶点。类似于正向索引。

- **优点**：节省空间，适合稀疏图
- **缺点**：查询两个顶点是否相连需要遍历链表

### 逆邻接表

与邻接表方向相反，记录的是"谁指向我"。类似倒排索引。在有向图中，邻接表记录出度，逆邻接表记录入度。

### 十字链表（Orthogonal List）

将邻接表和逆邻接表合并的结构，既能快速找到某顶点的出边，也能快速找到入边。适用于需要同时处理出度和入度的有向图场景。

## 图的遍历

### 深度优先搜索（DFS, Depth-First Search）

DFS 的策略是**一条路走到黑，走不通再回头**。沿着当前分支深入到最后一个节点，然后回溯到上一个分支继续探索。

核心特征：**回溯**。二叉树的前序、中序、后序遍历本质上都是深度优先遍历的特例。

DFS 通常使用递归或显式栈实现：

```python
def dfs(graph, node, visited):
    visited.add(node)
    for neighbor in graph[node]:
        if neighbor not in visited:
            dfs(graph, neighbor, visited)
```

时间复杂度：O(V + E)，其中 V 是顶点数，E 是边数。

### 广度优先搜索（BFS, Breadth-First Search）

BFS 的策略是**先访问所有邻居，再访问邻居的邻居**。逐层向外扩展，类似二叉树的层序遍历。

核心特征：**逐层扩展**。BFS 使用队列实现：

```python
from collections import deque

def bfs(graph, start):
    visited = {start}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
```

时间复杂度同样为 O(V + E)。BFS 天然适合**求最短路径**（无权图场景）。

## 最短路径算法

### Dijkstra 算法

解决**单源最短路径**问题：给定一个起点，求到图中所有其他顶点的最短路径。适用于**边权非负**的带权图。

核心思想是贪心：维护一个已确定最短路径的顶点集合，每次从未确定的顶点中选出距起点最近的，将其加入集合，并更新其邻居的距离。

```
初始化：起点距离为0，其余为∞
重复：
  1. 从未访问顶点中选出距离最小的顶点 u
  2. 标记 u 为已访问
  3. 对 u 的每个邻居 v：如果 dist[u] + weight(u,v) < dist[v]，更新 dist[v]
```

使用优先队列（最小堆）优化后，时间复杂度为 O((V + E) log V)。

参考阅读：[Dijkstra 算法详解](https://mp.weixin.qq.com/s/ALQntqQJkdWf4RbPaGOOhg)

### Floyd-Warshall 算法

解决**多源最短路径**问题：求任意两个顶点之间的最短路径。

核心思想是动态规划：对于每一对顶点 (i, j)，尝试经过每一个中间顶点 k，看是否能找到更短的路径。

```
for k in range(n):
    for i in range(n):
        for j in range(n):
            dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
```

时间复杂度 O(V³)，适合顶点数不太多的场景。

参考阅读：[Floyd-Warshall 算法详解](https://mp.weixin.qq.com/s/qnPSzv_xWSZN0VpdUgwvMg)

### A* 算法

A* 是对 Dijkstra 的优化，引入启发函数（Heuristic Function）来指导搜索方向，避免盲目扩展。广泛应用于游戏 AI 中的路径规划和地图导航。

评估函数：`f(n) = g(n) + h(n)`
- `g(n)`：从起点到当前节点的实际代价
- `h(n)`：从当前节点到终点的估计代价（启发函数）

参考阅读：[A* 算法详解](https://mp.weixin.qq.com/s/FYKR_1yBKR4GJTn0fFIuAA)

## 最小生成树

最小生成树（Minimum Spanning Tree, MST）要解决的问题是：在一个连通带权图中，找到一棵包含所有顶点的树，使得边权总和最小。典型应用如城市间铺设光缆的最小成本方案。

### Kruskal 算法

**以边为中心**的贪心策略：

1. 将所有边按权重排序
2. 依次选择权重最小的边
3. 如果该边连接的两个顶点不在同一个连通分量中（用并查集判断），则加入生成树
4. 重复直到生成树包含 V-1 条边

时间复杂度：O(E log E)，排序是主要开销。

参考阅读：[Kruskal 算法详解](https://blog.csdn.net/qq_41754350/article/details/81460643)

### Prim 算法

**以顶点为中心**的贪心策略：

1. 从任意一个顶点出发，将其加入已选集合
2. 在所有连接已选集合和未选集合的边中，选择权重最小的边
3. 将该边连接的未选顶点加入已选集合
4. 重复直到所有顶点都被选入

使用优先队列优化后，时间复杂度为 O((V + E) log V)。

参考阅读：[Prim 算法详解](https://mp.weixin.qq.com/s/x7JT7re7W7IgNCgMf1kJTA)

**Kruskal vs Prim**：Kruskal 适合稀疏图（边少），Prim 适合稠密图（边多）。

## Ford-Fulkerson 最大流算法

最大流问题：在一个有向图中，每条边有容量上限，求从源点（Source）到汇点（Sink）能够传输的最大流量。

实际应用场景：
- 物流网络中的最大运输量
- 网络带宽中的最大吞吐量
- 二分图匹配问题

Ford-Fulkerson 算法的核心思路：

1. 初始化所有边的流量为 0
2. 寻找一条从源点到汇点的增广路径（路径上所有边的剩余容量 > 0）
3. 沿增广路径增加流量（取路径上最小剩余容量）
4. 更新残余图（正向边减少容量，反向边增加容量）
5. 重复直到找不到增广路径

参考阅读：
- [Ford-Fulkerson 最大流算法](https://www.cnblogs.com/DarrenChan/p/9563511.html)
- [最大流算法详解](https://blog.csdn.net/sinat_41613352/article/details/84481115)

## 总结

图论算法是计算机科学中最丰富也最实用的算法领域之一。从基础的 DFS/BFS 遍历，到 Dijkstra/Floyd 最短路径，再到 Kruskal/Prim 最小生成树和 Ford-Fulkerson 最大流，这些算法在路由协议、社交网络分析、推荐系统、地图导航等领域都有广泛应用。

理解这些算法的关键在于把握其核心思想（贪心、动态规划、搜索），然后通过实际编码加深理解。建议从 LeetCode 的图论专题开始练手，逐步建立对图算法的直觉。
