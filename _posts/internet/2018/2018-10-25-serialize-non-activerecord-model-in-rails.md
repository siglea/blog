---
layout: post
title:  "在Rails中使用ActiveModel::Serializer序列化非ActiveRecord模型"
date:   2018-10-25 11:30:09 +0900
comments: true
tags:
- Ruby
- Rails
categories:
- 技术
---

在 Rails 开发中，我们通常使用 ActiveModel::Serializer 来控制 JSON 响应的格式。大多数教程都围绕 ActiveRecord 模型展开，但实际项目中经常会遇到需要序列化非 ActiveRecord 对象的场景——比如后端作为中间层对接第三方 API，需要将第三方返回的数据转换为特定的 JSON 格式再输出给前端。

本文将介绍如何使用 `ActiveModelSerializers::Model` 创建可序列化的纯 Ruby 对象，以及如何处理嵌套 JSON 结构。

---

## 背景

在实际项目中，后端服务往往需要连接其他 API 获取数据，然后以特定格式返回给客户端。这些数据并不存储在本地数据库中，自然也没有对应的 ActiveRecord 模型。如果直接手动拼装 Hash 来构建 JSON 响应，代码会变得难以维护且容易出错。

ActiveModel::Serializer 提供了一种优雅的解决方案：即使没有数据库表，我们也可以创建"虚拟模型"，利用 Serializer 的声明式 API 来管理 JSON 输出格式。

---

## 创建可序列化的资源

本文基于 [active_model_serializers 0.10.0](https://github.com/rails-api/active_model_serializers/tree/0-10-stable) 版本。根据文档，`ActiveModel::Serializer` 包装了一个 serializable resource。要创建一个可序列化的资源，我们需要：

1. 创建一个继承 `ActiveModelSerializers::Model` 的纯 Ruby 对象（PORO）
2. 创建对应的 Serializer

### 第一步：定义模型

```rb
class MyModel < ActiveModelSerializers::Model
  def initialize(title:, body:)
    @title = title
    @body = body
  end

  def converted_body
    # do something
  end
end
```

`ActiveModelSerializers::Model` 为普通 Ruby 对象提供了 ActiveModel 兼容的接口，使其可以被 Serializer 识别和处理。模型中可以定义任意方法来进行数据转换和加工。

### 第二步：定义 Serializer

```rb
class MyModelSerializer < ActiveModelSerializers::Serializer
  attributes :converted_body
end
```

Serializer 通过 `attributes` 声明需要输出的字段。这里只输出 `converted_body` 方法的返回值，而不是原始的 `title` 和 `body`。这正是 Serializer 的价值所在——**解耦了内部数据结构和外部 API 输出格式**。

### 使用方式

在 Controller 中使用方式与 ActiveRecord 模型完全一致：

```rb
class ApiController < ApplicationController
  def show
    model = MyModel.new(title: "Hello", body: "World")
    render json: model
  end
end
```

ActiveModelSerializers 会自动根据类名查找对应的 Serializer（`MyModel` → `MyModelSerializer`），无需手动指定。

---

## 处理嵌套 JSON

实际场景中 JSON 响应经常包含嵌套结构。ActiveModel::Serializer 提供了 `has_many` 和 `has_one` 方法来处理嵌套关系。需要注意的是，这里的 `has_many` / `has_one` **并不等同于 ActiveRecord 的关联关系**，它只是声明了 JSON 输出中的嵌套结构。

### 定义嵌套模型

```rb
class MyModel < ActiveModelSerializers::Model
  def initialize(object:)
    @object = object
  end

  def related_models
    @object.related_items.map do |related_item|
      RelatedModel.new(related_model: related_item)
    end
  end
end
```

模型中的 `related_models` 方法返回一个 `RelatedModel` 对象数组。每个 `RelatedModel` 同样继承 `ActiveModelSerializers::Model`，拥有自己的 Serializer。

### 定义嵌套 Serializer

```rb
class MyModelSerializer < ActiveModelSerializers::Serializer
  has_many :related_models
end
```

`ActiveModelSerializers::Serializer` 会自动根据关联名查找对应的 Serializer——`related_models` 的元素类型是 `RelatedModel`，所以会自动查找 `RelatedModelSerializer`。

### 输出示例

最终生成的 JSON 结构类似：

```json
{
  "related_models": [
    { "field1": "value1", "field2": "value2" },
    { "field1": "value3", "field2": "value4" }
  ]
}
```

---

## 实践建议

1. **命名约定很重要**：ActiveModelSerializers 依赖命名约定自动查找 Serializer，保持模型名和 Serializer 名的一致性可以避免手动指定
2. **保持模型轻量**：虚拟模型应该只负责数据的封装和简单转换，复杂的业务逻辑应该放到 Service 层
3. **善用 `attributes` 白名单**：只暴露必要的字段，避免意外泄露内部数据
4. **嵌套不宜过深**：超过 3 层的嵌套会导致 Serializer 难以维护，考虑使用扁平化设计或 GraphQL

---

## 总结

`ActiveModelSerializers::Model` 让我们能够在不依赖数据库的情况下，使用 Rails Serializer 的全部能力来构建结构化的 JSON 响应。这种模式在微服务架构中特别有用——当你的 Rails 应用作为 BFF（Backend for Frontend）层，需要聚合多个下游服务的数据并以统一格式输出时，虚拟模型 + Serializer 的组合能让代码保持清晰和可维护。

> 参考：[ActiveModelSerializers - What does a serializable resource look like?](https://github.com/rails-api/active_model_serializers/tree/0-10-stable#what-does-a-serializable-resource-look-like)
