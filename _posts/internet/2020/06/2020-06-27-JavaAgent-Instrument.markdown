---
layout: post
title:  "深入理解 Java Agent 与字节码增强技术"
date:   2020-06-27 22:25:00 +0900
comments: true
tags:
- Java
categories:
- 技术
---

在 Java 生态中，字节码增强技术是一项极具威力的底层能力。无论是热部署工具 JRebel、线上诊断利器 BTrace/Arthas，还是代码覆盖率工具 JaCoCo，它们的核心都依赖于 JVM 提供的 Agent 与 Instrumentation 机制。本文将从 Java Agent 的基本概念出发，结合 ASM、CGlib、Byte Buddy、Javassist 等字节码操作框架，系统梳理 Java 字节码增强技术的全貌。

---

### 一、Java Agent、Instrumentation 与 JVMTI

#### 1.1 什么是 Java Agent

自 JDK 1.5 起，Java 引入了 Agent 技术，允许开发者构建一个独立于应用程序的**代理程序（Agent）**，用来协助监测、运行甚至替换其他 JVM 上的程序。借助 Agent，我们可以实现虚拟机级别的 AOP 功能——在不修改原始代码的前提下，对类的加载和行为进行拦截与改写。

日常开发中，许多工具都基于这一机制实现：
- **热部署**：JRebel、spring-loaded
- **线上诊断**：BTrace、Greys、Arthas
- **代码覆盖率**：JaCoCo

#### 1.2 Instrumentation 接口

`Instrumentation` 是 Java Agent 的核心接口，提供了对类加载过程进行拦截和修改的能力。其关键方法如下：

```java
public interface Instrumentation {
    /**
     * 注册一个Transformer，从此之后的类加载都会被Transformer拦截。
     * Transformer可以直接对类的字节码byte[]进行修改
     */
    void addTransformer(ClassFileTransformer transformer);
    
    /**
     * 对JVM已经加载的类重新触发类加载。使用的就是上面注册的Transformer。
     * retransformation可以修改方法体，但是不能变更方法签名、增加和删除方法/类的成员属性
     */
    void retransformClasses(Class<?>... classes) throws UnmodifiableClassException;
    
    /**
     * 获取一个对象的大小
     */
    long getObjectSize(Object objectToSize);
    
    /**
     * 将一个jar加入到bootstrap classloader的 classpath里
     */
    void appendToBootstrapClassLoaderSearch(JarFile jarfile);
    
    /**
     * 获取当前被JVM加载的所有类对象
     */
    Class[] getAllLoadedClasses();
}
```

从接口定义可以看出，`Instrumentation` 不仅能在类加载时拦截字节码，还能对**已经加载的类**进行重新转换（retransform），以及获取 JVM 级别的对象大小和类信息——这些能力是普通 Java 代码无法触及的。

#### 1.3 Agent 的两种加载方式

Java Agent 提供了两种入口方法，分别对应不同的加载时机：

```java
/**
 * 以vm参数的形式载入，在程序main方法执行之前执行
 * 其jar包的manifest需要配置属性Premain-Class
 */
public static void premain(String agentArgs, Instrumentation inst);
/**
 * 以Attach的方式载入，在Java程序启动后执行
 * 其jar包的manifest需要配置属性Agent-Class
 */
public static void agentmain(String agentArgs, Instrumentation inst);
```

- **premain**：通过 JVM 启动参数 `-javaagent:agent.jar` 载入，在应用的 `main` 方法之前执行。适合在程序启动阶段就注入增强逻辑。
- **agentmain**：通过 JVM Attach API 在运行时动态载入。适合线上诊断场景，如 Arthas 就是通过 Attach 机制连接到目标 JVM 的。

#### 1.4 实战示例：使用 Javassist 实现方法耗时统计

下面的示例展示了如何编写一个 Java Agent，利用 Javassist 在类加载时动态修改字节码，为指定类的所有方法添加耗时统计：

```java
public class InstrumentationExample {
    // Java agent指定的premain方法，会在main方法之前被调用
    public static void premain(String args, Instrumentation inst) {
        // Instrumentation提供的addTransformer方法，在类加载时会回调ClassFileTransformer接口
        inst.addTransformer(new ClassFileTransformer() {
            @Override
            public byte[] transform(ClassLoader loader, String className, Class<?> classBeingRedefined,
                                    ProtectionDomain protectionDomain, byte[] classfileBuffer)
                                    throws IllegalClassFormatException {
                if (!"com/test/TestClass".equals(className)) {
                    // 只修改指定的Class
                    return classfileBuffer;
                }
        
                byte[] transformed = null;
                CtClass cl = null;
                try {
                    // CtClass、ClassPool、CtMethod、ExprEditor都是javassist提供的字节码操作的类
                    ClassPool pool = ClassPool.getDefault();
                    cl = pool.makeClass(new ByteArrayInputStream(classfileBuffer));
                    CtMethod[] methods = cl.getDeclaredMethods();
                    for (int i = 0; i < methods.length; i++) {
                        methods[i].instrument(new ExprEditor() {
        
                            @Override
                            public void edit(MethodCall m) throws CannotCompileException {
                                // 把方法体直接替换掉，其中 $proceed($$);是javassist的语法，用来表示原方法体的调用
                                m.replace("{ long stime = System.currentTimeMillis();" + " $_ = $proceed($$);"
                                          + "System.out.println(\"" + m.getClassName() + "." + m.getMethodName()
                                          + " cost:\" + (System.currentTimeMillis() - stime) + \" ms\"); }");
                            }
                        });
                    }
                    // javassist会把输入的Java代码再编译成字节码byte[]
                    transformed = cl.toBytecode();
                } catch (Exception e) {
                    e.printStackTrace();
                } finally {
                    if (cl != null) {
                        cl.detach();// ClassPool默认不会回收，需要手动清理
                    }                           
                }
                return transformed;
            }
        });
    }
    
}
```

这段代码的核心流程是：注册一个 `ClassFileTransformer`，在类加载时判断是否为目标类，若是则利用 Javassist 解析字节码、遍历所有方法并注入耗时统计代码，最后返回修改后的字节码数组。

下图展示了 Java Agent 的整体工作流程：

<img src="{{ site.baseurl }}/img/java-agent/JavaAgent.jpg" width="600px">

**参考资料：**
- <https://www.jianshu.com/p/be68d66afb85>
- <https://www.jianshu.com/p/b72f66da679f>

---

### 二、ASM 与 CGlib：底层字节码操作

#### 2.1 ASM 框架概述

ASM 是一个轻量级的 Java 字节码操作框架，采用**访问者模式（Visitor Pattern）** 遍历和修改 Class 文件结构。与 Javassist 不同，ASM 直接操作字节码指令，性能更高但学习曲线也更陡峭。CGlib 正是基于 ASM 实现的动态代理框架。

下图展示了 Java AOP 技术栈中各框架的层级关系：

<img src="{{ site.baseurl }}/img/java-agent/AOP.jpg" width="600px">

#### 2.2 ASM 实现安全检查注入

以下示例演示了如何使用 ASM 为目标类的 `operation` 方法注入安全检查逻辑，并通过动态生成子类的方式实现代理：

**ClassAdapter**——在访问到 `operation` 方法时替换为自定义的 MethodVisitor：

```java
class AddSecurityCheckClassAdapter extends ClassAdapter {
 
    public AddSecurityCheckClassAdapter(ClassVisitor cv) {
        //Responsechain 的下一个 ClassVisitor，这里我们将传入 ClassWriter，
        // 负责改写后代码的输出
        super(cv); 
    } 
     
    // 重写 visitMethod，访问到 "operation" 方法时，
    // 给出自定义 MethodVisitor，实际改写方法内容
    public MethodVisitor visitMethod(final int access, final String name, 
        final String desc, final String signature, final String[] exceptions) { 
        MethodVisitor mv = cv.visitMethod(access, name, desc, signature,exceptions);
        MethodVisitor wrappedMv = mv; 
        if (mv != null) { 
            // 对于 "operation" 方法
            if (name.equals("operation")) { 
                // 使用自定义 MethodVisitor，实际改写方法内容
                wrappedMv = new AddSecurityCheckMethodAdapter(mv); 
            } 
        } 
        return wrappedMv; 
    } 

    public MethodVisitor visitMethod(final int access, final String name, 
        final String desc, final String signature, final String[] exceptions) { 
        MethodVisitor mv = cv.visitMethod(access, name, desc, signature, exceptions); 
        MethodVisitor wrappedMv = mv; 
        if (mv != null) { 
            if (name.equals("operation")) { 
                wrappedMv = new AddSecurityCheckMethodAdapter(mv); 
            } else if (name.equals("<init>")) { 
                wrappedMv = new ChangeToChildConstructorMethodAdapter(mv, 
                    enhancedSuperName); 
            } 
        } 
        return wrappedMv; 
    }

    
    public void visit(final int version, final int access, final String name, 
            final String signature, final String superName, 
            final String[] interfaces) { 
        String enhancedName = name + "$EnhancedByASM";  // 改变类命名
        enhancedSuperName = name; // 改变父类，这里是"Account"
        super.visit(version, access, enhancedName, signature, 
        enhancedSuperName, interfaces); 
    }

}
```

**MethodAdapter**——在方法入口处插入安全检查调用：

```java
class AddSecurityCheckMethodAdapter extends MethodAdapter { 
    public AddSecurityCheckMethodAdapter(MethodVisitor mv) { 
        super(mv); 
    } 
 
    public void visitCode() { 
        visitMethodInsn(Opcodes.INVOKESTATIC, "SecurityChecker", 
           "checkSecurity", "()V"); 
    } 
}
```

**构造函数适配器**——确保动态生成的子类正确调用父类构造函数：

```java
class ChangeToChildConstructorMethodAdapter extends MethodAdapter { 
    private String superClassName; 
 
    public ChangeToChildConstructorMethodAdapter(MethodVisitor mv, 
        String superClassName) { 
        super(mv); 
        this.superClassName = superClassName; 
    } 
 
    public void visitMethodInsn(int opcode, String owner, String name, 
        String desc) { 
        // 调用父类的构造函数时
        if (opcode == Opcodes.INVOKESPECIAL && name.equals("<init>")) { 
            owner = superClassName; 
        } 
        super.visitMethodInsn(opcode, owner, name, desc);// 改写父类为 superClassName 
    } 
}
```

**将以上组件串联起来**——ClassReader 读取原始字节码，经过 ClassAdapter 改写后由 ClassWriter 输出新的字节码，最终通过自定义 ClassLoader 加载：

```java
public class SecureAccountGenerator { 
 
    private static AccountGeneratorClassLoader classLoader = 
        new AccountGeneratorClassLoade(); 
     
    private static Class secureAccountClass; 
     
    public Account generateSecureAccount() throws ClassFormatError, 
        InstantiationException, IllegalAccessException { 
        if (null == secureAccountClass) {            
            ClassReader cr = new ClassReader("Account"); 
            ClassWriter cw = new ClassWriter(ClassWriter.COMPUTE_MAXS); 
            ClassAdapter classAdapter = new AddSecurityCheckClassAdapter(cw);
            cr.accept(classAdapter, ClassReader.SKIP_DEBUG); 
            byte[] data = cw.toByteArray(); 
            secureAccountClass = classLoader.defineClassFromClassFile( 
               "Account$EnhancedByASM",data); 
        } 
        return (Account) secureAccountClass.newInstance(); 
    } 
     
    private static class AccountGeneratorClassLoader extends ClassLoader {
        public Class defineClassFromClassFile(String className, 
            byte[] classFile) throws ClassFormatError { 
            return defineClass("Account$EnhancedByASM", classFile, 0, 
            classFile.length());
        } 
    } 
}
```

这种模式（ClassReader → ClassAdapter → ClassWriter）是 ASM 的经典使用范式。CGlib 在此基础上做了更高级的封装，使动态代理的创建更加便捷。

**参考资料：**
- <https://www.ibm.com/developerworks/cn/java/j-lo-asm30/>

---

### 三、Byte Buddy 与 Javassist：更友好的字节码操作

除了底层的 ASM 之外，社区还提供了更高级别的字节码操作框架，让开发者无需直接与虚拟机指令打交道。

#### 3.1 Byte Buddy

Byte Buddy 由 Rafael Winterhalter 开发，在 2015 年荣获 Oracle 公爵选择奖（Duke's Choice Award），被赞誉为"对 Java 技术创新作出无与伦比的贡献"。Byte Buddy 提供了流畅的 API 设计，能够在运行时动态创建和修改类，是 Java 生态中不多的"黑科技"之一。Mockito 从 2.x 版本开始就底层使用 Byte Buddy 来生成 Mock 对象。

**参考资料：**
- <https://zhuanlan.zhihu.com/p/84514959>

#### 3.2 Javassist

Javassist 是由东京工业大学的千叶滋（Shigeru Chiba）教授创建的开源字节码操作类库。它已加入 JBoss 开源项目，为 JBoss 实现动态 AOP 框架提供了底层支持。Javassist 最大的优点在于**简单且快速**——开发者可以直接使用 Java 编码的形式来动态改变类的结构或生成新类，而不需要了解虚拟机指令，极大地降低了字节码操作的门槛。

**参考资料：**
- <https://blog.csdn.net/ShuSheng0007/article/details/81269295>

---

### 四、总结

Java 字节码增强技术体系可以按抽象层次从低到高排列：

| 层次 | 代表技术 | 特点 |
|------|----------|------|
| JVM 级别 | Java Agent + Instrumentation + JVMTI | 提供类加载拦截与运行时重定义能力 |
| 底层框架 | ASM | 直接操作字节码指令，性能最优 |
| 中层框架 | CGlib（基于 ASM） | 封装动态代理生成 |
| 高层框架 | Javassist、Byte Buddy | 以 Java 源码或流畅 API 方式操作字节码 |

在实际项目中，应根据场景选择合适的工具：如果追求极致性能（如 APM 探针），优先考虑 ASM；如果追求开发效率和可维护性，Byte Buddy 和 Javassist 是更好的选择。无论使用哪种工具，Java Agent + Instrumentation 都是实现非侵入式增强的基础——理解这一机制，是掌握 Java 高级技术的重要一步。
