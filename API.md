# 书遇 API 联调说明

基础地址：`http://127.0.0.1:8000`。除 `/api/health`、`/api/auth/register`、`/api/auth/login` 外，请求头均携带 `Authorization: Bearer <token>`。

所有响应 HTTP 状态为 200，JSON 结构固定为 `{ "code": 200|400|401, "data": ..., "message": "..." }`。

| 模块 | 方法与路径 | 说明 |
| --- | --- | --- |
| 健康 | `GET /api/health` | 返回服务状态 |
| 认证 | `POST /api/auth/register` | `email,password,nickname,avatarPath,gender,role` |
| 认证 | `POST /api/auth/login` | `email,password`，返回 token |
| 认证 | `GET /api/me` | 当前资料，前端以 `role` 跳转 |
| 上传 | `POST /api/uploads` | multipart：`file` + `purpose`；返回 `data.filePath` |
| 书籍 | `GET /api/books?keyword=&pageNum=&pageSize=` | Page<Book> |
| 书单 | `GET /api/me/books?status=` | `wantToRead/reading/read` |
| 书单 | `PUT /api/me/books` | `{bookId,readingStatus}` |
| 书单 | `DELETE /api/me/books/{bookId}` | 移出我的书单 |
| 书单 | `GET /api/me/current-reading` | 当前在读书籍 |
| 书籍 | `GET /api/books/{bookId}` | 书籍详情（含 `intro`） |
| 笔记 | `POST /api/notes` | `{bookId,content,isPublic,topics,keywords,sentiment}` |
| 笔记 | `GET /api/me/notes?isPublic=&reviewStatus=` | 我的笔记 |
| 笔记 | `DELETE /api/notes/{noteId}` | 软删除 |
| 匹配 | `GET /api/bottles/matches?noteId=&pageNum=&pageSize=` | 仅自己的公开、审核通过笔记可作源笔记 |
| 匹配 | `POST /api/bottles/{bottleId}/acquire` | 返回 `data.myInteraction.interactionId` |
| 书友 | `POST /api/interactions/{interactionId}/friend-requests` | 发起书友申请 |
| 书友 | `GET /api/me/friend-requests?direction=sent|received&status=` | Page<FriendRequest> |
| 书友 | `PATCH /api/friend-requests/{requestId}` | `{status: "accepted"|"rejected"}`，处理书友申请 |
| 书友 | `GET /api/me/friends` / `DELETE /api/me/friends/{userId}` | 查询、解除书友关系 |
| 读书墙 | `GET /api/wall/notes?pageNum=&pageSize=` | 仅我的已接受书友的已审核公开笔记，排除本人（`/api/wall` 也兼容） |
| 收藏 | `GET /api/me/favorites` | 我的可见收藏笔记，分页 |
| 互动 | `PUT/DELETE /api/notes/{noteId}/like` | 返回 NoteSocial（五个计数/状态字段） |
| 互动 | `PUT/DELETE /api/notes/{noteId}/favorite` | 返回 NoteSocial（五个计数/状态字段） |
| 互动 | `POST /api/notes/{noteId}/comments` | `{content}` |
| 互动 | `GET /api/notes/{noteId}/comments` | 评论分页列表 |
| 互动 | `DELETE /api/comments/{commentId}` | 删除自己的评论 |
| 管理 | `GET /api/admin/notes?reviewStatus=pending` | 待审笔记 |
| 管理 | `PUT /api/admin/notes/{noteId}/review` | `{reviewStatus,reviewReason}` |
| 管理 | `POST /api/admin/books` | 创建书籍 |
| 管理 | `PUT/DELETE /api/admin/books/{bookId}` | 修改、下架书籍 |
| AI 对接 | `PUT /api/bottles/{bottleId}/ai-status?aiStatus=ready` | C 同学完成向量化后标记 ready |
| AI 对接 | `GET /api/admin/bottles?aiStatus=pending` | 获取待向量化的笔记和 bottleId |

笔记上传时由 RAG 的 LLM 提取 AI 三栏；公开笔记审核通过后状态按 `pending → processing → ready / failed` 处理，只有 `ready` 才进入候选池。匹配调用硅基流动 bge-m3 的真实向量相似度，仅返回 `matchScore >= 55` 的候选并按分数降序；推荐语由 DeepSeek 为 Top 3 候选生成，失败时为 `null`。

## 给前端的约定结论

1. 上传成功固定读取 `data.filePath`。
2. 打开匹配项固定调用 `POST /api/bottles/{bottleId}/acquire`，申请书友使用 `data.myInteraction.interactionId`。
3. 书籍、书单、我的笔记、读书墙、书友申请与管理员列表均为 `data = { list, total, pageNum, pageSize }`；详情和单项操作返回对象。
4. 搜书参数名为 `keyword`。
5. 书友申请路径为 `/api/me/friend-requests`，`direction` 必填，字段为 `requestId/requester/receiver/status`（另有 bottleId、createdAt、handledAt）。
6. 点赞/收藏为 PUT 新增、DELETE 取消，均返回 `NoteSocial`：`noteId, likeCount, favoriteCount, commentCount, isLiked, isFavorited`。

补充兼容路径：发书友申请的正式写法为 `POST /api/friend-requests`，body 为 `{ "interactionId": 123 }`；旧的 `/api/interactions/{interactionId}/friend-requests` 仍可使用。

笔记 AI 三栏的时机：`POST /api/notes` 创建时立即提取并在该响应的 `data.topics`、`data.keywords`、`data.sentiment` 返回；审核只决定公开笔记能否入漂流瓶匹配池，不改变三栏展示时机。
