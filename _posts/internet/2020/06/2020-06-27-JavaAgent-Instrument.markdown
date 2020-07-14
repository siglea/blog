---
layout: post
title:  "JavaAgent-Instrument"
date:   2020-06-27 22:25:00 +0900
comments: true
tags:
- Java
categories:
- 技术
---
#### JavaAgent & Instrumentation & JWMTI Agent  (JVM Tool Interface)
- 定义：在JDK1.5以后，我们可以使用agent技术构建一个独立于应用程序的代理程序（即为Agent），用来协助监测、运行甚至替换其他JVM上的程序。使用它可以实现虚拟机级别的AOP功能。
- 我们日常应用的各种工具中，有很多都是基于他们实现的，例如常见的热部署（JRebel, spring-loaded）、各种线上诊断工具（btrace, Greys）、代码覆盖率工具（JaCoCo）等等。

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

<img src="/img/JavaAgent.jpg" width="600px">

- <https://www.jianshu.com/p/be68d66afb85>
- <https://www.jianshu.com/p/b72f66da679f>

#### ASM & CGlib 
<img src="/img/AOP.jpg" width="600px">

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
        enhancedSuperName = name; // 改变父类，这里是”Account”
        super.visit(version, access, enhancedName, signature, 
        enhancedSuperName, interfaces); 
    }

}
```

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
- <https://www.ibm.com/developerworks/cn/java/j-lo-asm30/>

#### Byte Buddy,Javassist
- Byte Buddy的作者是业界著名的Rafael Winterhalter。这个项目在2015年获得了Oracle的公爵选择奖，为了表彰它“对于Java技术创新作出的无与伦比的贡献”。说实话，这个评价实至名归。Byte Buddy确实是Java这个中规中矩略显死板的语言中不多的黑科技之一。
<https://zhuanlan.zhihu.com/p/84514959>
- Javassist是一个开源的分析、编辑和创建Java字节码的类库。是由东京工业大学的数学和计算机科学系的 Shigeru Chiba （千叶 滋）所创建的。它已加入了开放源代码JBoss 应用服务器项目,通过使用Javassist对字节码操作为JBoss实现动态AOP框架。javassist是jboss的一个子项目，其主要的优点，在于简单，而且快速。直接使用java编码的形式，而不需要了解虚拟机指令，就能动态改变类的结构，或者动态生成类。
<https://blog.csdn.net/ShuSheng0007/article/details/81269295>