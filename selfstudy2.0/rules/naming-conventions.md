# 命名规范

> 最后更新：2026-07-11

## 总则

- **MUST**：所有命名使用英文（拼音仅在引用中文专有名词时允许）
- **MUST**：命名应自解释——看到名字就知道它是什么
- **SHOULD**：避免缩写，除非是业界通用缩写（如 `api`、`ui`、`db`）

## 文件命名

### Markdown 文档

```
MUST: kebab-case（小写字母 + 连字符）

✅ interactive-teaching-plan.md
✅ collision-pi-knowledge-puzzle.md
✅ deep-teaching-backend-plan.md
❌ Interactive_Teaching_Plan.md
❌ interactiveTeachingPlan.md
❌ 教学方案.md（禁止中文文件名）
```

### Skill 文件

```
MUST: {功能领域}-{具体功能}.md

✅ video-knowledge-analyzer.md
✅ galgame-teacher.md
✅ learning-session-tracker.md
❌ knowledge_analyzer.md（缺少功能领域前缀）
❌ VideoAnalyzer.md（不允许大驼峰）
```

### 数据文件

```
SHOULD: snake_case.json / snake_case.yaml / snake_case.csv

✅ session_event.schema.json
✅ knowledge_package.json
❌ SessionEvent.schema.json
```

### 源代码文件

```
JavaScript/TypeScript: PascalCase 用于组件，camelCase 用于工具
✅ QuestionCard.tsx
✅ useBehaviorTracking.ts
❌ question_card.tsx

Python: snake_case
✅ video_processor.py
✅ batch_prepare.py
❌ videoProcessor.py
```

## 变量与数据字段

### JSON/YAML 数据字段

```
MUST: snake_case

✅ self_assessed_level
✅ response_time_ms
✅ ai_estimated_level
❌ selfAssessedLevel
❌ ResponseTimeMS
```

### JavaScript 变量

```
MUST: camelCase

✅ const responseTime = 8200;
✅ let hesitationCount = 0;
❌ const response_time = 8200;
❌ let HesitationCount = 0;
```

## Git 分支

```
MUST: {type}/{简短描述}

类型：feature / fix / docs / refactor / test

✅ feature/layer2-interactive
✅ fix/choice-validation
✅ docs/wiki-glossary
❌ my-branch
❌ new_feature_branch
```

## 目录命名

```
MUST: kebab-case 或 单英文单词

✅ rules/
✅ web/
✅ video-transcripts/
✅ _extracted/（下划线前缀表示"原始素材/非生成"）
❌ MyFolder/
❌ teaching_plans/
```

## 版本号

```
MUST: 语义化版本 MAJOR.MINOR.PATCH

✅ 0.2.0
✅ 1.0.0-beta.1
❌ v2
❌ 1.0（缺少PATCH）
```
