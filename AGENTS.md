# SelfStudy 2.0

> AI 不替学生完成学习；AI 创造条件，让学生展示、检查并修正自己的学习过程。

## 当前范围

- 第一门课程：《碰撞与π》
- 课程结构：一个视频对应一门课，阶段数量由知识点结构决定
- 《碰撞与π》知识拼图共 139 个节点：A=27、B=30、C=46、D=36。
- A 板块有 20 个承载题目的二级节点，共 140 道客观题。
- 题量按知识重要性分配，题库包含 13 个场景题组和 8 道计算题。
- 当前阶段：内容建模与作者工具；学生运行时、账号、支付和云部署尚未实现

## 必须遵守的题目边界

- 客观知识题有正确答案，用于验证知识与方法。
- 状态观察题没有正确答案，必须与客观题分开；当前版本暂不生成。
- 学生答错后不直接显示答案或解析；后续由错题追问 Agent 引导自我纠错。
- AI 不把一次答题结果解释为心理诊断。

## 其他核心约束

1. 知识节点是课程内容的统一索引；题目、视频片段和学习记录只引用 `node_id`。
2. 客观题标准答案只在作者端和判题端可见，不直接下发学生端。
3. 心理/学习状态观察模块可关闭，知识学习模块必须能独立运行。
4. 抽象概念首次出现时配自洽的物理世界比喻；城市比喻不得跨体系混用。
5. 视频内容为课程主来源，并用权威外部资料交叉核对和制作拓展内容；冲突应标记来源，不武断否定视频。

## 导航

- [项目说明](README.md)
- [自主学习理论](docs/theory/autonomous-learning.md)
- [心物方法论](docs/theory/mind-natural-philosophy.md)
- [知识拼图](content/courses/collision-pi/knowledge-puzzle.md)
- [客观题 Schema](schemas/objective_question_bank.schema.json)
- [本轮产品决策](docs/decisions/conversation-decisions.md)
- [错题追问 Agent](docs/product/error-followup-agent.md)
- [路线图](docs/roadmap.md)

## 常用命令

```powershell
python scripts/generate_collision_pi_a_questions.py
python scripts/build_collision_pi_question_editor.py
python -m unittest discover -s tests -v
node scripts/validate_question_editor.js
```
