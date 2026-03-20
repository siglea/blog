---
layout: post
title:  "Python 金融数据可视化入门：用 Matplotlib 绘制股票走势图"
date:   2018-10-23 21:30:09 +0900
comments: true
tags:
- programming
- python
categories:
- 技术
---

在量化金融和数据分析领域，数据可视化是最基础也最重要的技能之一。一张清晰的走势图往往比一万行数据更能揭示趋势和异常。Python 凭借 Matplotlib、Pandas 等强大的生态，成为金融数据分析的首选语言。本文将通过一个实际案例——绘制苹果公司股价走势图，介绍如何用 Python 进行基础的金融数据可视化。

## 环境准备

### 导入必要的库

金融数据可视化需要三个核心库：

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
%matplotlib inline
```

| 库 | 用途 |
|------|------|
| `numpy` | 数值计算基础库，提供高效的数组操作 |
| `pandas` | 数据处理与分析，DataFrame 是其核心数据结构 |
| `matplotlib` | Python 最经典的绑图库，`pyplot` 模块提供了类似 MATLAB 的绑图接口 |

`%matplotlib inline` 是 Jupyter Notebook 的魔法命令，使图表直接在 Notebook 中内联显示，而不是弹出新窗口。

## 绑制单只股票走势图

### 基本绘图

假设我们已经有了一个包含股票市场数据的 DataFrame `market_train_df`，要绘制苹果（AAPL）的收盘价走势：

```python
from pylab import rcParams
rcParams['figure.figsize'] = 50, 13

apple_data = market_train_df[market_train_df['assetCode'] == 'AAPL.O']
apple_data.set_index('time')['close'].plot(grid = True)
```

<img src="{{ site.baseurl }}/img/python-plot-financial-data-1.png" style="height:50%">

代码解析：

1. **`rcParams['figure.figsize'] = 50, 13`**：设置图表尺寸为 50×13 英寸。金融时间序列数据通常时间跨度长、数据点密集，较大的图表尺寸能避免数据点过于拥挤
2. **过滤数据**：通过 `assetCode == 'AAPL.O'` 筛选苹果公司的数据（`.O` 后缀通常表示在特定交易所上市）
3. **`set_index('time')`**：将时间列设为 DataFrame 的索引，Pandas 会自动将其作为 X 轴
4. **`['close'].plot(grid=True)`**：选取收盘价列并绘图，`grid=True` 添加网格线便于读数

### 图表美化建议

在实际项目中，可以进一步美化图表：

```python
fig, ax = plt.subplots(figsize=(50, 13))
apple_data.set_index('time')['close'].plot(ax=ax, grid=True, linewidth=1.5, color='#1f77b4')
ax.set_title('AAPL Stock Price', fontsize=20)
ax.set_xlabel('Date', fontsize=14)
ax.set_ylabel('Close Price (USD)', fontsize=14)
plt.tight_layout()
plt.show()
```

## 多股票对比分析

### 在同一张图中叠加绘制

在数据清洗过程中，我们经常需要通过可视化来发现异常数据。比如要检查一组"可疑"股票的走势：

```python
for code in suspicious_asset_code:
    asset_data = market_train_df[market_train_df['assetCode'] == code]
    asset_data.set_index('time')['close'].plot(grid=True)
```

<img src="{{ site.baseurl }}/img/python-financial-plot-2.png" style="height:50%">

这种方式会把所有股票画在同一张图上。当股票数量较多或价格量级差异大时，图表会变得难以辨认。

### 使用子图（Subplot）分别展示

更好的做法是使用 `subplot` 将每只股票画在独立的子图中：

```python
fig.add_subplot(rows, columns, index)
```

参数说明：
- `rows`：子图网格的行数
- `columns`：子图网格的列数
- `index`：当前子图的位置（从 1 开始，按行优先编号）

完整示例：

```python
fig = plt.figure(figsize=(50, 30))
for i, code in enumerate(suspicious_asset_code):
    ax = fig.add_subplot(len(suspicious_asset_code), 1, i + 1)
    asset_data = market_train_df[market_train_df['assetCode'] == code]
    asset_data.set_index('time')['close'].plot(ax=ax, grid=True)
    ax.set_title(code, fontsize=14)
plt.tight_layout()
plt.show()
```

<img src="{{ site.baseurl }}/img/python-plot-subplot.png" style="height:50%">

这样每只股票都有独立的坐标系，方便逐一检查数据异常——比如价格突然归零、出现负值、或者走势明显不合理的情况。

## 进阶技巧

如果你需要更专业的金融图表，以下库值得关注：

- **mplfinance**：专门用于绘制 K 线图（蜡烛图），支持成交量、均线等叠加
- **plotly**：交互式图表库，支持缩放、悬停查看数据点等功能，非常适合探索性分析
- **seaborn**：基于 Matplotlib 的高级统计可视化库，默认样式更美观

## 总结

数据可视化是金融数据分析的第一步，也是最直觉的质量检查手段。本文介绍的 Matplotlib 基础绑图技巧虽然简单，但在实际工作中非常实用：

1. 使用 `set_index` + `plot` 快速绑制时间序列
2. 通过 `rcParams` 调整图表尺寸适应数据密度
3. 使用 `subplot` 对比多组数据，发现异常

掌握这些基础之后，可以根据实际需求选择更专业的可视化工具，构建更丰富的金融数据分析流程。
