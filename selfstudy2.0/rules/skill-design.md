# Skill 设计规范

> 最后更新：2026-07-11
> 适用对象：设计或修改 Claude Code Skill 的人

## Skill 文件结构

### Frontmatter（必须）

```yaml
---
name: {kebab-case名称}
description: |
  {一句话功能描述}。{触发条件}。
  触发词：「{词1}」「{词2}」。
allowed-tools: [Read, Write, Bash, Glob, Grep, WebSearch, WebFetch, Agent]
triggers:              # [新增字段] 自动触发的关键词
  - "{关键词1}"
  - "{关键词2}"
dependencies:           # [新增字段] 依赖的其他Skill
  - ai-teacher
  - video-knowledge-analyzer
outputs:                # [新增字段] 产出的文件/数据类型
  - type: json
    path: "output/{topic}/knowledge_package.json"
---
```

### Body（必须包含的章节）

```markdown
# {Skill 中文名}

## 角色定位
{这个Skill在系统中扮演什么角色？和其他Skill的关系是什么？}

## 必读依赖
{启动前需要加载哪些其他Skill或数据文件？}

## 核心流程
{分步骤描述Skill的工作流程}

## 输出规范
{产出的数据格式、文件命名、存放位置}

## 约束与纪律
{不可违反的规则}
```

## 触发词设计原则

```
MUST: 触发词明确不冲突——同一个词不应触发多个Skill
MUST: 中文触发词配英文对应词（方便中英混合输入）
SHOULD: 斜杠命令格式和自然语言格式都支持
SHOULD: 触发词 3-5 个，不宜过多

✅ 触发词：「galgame」「游戏化学习」「/galgame-teacher」
❌ 触发词：「学习」（太宽泛，会误触发）
```

## allowed-tools 最小权限原则

```
MUST: 只列出Skill实际需要的工具
MUST: 不给 Write 权限除非Skill需要写文件
MUST: 不给 Bash 权限除非Skill需要执行命令
MUST: 不给 Agent 权限除非Skill需要启动子代理

原因：减少权限提示次数，降低安全风险。
```

## 调用其他Skill的规范

```
MUST: 在 dependencies 字段中声明依赖
MUST: 在"必读依赖"章节说明调用时机和方式
SHOULD: 调用其他Skill时传递必要的上下文（而非让被调用Skill重新分析）
```

✅ 正确：galgame-teacher 调用 ai-teacher → 传递学习主题和第一层评估结果

❌ 错误：在 Skill A 中通过 Bash 调用 Skill B（Skills 应通过 Agent 或直接引用协作）

## 设计检查清单

在提交一个新 Skill 之前，确认以下所有项：

- [ ] name 是 kebab-case
- [ ] description 包含触发词
- [ ] allowed-tools 是最小权限
- [ ] dependencies 声明了所有依赖
- [ ] outputs 描述了产出格式
- [ ] 有"角色定位"章节
- [ ] 有"核心流程"章节（分步骤）
- [ ] 有"约束与纪律"章节（至少3条）
- [ ] 触发词不与其他Skill冲突
- [ ] 在 skills/README.md 的决策树中注册了

## ✅ / ❌ 示例

### ✅ 好的 Skill 设计

```markdown
---
name: layer2-interactive
description: |
  执行第二层深度问答。基于第一层评估结果，从每个模块的8问中
  选择2-4个最相关的问题，以苏格拉底式追问推动深层理解。
  触发词：「/layer2」「深度问答」「第二层」。
allowed-tools: [Read, Write, Bash, Glob]
triggers:
  - "/layer2"
  - "深度问答"
  - "第二层展开"
dependencies:
  - ai-teacher
  - learning-session-tracker
outputs:
  - type: json
    path: "output/{session}/layer2_results.json"
---
```

### ❌ 不好的 Skill 设计

```markdown
---
name: helper
description: 帮助工具
allowed-tools: [Read, Write, Bash, Glob, Grep, WebSearch, WebFetch, Agent]
---

# 帮助工具

这个Skill帮你做各种事情。

## 使用方法
你只需要告诉它做什么，它就会做。
```

问题：
- name 太宽泛（"helper"）
- description 没有触发词
- allowed-tools 给了全部权限（不是最小权限）
- 缺少 dependencies、outputs
- Body 没有"角色定位""核心流程""约束与纪律"章节
- 没有在 skills/README.md 决策树中注册
