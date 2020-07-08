---
layout: post
title:  "排序算法概述"
date:   2020-05-31 12:25:00 +0900
comments: true
tags:
- 数据结构与算法
categories:
- 技术
---

#### 冒泡排序
<pre>
从左开始比较，大的往右换
或
从右开始比较，小的往左换
重复上一步骤
</pre>
#### 鸡尾排序
<pre>
也叫双向冒泡或者定向冒泡，
从左开始比较，大的往右换
与
从右开始比较，小的往左换
同时进行
</pre>
#### 选择排序
<pre>
与冒泡排序相比减少了多余的交换
找出最小的元素放在最左侧，接着找第二小的...直到最后排完(不稳定)
</pre>
#### 快速排序
<pre>
选中一个基准元素X，小于X放在左侧，大于X放在右侧，分而治之，不断重复
</pre>
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
#### 插入排序
<pre>
从左侧开始设定一个有序区，从第二个元素开始去有序找自己的位置插入进去
</pre>
#### 希尔排序
<pre>
按照跨度分成若干"小数组"，进行插入排序
逐渐缩小跨度为1，即完成
</pre>
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
#### 归并排序(比武排序)
<pre>
由一组数字分为两组，逐渐分为只包含2个元素的小组
开始比较大小，左小右大
比较完毕之后，开始合并，合并的时候按照小大顺序把2个小组合并成1个有序大组，直到最后1个最大有序组
</pre>
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
#### 计数排序
<pre>
建立【元素都为0】的空数组，开始遍历待排序数组
如果待排元素值等于空数组的位置角标，则【元素+1】
</pre>
#### 桶排序
<pre>
计数排序的升级版，计数排序每个索引只能记录一个值，
索引升级为桶（比如桶范围2.0-3.5）
此时，一个桶里就可以放多个数据范围内的数据
</pre>
#### 基数排序（按位排序）
<pre>
提取每个元素的最后一位进行计数排序
再提取倒数第二位进行计数排序
直到最前一位
比如：单词排序，长度不一的末尾用0代替
</pre>
#### 堆排序
<pre>
主要利用二叉堆是完全二叉堆这样的数据结构的特性
把无序数组构建成二叉堆。
循环删除堆顶元素，移到集合尾部，调节堆产生新的堆顶。

二叉堆虽然是一颗完全二叉树，但它的存储方式并不是链式存储，而是顺序存储。换句话说，二叉堆的所有节点都存储在数组当中。
利用大顶堆，删除顶点放于数组未部，此后二叉堆自我调整选出新的堆顶
</pre>
- <https://mp.weixin.qq.com/s/cq2EhVtOTzTVpNpLDXfeJg>

<img src="/img/sort.jpg" width="600px" />

#### 参考 <https://mp.weixin.qq.com/s/teOGQlslb6aP4AQrx7TTzA>