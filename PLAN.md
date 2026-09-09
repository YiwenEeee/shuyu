# 书遇

> 团队 3 人：A 前端 / B 后端 / C AI·数据
> 时间：D1 今天 / D2 明天 / D3 后天 / D4 大后天 / D5 大大后天（答辩）

## 项目定位

「书遇」—— 用读书内容寻找同频者的匿名社交应用。

核心特色（只做深这 **1 项**）：**轻量 RAG** —— 笔记向量化 → 相似度检索 → 排序 → LLM 生成推荐语。

## 功能清单（6 个）

1. 用户系统：注册登录 + 匿名/实名切换（权限管理）
2. 书单管理：在读 / 想读 / 已读
3. 笔记上传：AI 提取主题、关键词、情绪
4. **灵魂共振匹配**：RAG 向量相似度 + AI 推荐语（核心）
5. 读书墙：实时滚动（**可选**，D4 有余力再做）
6. 管理员后台：笔记审核 + 书籍管理（数据管理）

## 技术栈

- 前端：Vue 3 + Vite
- 后端：FastAPI + SQLite + SQLAlchemy
- 向量检索：API Embedding（硅基流动 bge-m3）+ NumPy 余弦相似度（无本地向量库，已砍 ChromaDB）
- LLM：DeepSeek
- 实时（可选）：WebSocket

## 总览

| 天 | 主线目标 | A 前端 | B 后端 | C AI·数据 | 交付物 |
|---|---|---|---|---|---|
| D1 今天 | 搭骨架 + 定协议 | 跑通前端、调样式 | 跑通后端、起草 API | 搞定两个 key | 前后端能跑 + API.md |
| D2 明天 | 后端接口 + RAG（生死线） | 3 个页面静态版 | 全部业务接口 | RAG 核心链路 | 上传→匹配→推荐语跑通 |
| D3 后天 | 前端联调 + 后台 | 接 API 完成交互 | 后台 + 审核 | 配合联调 | 全功能可用 |
| D4 大后天 | 测试 + 文档 + 读书墙(可选) | 读书墙前端 | 补测试、读书墙后端 | 技术文档 | 测试 + 文档齐 |
| D5 大大后天 | 答辩准备 + 答辩 | 答辩 PPT | README 完善 | 职业规划、排练 | 材料打包 + 答辩 |

## 每天任务

### D1 今天 · 搭骨架 + 定协议

- [ ] 环境搭好，后端 `/api/health` 返回 ok
- [ ] 前端 5173 显示「书遇 · 后端已连接」
- [ ] 两个 key 就绪（DeepSeek + 硅基流动）
- [ ] `backend/API.md` 接口协议定稿
- [ ] Vibe 日志 ①

分工：A 跑通前端 + 调样式 / B 跑通后端 + 起草 API.md / C 申请两个 key

### D2 明天 · 后端接口 + RAG 核心（生死线）

- [ ] 注册登录、书单、笔记、匹配确认接口
- [ ] RAG 链路：embedding → NumPy 检索 → DeepSeek 推荐语
- [ ] 上传/匹配结果/书单 三个页面静态版
- [ ] 下班前验证：对一条笔记返回 Top-N + 推荐语
- [ ] Vibe 日志 ② ③

分工：B 接口 / C RAG / A 页面

### D3 后天 · 前端联调 + 后台

- [ ] A 接 API 完成交互闭环
- [ ] B 管理员后台 + 笔记审核
- [ ] C 配合联调、修 embedding 细节
- [ ] Vibe 日志 ④

#### D3 · C 侧细化（定稿）：匹配只展示高分 + 反馈档位重构

> 需求变更：匹配书友**只出现匹配度较高的人**、按 `matchScore` 降序。原 S/A/B/C（覆盖到"没有匹配"）不再适用，做如下收敛。

- **匹配口径**：`match()` 只保留 `matchScore >= weak(55)` 的候选，按 `matchScore` 降序 → 只出现"匹配度较高的人"。
- **反馈档位改为按 `matchScore`(0~100) 分档，不再按余弦相似度**：
  - S（≥85）· 灵魂共振：DeepSeek 个性化推荐语，最热情
  - A（70~85）· 高相关：DeepSeek 个性化推荐语，语气稍收敛
  - B（55~70）· 较强相关：模板 + TA 的摘录（正向措辞，"你们在同频处相遇"）
  - C · 兜底 **只在「列表为空」时用**（鼓励再上传），不再作为逐条推荐语
- **配置对齐**：`.env` 用 `MATCH_SCORE_LOW/HIGH`（余弦→matchScore 映射）、`RAG_STRONG/HIGH/WEAK`（改成 matchScore 单位 85/70/55）、`RAG_TOP_N`（给几条生成推荐语）。
- **代码改动**：`llm.py` 暴露公开 `chat`；`feedback.py` 用 matchScore 分档、C 移出逐条、接入 `match()`；`match()` 过滤低分候选并走 `build_feedback`。

#### D3 · 联调接口信息（B 提供 · 上传笔记）

**上传笔记接口**：`POST http://10.180.24.176:8000/api/notes`

- 请求头：`Authorization: Bearer <登录返回的 token>`、`Content-Type: application/json`
- 最小请求体：

  ```json
  { "bookId": 2, "content": "自由不是想做什么就做什么……", "isPublic": true }
  ```

  `author` / `book` **无需前端/C 传**，后端从 Bearer Token 推导作者、按 `bookId` 查书籍。
- 可选传 AI 三栏 `{ topics, keywords, sentiment }`；正常联调不传，后端上传时会立即提取并返回。
- 成功响应重点字段：

  ```json
  { "code": 200, "data": { "noteId": 123, "author": { "userId": 1, "nickname": "联调读者", "avatarPath": "..." }, "book": { "bookId": 2, "title": "书名", "author": "作者" }, "bookId": 2, "content": "…", "isPublic": true, "reviewStatus": "pending", "topics": [], "keywords": [], "sentiment": "neu" } }
  ```

**C 侧流程（关键）**：上传后 `reviewStatus` 恒为 `pending`；公开笔记经管理员审核 `approved` 后，后端才创建 `aiStatus=pending` 的漂流瓶；C 完成向量化后再标记为 `ready`，才能被匹配接口查到。

#### D3 · 联调待办 / 验收清单（C）

**C 侧接口口径（最终结论）**：`match()` 只返回 `matchScore >= 55` 的候选，按真实分数降序；全量 11 字段；`recommendation` 只对 Top3 生成，其余 `null`；aiStatus 流 `pending → processing → ready / failed`，只有 `ready` 参与匹配。

- [ ] B 直连 `from app.services.rag_service import rag`，审核通过时调 `publish_note`、成功后调 `mark_ai_ready`、匹配接口调 `match`。
- [ ] B `.env` 填真 key（`SILICONFLOW_API_KEY` / `DEEPSEEK_API_KEY`）、`RAG_MOCK=0`；单 worker（`uvicorn --workers 1`）。
- [ ] B 捕获 `EmbeddingError` → 该笔记 `aiStatus=failed`。
- [ ] C 验收：`/api/health` 通。
- [ ] C 验收：`POST /api/notes` 返回 `noteId` + `topics/keywords/sentiment`。
- [ ] C 验收：审核通过入池后 `aiStatus=processing`，`mark_ai_ready` 后 `ready`。
- [ ] C 验收：`GET /api/bottles/matches` 只返回 `matchScore>=55`、降序、11 字段、Top3 有 `recommendation`。
- [ ] C 验收：`ready` 之前匹配查不到，之后才出现。
- [ ] 对齐 A：只展示 ≥55；`recommendation` 可空；`noteId` 绑交互、`bottleId` 是漂流瓶 ID。
- [ ] 提醒：mock 模式返回空（mock 相似度被 ≥55 过滤），演示用真实模式。
- [ ] Vibe 日志 ④。

### D4 大后天 · 测试 + 文档 + 读书墙（可选）

- [ ] 补测试、修 bug
- [ ] 技术文档 + README 完善
- [ ] （可选）读书墙 WebSocket
- [ ] Vibe 日志 ⑤
- [ ] 全体：开始写职业规划（1000 字）

### D5 大大后天 · 答辩准备 + 答辩

- [ ] 答辩 PPT（按 7 步顺序）
- [ ] 演示排练（真实运行，不用截图）
- [ ] 职业规划定稿
- [ ] 材料打包提交

## 答辩 7 步顺序（提醒）

1. 项目背景与真实需求
2. 小组分工
3. 系统功能演示
4. 数据流展示
5. 特色技术展示（RAG 链路）
6. Vibe Coding 关键迭代
7. 项目不足与优化方向

## 风险与红线

- **D2 是生死线**，RAG 链路必须跑通，否则全崩
- 严禁：假功能、技术堆砌、Vibe 日志伪造、前后端未连通
- 演示必须基于真实运行系统，**不能用截图代替**
- 接口字段今天定死，之后不改（改了前后端一起崩）
- 职业规划别拖到最后一天，D4 就开始写
