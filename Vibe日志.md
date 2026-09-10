# 前端 A · Vibe Coding 开发日志

> 记录人：前端 A（负责 Vue3 前端页面搭建、前后端联调、AI 数据展示）
> 格式：每条迭代含 6 要素——①本次迭代目标 ②使用的提示词(Prompt) ③AI 生成/输出 ④遇到的 bug/问题 ⑤迭代修改操作 ⑥小组对代码的理解，并在修改操作后附「关键代码」片段。
> 备注：②③⑥ 的提示词/AI 输出/理解按实际操作还原，措辞请对照真实下达的指令核对后微调。

---

### 迭代 1：前端页面骨架搭建（预览模式假数据）

- **① 本次迭代目标**：用 Vue3 单文件组件搭出登录页、主页、四卡片等基础页面，先用假数据把 UI 跑通。
- **② 使用的提示词**：
  > 「用 Vue3 组合式 API 帮我搭『书遇』的登录页：邮箱 + 密码两个输入框、一个登录按钮，卡片式居中布局，配色用暖色书卷风；同时用 currentPage 变量做页面切换，预留主页和书单区域。」
- **③ AI 生成/输出**：生成了 `App.vue` 单文件组件，含登录表单、`currentPage` 页面切换逻辑、基础 CSS，各页面先用 `preview*` 假数据填充。
- **④ 遇到的 bug/问题**：初版页面全部是静态假数据，没有后端。
- **⑤ 迭代修改操作**：建立 `currentPage` 状态管理，按值切换登录/主页/书单/笔记等区域。

```js
// App.vue：单变量 currentPage 切换页面（9 个页面区域共用一份模板）
const currentPage = ref('login')
// login / home / shelf / note / bookDetail / match / wall / friends / admin

// 模板里按 currentPage 条件渲染各页面区域（截取）
<div v-if="currentPage === 'login'" class="auth-page">…</div>
<div v-else-if="currentPage === 'home'" class="home-page">…</div>
```

- **⑥ 小组对代码的理解**：单文件 `App.vue` + `currentPage` 切换，起步快、适合快速验证；缺点是功能多了会臃肿，后续应拆组件。

### 迭代 2：登录/注册真实鉴权

- **① 本次迭代目标**：把假登录换成真实鉴权，登录后能区分 user/admin 并按角色跳转。
- **② 使用的提示词**：
  > 「把登录改成调 `POST /api/auth/login`，body 是 email+password；成功后把返回的 token 存 localStorage，再调 `GET /api/me` 拿 role：role=user 进主页、role=admin 进管理员页；请求统一封装成带 Bearer token 的 request 函数。」
- **③ AI 生成/输出**：生成了统一 `request()` 封装（自动带 `Authorization: Bearer`），以及登录 → `/api/me` → 按 role 跳转的完整链路。
- **④ 遇到的 bug/问题**：不确定 token 存哪、后端返回 401 时怎么处理。
- **⑤ 迭代修改操作**：token 存 localStorage（7 天）；`request()` 统一处理 `code` 200/400/401，401 自动跳登录页。

```js
// 统一请求封装：自动带 Bearer token，401 自动跳登录
async function request(path, options = {}) {
  const headers = { ...(options.headers || {}) }
  if (options.body && !(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json'
  }
  if (token.value) headers['Authorization'] = 'Bearer ' + token.value
  const res = await fetch(path, { ...options, headers })
  const json = await res.json()
  if (json.code === 401) { logout(); throw new Error(json.message || '请先登录') }
  return json
}

// 登录：存 token → 拉资料 → 按 role 分流
async function handleLogin() {
  const json = await request('/api/auth/login', { method: 'POST', body: JSON.stringify(loginForm.value) })
  if (json.code === 200) {
    token.value = json.data.token
    localStorage.setItem('token', json.data.token)
    await loadMe()
  }
}
async function loadMe() {
  const json = await request('/api/me')
  if (json.code === 200) {
    currentUser.value = json.data
    currentPage.value = json.data.role === 'admin' ? 'admin' : 'home'
  }
}
```

- **⑥ 小组对代码的理解**：登录态 = token 存本地 + 请求统一带 Bearer + 401 兜底跳登录，这是后面所有接口的前置条件。

### 迭代 3：各模块接真实接口（书单/笔记/匹配/读书墙/书友/管理员）

- **① 本次迭代目标**：把主页各卡片和各功能页的假数据逐个换成真实后端接口。
- **② 使用的提示词**（示例）：
  > 「书单卡片改成调 `GET /api/me/books`，按 readingStatus 分『在读/想读/已读』三栏，数据从返回的 `data.list` 读，空数据显示空态文案。」
- **③ AI 生成/输出**：为每个模块生成对应的请求函数和渲染逻辑，按模块逐个替换。
- **④ 遇到的 bug/问题**：多个模块字段名不确定（matchScore / reviewStatus / isPublic 等），分页返回结构不统一。
- **⑤ 迭代修改操作**：统一按 `{code,data,message}` 读、列表统一读 `data.list`/`data.total`、字段统一 camelCase。

```js
// 书单：调真实接口，统一读 data.list
async function loadShelf() {
  const json = await request('/api/me/books?pageSize=100')
  if (json.code === 200) {
    shelfBooks.value = (json.data.list || []).map((item) => ({
      ...item.book,
      readingStatus: item.readingStatus,
    }))
  }
}
```

- **⑥ 小组对代码的理解**：后端统一返回 `{code,data,message}`，列表统一 `{list,total,pageNum,pageSize}`，前端按这个契约写，不再猜字段。

### 迭代 4：接口缺失 + 路径对齐（比对 openapi.json）

- **① 本次迭代目标**：联调时前端多个接口 404/405，找出缺失接口和路径不一致。
- **② 使用的提示词**：
  > 「拉取后端 `/openapi.json`，逐条比对前端调用的所有接口，列出哪些返回 404、哪些路径对不上，输出一张缺失/不一致清单。」
- **③ AI 生成/输出**：发现后端缺 6 个接口（`DELETE /api/me/books/{bookId}`、`GET /api/books/{bookId}`、`GET /api/me/friends` 等）+ 2 个路径对不上（`/api/wall/notes` vs `/api/wall`、发书友申请的路径），给出清单。
- **④ 遇到的 bug/问题**：6 个接口后端没实现、2 个路径改名，导致前端 404/405。
- **⑤ 迭代修改操作**：把清单反馈给后端，后端补全接口 + 对两处路径做兼容，前端代码无需改。

```js
// 联调时前端已调用、但后端 404 的接口（比对 openapi.json 后反馈后端补齐）
await request(`/api/me/books/${book.bookId}`, { method: 'DELETE' })  // 移除书
await request(`/api/books/${bookId}`)                                  // 书籍详情
await request('/api/me/friends')                                       // 书友列表
// 共 6 个接口缺失 + 2 个路径对不上（/api/wall/notes → /api/wall 等），后端补全 + 做兼容，前端无需改
```

- **⑥ 小组对代码的理解**：接口契约要以后端 `openapi.json` 为准，前端不能凭感觉猜路径和字段。

### 迭代 5：删掉 PREVIEW_MODE 假数据

- **① 本次迭代目标**：联调全部跑通后，清掉所有预览假数据，只保留真实接口。
- **② 使用的提示词**：
  > 「删掉 `App.vue` 里的 `PREVIEW_MODE` 开关、所有 `preview*` 假数据、`previewAiResult`/`previewHome` 以及全部 fallback 分支和预览相关 CSS，删完 dev server 编译要通过。」
- **③ AI 生成/输出**：删了 9 个 preview 假数据 + previewAiResult/previewHome + 全部 fallback 分支 + 模板 preview-link + 对应 CSS。
- **④ 遇到的 bug/问题**：假数据和真接口并存，容易误用、演示时可能点到假数据。
- **⑤ 迭代修改操作**：删除 `PREVIEW_MODE` 及所有预览分支，确认 `npm run dev` 编译通过。

```js
// 删除 PREVIEW_MODE 及全部 preview 假数据后，启动只走真实鉴权
onMounted(async () => {
  if (token.value) {           // 有 token 就尝试恢复登录态
    try {
      await loadMe()
    } catch (e) {
      // request 已处理 401，这里不用额外操作
    }
  }
})
```

- **⑥ 小组对代码的理解**：预览模式只是联调前的过渡，联调完成后必须清干净，避免答辩演示点到假数据。

### 迭代 6：头像显示真实头像

- **① 本次迭代目标**：让各处头像显示用户真实头像图片，而不是「昵称首字」占位。
- **② 使用的提示词**：
  > 「把头像从『昵称首字』占位改成显示真实头像 `avatarPath` 图片，图片加载失败时自动回退到首字；同时 `vite.config.js` 加 `/uploads` 代理转发到后端。」
- **③ AI 生成/输出**：生成「首字 span + 绝对定位 img + `@error` 移除图片」的复用模式，改了 14 处头像位，并在 `vite.config.js` 加了 `/uploads` 代理。
- **④ 遇到的 bug/问题**：后端返回相对路径 `/uploads/xxx`，前端没配代理会 404。
- **⑤ 迭代修改操作**：14 处头像位统一改成「首字兜底 + 真实图叠加」，`vite.config.js` 加 `/uploads` 代理。

```html
<!-- 头像：首字兜底 + 真实图片叠加，图片加载失败自动回退首字 -->
<span class="user-avatar">
  {{ (currentUser?.nickname || currentUser?.username || '书').slice(0, 1) }}
  <img v-if="currentUser?.avatarPath" class="avatar-img"
       :src="currentUser.avatarPath" alt="" @error="$event.target.remove()" />
</span>
```

```css
.user-avatar { position: relative; overflow: hidden; }
.avatar-img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
```

```js
// vite.config.js：/uploads 代理转发到后端
proxy: {
  '/api':      { target: 'http://10.180.24.176:8000', changeOrigin: true },
  '/uploads':  { target: 'http://10.180.24.176:8000', changeOrigin: true },
}
```

- **⑥ 小组对代码的理解**：头像 = 首字兜底 + 真实图叠加，图片加载失败自动回退；`/uploads` 静态资源要走代理转发到后端。
