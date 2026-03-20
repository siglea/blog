---
layout: post
title:  "Java 并发编程核心：从锁机制到线程安全实践"
date:   2019-11-12 11:25:00 +0900
comments: true
tags:
- Java
categories:
- 技术
---

并发编程是 Java 后端开发的核心能力之一。从最基础的 `synchronized` 到 JUC 包中丰富的并发工具类，Java 为开发者提供了多层次的并发编程支持。本文将系统梳理 Java 并发编程中的核心概念，包括锁的分类与升级机制、AQS 框架、volatile 语义、线程安全的集合类、阻塞队列，以及各种并发工具的使用场景与最佳实践。

---

### 一、线程安全的基本概念

#### 1.1 绝对线程安全与相对线程安全

绝对线程安全意味着不管运行时环境如何，调用者都不需要任何额外的同步措施。而 Java 中大多数所谓的"线程安全"类（如 `Vector`、`Hashtable`）实际上是**相对线程安全**——单个操作是线程安全的，但组合操作仍需要外部同步。

线程安全的三大核心问题：**可见性、有序性、原子性**。

**参考资料：**
- <https://www.cnblogs.com/duanxz/p/6099983.html>
- <https://www.jianshu.com/p/98b0241bc8e2>

---

### 二、AQS（AbstractQueuedSynchronizer）

#### 2.1 AQS 概述

`AbstractQueuedSynchronizer` 如其名——**抽象的队列式同步器**。AQS 定义了一套多线程访问共享资源的同步器框架，是 JUC 包中许多同步类的基石，如 `ReentrantLock`、`Semaphore`、`CountDownLatch` 等都依赖于它。

#### 2.2 两种资源共享方式

- **Exclusive（独占）**：只有一个线程能执行，如 `ReentrantLock`
- **Share（共享）**：多个线程可同时执行，如 `Semaphore`、`CountDownLatch`

#### 2.3 CLH 锁

CLH（Craig, Landin, and Hagersten）锁是一种自旋锁，能确保无饥饿性并提供先来先服务的公平性。CLH 锁是一种基于链表的可扩展、高性能、公平的自旋锁，申请线程只在本地变量上自旋，不断轮询前驱的状态，如果发现前驱释放了锁就结束自旋。

**参考资料：**
- <https://www.jianshu.com/p/4682a6b0802d>
- <https://www.jianshu.com/p/d291a6a1879c>

---

### 三、CAS（Compare And Swap）

CAS 算法包含 3 个参数：`CAS(V, E, N)`——V 表示要更新的变量（内存值），E 表示预期值（旧的），N 表示新值。当且仅当 V 等于 E 时，才将 V 设为 N；如果不同，则说明已有其他线程做了更新，当前线程什么都不做。

CAS 操作是**乐观锁**的典型实现：它总是认为自己可以成功完成操作。当多个线程同时使用 CAS 操作一个变量时，只有一个会胜出并成功更新，其余均会失败（但不会被挂起，允许再次尝试或放弃操作）。基于这样的原理，CAS 即使没有锁也可以发现其他线程对当前线程的干扰，并进行恰当的处理。

---

### 四、volatile 关键字

#### 4.1 核心特性

Java 语言提供了一种稍弱的同步机制——`volatile` 变量，用来确保将变量的更新操作通知到其他线程。volatile 变量具备两种特性：

- **变量可见性**：保证该变量对所有线程可见。当一个线程修改了变量的值，新值对于其他线程可以立即获取。本质上，JVM 保证了每次读 volatile 变量都从内存中读，跳过 CPU cache。
- **禁止指令重排序**：通过插入内存屏障指令来保证有序性。

在访问 volatile 变量时不会执行加锁操作，因此不会使执行线程阻塞，是一种比 `synchronized` 更轻量级的同步机制。

#### 4.2 适用场景

对 volatile 变量的**单次读/写**操作可以保证原子性（如 long 和 double 类型变量），但**不能保证 `i++` 这种复合操作的原子性**（因为本质上 `i++` 是读、写两次操作）。必须同时满足以下两个条件才能在并发环境中使用 volatile 保证线程安全：

1. 对变量的写操作不依赖于当前值（比如 `i++` 不行，但 `boolean flag = true` 可以）
2. 该变量没有包含在具有其他变量的不变式中（不同的 volatile 变量之间不能互相依赖）

---

### 五、锁的状态与升级

Java 对象头中的 Mark Word 记录了锁的状态信息，锁共有四种状态：**无锁、偏向锁、轻量级锁、重量级锁**。

#### 5.1 偏向锁

HotSpot 作者研究发现，大多数情况下锁不仅不存在多线程竞争，而且总是由同一线程多次获得。偏向锁的目的是在某个线程获得锁之后，消除这个线程锁重入（CAS）的开销。引入偏向锁是为了在无多线程竞争的情况下尽量减少不必要的轻量级锁执行路径——偏向锁只需在置换 ThreadID 时依赖一次 CAS 原子指令，而轻量级锁的获取及释放依赖多次 CAS。

#### 5.2 锁升级

随着竞争加剧，锁可以从偏向锁升级到轻量级锁，再升级到重量级锁（升级是单向的，不会降级）。

- **轻量级锁**：适应的场景是线程**交替执行**同步块，如果存在同一时间访问同一锁的情况，就会膨胀为重量级锁。
- **重量级锁（Mutex Lock）**：`synchronized` 通过对象内部的监视器锁（Monitor）来实现，Monitor 本质依赖于底层操作系统的 Mutex Lock，线程切换需要从用户态转换到核心态，代价高昂。JDK 1.6 以后引入"轻量级锁"和"偏向锁"来减少这种开销。

---

### 六、锁的使用

#### 6.1 主要锁类型

- **Synchronized**：JVM 级别的同步锁（基于 Monitor）
- **ReentrantLock**：可重入锁（基于 Lock 接口、Condition），核心类 `AbstractQueuedSynchronizer` 通过构造基于阻塞的 CLH 队列容纳所有阻塞线程，对队列操作均通过 Lock-Free（CAS）实现，并实现了偏向锁功能
- **ReentrantReadWriteLock**：可重入读写锁（基于 ReadWriteLock 接口、Condition）。ReadLock 是共享的，WriteLock 是独占的。用一个 32 位 int state 标示和记录读/写锁重入次数——高 16 位用作读锁，低 16 位用作写锁，因此无论读锁还是写锁最多只能被持有 65535 次
- **StampedLock**：戳锁，有三种模式（排它写、悲观读、乐观读），锁获取方法返回一个数字作为票据 stamp

**参考：** <https://www.cnblogs.com/dennyzhangdd/p/6925473.html>

#### 6.2 Condition

`Condition` 是 JDK 1.5 引入的，用来替代传统的 `Object.wait()/notify()`，实现线程间协作。相比 `synchronized` 搭配 `wait/notify` 的方式：

1. Condition 可以实现**多路通知**功能——在一个 Lock 对象里可以创建多个 Condition 实例，线程可以注册在指定的 Condition 中，有选择地进行线程通知
2. 而 `synchronized` 相当于整个 Lock 对象中只有一个 Condition，`notifyAll()` 时需要通知所有 WAITING 线程，效率较低
3. 调用 Condition 的 `await()` 和 `signal()` 方法必须在 `lock.lock()` 和 `lock.unlock()` 之间

#### 6.3 LockSupport.park() 与 Object.wait() 的区别

主要区别在于面向的对象不同：`LockSupport` 的 `park/unpark` 以**线程**作为方法参数，语义更清晰，使用更方便。而 `wait/notify` 使得阻塞/唤醒对线程本身来说是被动的，要准确控制哪个线程阻塞/唤醒很困难——要么随机唤醒一个（`notify`），要么唤醒所有（`notifyAll`）。

**参考资料：**
- <https://www.jianshu.com/p/ceb8870ef2c5>
- <https://www.jianshu.com/p/e3afe8ab8364>

#### 6.4 synchronized 与 ReentrantLock 的区别

**共同点：**
1. 都用来协调多线程对共享对象、变量的访问
2. 都是可重入锁
3. 都保证了可见性和互斥性

**不同点：**
1. ReentrantLock 显式获得/释放锁，synchronized 隐式获得释放锁
2. ReentrantLock 可响应中断、可轮回，synchronized 不可响应中断
3. ReentrantLock 是 API 级别，synchronized 是 JVM 级别
4. ReentrantLock 可以实现公平锁
5. ReentrantLock 通过 Condition 可以绑定多个条件
6. 底层实现不同：synchronized 是同步阻塞（悲观并发策略），Lock 是同步非阻塞（乐观并发策略）
7. Lock 是接口，synchronized 是关键字（内置语言实现）
8. synchronized 发生异常时自动释放锁，Lock 需要在 finally 中手动释放
9. Lock 可以让等待锁的线程响应中断，synchronized 不行
10. 通过 Lock 可以知道有没有成功获取锁
11. Lock 可以提高多线程读操作的效率（读写锁）

---

### 七、锁优化策略

针对锁的使用，Java 提供了多种优化思路：

- **减少锁持有时间**：只在有线程安全要求的程序上加锁
- **减小锁粒度**：将大对象拆成小对象，增加并行度，降低锁竞争。最典型的案例就是 `ConcurrentHashMap`
- **锁分离**：最常见的就是读写锁 `ReadWriteLock`，读读不互斥，读写互斥，写写互斥。可以延伸到只要操作互不影响就可以分离，比如 `LinkedBlockingQueue` 从头部取出、从尾部放数据
- **锁粗化**：如果对同一个锁不停地请求、同步和释放，其本身也会消耗资源，适当合并同步块反而更优
- **锁消除**：编译器级别的优化。在即时编译时，如果发现不可能被共享的对象，则可以消除这些对象的锁操作

---

### 八、自旋锁

#### 8.1 原理

如果持有锁的线程能在很短时间内释放锁资源，那么等待竞争锁的线程就不需要做内核态和用户态之间的切换进入阻塞挂起状态，它们只需要等一等（自旋），等持有锁的线程释放锁后即可立即获取锁。但如果一直获取不到锁，线程也不能一直占用 CPU 自旋做无用功，需要设定一个自旋等待的最大时间。

#### 8.2 优缺点

- **优点**：减少线程阻塞，对于锁竞争不激烈且占用锁时间很短的代码块性能大幅提升
- **缺点**：如果锁竞争激烈或持有锁时间长，自旋会浪费 CPU 资源

#### 8.3 适应性自旋锁（JDK 1.6+）

JDK 1.6 引入了适应性自旋锁，自旋时间不再固定，而是由前一次在同一个锁上的自旋时间以及锁的拥有者状态来决定。JVM 还会针对当前 CPU 负荷情况做优化：

- 平均负载小于 CPUs 则一直自旋
- 超过 CPUs/2 个线程正在自旋则后来线程直接阻塞
- 正在自旋的线程发现 Owner 发生变化则延迟自旋时间或进入阻塞

```shell
-XX:+UseSpinning 开启; -XX:PreBlockSpin=10 为自旋次数; // JDK1.6(JDK1.7 后，去掉此参数，由 jvm 控制)
```

---

### 九、可重入锁

广义上的可重入锁（也叫递归锁），指的是同一线程外层函数获得锁之后，内层递归函数仍然能获取该锁的代码但不受影响。在 Java 中 `ReentrantLock` 和 `synchronized` 都是可重入锁。

---

### 十、乐观锁与悲观锁

- **乐观锁**：认为读多写少，每次拿数据都认为别人不会修改，不上锁。但在更新时会判断在此期间别人有没有更新这个数据。Java 中的乐观锁基本都通过 CAS 操作实现。
- **悲观锁**：认为写多，每次读写数据都会上锁。Java 中的 `synchronized` 是典型的悲观锁，AQS 框架下的锁则是先尝试 CAS 乐观锁获取，获取不到才转换为悲观锁。

---

### 十一、线程终止

#### 11.1 通过 interrupt 标志

注意区分以下三个方法：

- `t.interrupt()`：修改中断标志
- `t.isInterrupted()`：查询中断状态，不恢复中断状态
- `Thread.interrupted()`：类方法，只在中断状态为 true 时恢复中断状态并返回 true

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

#### 11.2 其他方式

- **自定义共享状态变量**：修改该状态来实现类似效果（状态变量需要用 `volatile` 修饰）
- **stop 方法（不推荐）**：线程不安全。`stop` 调用之后会抛出 `ThreadDeathError`，并释放子线程所持有的所有锁，可能导致被保护数据不一致

#### 11.3 业务场景思考

目前暂时没有发现真正能**立即且安全**停止线程的方法：
- `stop` 会带来数据不同步等线程安全问题
- `interrupt` 需要及时判断状态才能实时生效（业务中不可能循环或多处判断中断状态）
- 本质上，运行中的线程需要立即停止一定会带来各种问题

---

### 十二、并发工具类

#### 12.1 CyclicBarrier、CountDownLatch、Semaphore

这三者都能实现线程之间的等待，但侧重点不同：

- **CountDownLatch（等多搞一）**：某个线程 A 等待若干个其他线程执行完任务之后才执行。不能重用。
- **CyclicBarrier（等多搞多）**：一组线程互相等待至某个状态，然后同时执行。可以重用。
- **Semaphore（信号量）**：控制对某组资源的访问权限。类比"8 个工人 5 台机器"的场景。

**参考：** <https://www.cnblogs.com/dolphin0520/p/3920397.html>

#### 12.2 ConcurrentHashMap

`SynchronizedMap` 一次锁住整张表来保证线程安全，每次只能有一个线程访问。`ConcurrentHashMap` 使用**分段锁**（JDK 7）或 **CAS + synchronized**（JDK 8）来保证多线程下的性能——默认将 Hash 表分为 16 个桶，get/put/remove 等操作只锁当前需要用到的桶，并发性能显著提升。

另外，`ConcurrentHashMap` 使用了一种不同的迭代方式：当 iterator 被创建后集合再发生改变，不再抛出 `ConcurrentModificationException`，而是在改变时 new 新的数据从而不影响原有数据。

#### 12.3 CopyOnWriteArrayList

增删改都需要获得锁（且锁只有一把），而读操作不需要获得锁，支持并发读。增删改中都会创建一个新的数组，操作完成后再赋给原来的引用——这是为了保证 get 的时候都能获取到元素。

与 `Vector` 相比：Vector 增删改查方法都加了 `synchronized`，性能下降明显。而 `CopyOnWriteArrayList` 只在增删改上加锁，读不加锁，适合**读多写少**的并发场景。

---

### 十三、阻塞队列

阻塞队列在普通队列基础上增加了两个附加操作：当队列为空时获取元素的线程会等待，当队列满时存储元素的线程会等待。这一特性使其成为**生产者-消费者模式**的天然实现。

#### JDK 7 提供的 7 个阻塞队列

- **ArrayBlockingQueue**：数组结构的有界阻塞队列
- **LinkedBlockingQueue**：链表结构的有界阻塞队列
- **PriorityBlockingQueue**：支持优先级排序的无界阻塞队列
- **DelayQueue**：使用优先级队列实现的无界阻塞队列
- **SynchronousQueue**：不存储元素的阻塞队列
- **LinkedTransferQueue**：链表结构的无界阻塞队列
- **LinkedBlockingDeque**：链表结构的双向阻塞队列

`BlockingQueue` 接口的主要用途不是作为容器，而是作为**线程同步工具**。最经典的应用场景就是 Socket 客户端数据的读取和解析——读取数据的线程不断将数据放入队列，解析线程不断从队列取数据解析。

---

### 十四、其他并发知识点

#### Thread.sleep(0) 的作用

由于 Java 采用抢占式的线程调度算法，可能出现某条线程常常获取到 CPU 控制权的情况。`Thread.sleep(0)` 可以手动触发一次操作系统分配时间片的操作，让优先级较低的线程也有机会获取到 CPU 控制权——这是平衡 CPU 控制权的一种技巧。

#### Java 内存模型（JMM）

Java 内存模型定义了多线程访问 Java 内存的规范：

1. 将内存分为**主内存和工作内存**。共享变量存储在主内存中，线程读取时在工作内存中保留一份拷贝，操作完后更新回主内存。
2. 定义了几个原子操作，用于操作主内存和工作内存中的变量。
3. 定义了 volatile 变量的使用规则。
4. **happens-before 原则**：只要符合这些规则，就不需要额外做同步措施。不符合的代码一定是线程不安全的。

#### 线程池队列已满时的处理

1. **无界队列（LinkedBlockingQueue）**：继续添加任务到阻塞队列中等待执行
2. **有界队列（ArrayBlockingQueue）**：首先会根据 `maximumPoolSize` 增加线程数量，如果还处理不过来，则使用**拒绝策略** `RejectedExecutionHandler` 处理（默认是 `AbortPolicy`）

---

### 十五、参考资料

- 并发编程 <https://segmentfault.com/a/1190000022039255>
- 高并发中的线程通信 <https://mp.weixin.qq.com/s/Gtz6aVPm-YnSh5pjs5JhkA>
- 高频多线程&并发面试题 <https://c.lanmit.com/bianchengkaifa/Java/53679.html>
- Java 编程艺术笔记 <https://www.jianshu.com/p/8d90dc5b341e>
- 面试题 <https://blog.csdn.net/qq_34039315/article/details/78549311>
- <https://mp.weixin.qq.com/s/oL2Vrsr2IcT_8oncdcwf-g>
- <https://mp.weixin.qq.com/s/rqzlISVShFqmo-96Hw2ZNA>
- <https://mp.weixin.qq.com/s/Ya_aw4_4s8UdZ-y9YjMiFw>
