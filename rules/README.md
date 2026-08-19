# 项目规则体系

> 告诉所有人（人和AI）"在这个项目里，事情应该怎么做"。

## 规则索引

| 规则文件 | 适用对象 | 何时阅读 |
|---------|---------|---------|
| [project-identity.md](project-identity.md) | 所有人 | 首次进入项目时 |
| [naming-conventions.md](naming-conventions.md) | 所有人 | 命名任何文件/变量/字段前 |
| [content-standards.md](content-standards.md) | 写文档的人 | 创建/修改任何 .md 文件前 |
| [conversation-style.md](conversation-style.md) | AI / 写对话脚本的人 | 编写任何面向学生的文本前 |
| [skill-design.md](skill-design.md) | 设计Skill的人 | 新建或修改Skill前 |
| [data-schemas.md](data-schemas.md) | 数据建模者 | 修改 schemas/ 或数据模型前 |
| [web-frontend.md](web-frontend.md) | 前端开发者 | 修改 web/ 目录前 |

## 规则分级

每个规则文件中的条款使用以下标记：

- **MUST** — 必须遵守。违反会导致构建失败或行为异常。
- **SHOULD** — 应该遵守。特殊情况可以例外，需在代码中注释原因。
- **MAY** — 可以参考。推荐做法，不强制。

## 如何使用

1. 首次进入项目 → 先读 `project-identity.md` 了解项目定位
2. 开始写代码/文档 → 查阅对应的规则文件
3. 不确定命名 → 查 `naming-conventions.md`
4. 设计新Skill → 先看 `skill-design.md` 的模板和示例

## 规则和AI

Claude Code 在启动时会自动加载 `CLAUDE.md`。本目录中的规则文件通过 CLAUDE.md 中的索引被 AI 发现。关键规则应同时在 CLAUDE.md 中简要提及，确保 AI 在对话早期就了解核心约束。
