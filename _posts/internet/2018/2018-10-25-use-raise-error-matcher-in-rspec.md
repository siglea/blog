---
layout: post
title:  "RSpec 中 raise_error 匹配器的正确用法与常见陷阱"
date:   2018-10-25 11:30:09 +0900
comments: true
tags:
- programming
categories:
- 技术
---

在 Ruby 项目的测试中，验证代码是否正确抛出异常是一个常见需求。RSpec 提供了 `raise_error` 匹配器来处理这类断言，但它的使用方式有一个不太直觉的"坑"——如果你用错了语法，测试会在断言之前就崩溃。本文将深入解析这个问题的原因，并给出正确的写法。

## 问题场景

假设我们有一段代码，在某些条件下会抛出 `SomeError` 异常，我们想测试这个行为。最自然的写法可能是：

```ruby
it { is_expected.to raise_error(SomeError) }
```

然而运行这个测试后，你不会看到绿色的通过信息，而是看到测试直接报错中断了——异常在 `raise_error` 有机会捕获之前就已经抛出。

## 根本原因：值表达式 vs 块表达式

理解这个问题的关键在于区分 RSpec 中的两种 `expect` 形式：

### 值表达式（Value Expression）

```ruby
expect(subject)
```

这里 `subject` 会被**立即求值**，其返回值传给 `expect`。如果 `subject` 在求值过程中抛出了异常，异常会直接冒泡到测试框架，`raise_error` 匹配器根本没有机会介入。

`is_expected.to` 是 `expect(subject).to` 的简写，所以它本质上也是值表达式。

### 块表达式（Block Expression）

```ruby
expect { subject }
```

这里传给 `expect` 的是一个**块（Block）**，代码不会立即执行。`raise_error` 匹配器会在自己的上下文中执行这个块，并捕获其中抛出的异常进行匹配。

这就是为什么 `raise_error` **必须配合块表达式使用**。

## 正确写法

### 写法一：直接使用块表达式（推荐）

```ruby
subject { some_method_that_raises }

it 'raises SomeError' do
  expect { subject }.to raise_error(SomeError)
end
```

这是最清晰、最常用的写法。`expect { subject }` 将 `subject` 的执行包装在块中，`raise_error` 可以正确捕获异常。

### 写法二：将 subject 定义为 Lambda

```ruby
subject { -> { raise SomeError } }

it { is_expected.to raise_error(SomeError) }
```

这种写法将 `subject` 本身定义为一个 Lambda（Proc 对象），所以 `expect(subject)` 求值得到的是一个 Lambda 而不是异常。RSpec 检测到 `subject` 是一个 callable 对象时，会自动调用它。

虽然语法上更紧凑，但 Lambda 包装的写法可读性较差，在团队协作中不推荐。

## 更多 raise_error 用法

`raise_error` 匹配器支持多种匹配方式：

### 匹配异常类型

```ruby
expect { dangerous_operation }.to raise_error(ArgumentError)
```

### 匹配异常消息

```ruby
expect { dangerous_operation }.to raise_error("invalid input")
```

### 同时匹配类型和消息

```ruby
expect { dangerous_operation }.to raise_error(ArgumentError, "invalid input")
```

### 使用正则匹配消息

```ruby
expect { dangerous_operation }.to raise_error(ArgumentError, /invalid/)
```

### 使用块进行复杂断言

```ruby
expect { dangerous_operation }.to raise_error(ArgumentError) do |error|
  expect(error.message).to include("invalid")
  expect(error.cause).to be_nil
end
```

### 验证不抛出异常

```ruby
expect { safe_operation }.not_to raise_error
```

注意：`not_to raise_error` 后面不要指定具体异常类型。`expect { x }.not_to raise_error(SomeError)` 这种写法已经被 RSpec 废弃，因为它可能掩盖其他意料之外的异常。

## 类似的块匹配器

除了 `raise_error`，RSpec 中还有其他需要块表达式的匹配器：

```ruby
expect { @count += 1 }.to change { @count }.by(1)

expect { post :create, params: { user: attrs } }.to change(User, :count).by(1)

expect { long_running_task }.to perform_under(200).ms

expect { puts "hello" }.to output("hello\n").to_stdout
```

这些匹配器的共同特点是：它们需要观察**一段代码执行前后的变化**或**执行过程中的行为**，因此必须使用块表达式。

## 总结

| 写法 | 是否正确 | 原因 |
|------|---------|------|
| `expect(subject).to raise_error(...)` | 错误 | subject 立即求值，异常在匹配前抛出 |
| `is_expected.to raise_error(...)` | 错误 | 等价于上面的写法 |
| `expect { subject }.to raise_error(...)` | 正确 | 块延迟执行，匹配器可以捕获异常 |
| `subject { -> { ... } }` + `is_expected.to` | 正确但不推荐 | 可读性差 |

核心原则：**凡是需要观察代码执行行为（而非返回值）的匹配器，都必须使用块表达式 `expect { ... }`**。

参考资料：[RSpec GitHub Issue #805 - raise_error 与 is_expected 的讨论](https://github.com/rspec/rspec-expectations/issues/805#issuecomment-112239820)
