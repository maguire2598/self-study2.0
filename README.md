# SelfStudy 2.0

SelfStudy 2.0 是面向自主学习的课程生产与学习支撑系统。本地 Demo 将课程内容、后端判题、学习记录和授权作者审核连接起来。

## 当前成果

- 《碰撞与π》知识拼图共 136 个节点：A=27、B=27、C=46、D=36。
- A 板块有 20 个承载题目的二级节点，共 140 道客观题。
- B 板块有 22 个承载题目的二级节点，共 168 道客观题。
- B 题库包含 15 个场景题组和 32 道计算题。
- C 板块有 180 道客观题和 36 张验证过的 SVG；A/B/C 合计 488 题，D 出题待定。
- SQLite 保存课程节点、题目、独立答案记录、作答、反思和作者启停记录。
- 可编辑题库筛选器：修改、启用/停用、本地草稿、恢复和提交
- 客观题与状态观察分离；状态评估暂缓
- 错题追问 Agent 已确定产品边界；Demo 只演示最多3阶段的规则引导，不是真实 AI，不收费。

## 本地 Demo

在本 README 所在项目目录运行（Python 3.10+，仅标准库）：

```powershell
python scripts/run_demo.py --port 8765
```

- 学习端：http://127.0.0.1:8765/
- 作者端：http://127.0.0.1:8765/author
- 健康检查：http://127.0.0.1:8765/api/health
- 数据库：`.local/selfstudy-demo.sqlite3`，首次启动自动建表并导入488题，重复启动保留进度和启停设置。
- 作者令牌：`.local/author-token.txt`，在本机打开并粘贴到作者登录页；不要分享或提交此文件。

服务只监听本机，静态文件采用白名单，不向学生提供原题库、答案或解析。作者端需登录后才能查看答案和启停题目；修改时校验修订号。原有全字段作者编辑器仍是独立工具，不通过学生服务公开。

学习者用持久 cookie 识别，无云账号。清除浏览器 cookie 或换浏览器会成为新学习者，已有数据库记录仍保留；本轮没有账号找回或跨设备同步。作者登录在服务重启后失效。

视频播放器、真实 AI 追问、云账号、支付和云部署尚未接入。请勿把这个本机演示直接暴露到公网。D 仅保留知识目录，不自动出题。

设计资料：[数据库与前后端设计](docs/superpowers/specs/2026-09-13-local-learning-demo-design.md)、[实施计划](docs/superpowers/plans/2026-09-13-local-learning-demo.md)、[界面约定](docs/product/demo-design.md)。

## 目录

```text
content/    课程知识拼图与题库
authoring/  作者筛选和编辑工具
demo/       本地 SQLite、HTTP API 和学习/作者网页
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
python scripts/generate_collision_pi_b_questions.py
python scripts/generate_collision_pi_c_questions.py
python scripts/build_collision_pi_question_editor.py
python -m unittest discover -s tests -v
node scripts/validate_question_editor.js
```

浏览器打开 `authoring/collision-pi-question-editor.html` 可以切换、筛选和修改 A/B 板块题目。本地模式会复制修改内容；在支持对话回传的环境中可直接提交。

## 下一步

先验证本地学习与作者审核闭环，再设计真实错题追问 Agent、视频接入和账号恢复。D 出题等待确认；支付和云部署排在学习流程稳定之后。

> **版本**：0.1.0
> **迁移日期**：2026-08-19
