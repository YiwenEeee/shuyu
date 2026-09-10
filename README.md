# 书遇

> 用读书内容寻找同频者的匿名社交应用。
> 你的摘录，会替你找到懂它的那个人。

## 项目定位

书遇是一个以 RAG 内容匹配为核心的**昵称展示的匿名书友社区**。用户上传读书笔记，系统通过向量相似度找到笔记内容最相近的人，AI 生成推荐语，帮助彼此建立书友关系。

数据闭环：上传笔记 → 后端存库 + AI 提取主题/关键词/情绪 → 列表刷新 → 管理员审核 → 公开笔记进读书墙 / 匹配池 → 匹配到同频书友。

## 功能

1. **用户系统**：邮箱注册登录（公开页只显示昵称和头像，不暴露真实邮箱），token 鉴权 + user/admin 双角色
2. **书单管理**：在读 / 想读 / 已读，书籍搜索与详情
3. **笔记上传**：AI 实时提取主题、关键词、情绪
4. **灵魂共振匹配**：RAG 向量相似度 + AI 推荐语（核心）
5. **读书墙**：只展示「已接受书友」的公开、审核通过、未删除笔记，并排除当前用户本人；支持点赞 / 评论 / 收藏
6. **书友关系**：发申请 → 接受 / 拒绝，管理书友列表
7. **管理员后台**：笔记审核 + 书籍上下架

## 技术栈

- 前端：Vue 3 + Vite
- 后端：Python FastAPI
- 数据库：SQLite
- 向量检索：NumPy 余弦相似度 + JSON 轻量持久化（无需本地向量库）
- LLM：DeepSeek（主题提取、推荐语）
- Embedding：硅基流动 bge-m3（API）

## 目录结构

前后端分属两个仓库。

**前端 `shuyu/`（A）**

```
shuyu/
├── frontend/
│   ├── index.html
│   ├── vite.config.js       # 含 /api、/uploads 代理
│   ├── package.json
│   └── src/
│       ├── main.js          # 入口
│       ├── App.vue          # 单文件组件（页面 + 逻辑）
│       └── style.css
└── README.md 等文档
```

**后端 `shuyu-houduan/`（B）**

```
shuyu-houduan/
├── app/
│   ├── main.py              # FastAPI 路由 + SQLAlchemy 模型 + SQLite 配置
│   └── services/            # RAG 服务（已实际接入）
│       ├── rag_service.py
│       ├── embedding.py
│       ├── llm.py
│       ├── vector_store.py
│       ├── feedback.py
│       └── rag_config.py
├── data/
│   └── vectors.json         # 向量数据
├── API.md                   # 接口说明
├── .env.example
└── requirements.txt
```

## 快速开始

### 后端（shuyu-houduan）

```powershell
cd shuyu-houduan
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env   # 填入 SILICONFLOW_API_KEY、DEEPSEEK_API_KEY，RAG_MOCK=0
uvicorn app.main:app --reload
```

真实 RAG 演示时用：

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
```

### 前端（shuyu/frontend）

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173

> 前端通过 `vite.config.js` 的 proxy 把 `/api`、`/uploads` 转发到后端。如后端地址不是 `10.180.24.176:8000`，请改成你自己的后端地址。

## 团队分工

- **前端**：页面与交互、前后端联调（28+ 接口）、AI 数据展示
- **后端**：FastAPI、SQLite、接口与数据模型、管理员后台
- **AI/数据**：Embedding、NumPy 向量检索、LLM 调用、RAG 链路
