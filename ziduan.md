# 书遇 · 必须确认的字段名清单（跟 B 对齐）

> 本文档按网页 6 大功能列出**必须一次性定死**的字段名，供 C 与 B 确认。
> 标记 ★ 的是 C（AI·数据）生命线字段，错名会直接导致私密笔记泄漏进池 / 匹配结果取不到 / 交书友申请无法路由。
> 约定：字段定死后**不再改名**（不然前后端一起崩）。

## 命名规范（统一使用）

- JSON 字段一律 **snake_case**：`recommendation_text`、`similarity_score`
- id 统一 `*_id`；数组用复数：`topics`、`keywords`、`comments`
- 布尔用 `is_` 前缀：`is_liked`、`is_favorited`；状态用枚举字符串

---

## 1. 用户系统（注册/登录，用户、管理员两入口）

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | int | 用户 id |
| `username` | string | 登录名（唯一） |
| `password` | string | 密码（存哈希，勿明文） |
| `nickname` | string | 展示名 / 匿名昵称 |
| `role` | string | `"user"` / `"admin"` —— 决定进用户界面还是管理员界面 |

登录后最简方案：前端只存 `user_id`，请求都带 `user_id`。

---

## 2. 书单管理（在读 / 已读 / 想读）

| 字段 | 类型 | 说明 |
|---|---|---|
| `user_id` | int | 归属用户 |
| `book_id` | int | 书籍 id |
| `status` | string | `"reading"` / `"read"` / `"want"` |
| `title`、`author` | string | 返回时由 B 关联书籍补上，供前端显示 |

---

## 3. 笔记上传（公开/私密 + AI 提取主体·关键词·情绪）

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | int | 笔记 id（向量索引主键） |
| `user_id` | int | 上传者 |
| `book_id` | int | 所属书籍 |
| `content` | text | 笔记正文（做 embedding 的原文） |
| `visibility` ★ | string | `"public"` / `"private"` —— 是否进匹配池 |
| `status` ★ | string | `"pending"` / `"approved"` / `"rejected"` —— 管理员审核 |
| `topics` | string[] | 主题（AI 提取） |
| `keywords` | string[] | 关键词（AI 提取） |
| `sentiment` | string | `"pos"` / `"neu"` / `"neg"`（AI 提取） |
| `created_at` | datetime | 上传时间 |

**进池规则**：`visibility=public 且 status=approved` 才向量化进池；私密或未过审只存储、不参与匹配。

---

## 4. 漂流瓶（书友匹配）

输入：

| 字段 | 类型 | 说明 |
|---|---|---|
| `user_id` | int | 发起方 |
| `note_id` | int | 用户挑的**自己公开**的笔记（作 query） |

输出：`matched_user_id` ★、`matched_note_id` ★、`similarity_score` ★、`recommendation_text` ★、`tier`（可选，S/A/B/C）

| 字段 | 类型 | 说明 |
|---|---|---|
| `matched_user_id` ★ | int | 匹配到的人（B 靠它发交书友申请） |
| `matched_note_id` ★ | int | 匹配到的公开笔记 |
| `similarity_score` ★ | float(0~1) | 匹配度，越高越接近 |
| `recommendation_text` ★ | string | 灵魂共振推荐语 |
| `tier` | string | `"S"`/`"A"`/`"B"`/`"C"`，供前端区分展示 |

申请状态（B 维护）：

| 字段 | 类型 | 说明 |
|---|---|---|
| `request_status` | string | `"pending"` / `"accepted"` / `"rejected"` |

---

## 5. 读书墙（实时公开笔记 + 点赞/评论/收藏）

前提：只展示 `visibility=public 且 status=approved` 的笔记。

| 字段 | 类型 | 说明 |
|---|---|---|
| `like_count` | int | 点赞数 |
| `is_liked` | bool | 当前用户是否已点赞 |
| `favorite_count` | int | 收藏数 |
| `is_favorited` | bool | 当前用户是否已收藏 |
| `comment_count` | int | 评论数 |
| `comments` | 对象数组 | 每条 `{ id, note_id, user_id, content, created_at }` |

---

## 6. 管理员（审核公开笔记 + 管理书籍）

| 字段 | 类型 | 说明 |
|---|---|---|
| `status` ★ | string | 笔记审核：`pending` → `approved` / `rejected` |
| `reviewed_by` | int | 审核管理员 id |
| `book` 字段 | object | `{ id, title, author, description, cover_url }` |

---

## 需要 C 与 B 一起拍板（3 项）

- [ ] `Top-N` 返回几条（建议 3~5，C 默认按 3，config 可调）
- [ ] 匹配度给用户看：原始百分比，还是映射成"契合度 60%~99%"（建议后者）
- [ ] 审核通过才进池，还是上传即进池（建议：上传即提取元信息、**审核通过才入池**）
