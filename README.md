# 书遇

> 用读书内容寻找同频者的匿名社交应用。
> 你的摘录，会替你找到懂它的那个人。

## 项目定位

书遇是一个以 RAG 内容匹配为核心的匿名书友社区。用户上传读书笔记，系统通过向量相似度找到笔记内容最相近的人，AI 生成推荐语，帮助彼此建立书友关系。

## 功能

1. **用户系统**：注册登录 + 匿名/实名切换
2. **书单管理**：在读 / 想读 / 已读
3. **笔记上传**：AI 提取主题、关键词、情绪
4. **灵魂共振匹配**：RAG 向量相似度 + AI 推荐语（核心）
5. **读书墙**：WebSocket 实时滚动最新笔记
6. **管理员后台**：笔记审核 + 书籍管理

## 技术栈

- 前端：Vue 3 + Vite
- 后端：Python FastAPI
- 数据库：SQLite
- 向量检索：API Embedding + NumPy 余弦相似度（轻量，无需本地向量库）
- LLM：DeepSeek（主题提取、推荐语）
- Embedding：硅基流动 bge-m3（API）
- 实时通信：WebSocket

## 目录结构

```
shuyu/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI 入口
│   │   ├── config.py        # 配置
│   │   ├── database.py      # SQLite 连接
│   │   ├── models.py        # 数据表
│   │   ├── routers/         # 路由
│   │   └── services/        # LLM / Embedding / 向量库
│   ├── data/books.json      # 书籍元数据
│   ├── requirements.txt
│   └── .env.example
└── frontend/                # Vue 3 + Vite
```

## 快速开始

### 后端

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate  |  macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # 填入 API key
uvicorn app.main:app --reload
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173

## 团队分工

- **前端**：页面与交互、WebSocket 客户端
- **后端**：FastAPI、SQLite、WebSocket 服务端、管理员后台
- **AI/数据**：Embedding、NumPy 向量检索、LLM 调用、RAG 链路
