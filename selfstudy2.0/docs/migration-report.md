# SelfStudy 2.0 迁移报告

## 迁移结果

SelfStudy 2.0 以精简内容平台形式建立。旧项目只作为来源读取，所有 2.0 文件先在独立 staging 目录生成和验证，再移动到最终项目目录。

## 已迁移

- 两份理论摘要与三份理论原始文本
- 项目命名、Schema、对话、内容和作者前端规则
- 精简后的 Wiki：架构、教学方法、知识拼图、术语、城市比喻和 FAQ
- 本轮确认的课程、题型、模块边界和错题追问产品决策
- 《碰撞与π》A/B/C/D 共 144 个知识节点
- A 板块 32 个节点的 192 道客观题
- 客观题与知识拼图 Schema
- 知识节点导入、题库生成、编辑器构建和脚本验证工具
- 作者题库筛选与编辑页面
- 项目合同、知识拼图、题库和独立性测试

## 路径转换

| 旧位置 | 2.0 位置 |
|:---|:---|
| `_extracted/*.txt` | `sources/theory/*.txt` |
| 对话筛选器内的节点数组 | `content/courses/collision-pi/knowledge-puzzle.json` |
| `web/data/collision_pi_a_questions.json` | `content/courses/collision-pi/question-bank-a.json` |
| `web/authoring/` | `authoring/` |
| `backend/tests/` 中的题库测试 | 顶层 `tests/` 标准库测试 |

生成器与编辑器构建器只使用 2.0 根目录的相对路径，不依赖旧项目或 Codex 临时目录。

## 未迁移

- 测试账号、数据库和用户进度
- 旧场景剧本及旧版无正确答案题库
- FastAPI、ORM、会话引擎和旧网页运行时
- 视频、OCR 帧和大型中间文件
- Galgame 演出层
- 旧 Git 历史

这些内容仍保留在旧项目中，没有被移动或删除。

## 验证

```powershell
python scripts/generate_collision_pi_a_questions.py
python scripts/build_collision_pi_question_editor.py
python -m unittest discover -s tests -v
node scripts/validate_question_editor.js
```

验收内容包括：144 节点及各板块数量、节点 ID 唯一性、C9 选修属性、A 题库 3/2/1 分布、答案和解析完整性、状态评估关闭、错题追问路由，以及项目路径独立性。

## 下一项设计任务

优先设计学生答题运行时：答案隔离、判题、多空匹配、进度保存及错题路由。运行时合同稳定后，再实现付费错题追问 Agent 和支付权益。

> **文档版本**：1.0.0
> **日期**：2026-08-19
