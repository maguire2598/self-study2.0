# SelfStudy 2.0

SelfStudy 2.0 是面向自主学习的课程生产与学习支撑系统。当前先建立稳定的课程内容合同和作者工具，再开发学生运行时。

## 当前成果

- 《碰撞与π》知识拼图共 139 个节点：A=27、B=30、C=46、D=36。
- A 板块有 20 个承载题目的二级节点，共 140 道客观题。
- 题量按知识重要性分配，题库包含 13 个场景题组和 8 道计算题。
- 可编辑题库筛选器：修改、启用/停用、本地草稿、恢复和提交
- 客观题与状态观察分离；状态评估暂缓
- 错题追问 Agent 已确定产品边界，尚未实现服务和付费系统

## 目录

```text
content/    课程知识拼图与题库
authoring/  作者筛选和编辑工具
schemas/    内容数据合同
scripts/    题库与作者工具生成、验证脚本
tests/      项目合同与内容测试
docs/       理论、决策、产品设计和路线图
sources/    理论原始资料
rules/      项目规则
wiki/       快速导航与概念说明
```

## 使用

```powershell
python scripts/generate_collision_pi_a_questions.py
python scripts/build_collision_pi_question_editor.py
python -m unittest discover -s tests -v
node scripts/validate_question_editor.js
```

浏览器打开 `authoring/collision-pi-question-editor.html` 可以筛选和修改 A 板块题目。本地模式会复制修改内容；在支持对话回传的环境中可直接提交。

## 下一步

先设计学生答题运行时及答案隔离，再设计错题追问 Agent。账号、支付和云部署均排在内容与学习流程稳定之后。

> **版本**：0.1.0
> **迁移日期**：2026-08-19
