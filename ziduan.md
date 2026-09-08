# 书遇 · 字段定义（AI/数据 C 侧）

> 本文件记录 C（AI·数据）依赖与产出的字段，跟 `backend/API.md` 对齐。
> 原则：**D1 定死，之后不改**。本文档只针对 RAG 链路相关字段。

## 一、C 依赖的输入字段（来自 B 的接口）

### 1. 笔记上传 `POST /api/notes`

body：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `book_id` | int | 是 | 笔记所属书籍 id |
| `content` | text | 是 | 笔记正文（做 embedding 的原始文本） |

C 需要拿到的（入库后）：

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | int | 笔记 id，作为向量索引主键 |

### 2. 发起匹配 `POST /api/matches`

body：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `note_id` | int | 是 | 用哪条笔记作为 query 去检索 |

--- 

## 二、C 产出的字段（供 A 展示 / B 返回）

### 1. 笔记元信息（AI 提取，随 `POST /api/notes` 返回）

| 字段 | 类型 | 说明 |
|---|---|---|
| `topics` | string[] | 主题（DeepSeek 提取） |
| `keywords` | string[] | 关键词 |
| `sentiment` | string | 情绪（pos / neu / neg） |
| `status` | string | 审核状态（pending / approved / rejected） |

### 2. 匹配结果（`POST /api/matches` 返回 data，数组）

| 字段 | 类型 | 说明 |
|---|---|---|
| `matched_user_id` | int | 匹配到的用户 id |
| `matched_note_id` | int | 匹配到的笔记 id |
| `similarity_score` | float(0~1) | 余弦相似度，越高越接近 |
| `recommendation_text` | string | DeepSeek 生成的推荐语 |

--- 

## 三、RAG 链路内部字段（向量化 / 检索）

| 字段 | 类型 | 说明 |
|---|---|---|
| `embedding` | float[1024] | bge-m3 向量，维度固定 1024 |
| `top_n` | int | 返回条数，**待定（建议 3~5，见 API.md 待确认项）** |
| `threshold` | float | 相似度下限，低于此值返回兜底推荐语 |

## 四、待确认 / 约定

- [ ] Top-N 取几个（建议 3~5，C 默认按 3 实现，可在 config 调整）
- [ ] 相似度是否归一化后再展示（建议保留原始 0~1 余弦值）
- [ ] 无结果 / 全低分的兜底推荐语文案统一（C 提供，B 前端共用）
