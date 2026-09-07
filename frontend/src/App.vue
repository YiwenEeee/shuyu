<script setup>
import { ref, onMounted } from 'vue'

// ========== 页面状态 ==========
const currentPage = ref('login')  // login / home / shelf / note / match / wall
const isRegister = ref(false)     // 登录页里显示「登录」还是「注册」表单
const backendStatus = ref('检查中...')

// ========== 表单数据 ==========
const loginForm = ref({ username: '', password: '' })
const registerForm = ref({ username: '', password: '', nickname: '' })

// 当前登录的用户信息
const currentUser = ref(null)

// ========== 页面跳转 ==========
function go(page) {
  currentPage.value = page
}

// （临时）预览主页用，等后端登录接口做好后删除
function previewHome() {
  currentUser.value = { id: 1, username: 'test', nickname: '测试用户' }
  currentPage.value = 'home'
}

// ========== 页面一加载就做两件事 ==========
onMounted(() => {
  checkBackend()
  // 如果之前登录过（localStorage 里有记录），直接恢复登录态
  const saved = localStorage.getItem('user')
  if (saved) {
    currentUser.value = JSON.parse(saved)
    currentPage.value = 'home'
  }
})

// 检查后端是否连通（显示在登录页上）
async function checkBackend() {
  try {
    const res = await fetch('/api/health')
    backendStatus.value = res.ok ? '后端已连接' : '后端未响应'
  } catch {
    backendStatus.value = '后端未连接'
  }
}

// ========== 登录 ==========
async function handleLogin() {
  const res = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(loginForm.value),
  })
  const json = await res.json()
  if (json.code === 0) {
    currentUser.value = json.data
    localStorage.setItem('user', JSON.stringify(json.data))
    currentPage.value = 'home'
  } else {
    alert(json.message || '登录失败')
  }
}

// ========== 注册 ==========
async function handleRegister() {
  const res = await fetch('/api/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(registerForm.value),
  })
  const json = await res.json()
  if (json.code === 0) {
    alert('注册成功，请登录')
    isRegister.value = false
    loginForm.value.username = registerForm.value.username
  } else {
    alert(json.message || '注册失败')
  }
}

// ========== 退出登录 ==========
function logout() {
  currentUser.value = null
  localStorage.removeItem('user')
  currentPage.value = 'login'
}
</script>

<template>
  <!-- 登录 / 注册页 -->
  <div v-if="currentPage === 'login'" class="auth-page">
    <div class="auth-box">
      <div class="quote-mark">“</div>
      <h1 class="logo">书遇</h1>
      <p class="slogan">读过同一页，就是见过面</p>

      <!-- 登录表单 -->
      <form v-if="!isRegister" class="form" @submit.prevent="handleLogin">
        <input v-model="loginForm.username" placeholder="用户名" required />
        <input v-model="loginForm.password" type="password" placeholder="密码" required />
        <button type="submit">登 录</button>
      </form>

      <!-- 注册表单 -->
      <form v-else class="form" @submit.prevent="handleRegister">
        <input v-model="registerForm.username" placeholder="用户名" required />
        <input v-model="registerForm.password" type="password" placeholder="密码" required />
        <input v-model="registerForm.nickname" placeholder="昵称" required />
        <button type="submit">注 册</button>
      </form>

      <p class="switch" @click="isRegister = !isRegister">
        {{ isRegister ? '已有账号？去登录' : '没有账号？去注册' }}
      </p>
      <p class="status">后端状态：{{ backendStatus }}</p>
      <p class="preview-link" @click="previewHome">（临时）直接进入主页预览</p>
    </div>
  </div>

  <!-- 主页 -->
  <div v-else-if="currentPage === 'home'" class="home-page">
    <header class="topbar">
      <div class="brand">书遇</div>
      <div class="user-area">
        <span class="username">{{ currentUser?.nickname || currentUser?.username }}</span>
        <button class="logout-btn" @click="logout">退出</button>
      </div>
    </header>

    <main class="home-content">
      <section class="greeting">
        <h1>你好，{{ currentUser?.nickname || currentUser?.username }}</h1>
        <p>今天，想读点什么？</p>
        <p class="greeting-quote">“读过同一页，就是见过面”</p>
      </section>

      <section class="card-grid">
        <div class="card" @click="go('shelf')">
          <span class="card-icon icon-shelf">书</span>
          <h2>我的书单</h2>
          <p>在读 · 想读 · 已读</p>
        </div>
        <div class="card" @click="go('note')">
          <span class="card-icon icon-note">笔</span>
          <h2>上传笔记</h2>
          <p>记录你的摘录与感悟</p>
        </div>
        <div class="card card-primary" @click="go('match')">
          <span class="card-icon icon-match">遇</span>
          <h2>交个书友</h2>
          <p>让摘录找到懂你的人</p>
        </div>
        <div class="card" @click="go('wall')">
          <span class="card-icon icon-wall">墙</span>
          <h2>读书墙</h2>
          <p>看大家此刻在读什么</p>
        </div>
      </section>
    </main>
  </div>

  <!-- 书单占位页 -->
  <div v-else-if="currentPage === 'shelf'" class="placeholder-page">
    <h1>我的书单</h1>
    <p>这个页面还没做，后面会填上。</p>
    <button class="back-btn" @click="go('home')">返回主页</button>
  </div>

  <!-- 上传笔记占位页 -->
  <div v-else-if="currentPage === 'note'" class="placeholder-page">
    <h1>上传笔记</h1>
    <p>这个页面还没做，后面会填上。</p>
    <button class="back-btn" @click="go('home')">返回主页</button>
  </div>

  <!-- 匹配占位页 -->
  <div v-else-if="currentPage === 'match'" class="placeholder-page">
    <h1>找同频的人</h1>
    <p>这个页面还没做，后面会填上。</p>
    <button class="back-btn" @click="go('home')">返回主页</button>
  </div>

  <!-- 读书墙占位页 -->
  <div v-else-if="currentPage === 'wall'" class="placeholder-page">
    <h1>读书墙</h1>
    <p>这个页面还没做，后面会填上。</p>
    <button class="back-btn" @click="go('home')">返回主页</button>
  </div>
</template>

<style scoped>
/* ===== 登录页 ===== */
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background:
    radial-gradient(circle at 18% 18%, rgba(185, 138, 94, 0.07), transparent 45%),
    radial-gradient(circle at 82% 82%, rgba(185, 138, 94, 0.06), transparent 45%),
    linear-gradient(160deg, #fbf8f2 0%, #f5ecdd 100%);
}
.auth-box {
  width: 100%;
  max-width: 380px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid #efe6d8;
  border-radius: 20px;
  padding: 40px 36px 44px;
  box-shadow: 0 16px 48px rgba(139, 94, 60, 0.10);
  text-align: center;
  animation: card-in 0.5s ease;
}
.quote-mark {
  font-family: Georgia, 'Times New Roman', serif;
  font-size: 48px;
  line-height: 1;
  color: #e4d5c0;
  margin-bottom: 2px;
}
.logo {
  font-family: 'Songti SC', 'STSong', 'SimSun', 'Noto Serif SC', serif;
  font-size: 42px;
  letter-spacing: 12px;
  margin: 0 0 10px;
  color: #7d5233;
}
.slogan {
  color: #a58a6e;
  font-size: 15px;
  font-style: italic;
  letter-spacing: 1px;
  margin: 0 0 30px;
}
.form {
  display: flex;
  flex-direction: column;
  gap: 14px;
  animation: fade-in 0.35s ease;
}
.form input,
.form select {
  width: 100%;
  padding: 13px 15px;
  border: 1px solid #e8ddd0;
  border-radius: 12px;
  font-size: 15px;
  background: #fdfaf6;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.form input:focus,
.form select:focus {
  border-color: #b98a5e;
  box-shadow: 0 0 0 3px rgba(185, 138, 94, 0.12);
}
.form button {
  padding: 13px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #9a6a45, #7d5233);
  color: #fff;
  font-size: 16px;
  letter-spacing: 6px;
  cursor: pointer;
  transition: background 0.2s, transform 0.1s;
}
.form button:hover {
  background: #7d5233;
}
.form button:active {
  transform: scale(0.98);
}
.switch {
  margin-top: 20px;
  color: #a58a6e;
  font-size: 14px;
  cursor: pointer;
  transition: color 0.2s;
}
.switch:hover {
  color: #7d5233;
}
.status {
  margin-top: 12px;
  color: #c9bfb2;
  font-size: 12px;
}
.preview-link {
  margin-top: 14px;
  color: #c9bfb2;
  font-size: 12px;
  cursor: pointer;
  text-decoration: underline;
}
.form input::placeholder {
  color: #c5b8a6;
}

/* ===== 主页 ===== */
.home-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at 18% 18%, rgba(185, 138, 94, 0.07), transparent 45%),
    radial-gradient(circle at 82% 82%, rgba(185, 138, 94, 0.06), transparent 45%),
    linear-gradient(160deg, #fbf8f2 0%, #f5ecdd 100%);
}
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 40px;
  border-bottom: 1px solid #f0e7da;
}
.brand {
  font-family: 'Songti SC', 'STSong', 'SimSun', 'Noto Serif SC', serif;
  font-size: 24px;
  letter-spacing: 8px;
  color: #7d5233;
}
.user-area {
  display: flex;
  align-items: center;
  gap: 14px;
}
.username {
  color: #8a7a68;
  font-size: 14px;
}
.logout-btn {
  padding: 7px 18px;
  border: 1px solid #e5ddd3;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.7);
  color: #8a7a68;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}
.logout-btn:hover {
  color: #7d5233;
  border-color: #b98a5e;
}

.home-content {
  max-width: 1080px;
  margin: 0 auto;
  padding: 40px 24px 60px;
}
.greeting {
  margin-bottom: 36px;
}
.greeting h1 {
  font-size: 30px;
  font-weight: 600;
  color: #4a3a2a;
  margin: 0 0 8px;
}
.greeting p {
  font-size: 15px;
  color: #a58a6e;
  margin: 0;
}
.greeting .greeting-quote {
  margin-top: 18px;
  padding-left: 14px;
  border-left: 2px solid #b98a5e;
  font-family: 'Songti SC', 'STSong', 'SimSun', 'Noto Serif SC', serif;
  font-style: italic;
  font-size: 14px;
  color: #b08a5e;
  letter-spacing: 2px;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 22px;
}
.card {
  background: #fff;
  border: 1px solid #efe6d8;
  border-radius: 18px;
  padding: 30px 22px 26px;
  cursor: pointer;
  text-align: center;
  transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
  animation: card-in 0.5s ease backwards;
}
.card:nth-child(1) { animation-delay: 0s; }
.card:nth-child(2) { animation-delay: 0.1s; }
.card:nth-child(3) { animation-delay: 0.2s; }
.card:nth-child(4) { animation-delay: 0.3s; }
.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 14px 36px rgba(139, 94, 60, 0.15);
  border-color: #e0c9a8;
}
.card-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 54px;
  height: 54px;
  border-radius: 50%;
  font-family: 'Songti SC', 'STSong', 'SimSun', 'Noto Serif SC', serif;
  font-size: 26px;
  margin-bottom: 18px;
  box-shadow: 0 4px 12px rgba(139, 94, 60, 0.12);
  transition: transform 0.2s ease;
}
.card:hover .card-icon {
  transform: scale(1.06);
}
.icon-shelf {
  background: #f3e9db;
  color: #b98a5e;
}
.icon-note {
  background: #f7e8d8;
  color: #c98a5a;
}
.icon-match {
  background: linear-gradient(135deg, #b98a5e, #9a6a45);
  color: #fff;
}
.icon-wall {
  background: #f6ead9;
  color: #a97b50;
}
.card h2 {
  font-size: 17px;
  color: #5f4a33;
  margin: 0 0 8px;
}
.card p {
  font-size: 13px;
  color: #a58a6e;
  margin: 0;
  line-height: 1.6;
}
.card-primary {
  background: #fff;
  border-color: #d9b98a;
}
.card-primary h2 {
  color: #5f4a33;
}
.card-primary p {
  color: #a58a6e;
}

/* ===== 占位页 ===== */
.placeholder-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  background:
    radial-gradient(circle at 18% 18%, rgba(185, 138, 94, 0.07), transparent 45%),
    radial-gradient(circle at 82% 82%, rgba(185, 138, 94, 0.06), transparent 45%),
    linear-gradient(160deg, #fbf8f2 0%, #f5ecdd 100%);
}
.placeholder-page h1 {
  color: #5f4a33;
}
.placeholder-page p {
  color: #a58a6e;
  font-size: 14px;
}
.back-btn {
  padding: 10px 24px;
  border: 1px solid #e5ddd3;
  border-radius: 20px;
  background: #fff;
  color: #8a7a68;
  cursor: pointer;
  transition: all 0.2s;
}
.back-btn:hover {
  color: #7d5233;
  border-color: #b98a5e;
}

/* ===== 动画 ===== */
@keyframes card-in {
  from {
    opacity: 0;
    transform: translateY(16px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
