# 书遇 · 字段定义（最终合理版 · 定稿）

> 依据：`houduan` 分支 `apireadme.md`（40 个接口）+ 团队细化的 6 大功能。
> 结论：**保留 AI 三栏**（主体/关键词/情绪）、匹配改为**智能匹配**、匹配度用 `matchScore 0~100`。
> 命名统一 **camelCase**。★ 标记 C（AI·数据）生命线字段，错名会直接导致私密笔记泄漏进池 / 匹配结果取不到 / 书友申请无法路由。
> **本文件为定稿，之后不再变动。**

## 命名规范

- 字段一律 camelCase：`matchScore`、`reviewStatus`、`isPublic`、`noteId`
- id 统一 `*Id`；布尔用 `is*`；数组用复数：`topics`、`keywords`、`comments`
- 统一返回 `{ code, data, message }`，HTTP 恒为 200；code=200 成功 / 400 失败 / 401 需登录
- 除注册、登录、头像上传外，均用 **Bearer Token**

---

## 1. 用户系统（注册/登录，用户、管理员两入口）

| 字段 | 类型 | 说明 |
|---|---|---|
| `userId` | int | 用户 id |
| `email` | string | 登录名，唯一（区别于旧版 username） |
| `password` | string | 密码（存哈希，勿明文） |
| `token` | string | 登录返回，有效期默认 7 天 |
| `expiresAt` | date-time | token 到期时间，UTC |
| `nickname` | string | 展示名 / 匿名昵称 |
| `avatarPath` | string | 头像路径，**必填且不可清空** |
| `gender` | string | `male`/`female`/`unspecified` |
| `role` | string | `user`/`admin` —— 决定进用户界面还是管理员界面 |

统一登录 `/api/auth/login`（email+password）→ 返回 token → `GET /api/me` 取资料+role，前端按 role 跳转。

---

## 2. 书单管理（在读 / 已读 / 想读）

| 字段 | 类型 | 说明 |
|---|---|---|
| `userId` | int | 归属用户 |
| `bookId` | int | 书籍 id |
| `readingStatus` | string | `wantToRead`(想读) / `reading`(在读) / `read`(已读) |
| `book` | object | `{ bookId, title, author, coverPath, status }` |
| `currentReading` | object | 当前阅读 `{ book, updatedAt }`，可设为 null 停止 |

---

## 3. 笔记上传（私密/公开 + AI 自动提取主体/关键词/情绪）

| 字段 | 类型 | 必选 | 说明 |
|---|---|---|---|
| `noteId` | int | — | 笔记 id（向量索引主键） |
| `author` | object | — | `{ userId, nickname, avatarPath }` |
| `book` | object | — | `{ bookId, title, author, coverPath, status }` |
| `bookId` | int | 是 | 关联上架书籍 |
| `content` | text | 是 | 笔记正文（embedding/推荐语原文） |
| `isPublic` ★ | bool | 否 | `true` 公开（过审后入池）；`false` 私密，不入池。默认 false |
| `reviewStatus` ★ | string | — | `pending`/`approved`/`rejected`，创建时恒为 `pending` |
| `reviewReason` | string/null | — | 拒绝原因；通过时 null |
| `topics` ★ | string[] | — | 主题（AI 上传时实时提取，本次**保留**） |
| `keywords` ★ | string[] | — | 关键词（AI 上传时实时提取） |
| `sentiment` ★ | string | — | `pos`/`neu`/`neg`（AI 上传时实时提取） |
| `createdAt`、`updatedAt`、`deletedAt` | date-time | — | 时间戳；软删除 |
| `likeCount`/`favoriteCount`/`commentCount` | int | — | 社交统计 |
| `isLiked`/`isFavorited` | bool | — | 当前用户是否已点赞/收藏 |

**进池规则**：`isPublic=true 且 reviewStatus=approved` 才入池（创建漂流瓶 + 启动匹配 AI）。私密、未过审、被拒只存储、不参与匹配。

---

## 4. 漂流瓶（书友匹配 · 核心 RAG）· 智能匹配

输入：`GET /api/bottles/matches`

| 字段 | 类型 | 说明 |
|---|---|---|
| `noteId` | int | 来源笔记：**本人 + approved + 公开 + 未删除**（可选列表来自 `GET /api/me/notes?isPublic=true&reviewStatus=approved`） |
| `pageNum` | int | 页码，默认 1 |
| `pageSize` | int | 每页 1~100，默认 10 |

输出：`Page<MatchItem>`（按 `matchScore` 降序，同分按 `bottleId` 降序，分页；`total` 为整个合格候选池数量）

| 字段 | 类型 | 说明 |
|---|---|---|
| `bottleId` ★ | int | 漂流感 ID（候选） |
| `author` ★ | object | `{ userId, nickname, avatarPath }` —— **即匹配到的人**，对应旧 `matched_user_id` |
| `book` | object | `{ bookId, title, author, coverPath, status }` |
| `status` | string | `active`/`expired`/`withdrawn` |
| `aiStatus` ★ | string | `pending`/`processing`/`ready`/`failed` —— AI 处理状态 |
| `createdAt` | date-time | 实际入池时间（审核通过且公开后），非提交时间 |
| `expiresAt` | date-time | 入池后 7 天，UTC |
| `contentPreview` | string | 正文前 100 字 |
| `noteId` ★ | int | 候选原笔记 id（点赞/收藏/评论用这个，不是 bottleId） |
| `recommendation` ★ | string/null | AI 推荐语，1~100 字；生成失败为 null，不影响分数 |
| `matchScore` ★ | number | 匹配度 **0~100**，前端显示百分比（如 86.5%），**非原始向量距离**，绝不虚构 |

**匹配规则**：智能匹配（按内容相似度），**非随机**；候选排除 本人 / 已获取 / 过期 / 撤回 / 原笔记未过审或非公开 / 已删除 / AI 未就绪。
**获取流程**：列表浏览不产生记录；**点开某条**才生成 `interactionId` → `POST` 发书友申请 → 对方 `accept`/`reject`；对方 `accept` 后即成为**书友**，落库 `书友关系`（见下）。

**书友关系**（对方 `accept` 后落库；`friendId` 即匹配候选返回的 `author.userId`）：

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | int | 关系 id |
| `userId` | int | 主动发起书友申请的人 |
| `friendId` | int | 书友用户 id（被 accept 的一方），即匹配候选 `author.userId` |
| `status` | string | `pending`/`accepted`/`rejected` |
| `createdAt` | date-time | 关系创建时间，UTC |

---

## 5. 读书墙（实时公开笔记 + 点赞 / 评论 / 收藏）

前提：只展示**我的书友（已 `accept` 的匹配好友）** 的读书笔记，即 `author.userId ∈ 我的书友集合` 且 `isPublic=true 且 reviewStatus=approved`。

| 字段 | 类型 | 说明 |
|---|---|---|
| `noteId` | int | 原笔记 id（点赞/收藏/评论绑定它，不是 bottleId） |
| `author` | object | `{ userId, nickname, avatarPath }` |
| `content` | text | 正文 |
| `likeCount` / `isLiked` | int / bool | 点赞 |
| `favoriteCount` / `isFavorited` | int / bool | 收藏 |
| `commentCount` | int | 评论数 |
| `comments` | object[] | 每条 `{ commentId, noteId, author, content, createdAt, canDelete }` |

实时滚动为 WebSocket（可选，D4 有余力再做）。

---

## 6. 管理员（审核公开笔记 + 管理书籍）

| 字段 | 类型 | 说明 |
|---|---|---|
| `reviewStatus` ★ | string | 审核：`pending` → `approved`/`rejected` |
| `reviewReason` | string/null | 拒绝时必填（1~500 字）；通过时 null |
| `reviewedBy` | int | 审核管理员 id |
| 书籍 `book` | object | `{ bookId, title, author, isbn, coverPath, intro, status, createdAt, updatedAt }` |

---

## C 与 B 已敲定的决定（定稿）

- 匹配 = **智能匹配**（按 matchScore），弃用"随机匹配"
- 保留 **AI 三栏**（`topics`/`keywords`/`sentiment`），上传时实时提取，独立于匹配 AI
- 匹配度用 **`matchScore` 0~100**，由 C 从余弦相似度真实归一化，绝不虚构
- 私密/未过审/被拒笔记 **不入池**

> 唯一未落定细节：`matchScore 0~100` 的具体归一化公式（C 实现，保证"计算失败不返回虚构分数"）。
