---
layout: post
title:  "NumPy入门指南：数组操作、切片与广播机制详解"
date:   2018-12-26 10:30:09 +0900
comments: true
tags:
- python
categories:
- 技术
---

### 引言

NumPy（Numerical Python）是 Python 科学计算生态的基石，几乎所有数据分析和机器学习库（如 Pandas、Scikit-learn、TensorFlow）都建立在它之上。NumPy 的核心是 `ndarray`（N-dimensional array）——一个高效的多维数组对象，支持向量化运算，性能远超 Python 原生列表。本文将从数组创建、形状操作、切片索引到广播机制，系统性地介绍 NumPy 的基础用法。

---

### np.array：从 Python 列表创建数组

`np.array` 是最基本的数组创建方式，它接受 Python 列表或元组并转换为 ndarray。

关键属性：
- **ndim**：数组的维度数（嵌套层数）
- **dtype**：数组元素的数据类型，整个数组中所有元素必须是同一类型

```py
a = np.array([1, 2, 3,4,5], ndmin = 2, dtype=complex)
# => [[ 1.+0.j,  2.+0.j,  3.+0.j]]
```

`ndmin=2` 强制将结果提升为至少 2 维，`dtype=complex` 将所有元素转换为复数类型。

---

### np.dtype：数据类型对象

`dtype` 在 NumPy 中是一个**对象**而非简单的常量。需要区分 `np.int32`（type class）和 `np.dtype`（dtype 对象）：

```py
dt = np.dtype(np.int32)
```

`np.dtype` 可以描述更复杂的数据结构（如结构化数组），而 `np.int32` 只是一个类型标识符。

---

### ndarray.shape：数组形状

`shape` 属性返回数组各维度的大小。直接修改 `shape` 可以原地 reshape（会覆盖原数组），而 `reshape()` 方法返回新数组：

```py
a = np.array([[1,2,3],[4,5,6]])
a.shape = (3,2)
b = a.reshape((6, 1))
```

需要注意：reshape 后维度不会改变元素总数，即各维度之积必须等于元素总数。`reshape` 返回新数组，不影响原数组；直接赋值 `shape` 则是原地操作。

---

### ndarray.ndim：维度数

`ndim` 返回一个整数，表示数组的维度。例如一维数组的 `ndim` 为 1，二维数组为 2。

---

### 创建数组的常用函数

NumPy 提供了多种快捷的数组创建方式：

| 函数 | 说明 | 默认 dtype |
|------|------|-----------|
| `np.empty(shape)` | 创建未初始化的数组（值随机） | float64 |
| `np.ones(shape)` | 创建全 1 数组 | float64 |
| `np.zeros(shape)` | 创建全 0 数组 | float64 |

`shape` 参数可以是元组 `(1, 2)` 或列表 `[1, 2]`。如果只指定 `int` 类型（如 `dtype=int`），默认使用 `int64`。

---

### 从已有数据创建数组

`np.asarray` 可以将 Python 列表或元组转换为 ndarray。转换后的 ndarray 与原始数据一定是两个独立的对象。

需要特别注意元组的对齐规则：

```py
np.asarray(1,2,3),(4,5,6)) #返回二元数组，dtype是int
np.asarray(1,2,3),(4,5)) #返回一元数组，dtype是object
```

当元组中各子序列长度一致时，NumPy 可以推断为规整的多维数组；长度不一致时退化为包含 Python 对象的一维数组。

---

### np.arange：等差数列

`np.arange` 类似 Python 的 `range`，但返回 ndarray：

```py
np.arange(5, dtype = float)
```

默认 dtype 为 int。输入浮点数时小数部分会被截断（如果指定了 int dtype）。`endpoint=False` 参数可以控制是否包含终点值。

---

### np.linspace：等间隔序列

`np.linspace` 生成指定数量的等间隔点，适合需要精确控制点数的场景：

```py
np.linspace(10,20,5) # 起点，终点，点数
```

三个参数分别是起始值、终止值和生成的元素个数。默认包含终点。`np.logspace` 是其对数版本，`base` 参数控制对数的底（默认为 10）。

---

### 切片与索引

NumPy 数组的切片索引功能比 Python 列表更强大，支持多维切片和布尔索引。

#### 方法一：slice 对象

```py
a = np.arange(10)
s = slice(2,7,2)
```

#### 方法二：冒号语法 [start:stop:step]

```py
a[2:7:2]
```

对于多维数组，可以在各维度上独立切片：

```py
a = np.array([[1,2,3],[3,4,5],[4,5,6]])
a[1] == a[1, :]
a[:, 1] == a[..., 1] # => True
```

其中 `...`（省略号）表示"选取其余所有维度"，在高维数组操作中非常实用。

#### 方法三：布尔索引

```py
a = np.array([[1,2,3],[3,4,5],[4,5,6]])
a[a > 5] # => 返回一维数组
```

布尔索引根据条件筛选元素，结果总是一维数组。这在数据清洗和条件过滤中极为常用。

---

### 广播机制（Broadcasting）

广播是 NumPy 最强大的特性之一，它允许不同形状的数组进行算术运算。

#### 规则

1. **形状完全相同**时，操作是逐元素（element-wise）进行的
2. **可广播的条件**：从尾部维度开始对齐，每个维度的大小要么相同，要么其中一个为 1

例如，形状为 `(n, 1)` 的数组可以与形状为 `(n, m)` 的数组进行广播运算——NumPy 会自动将 `(n, 1)` 沿第二维"复制"为 `(n, m)`。

广播的意义在于避免了显式的数据复制，既节省内存又提升性能。理解广播规则是高效使用 NumPy 的关键。

---

### 总结

NumPy 的核心价值在于用 C 语言实现的 ndarray 和向量化运算，使得 Python 在数值计算领域具备了与 MATLAB 等专业工具媲美的性能。掌握数组创建（`array`、`zeros`、`arange`、`linspace`）、形状操作（`shape`、`reshape`）、切片索引（冒号语法、布尔索引）和广播机制，就具备了使用 NumPy 进行数据处理和科学计算的基础能力。建议在实际练习中多关注 `dtype` 的隐式转换和广播规则的边界情况，这是初学者最容易踩坑的地方。
