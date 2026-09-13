# SelfStudy 本地学习 Demo：数据库与前后端设计

## 依据与本轮范围

用户要求完成数据库、结合既有记录完成前后端计划并尽快交付 Demo。沿用 conversation-decisions、error-followup-agent 及后续 A/B/C 已验收题源。当前实际数据为 136 个节点，A 140、B 168、C 180 共 488 道客观题；旧文档的 144 节点、A 192 题已过期。本轮不改已审核的题目内容。D 节点保留，状态 pending，不生成题目。

本轮交付本机可运行的课程学习、答题、进度恢复、有限规则式错后反思、授权作者筛选及启停题目。真实 AI 追问、视频上传/转码、云账号、支付、部署不在本轮范围。视频来源只有文字材料时明确显示未接入播放器，不伪造视频。规则式反思明确标注“演示引导，非 AI”，不使用作者答案生成提示。

## 架构选择

采用 Python 标准库 HTTP 服务 + SQLite + 原生 HTML/CSS/JavaScript。无需外部数据库、npm 安装、API 密钥即可启动，适合本地演示和现有 Python 题库。FastAPI/PostgreSQL 适合多用户部署但增加当前安装成本；纯静态 localStorage 无法完成后端判题与数据库持久化。正式版可保持同一 HTTP 契约更换服务框架和数据库。

应用仅监听 127.0.0.1:8765。只提供 demo/web 白名单静态文件与 manifest 中的 SVG，绝不提供仓库目录、源题库、数据库或作者密钥。学生 JSON 采用明确白名单，无 correct_answers、accepted_answers、explanation、answer_contract、visible_physics_contract、author_notes。选择题答案及填空答案单独存储，仅服务器判题和授权作者 API 可读取。

## 数据库

运行数据位于 .local/selfstudy-demo.sqlite3（忽略提交），SQLite foreign_keys=ON、WAL、版本化建表。表包括 schema_migrations、courses、sections、nodes、diagrams、questions、answer_keys、learners、attempts、reflections、author_changes；节点进度按当前学习者 attempts 聚合，避免多份事实失同步。所有题目、作答只引用稳定 node_id/question_id。

questions 保存 public_json、section_id、node_id、排序、enabled、revision、源指纹；answer_keys 保存答案、作者解析、源 JSON。attempts 保存学习者、题目、提交答案、正确与否、题目版本、时间。reflections 关联尝试、学习者文字和有限引导阶段。author_changes 记录启停与版本，防止作者编辑无追踪。

初始化事务性幂等导入课程和节点、A/B 已生成题库，以及经现有验证器生成的 C 正式题库和 36 张图。重复启动不清空学习记录、不覆盖作者启停。D 有 sections 行但无 questions。现有 A/B 文件字节保持不变。任何导入失败整体回滚。

## API 契约

所有 JSON UTF-8；错误统一 {error: string}，400 输入非法，401 未授权，404 不存在，409 版本冲突。写请求要求 JSON 与 X-SelfStudy-Request: 1；拒绝非本站 Origin、非本地 Host，限制请求体 64 KiB。不提供 CORS。学习者 cookie 随机不可预测、HttpOnly、SameSite=Strict。无 cookie 自动创建本地学习者，不接受客户端指定 learner_id。

| 方法 / 路径 | 行为与返回 |
| --- | --- |
| GET /api/health | {status:'ok', database:'ok', question_count:488, sections:{A:140,B:168,C:180,D:0}} |
| GET /api/course | {id,title,sections:[{id,title,status,question_count}],nodes:[{id,section_id,parent_id,title,summary,depth,question_count}],video_available:false} |
| GET /api/questions?section=A&node_id=...&type=...&offset=0&limit=20 | {items:[public question],total}; 默认 enabled，只返回白名单 |
| GET /api/questions/{id} | public question；禁用题返回404 |
| POST /api/attempts | {question_id,answers:[option IDs] 或 {blank_id:text}} -> {attempt_id,correct,next_action:'next_question'或'reflection',message}；绝不返回标准答案/解析；单多选集合判定，多空全部匹配 |
| GET /api/progress | {attempts,correct_attempts,completed_questions,last_question_id,nodes:[{node_id,attempts,correct_attempts,completed_questions}],recent:[{question_id,node_id,correct,created_at}]}；按 cookie 隔离 |
| POST /api/reflections | {attempt_id,text} -> {stage,prompt,can_retry:true,mode:'rule_demo'}；仅本人记录，最多3阶段，支持重试/跳过，不限制付费 |
| POST /api/author/login | {token} -> {authenticated:true}；独立随机 HttpOnly 作者会话，错误401 |
| POST /api/author/logout | 清除作者会话 |
| GET /api/author/questions?section=&node_id=&type=&offset=&limit= | 需作者会话；{items:[作者题目，含答案和解析],total}；包含禁用题 |
| PATCH /api/author/questions/{id} | 需作者会话；{enabled:boolean,revision:int} -> {id,enabled,revision}；旧revision返回409并记录审核日志 |
| GET /api/diagrams/{diagram_id}.svg | 仅manifest白名单SVG，无路径穿越 |

public question 字段：id,node_id,node_title,section_id,question_type,question_style,difficulty,prompt,revision,presentation_mode,figure_refs，options:[{id,text,figure_ref?}] 或 blanks:[{id}]。不嵌入其他作者字段。填空使用 NFKC/空白/负号归一，明确接受列表或安全有限数值/分数等价；不用 eval，不擅自接受单位换算或符号代数，不泄漏每空正确性。

作者访问令牌首次启动生成并保存在 .local/author-token.txt，不通过学生端 API 返回；作者登录页解释本地令牌文件位置。作者端和学习端入口明确分开。此认证仅用于本地演示，不宣称多租户生产认证。

## 前端设计

学习者在桌面或手机专注阅读物理题。采用暖白纸面、深墨文字、森林绿主操作与细线目录，标题使用系统中文衬线、正文系统无衬线。原生 CSS 变量统一间距、色彩与焦点。应用布局是左侧课程目录、中央答题纸、右侧轻量学习进度；375px 下依次流式折叠，无水平溢出。选择高亮、提交反馈和进度条短暂过渡，支持 reduced-motion。

首页即课程工作台：当前课程、A/B/C/D 板块切换、知识节点筛选、题型筛选、当前题、上一题/下一题、已尝试与已通过统计。D 显示空状态。题干保留情境段落；C 支持题干图、四选项图、图序。题干图可查看大图，匿名选项图只用“图A”等可访问名称，不显示图注答案线索。

答错显示“先检查依据”，展开反思输入和规则引导；不显示答案、解析、正确选项或每空判分。提交按钮防重复，跳题允许退出，重试保留同题。答对提示已记录并可下一题或主动反思。恢复上次学习位置及记录，显示持久化真实数据。空/加载/网络错误状态均有明确文字。

作者页提供令牌登录、A/B/C/D 和节点题型筛选、分页、题目/答案/解析、启停按钮与revision并发提示。完整任意文本编辑沿用后续作者审核流程，本 Demo 不加入未验证的全字段改题。

## 验收

数据库真实存在，重复初始化后488题、D为0，学习记录和作者启停不丢；A/B字节不变；C生成可复现。学生API及静态路由无答案字段、源文件、数据库与令牌泄漏。三种题型能提交，错误答案无解析，反思不会泄漏答案且有限阶段。两个cookie互相隔离，作者授权与冲突处理有效。桌面和375px浏览器验证选择/提交/反思/恢复/C图/D空状态/作者启停。启动命令和本地URL写入README，给出测试与已知演示边界。
