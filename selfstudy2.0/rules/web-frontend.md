# 作者工具前端规范

> 最后更新：2026-08-19

## 当前范围

- 使用原生 HTML/CSS/JavaScript。
- `authoring/` 只服务课程作者，不等同学生答题运行时。
- 作者工具可以读取标准答案和解析；未来学生端不得接收这些字段。
- 页面必须支持键盘操作、窄屏重排和本地草稿恢复。

## 数据来源

- 知识节点：`content/courses/<course-id>/knowledge-puzzle.json`
- 客观题库：`content/courses/<course-id>/question-bank-<section>.json`
- 数据结构：`schemas/`

## 命名与交互

- JavaScript 变量使用 camelCase。
- JSON 字段使用 snake_case。
- 编辑器修改不应直接覆盖源数据；先保存草稿或提交变更集。
- 删除、批量停用和覆盖正式题库必须二次确认。

> **文档版本**：0.1.0
