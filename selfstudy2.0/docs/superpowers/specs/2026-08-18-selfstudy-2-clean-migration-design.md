# SelfStudy 2.0 Clean Migration Design

## 目标

在 `C:\Users\MECHREVO\selfstudy2.0` 建立一个独立、精简、可继续演进的新项目，只迁移本轮已经确认的理论、课程框架、知识拼图、客观题库与作者工具，不继承旧版冗余运行代码和已作废题目规则。

## 核心原则

1. 旧项目保持原样，迁移采用复制而非移动。
2. 2.0 以内容模型和课程生产链为核心，暂不复制旧账号数据、旧场景剧本和完整前后端。
3. 新版客观题具有正确答案；旧版“选择题无正确答案”仅保留为历史规则，不进入 2.0 的客观题运行规范。
4. 心理/学习状态观察与知识学习保持模块隔离。状态评估题暂缓生成。
5. 错题追问 Agent 是后续独立付费服务：答错时不直接展示答案和解析，引导学生定位漏洞并自行得出答案；本次迁移只记录接口与产品约束，不实现服务和支付。
6. 第一门课程仍为《碰撞与π》，采用一个视频对应一门课程、知识点数量决定阶段数量的模式。

## 迁移范围

### 项目治理与理论

- `AGENTS.md`
- `rules/`
- `wiki/`
- `docs/theory/`
- `_extracted/自主学习主科草稿.txt`
- `_extracted/弹性碰撞与π.txt`
- `_extracted/《心灵世界的自然哲学》（作者定稿）.txt`

### 课程与知识体系

- `docs/courses/collision-pi.md`
- 当前 A/B/C/D 知识拼图和 144 个知识节点
- A 板块 32 个知识节点的 192 道客观题
- 每节点固定比例：3 单选、2 多选、1 多空填空

### 题库工程

- `web/data/collision_pi_a_questions.json`
- `web/authoring/collision_pi_question_editor.template.html`
- `web/authoring/collision_pi_question_editor.html`
- `schemas/objective_question_bank.schema.json`
- `scripts/generate_collision_pi_a_questions.py`
- `scripts/build_collision_pi_question_editor.py`
- `scripts/validate_question_editor.js`
- `backend/tests/test_collision_pi_a_question_bank.py`

### 新增的 2.0 项目文档

- `README.md`：项目定位、当前状态和常用命令
- `docs/decisions/conversation-decisions.md`：本轮已确认产品决策
- `docs/product/error-followup-agent.md`：付费错题追问 Agent 的边界和待设计项
- `docs/roadmap.md`：课程内容、作者工具、学习运行时和付费服务的实施顺序
- `changes/CHANGELOG.md`：2.0 独立变更记录
- 本迁移设计文档

## 明确不迁移

- 测试学生账号和数据库
- 旧版 `web/scenario.json` 及以无正确答案选项为核心的旧运行题库
- 旧版登录、画像、城市界面、会话引擎和服务器部署代码
- 视频文件、OCR 帧和可重新生成的大型中间产物
- 旧项目的 Git 历史与未明确纳入 2.0 的临时文件

这些内容不会删除，仍保留在 `selfstudy` 中供追溯；确有需要时再按模块迁移。

## 目标目录结构

```text
selfstudy2.0/
├── AGENTS.md
├── README.md
├── rules/
├── wiki/
├── docs/
│   ├── theory/
│   ├── courses/
│   ├── decisions/
│   ├── product/
│   ├── superpowers/specs/
│   └── roadmap.md
├── sources/
│   └── theory/
├── schemas/
├── content/
│   └── courses/collision-pi/
│       ├── knowledge-puzzle.md
│       └── question-bank-a.json
├── authoring/
│   └── collision-pi-question-editor.html
├── scripts/
├── tests/
└── changes/
```

## 路径调整

迁移时不机械保留旧目录名：

- `_extracted/` 理论原文进入 `sources/theory/`。
- `web/data/collision_pi_a_questions.json` 进入 `content/courses/collision-pi/question-bank-a.json`。
- 作者筛选器进入 `authoring/`。
- 题库测试从 `backend/tests/` 进入顶层 `tests/`。
- 生成器中的输入输出路径全部改为 2.0 目录结构，禁止依赖旧项目绝对路径。
- Codex 对话内展示版本继续生成到当前任务允许写入的 visualization 目录，但不把该临时路径写成项目依赖。

## 数据与模块边界

### 课程内容层

知识节点是课程内容的单一索引。题目通过 `node_id` 关联知识节点；未来视频片段、讲解、练习与学习记录也只引用节点 ID，不复制节点定义。

### 客观题库层

客观题库保存标准答案和作者解析。学生答题接口只返回作答所需字段，不返回答案与解析。作者工具可以编辑完整数据。

### 错题追问层

运行时答错后只产生 `wrong_answer_action=error_followup_agent`。Agent、订阅资格、对话记录和最终掌握验证属于后续模块，通过接口连接题库，不写入题目正文。

### 状态观察层

状态观察不混入客观题。当前 `status_assessment.enabled=false`，后续单独设计触发条件、授权开关和数据保存策略。

## 迁移流程

1. 创建 `selfstudy2.0` 及目标目录。
2. 复制治理、理论和课程资料。
3. 将知识拼图与题库按新目录归档。
4. 调整生成器、构建器、测试和文档中的相对路径。
5. 新建 2.0 README、决策记录、Agent 产品说明与路线图。
6. 运行题库生成、结构测试和编辑器脚本校验。
7. 输出迁移清单和未迁移清单，不修改或删除旧项目文件。

## 验收标准

- `C:\Users\MECHREVO\selfstudy2.0` 可独立读取和生成 A 板块题库。
- A 板块仍为 32 个节点、192 道题，题型比例为 3/2/1。
- 所有客观题具有标准答案和解析，状态评估题数量为零。
- 作者编辑器不依赖旧项目路径，支持编辑、暂存、恢复和提交修改。
- 题库测试和编辑器校验全部通过。
- 旧项目没有文件被移动、删除或覆盖。
- README 能说明如何在 2.0 中继续讨论和开发。

## 风险与处理

- **知识拼图来源分散**：迁移时生成一份 2.0 权威知识拼图文件，并注明其节点 ID 是题库关联基准。
- **旧规则污染新题库**：新版 Schema 使用独立名称，AGENTS 与内容规则明确区分客观题和状态观察题。
- **作者工具依赖 Codex 环境**：本地模式保留复制修改内容的降级路径；Codex 模式才调用 `window.openai.sendFollowUpMessage`。
- **付费服务耦合过早**：只记录交付策略和接口需求，不在本次迁移中实现支付或 Agent。

> **文档版本**：1.0.0
> **编制日期**：2026-08-18
