---
layout: post
title:  "Java Concurrent"
date:   2019-11-12 11:25:00 +0900
comments: true
tags:
- Java
categories:
- 技术
---
#### 绝对线程安全和相对线程安全
- <https://www.cnblogs.com/duanxz/p/6099983.html>
- <https://www.jianshu.com/p/98b0241bc8e2>
- 可见性、有序性、原子性

#### AQS AbstractQueuedSynchronizer
- AbstractQueuedSynchronizer 类如其名，抽象的队列式的同步器，AQS 定义了一套多线程访问,共享资源的同步器框架，许多同步类实现都依赖于它，如常用的 ReentrantLock/Semaphore/CountDownLatch。
- AQS 定义两种资源共享方式
    - Exclusive(独占资源，只有一个线程能执行，如 ReentrantLock)
    - Share(共享资源，多个线程可同时执行，如 Semaphore/CountDownLatch)
- CLH锁,CLH CLH(Craig, Landin, and Hagersten locks): 是一个自旋锁，能确保无饥饿性，提供先来先服务的公平性。
  CLH锁也是一种基于链表的可扩展、高性能、公平的自旋锁，申请线程只在本地变量上自旋，它不断轮询前驱的状态，如果发现前驱释放了锁就结束自旋。
  <https://www.jianshu.com/p/4682a6b0802d>
  <https://www.jianshu.com/p/d291a6a1879c>
  
#### CAS Compare And Swap
- CAS(Compare And Swap/Set)比较并交换，CAS 算法的过程是这样:它包含 3 个参数 CAS(V,E,N)。V 表示要更新的变量(内存值)，E 表示预期值(旧的)，N 表示新值。当且仅当 V 值等于 E 值时，才会将 V 的值设为 N，如果 V 值和 E 值不同，则说明已经有其他线程做了更新，则当 前线程什么都不做。最后，CAS 返回当前 V 的真实值。CAS 操作是抱着乐观的态度进行的(乐观锁)，它总是认为自己可以成功完成操作。当多个线程同时 使用 CAS 操作一个变量时，只有一个会胜出，并成功更新，其余均会失败。失败的线程不会被挂 起，仅是被告知失败，并且允许再次尝试，当然也允许失败的线程放弃操作。基于这样的原理， CAS 操作即使没有锁，也可以发现其他线程对当前线程的干扰，并进行恰当的处理。

#### volatile 关键字的作用(变量可见性、禁止重排序)
- Java 语言提供了一种稍弱的同步机制，即 volatile 变量，用来确保将变量的更新操作通知到其他 线程。volatile 变量具备两种特性，volatile 变量不会被缓存在寄存器或者对其他处理器不可见的 地方，因此在读取 volatile 类型的变量时总会返回最新写入的值。
- 变量可见性,其一是保证该变量对所有线程可见，这里的可见性指的是当一个线程修改了变量的值，那么新的 值对于其他线程是可以立即获取的。
- 在访问 volatile 变量时不会执行加锁操作，因此也就不会使执行线程阻塞，因此 volatile 变量是一 种比 sychronized 关键字更轻量级的同步机制。volatile 适合这种场景:一个变量被多个线程共 享，线程直接给这个变量赋值。
- 当对非 volatile 变量进行读写的时候，每个线程先从内存拷贝变量到 CPU 缓存中。如果计算机有 多个 CPU，每个线程可能在不同的 CPU 上被处理，这意味着每个线程可以拷贝到不同的 CPU cache 中。而声明变量是 volatile 的，JVM 保证了每次读变量都从内存中读，跳过 CPU cache 这一步。
- 适用场景,值得说明的是对 volatile 变量的单次读/写操作可以保证原子性的，如 long 和 double 类型变量， 但是并不能保证 i++这种操作的原子性，因为本质上 i++是读、写两次操作。在某些场景下可以 代替 Synchronized。但是,volatile 的不能完全取代 Synchronized 的位置，只有在一些特殊的场
  景下，才能适用 volatile。总的来说，必须同时满足下面两个条件才能保证在并发环境的线程安全:
  1. 对变量的写操作不依赖于当前值(比如 i++)，或者说是单纯的变量赋值(boolean flag = true)。
  2. 该变量没有包含在具有其他变量的不变式中，也就是说，不同的 volatile 变量之间，不 能互相依赖。只有在状态真正独立于程序内其他内容时才能使用 volatile。

#### 锁状态 无锁状态、偏向锁、轻量级锁和重量级锁
- 偏向锁，Hotspot 的作者经过以往的研究发现大多数情况下锁不仅不存在多线程竞争，而且总是由同一线
      程多次获得。偏向锁的目的是在某个线程获得锁之后，消除这个线程锁重入(CAS)的开销，看起
      来让这个线程得到了偏护。引入偏向锁是为了在无多线程竞争的情况下尽量减少不必要的轻量级
      锁执行路径，因为轻量级锁的获取及释放依赖多次 CAS 原子指令，而偏向锁只需要在置换
      ThreadID 的时候依赖一次 CAS 原子指令(由于一旦出现多线程竞争的情况就必须撤销偏向锁，所
      以偏向锁的撤销操作的性能损耗必须小于节省下来的 CAS 原子指令的性能消耗)。上面说过，轻
      量级锁是为了在线程交替执行同步块时提高性能，而偏向锁则是在只有一个线程执行同步块时进
      一步提高性能。
- 锁升级， 随着锁的竞争，锁可以从偏向锁升级到轻量级锁，再升级的重量级锁(但是锁的升级是单向的，
       也就是说只能从低到高升级，不会出现锁的降级)。
      “轻量级”是相对于使用操作系统互斥量来实现的传统锁而言的。但是，首先需要强调一点的是，
      轻量级锁并不是用来代替重量级锁的，它的本意是在没有多线程竞争的前提下，减少传统的重量
      级锁使用产生的性能消耗。在解释轻量级锁的执行过程之前，先明白一点，轻量级锁所适应的场
      景是线程交替执行同步块的情况，如果存在同一时间访问同一锁的情况，就会导致轻量级锁膨胀
      为重量级锁。
- 重量级锁(Mutex Lock)，Synchronized 是通过对象内部的一个叫做监视器锁(monitor)来实现的。但是监视器锁本质又
      是依赖于底层的操作系统的 Mutex Lock 来实现的。而操作系统实现线程之间的切换这就需要从用
      户态转换到核心态，这个成本非常高，状态之间的转换需要相对比较长的时间，这就是为什么
      Synchronized 效率低的原因。因此，这种依赖于操作系统 Mutex Lock 所实现的锁我们称之为
      “重量级锁”。JDK 中对 Synchronized 做的种种优化，其核心都是为了减少这种重量级锁的使用。
      JDK1.6 以后，为了减少获得锁和释放锁所带来的性能消耗，提高性能，引入了“轻量级锁”和
      “偏向锁”。

#### 锁使用
- Synchronized 同步锁（Jvm monitor）
- ReentrantLock 可重入锁（Lock接口、Condition)
  - 核心类AbstractQueuedSynchronizer，通过构造一个基于阻塞的CLH队列容纳所有的阻塞线程，而对该队列的操作均通过Lock-Free（CAS）操作，但对已经获得锁的线程而言，ReentrantLock实现了偏向锁的功能。
- ReentrantReadWriteLock 可重入读写锁（ReadWriteLock接口、Condition)
  - ReadLock和WriteLock：都是Lock实现类，分别实现了读、写锁。ReadLock是共享的，而WriteLock是独占的。于是Sync类覆盖了AQS中独占和共享模式的抽象方法(tryAcquire/tryAcquireShared等)，用同一个等待队列来维护读/写排队线程，而用一个32位int state标示和记录读/写锁重入次数--Doug Lea把状态的高16位用作读锁，记录所有读锁重入次数之和，低16位用作写锁，记录写锁重入次数。所以无论是读锁还是写锁最多只能被持有65535次。
- StampedLock 戳锁,
  - 有三种模式（排它写，悲观读，乐观读），一个StampedLock状态是由版本和模式两个部分组成，锁获取方法返回一个数字作为票据stamp，它用相应的锁状态表示并控制访问。

<https://www.cnblogs.com/dennyzhangdd/p/6925473.html>

##### Condition
1. Condition是在java 1.5中才出现的，它用来替代传统的Object的wait()、notify()实现线程间的协作，相比使用Object的wait()、notify()，使用Condition的await()、signal()这种方式实现线程间协作更加安全和高效。因此通常来说比较推荐使用Condition。
    Condition类能实现synchronized和wait、notify搭配的功能，另外比后者更灵活，Condition可以实现多路通知功能，也就是在一个Lock对象里可以创建多个Condition（即对象监视器）实例，线程对象可以注册在指定的Condition中，从而可以有选择的进行线程通知，在调度线程上更加灵活。而synchronized就相当于整个Lock对象中只有一个单一的Condition对象，所有的线程都注册在这个对象上。线程开始notifyAll时，需要通知所有的WAITING线程，没有选择权，会有相当大的效率问题。
1. Condition是个接口，基本的方法就是await()和signal()方法。
1. Condition依赖于Lock接口，生成一个Condition的基本代码是lock.newCondition()，参考下图。 
1. 调用Condition的await()和signal()方法，都必须在lock保护之内，就是说必须在lock.lock()和lock.unlock之间才可以使用。
1. Conditon中的await()对应Object的wait()，Condition中的signal()对应Object的notify()，Condition中的signalAll()对应Object的notifyAll()。

##### LockSupport.park()和unpark()，与object.wait()和notify()的区别？
- 主要的区别应该说是它们面向的对象不同。阻塞和唤醒是对于线程来说的，LockSupport的park/unpark更符合这个语义，以“线程”作为方法的参数， 语义更清晰，使用起来也更方便。而wait/notify的实现使得“阻塞/唤醒对线程本身来说是被动的，要准确的控制哪个线程、什么时候阻塞/唤醒很困难， 要不随机唤醒一个线程（notify）要不唤醒所有的（notifyAll）。
- <https://www.jianshu.com/p/ceb8870ef2c5>
- <https://www.jianshu.com/p/e3afe8ab8364>

##### synchronized 和 ReentrantLock 的区别
- 两者的共同点:
    1. 都是用来协调多线程对共享对象、变量的访问
    1. 都是可重入锁，同一线程可以多次获得同一个锁
    1. 都保证了可见性和互斥性
- 两者的不同点:
1. ReentrantLock 显示的获得、释放锁，synchronized 隐式获得释放锁
1. ReentrantLock 可响应中断、可轮回，synchronized 是不可以响应中断的，为处理锁的不可用性提供了更高的灵活性
1. ReentrantLock 是 API 级别的，synchronized 是 JVM 级别的
1. ReentrantLock 可以实现公平锁
1. ReentrantLock 通过 Condition 可以绑定多个条件
1. 底层实现不一样， synchronized 是同步阻塞，使用的是悲观并发策略，lock 是同步非阻塞，采用的是乐观并发策略
1. Lock 是一个接口，而 synchronized 是 Java 中的关键字，synchronized 是内置的语言实现。
1. synchronized 在发生异常时，会自动释放线程占有的锁，因此不会导致死锁现象发生;而Lock 在发生异常时，如果没有主动通过 unLock()去释放锁，则很可能造成死锁现象，因此使用 Lock 时需要在 finally 块中释放锁。
1. Lock 可以让等待锁的线程响应中断，而 synchronized 却不行，使用 synchronized 时，等待的线程会一直等待下去，不能够响应中断。
1. 通过 Lock 可以知道有没有成功获取锁，而 synchronized 却无法办到。
1. Lock 可以提高多个线程进行读操作的效率，既就是实现读写锁等。

#### 锁优化
- 减少锁持有时间，
  只用在有线程安全要求的程序上加锁
- 减小锁粒度，  
    将大对象(这个对象可能会被很多线程访问)，拆成小对象，大大增加并行度，降低锁竞争。
    降低了锁的竞争，偏向锁，轻量级锁成功率才会提高。最最典型的减小锁粒度的案例就是ConcurrentHashMap
- 锁分离，
    最常见的锁分离就是读写锁 ReadWriteLock，根据功能进行分离成读锁和写锁，这样读读不互
    斥，读写互斥，写写互斥，即保证了线程安全，又提高了性能。
    JDK 并发包 1。读写分离思想可以延伸，只要操作互不影响，锁就可以分离。比如
    LinkedBlockingQueue 从头部取出，从尾部放数据
- 锁粗化，通常情况下，为了保证多线程间的有效并发，会要求每个线程持有锁的时间尽量短，即在使用完
      公共资源后，应该立即释放锁。但是，凡事都有一个度，如果对同一个锁不停的进行请求、同步
      和释放，其本身也会消耗系统宝贵的资源，反而不利于性能的优化 。
- 锁消除， 锁消除是在编译器级别的事情。在即时编译器时，如果发现不可能被共享的对象，则可以消除这
       些对象的锁操作，多数是因为程序员编码不规范引起。
       
#### 自旋锁
- 自旋锁原理非常简单，如果持有锁的线程能在很短时间内释放锁资源，那么那些等待竞争锁
    的线程就不需要做内核态和用户态之间的切换进入阻塞挂起状态，它们只需要等一等(自旋)，
    等持有锁的线程释放锁后即可立即获取锁，这样就避免用户线程和内核的切换的消耗。
    线程自旋是需要消耗 cup 的，说白了就是让 cup 在做无用功，如果一直获取不到锁，那线程
    也不能一直占用 cup 自旋做无用功，所以需要设定一个自旋等待的最大时间。
    如果持有锁的线程执行的时间超过自旋等待的最大时间扔没有释放锁，就会导致其它争用锁
    的线程在最大等待时间内还是获取不到锁，这时争用线程会停止自旋进入阻塞状态。
- 自旋锁的优缺点
    自旋锁尽可能的减少线程的阻塞，这对于锁的竞争不激烈，且占用锁时间非常短的代码块来
    说性能能大幅度的提升，因为自旋的消耗会小于线程阻塞挂起再唤醒的操作的消耗，这些操作会
    导致线程发生两次上下文切换!
    但是如果锁的竞争激烈，或者持有锁的线程需要长时间占用锁执行同步块，这时候就不适合
    使用自旋锁了，因为自旋锁在获取锁前一直都是占用 cpu 做无用功，占着 XX 不 XX，同时有大量
    线程在竞争一个锁，会导致获取锁的时间很长，线程自旋的消耗大于线程阻塞挂起操作的消耗，
    其它需要 cup 的线程又不能获取到 cpu，造成 cpu 的浪费。所以这种情况下我们要关闭自旋锁;
- 自旋锁时间阈值(1.6 引入了适应性自旋锁)
    自旋锁的目的是为了占着 CPU 的资源不释放，等到获取到锁立即进行处理。但是如何去选择
    自旋的执行时间呢?如果自旋执行时间太长，会有大量的线程处于自旋状态占用 CPU 资源，进而
    会影响整体系统的性能。因此自旋的周期选的额外重要!
    JVM 对于自旋周期的选择，jdk1.5 这个限度是一定的写死的，在 1.6 引入了适应性自旋锁，适应
    性自旋锁意味着自旋的时间不在是固定的了，而是由前一次在同一个锁上的自旋时间以及锁的拥
    有者的状态来决定，基本认为一个线程上下文切换的时间是最佳的一个时间，同时 JVM 还针对当
    前 CPU 的负荷情况做了较多的优化，如果平均负载小于 CPUs 则一直自旋，如果有超过(CPUs/2)
    个线程正在自旋，则后来线程直接阻塞，如果正在自旋的线程发现 Owner 发生了变化则延迟自旋
    时间(自旋计数)或进入阻塞，如果 CPU 处于节电模式则停止自旋，自旋时间的最坏情况是 CPU
    的存储延迟(CPU A 存储了一个数据，到 CPU B 得知这个数据直接的时间差)，自旋时会适当放
    弃线程优先级之间的差异。
    自旋锁的开启
    
```shell
-XX:+UseSpinning 开启; -XX:PreBlockSpin=10 为自旋次数; // JDK1.6(JDK1.7 后，去掉此参数，由 jvm 控制)
```

#### 重入锁
广义上的可重入锁，而不是单指 JAVA 下的 ReentrantLock。可重入锁，也叫
做递归锁，指的是同一线程 外层函数获得锁之后 ，内层递归函数仍然有获取该锁的代码，但不受
影响。在 JAVA 环境下 ReentrantLock 和 synchronized 都是 可重入锁。

#### 乐观锁、悲观锁
- 乐观锁是一种乐观思想，即认为读多写少，遇到并发写的可能性低，每次去拿数据的时候都认为
别人不会修改，所以不会上锁，但是在更新的时候会判断一下在此期间别人有没有去更新这个数
据，采取在写时先读出当前版本号，然后加锁操作(比较跟上一次的版本号，如果一样则更新)，
如果失败则要重复读-比较-写的操作。
 java 中的乐观锁基本都是通过 CAS 操作实现的，CAS 是一种更新的原子操作，比较当前值跟传入
 值是否一样，一样则更新，否则失败。
- 悲观锁是就是悲观思想，即认为写多，遇到并发写的可能性高，每次去拿数据的时候都认为别人
  会修改，所以每次在读写数据的时候都会上锁，这样别人想读写这个数据就会 block 直到拿到锁。
  java 中的悲观锁就是 Synchronized,AQS 框架下的锁则是先尝试 cas 乐观锁去获取锁，获取不到，
  才会转换为悲观锁，如 RetreenLock。

#### 终止线程
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

#### CyclicBarrier CountDownLatch Semphore
- CountDownLatch和CyclicBarrier都能够实现线程之间的等待，只不过它们侧重点不同：
    CountDownLatch一般用于某个线程A等待若干个其他线程执行完任务之后，它(发起await()的线程)才执行；
    而CyclicBarrier一般用于一组线程互相等待至某个状态，然后这一组线程再同时执行；
    另外，CountDownLatch是不能够重用的，而CyclicBarrier是可以重用的。
- Semaphore其实和锁有点类似，它一般用于控制对某组资源的访问权限
<https://www.cnblogs.com/dolphin0520/p/3920397.html>

#### ConcurrentHashMap ConcurrentSkipListMap ConcurrentLinkedQueue
- SynchronizedMap一次锁住整张表来保证线程安全，所以每次只能有一个线程来访为map。
    ConcurrentHashMap使用分段锁来保证在多线程下的性能。ConcurrentHashMap中则是一次锁住一个桶。ConcurrentHashMap默认将hash表分为16个桶，诸如get,put,remove等常用操作只锁当前需要用到的桶。这样，原来只能一个线程进入，现在却能同时有16个写线程执行，并发性能的提升是显而易见的。
    另外ConcurrentHashMap使用了一种不同的迭代方式。在这种迭代方式中，当iterator被创建后集合再发生改变就不再是抛出ConcurrentModificationException，取而代之的是在改变时new新的数据从而不影响原有的数据 ，iterator完成后再将头指针替换为新的数据 ，这样iterator线程可以使用原来老的数据，而写线程也可以并发的完成改变。

#### CopyOnWriteArrayList 
- 增删改都需要获得锁，并且锁只有一把，而读操作不需要获得锁，支持并发。为什么增删改中都需要创建一个新的数组，操作完成之后再赋给原来的引用？这是为了保证get的时候都能获取到元素，如果在增删改过程直接修改原来的数组，可能会造成执行读操作获取不到数据。
- 我知道Vector是增删改查方法都加了synchronized，保证同步，但是每个方法执行的时候都要去获得锁，性能就会大大下降，而CopyOnWriteArrayList 只是在增删改上加锁，但是读不加锁，在读方面的性能就好于Vector，CopyOnWriteArrayList支持读多写少的并发情况。

#### 阻塞队列
- 这两个附加的操作是：在队列为空时，获取元素的线程会等待队列变为非空。当队列满时，存储元素的线程会等待队列可用。阻塞队列常用于生产者和消费者的场景，生产者是往队列里添加元素的线程，消费者是从队列里拿元素的线程。阻塞队列就是生产者存放元素的容器，而消费者也只从容器里拿元素。
- JDK7提供了7个阻塞队列。分别是：
    - ArrayBlockingQueue ：一个由数组结构组成的有界阻塞队列。
    - LinkedBlockingQueue ：一个由链表结构组成的有界阻塞队列。
    - PriorityBlockingQueue ：一个支持优先级排序的无界阻塞队列。
    - DelayQueue：一个使用优先级队列实现的无界阻塞队列。
    - SynchronousQueue：一个不存储元素的阻塞队列。
    - LinkedTransferQueue：一个由链表结构组成的无界阻塞队列。
    - LinkedBlockingDeque：一个由链表结构组成的双向阻塞队列。
- Java 5之前实现同步存取时，可以使用普通的一个集合，然后在使用线程的协作和线程同步可以实现生产者，消费者模式，主要的技术就是用好，wait ,notify,notifyAll,sychronized这些关键字。而在java 5之后，可以使用阻塞队列来实现，此方式大大简少了代码量，使得多线程编程更加容易，安全方面也有保障。
BlockingQueue接口是Queue的子接口，它的主要用途并不是作为容器，而是作为线程同步的的工具，因此他具有一个很明显的特性，当生产者线程试图向BlockingQueue放入元素时，如果队列已满，则线程被阻塞，当消费者线程试图从中取出一个元素时，如果队列为空，则该线程会被阻塞，正是因为它所具有这个特性，所以在程序中多个线程交替向BlockingQueue中放入元素，取出元素，它可以很好的控制线程之间的通信。
阻塞队列使用最经典的场景就是socket客户端数据的读取和解析，读取数据的线程不断将数据放入队列，然后解析线程不断从队列取数据解析。

#### Thread.sleep(0)的作用是什么
由于Java采用抢占式的线程调度算法，因此可能会出现某条线程常常获取到CPU控制权的情况，为了让某些优先级比较低的线程也能获取到CPU控制权，可以使用Thread.sleep(0)手动触发一次操作系统分配时间片的操作，这也是平衡CPU控制权的一种操作。

#### 什么是Java内存模型
- Java内存模型定义了一种多线程访问Java内存的规范。Java内存模型要完整讲不是这里几句话能说清楚的，我简单总结一下Java内存模型的几部分内容：
1. Java内存模型将内存分为了主内存和工作内存。类的状态，也就是类之间共享的变量，是存储在主内存中的，每次Java线程用到这些主内存中的变量的时候，会读一次主内存中的变量，并让这些内存在自己的工作内存中有一份拷贝，运行自己线程代码的时候，用到这些变量，操作的都是自己工作内存中的那一份。在线程代码执行完毕之后，会将最新的值更新到主内存中去
1. 定义了几个原子操作，用于操作主内存和工作内存中的变量
1. 定义了volatile变量的使用规则
1. happens-before，即先行发生原则，定义了操作A必然先行发生于操作B的一些规则，比如在同一个线程内控制流前面的代码一定先行发生于控制流后面的代码、一个释放锁unlock的动作一定先行发生于后面对于同一个锁进行锁定lock的动作等等，只要符合这些规则，则不需要额外做同步措施，如果某段代码不符合所有的happens-before规则，则这段代码一定是线程非安全的

#### 如果你提交任务时，线程池队列已满，这时会发生什么
1. 如果使用的是无界队列LinkedBlockingQueue，也就是无界队列的话，没关系，继续添加任务到阻塞队列中等待执行，因为LinkedBlockingQueue可以近乎认为是一个无穷大的队列，可以无限存放任务
1. 如果使用的是有界队列比如ArrayBlockingQueue，任务首先会被添加到ArrayBlockingQueue中，ArrayBlockingQueue满了，会根据maximumPoolSize的值增加线程数量，如果增加了线程数量还是处理不过来，ArrayBlockingQueue继续满，那么则会使用拒绝策略RejectedExecutionHandler处理满了的任务，默认是AbortPolicy

#### CyclicBarrier、CountDownLatch、Semaphore 的用法
- CountDownLatch，等多搞一
- CyclicBarrier，等多搞多
- Semaphore，8个工人5台机器

#### 参考资料
并发编程 <https://segmentfault.com/a/1190000022039255>

高并发中的线程通信 <https://mp.weixin.qq.com/s/Gtz6aVPm-YnSh5pjs5JhkA>

高频多线程&并发面试题 <https://c.lanmit.com/bianchengkaifa/Java/53679.html>

Java编程艺术笔记 <https://www.jianshu.com/p/8d90dc5b341e>

面试题 <https://blog.csdn.net/qq_34039315/article/details/78549311>


<https://mp.weixin.qq.com/s/oL2Vrsr2IcT_8oncdcwf-g>

<https://mp.weixin.qq.com/s/rqzlISVShFqmo-96Hw2ZNA>

<https://mp.weixin.qq.com/s/Ya_aw4_4s8UdZ-y9YjMiFw>