---
layout: post
title:  "十大经典排序算法详解：原理、Java 实现与复杂度对比"
date:   2020-05-31 12:25:00 +0900
comments: true
tags:
- 数据结构与算法
categories:
- 技术
---

排序算法是计算机科学中最基础也最重要的算法类别之一。无论是数据库的索引构建、搜索引擎的结果排列，还是日常开发中的数据处理，排序都无处不在。本文将系统地介绍十大经典排序算法的原理、Java 实现代码以及复杂度特征，帮助读者建立完整的排序算法知识体系。

---

### 一、比较类排序

比较类排序通过元素之间的比较来决定相对次序，其时间复杂度下界为 O(n log n)。

#### 1.1 冒泡排序（Bubble Sort）

<pre>
从左开始比较，大的往右换
或
从右开始比较，小的往左换
重复上一步骤
</pre>

冒泡排序是最直观的排序算法：每一轮遍历都将当前未排序部分中最大的元素"冒泡"到最右侧。它的平均和最坏时间复杂度都是 O(n²)，但当数据已经基本有序时，可以通过提前终止优化到 O(n)。

#### 1.2 鸡尾酒排序（Cocktail Sort）

<pre>
也叫双向冒泡或者定向冒泡，
从左开始比较，大的往右换
与
从右开始比较，小的往左换
同时进行
</pre>

鸡尾酒排序是冒泡排序的变种，解决了冒泡排序中"乌龟问题"——即小元素位于数组末尾时需要很多轮才能移到前面。双向冒泡在某些场景下能减少排序的总轮次。

#### 1.3 选择排序（Selection Sort）

<pre>
与冒泡排序相比减少了多余的交换
找出最小的元素放在最左侧，接着找第二小的...直到最后排完(不稳定)
</pre>

选择排序每轮只做一次交换（将最小元素放到正确位置），因此交换次数为 O(n)。但由于每轮都需要遍历剩余所有元素来找最小值，比较次数仍然是 O(n²)。选择排序是**不稳定**的排序算法。

#### 1.4 快速排序（Quick Sort）

<pre>
选中一个基准元素X，小于X放在左侧，大于X放在右侧，分而治之，不断重复
</pre>

快速排序是实际应用中最高效的比较排序算法之一，平均时间复杂度为 O(n log n)。其核心思想是"分治"：选择一个基准元素，将数组分为小于和大于基准的两部分，然后对两部分分别递归排序。

```java
public class QuickSort {
    public static void main(String[] args) {
        int[] arr = new int[] {4,7,6,5,3,2,8,1};
        quickSort(arr, 0, arr.length-1);
        System.out.println(Arrays.toString(arr));
    }
    public static void quickSort(int[] arr, int startIndex, int endIndex) {
        // 递归结束条件：startIndex大等于endIndex的时候
        if (startIndex >= endIndex) {
            return;
        }
        // 得到基准元素位置
        int pivotIndex = partition(arr, startIndex, endIndex);
        // 用分治法递归数列的两部分
        quickSort(arr, startIndex, pivotIndex - 1);
        quickSort(arr, pivotIndex + 1, endIndex);
    }

    private static int partition(int[] arr, int startIndex, int endIndex) {
        // 取第一个位置的元素作为基准元素
        int pivot = arr[startIndex];
        int left = startIndex;
        int right = endIndex;
        // 坑的位置，初始等于pivot的位置
        int index = startIndex;
        //大循环在左右指针重合或者交错时结束
        while ( right >= left  ){
            //right指针从右向左进行比较
            while ( right >= left ) {
                if (arr[right] < pivot) {
                    arr[left] = arr[right];
                    index = right;
                    left++;
                    break;
                }
                right--;
            }
            //left指针从左向右进行比较
            while ( right >= left ) {
                if (arr[left] > pivot) {
                    arr[right] = arr[left];
                    index = left;
                    right--;
                    break;
                }
                left++;
            }
        }
        arr[index] = pivot;
        return index;
    }

    
}
```

上述代码使用了"挖坑法"实现 partition：先将基准元素取出形成一个"坑"，然后从右向左找比基准小的填左边的坑，再从左向右找比基准大的填右边的坑，最终将基准元素放到最终的坑位上。

#### 1.5 插入排序（Insertion Sort）

<pre>
从左侧开始设定一个有序区，从第二个元素开始去有序找自己的位置插入进去
</pre>

插入排序的思路类似于整理扑克牌：维护一个有序区，每次将新元素插入到有序区的正确位置。对于小规模数据或基本有序的数据，插入排序非常高效。

#### 1.6 希尔排序（Shell Sort）

<pre>
按照跨度分成若干"小数组"，进行插入排序
逐渐缩小跨度为1，即完成
</pre>

希尔排序是插入排序的改进版本。通过引入"增量"的概念，先让间距较远的元素进行排序，使数组快速趋向有序，然后逐步缩小增量直到 1，最终完成排序。其时间复杂度取决于增量序列的选择，通常在 O(n^1.3) 到 O(n²) 之间。

```java
public class ShellSort {
    public static void sort(int [] array){
        //希尔排序的增量
        int d=array.length;
        while(d>1) {
            //使用希尔增量的方式，即每次折半
            d=d/2;
            for(int x=0;x<d;x++) {
                //开始跨度内的插入排序
                for(int i=x+d;i<array.length;i=i+d) {
                    int temp=array[i];
                    int j;
                    for(j=i-d;j>=0&&array[j]>temp;j=j-d) {
                        array[j+d]=array[j];
                    }
                    array[j+d]=temp;
                }
            }
        }
    }
    public static void main(String [] args)
    {
        int[] array = {5,3,9,12,6,1,7,2,4,11,8,10};
        sort(array);
        System.out.println(Arrays.toString(array));
    }
}
```

#### 1.7 归并排序（Merge Sort）

<pre>
由一组数字分为两组，逐渐分为只包含2个元素的小组
开始比较大小，左小右大
比较完毕之后，开始合并，合并的时候按照小大顺序把2个小组合并成1个有序大组，直到最后1个最大有序组
</pre>

归并排序也是基于分治思想，但与快速排序不同，归并排序的"分"是简单的对半拆分，关键在于"合"——将两个已排序的子数组合并为一个有序数组。归并排序的时间复杂度稳定在 O(n log n)，是一种**稳定**的排序算法，代价是需要 O(n) 的额外空间。

```java
public class MergeSort {
    public static void main(String[] args) {
        int[] array = { 5, 8, 6, 3, 9, 2, 1, 7 };
        mergeSort(array, 0, array.length-1);
        System.out.println(Arrays.toString(array));
    }
    static public void mergeSort(int[] array, int start, int end){
        if(start < end){
            //折半成两个小集合，分别进行递归
            int mid=(start+end)/2;
            mergeSort(array, start, mid);
            mergeSort(array, mid+1, end);
            //把两个有序小集合，归并成一个大集合
            merge(array, start, mid, end);
        }
    }
    static private void merge(int[] array, int start, int mid, int end){
        //开辟额外大集合，设置指针
        int[] tempArray = new int[end-start+1];
        int p1=start, p2=mid+1, p=0;
        //比较两个小集合的元素，依次放入大集合
        while(p1<=mid && p2<=end){
            if(array[p1]<=array[p2])
                tempArray[p++]=array[p1++];
            else
                tempArray[p++]=array[p2++];
        }
        //左侧小集合还有剩余，依次放入大集合尾部
        while(p1<=mid)
            tempArray[p++]=array[p1++];
        //右侧小集合还有剩余，依次放入大集合尾部
        while(p2<=end)
            tempArray[p++]=array[p2++];
        //把大集合的元素复制回原数组
        for (int i=0; i<tempArray.length; i++)
            array[i+start]=tempArray[i];
    }
}
```

#### 1.8 堆排序（Heap Sort）

<pre>
主要利用二叉堆是完全二叉堆这样的数据结构的特性
把无序数组构建成二叉堆。
循环删除堆顶元素，移到集合尾部，调节堆产生新的堆顶。

二叉堆虽然是一颗完全二叉树，但它的存储方式并不是链式存储，而是顺序存储。换句话说，二叉堆的所有节点都存储在数组当中。
利用大顶堆，删除顶点放于数组未部，此后二叉堆自我调整选出新的堆顶
</pre>

堆排序利用了二叉堆的性质：先将无序数组构建为大顶堆，然后不断取出堆顶（最大值）放到数组末尾，再调整堆结构。时间复杂度稳定在 O(n log n)，且不需要额外空间（原地排序），但由于缓存不友好（跳跃式访问数组元素），实际性能通常不如快速排序。

- 堆排序详解：<https://mp.weixin.qq.com/s/cq2EhVtOTzTVpNpLDXfeJg>

---

### 二、非比较类排序

非比较类排序不通过元素之间的比较来确定顺序，在特定条件下可以突破 O(n log n) 的下界，达到线性时间复杂度。

#### 2.1 计数排序（Counting Sort）

<pre>
建立【元素都为0】的空数组，开始遍历待排序数组
如果待排元素值等于空数组的位置角标，则【元素+1】
</pre>

计数排序的核心思路是用额外的数组来统计每个值出现的次数，然后按顺序输出。它的时间复杂度为 O(n+k)，其中 k 是数据的范围。适用于数据范围不大且为整数的场景。

#### 2.2 桶排序（Bucket Sort）

<pre>
计数排序的升级版，计数排序每个索引只能记录一个值，
索引升级为桶（比如桶范围2.0-3.5）
此时，一个桶里就可以放多个数据范围内的数据
</pre>

桶排序将数据分到有限数量的桶里，每个桶再分别排序（可以使用其他排序算法或递归桶排序）。当数据分布较为均匀时，桶排序可以达到接近 O(n) 的时间复杂度。

#### 2.3 基数排序（Radix Sort）

<pre>
提取每个元素的最后一位进行计数排序
再提取倒数第二位进行计数排序
直到最前一位
比如：单词排序，长度不一的末尾用0代替
</pre>

基数排序按位进行排序，从最低位到最高位（LSD）或从最高位到最低位（MSD）。每一位的排序使用稳定的排序算法（如计数排序）。时间复杂度为 O(d × (n+k))，其中 d 是最大位数，k 是每位的取值范围。

---

### 三、复杂度对比

<img src="{{ site.baseurl }}/img/sort.jpg" width="600px" />

| 排序算法 | 平均时间复杂度 | 最坏时间复杂度 | 空间复杂度 | 稳定性 |
|----------|---------------|---------------|-----------|--------|
| 冒泡排序 | O(n²) | O(n²) | O(1) | 稳定 |
| 选择排序 | O(n²) | O(n²) | O(1) | 不稳定 |
| 插入排序 | O(n²) | O(n²) | O(1) | 稳定 |
| 希尔排序 | O(n^1.3) | O(n²) | O(1) | 不稳定 |
| 快速排序 | O(n log n) | O(n²) | O(log n) | 不稳定 |
| 归并排序 | O(n log n) | O(n log n) | O(n) | 稳定 |
| 堆排序 | O(n log n) | O(n log n) | O(1) | 不稳定 |
| 计数排序 | O(n+k) | O(n+k) | O(k) | 稳定 |
| 桶排序 | O(n+k) | O(n²) | O(n+k) | 稳定 |
| 基数排序 | O(d(n+k)) | O(d(n+k)) | O(n+k) | 稳定 |

---

### 四、如何选择排序算法？

- **数据量小**（n < 50）：插入排序，简单且高效
- **数据基本有序**：插入排序或冒泡排序（优化版）
- **大规模通用排序**：快速排序（实际中最常用）
- **要求稳定性**：归并排序
- **数据范围有限**：计数排序或基数排序
- **内存敏感**：堆排序（原地排序，O(1) 额外空间）

---

### 五、总结

排序算法的选择没有绝对的优劣之分，关键在于匹配数据特征和应用场景。理解每种算法的原理和适用条件，比死记硬背复杂度表格更为重要。在实际开发中，大多数编程语言的标准库已经提供了高度优化的排序实现（如 Java 的 `Arrays.sort` 使用 TimSort），但掌握底层原理有助于在特殊场景下做出正确的优化决策。

#### 参考

- <https://mp.weixin.qq.com/s/teOGQlslb6aP4AQrx7TTzA>
