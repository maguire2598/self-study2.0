# 数据结构与Schema管理规范

> 最后更新：2026-07-11
> 适用对象：数据建模者、Schema维护者

## Schema文件位置

```
schemas/
├── dimensions.yaml                 # 六维定义（单一真相来源）
├── session_event.schema.json       # 会话事件Schema
├── knowledge_package.schema.json   # 知识包Schema
├── question_bank.schema.json       # 题库Schema
├── student_profile.schema.json     # 学生画像Schema
├── city_update.schema.json         # 城市状态更新Schema（SSE事件）
└── next_action.schema.json         # API响应格式Schema（核心协议）
```

## Schema版本管理

```
MUST: 每个Schema文件标注 $schema 版本
MUST: Schema变更必须记录在 changes/CHANGELOG.md 中
MUST: 破坏性变更（不向后兼容）必须递增 MAJOR 版本
SHOULD: 新增字段（向后兼容）递增 MINOR 版本
MAY: 修正描述文字递增 PATCH 版本
```

## YAML Schema 规范

`schemas/dimensions.yaml` 是六维定义的单一真相来源。所有前端和后端的维度定义都从此文件生成。

```
MUST: 修改 dimensions.yaml 后同步更新前端和后端的维度定义
MUST: 维度缩写（ATT/REF/KNW/MTH/SLF/EXM）保持不变——它们是API的稳定标识符
SHOULD: 新增维度级别时保持1-5的整数映射
```

## JSON Schema 规范

```
MUST: 使用 JSON Schema draft 2020-12
MUST: 根级别包含 "$schema": "https://json-schema.org/draft/2020-12/schema"
MUST: required 字段明确列出所有必填字段
SHOULD: description 用中文，便于项目成员理解
SHOULD: 数值字段标注 minimum/maximum
SHOULD: 枚举字段标注 enum
```

## 数据字段命名

参考 [naming-conventions.md](naming-conventions.md)：

```
MUST: 所有数据字段使用 snake_case
✅ self_assessed_level
✅ response_time_ms
❌ selfAssessedLevel
❌ ResponseTimeMS
```

## 模块边界合同

模块边界定义在 [contracts/](../contracts/) 目录中。每个模块对之间的数据交换需要：

```
MUST: 定义 input（输入数据格式）
MUST: 定义 output（输出数据格式）
MUST: 定义 output_schema（验证Schema路径）
SHOULD: 定义 protocol（通信协议）
MAY: 定义 validation（验证命令）
```

当前边界合同来源：[contracts.json](../contracts.json) 和 [traceability.csv](../traceability.csv)。
