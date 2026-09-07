<script setup>
import { ref, onMounted } from 'vue'

// ========== 页面状态 ==========
const currentPage = ref('login')  // 当前显示哪个页面：'login' 或 'home'
const isRegister = ref(false)     // 登录页里显示「登录」还是「注册」表单
const backendStatus = ref('检查中...')

// ========== 表单数据 ==========
const loginForm = ref({ username: '', password: '' })
const registerForm = ref({ username: '', password: '', nickname: '', mode: 'anonymous' })

// 当前登录的用户信息
const currentUser = ref(null)

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

// 检查后端是否连通（显示在页面上，方便你确认前后端连接正常）
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
        <select v-model="registerForm.mode">
          <option value="anonymous">匿名模式</option>
          <option value="real">实名模式</option>
        </select>
        <button type="submit">注 册</button>
      </form>

      <p class="switch" @click="isRegister = !isRegister">
        {{ isRegister ? '已有账号？去登录' : '没有账号？去注册' }}
      </p>
      <p class="status">后端状态：{{ backendStatus }}</p>
    </div>
  </div>

  <!-- 主页（占位，后续功能从这里进入） -->
  <div v-else class="home-page">
    <h1>欢迎，{{ currentUser?.nickname || currentUser?.username }}</h1>
    <p class="tip">主页骨架已搭好，书单 / 笔记 / 匹配功能后面从这里进入。</p>
    <button class="logout-btn" @click="logout">退出登录</button>
  </div>
</template>

<style scoped>
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
.form input::placeholder {
  color: #c5b8a6;
}
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
.home-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
}
.home-page h1 {
  color: #333;
}
.tip {
  color: #999;
  font-size: 14px;
}
.logout-btn {
  padding: 10px 24px;
  border: 1px solid #e5ddd3;
  border-radius: 10px;
  background: #fff;
  color: #666;
  cursor: pointer;
}
</style>
