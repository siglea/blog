---
layout: post
title:  "Java Concurrent"
date:   2019-11-12 11:25:00 +0900
comments: true
tags:
- Concurrent
categories:
- 技术
---

### AQS AbstractQueuedSynchronizer
### CAS Compare And Swap
#### 锁
- Synchronized 
- Lock ReentrantLock ReentrantReadWriteLock
- Condition

##### 终止线程

- 通过interrupt标志的方式(注意区分以下三个Java方法)
  - t.interrupt(); // 修改标志，其他地方根据该标志或者捕获异常来决定处理方式
  - t.isInterrupted(); 内部调用了当前线程的currentThread().isInterrupted(false);
    - 该方法仅仅是查询中断状态，不恢复中断状态
  - Thread有个类方法Thread.interrupted(); 内部调用了当前线程的currentThread().isInterrupted(true);
    - 该方法只有在中断状态为true时，才会恢复中断状态并返回true;否则，都是返回false
    
```java
public class KillThread{
    public static void main (String args[]){
        Thread t = new MyThread();
        t.start();
        //此处仅仅是修改状态,通常需要再run方法内部判断来决定是否终止线程
        t.interrupt();
    }
    public static class MyThread extends Thread{
        public void run(){
            while (!isInterrupted()) {  //非阻塞过程中通过判断中断标志来退出
                try {
                    Thread.sleep(5 * 1000);  // 阻塞过程捕获中断异常来退出
                } catch (InterruptedException e) {
                    e.printStackTrace();
                    break;  // 捕获到异常之后，执行 break 跳出循环
                }
            }
            
        }
    }
}
```
- 自定义一个共享状态变量，来修改该状态来实现类似方法一的效果(注意此方法的状态变量需要用volatile修饰)
- stop 方法终止线程 (线程不安全)
  - 程序中可以直接使用 stop 来强行终止线程，但是 stop 方法是很危险的，就象突然关闭计算机电源，而不是按正常程序关机一样，可能会产生不可预料的结果。
    不安全主要是：stop 调用之后，创建子线程的线程就会抛出 ThreadDeatherror 的错误，并且会释放子线程所持有的所有锁。
    一般任何进行加锁的代码块，都是为了保护数据的一致性，如果在调用 stop 后导致了该线程所持有的所有锁的突然释放 (不可控制)，那么被保护数据就有可能呈现不一致性，其他线程在使用这些被破坏的数据时，有可能导致一些很奇怪的应用程序错误。因此，并不推荐使用 stop 方法来终止线程。
- 业务场景中的使用，目前暂时没有发现真正能立即安全停止线程的方法
  - 用stop方法会带来数据不同步等线程安全问题
  - interrupt 主要需要及时判断状态，才能实时失效（业务中不可能循环或者多处判断中断状态）
  - 本质上，运行中的线程需要立即停止一定会带来各种问题，如需要支持kill进程  

##### 参考资料
并发编程 <https://segmentfault.com/a/1190000022039255>

高并发中的线程通信 <https://mp.weixin.qq.com/s/Gtz6aVPm-YnSh5pjs5JhkA>

高频多线程&并发面试题 <https://c.lanmit.com/bianchengkaifa/Java/53679.html>

Java编程艺术笔记 <https://www.jianshu.com/p/8d90dc5b341e>