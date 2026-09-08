<script setup>
import { ref, onMounted, computed } from 'vue'

// ========== 页面状态 ==========
const currentPage = ref('login')  // login / home / shelf / note / bookDetail / match / wall / friends / admin
const isRegister = ref(false)     // 登录页里显示「登录」还是「注册」表单
const loginRole = ref('user')     // 登录身份：user 用户 / admin 管理员

function switchRole(role) {
  loginRole.value = role
  isRegister.value = false
}

// ========== 表单数据 ==========
const loginForm = ref({ email: '', password: '' })
const registerForm = ref({ nickname: '', email: '', password: '', gender: 'unspecified' })
const avatarFile = ref(null)

// 当前登录的用户信息
const currentUser = ref(null)

// 登录 token：只持久缓存 token，资料用 token 调 /api/me 拿
const token = ref(localStorage.getItem('token') || '')

// 统一请求：自动带 token，401 跳登录
async function request(path, options = {}) {
  const headers = { ...(options.headers || {}) }
  if (options.body && !(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json'
  }
  if (token.value) headers['Authorization'] = 'Bearer ' + token.value
  let json
  try {
    const res = await fetch(path, { ...options, headers })
    json = await res.json()
  } catch (e) {
    // 后端没启动 / 代理 502 / 非 JSON 响应：按失败返回，让调用方走 PREVIEW_MODE 兜底
    return { code: -1, data: null, message: '后端未连接' }
  }
  if (json.code === 401) {
    logout()
    throw new Error(json.message || '请先登录')
  }
  return json
}

// ========== 临时预览数据（后端接口没做前，先填假数据看效果；B 接口好了后删掉这里 + 相关 fallback） ==========
const PREVIEW_MODE = true

const previewBooks = [
  { bookId: 1, title: '百年孤独', author: '加西亚·马尔克斯', readingStatus: 'reading', intro: '魔幻现实主义代表作，布恩迪亚家族七代人的传奇。', isbn: '9787544253994' },
  { bookId: 4, title: '围城', author: '钱钟书', readingStatus: 'reading', intro: '城外的人想冲进去，城里的人想逃出来。', isbn: '9787020024750' },
  { bookId: 2, title: '三体', author: '刘慈欣', readingStatus: 'wantToRead', intro: '中国科幻里程碑，人类文明与三体文明的生死博弈。', isbn: '9787536692930' },
  { bookId: 5, title: '小王子', author: '圣埃克苏佩里', readingStatus: 'wantToRead', intro: '写给大人的童话，关于爱与责任。', isbn: '9787020042494' },
  { bookId: 3, title: '活着', author: '余华', readingStatus: 'read', intro: '一个人和他命运之间的友情，讲述苦难中的坚韧。', isbn: '9787506365437' },
  { bookId: 6, title: '平凡的世界', author: '路遥', readingStatus: 'read', intro: '普通人在大时代历史进程中的奋斗与挣扎。', isbn: '9787506376040' },
]

const previewNotes = [
  { noteId: 101, bookId: 1, bookTitle: '百年孤独', content: '许多年之后，面对行刑队，奥雷里亚诺·布恩迪亚上校将会回想起父亲带他去见识冰块的那个遥远的下午。\n\n开头就把过去、现在、未来折叠在一起，太惊艳了。', isPublic: true, reviewStatus: 'approved', createdAt: '2026-09-01' },
  { noteId: 102, bookId: 1, bookTitle: '百年孤独', content: '家族的第一个人被捆在树上，最后一个人正被蚂蚁吃掉。\n\n宿命的循环感扑面而来。', isPublic: false, reviewStatus: 'pending', createdAt: '2026-09-03' },
  { noteId: 103, bookId: 3, bookTitle: '活着', content: '人是为了活着本身而活着，而不是为了活着之外的任何事物而活着。\n\n这句话回答了整本书的题眼。', isPublic: true, reviewStatus: 'approved', createdAt: '2026-08-28' },
  { noteId: 104, bookId: 2, bookTitle: '三体', content: '给岁月以文明，而不是给文明以岁月。\n\n', isPublic: true, reviewStatus: 'approved', createdAt: '2026-09-05' },
  { noteId: 105, bookId: 2, bookTitle: '三体', content: '\n\n把文明的尺度拉到宇宙级别，读完久久不能平静。', isPublic: false, reviewStatus: 'pending', createdAt: '2026-09-06' },
  { noteId: 106, bookId: 4, bookTitle: '围城', content: '婚姻是一座围城，城外的人想进去，城里的人想出来。\n\n不止婚姻，人生处处是围城。', isPublic: true, reviewStatus: 'approved', createdAt: '2026-09-06' },
  { noteId: 107, bookId: 6, bookTitle: '平凡的世界', content: '生活不能等待别人来安排，要自己去争取和奋斗。\n\n孙少平让我看到平凡人身上的光。', isPublic: true, reviewStatus: 'approved', createdAt: '2026-09-07' },
  { noteId: 108, bookId: 5, bookTitle: '小王子', content: '真正重要的东西，用眼睛是看不见的，要用心去看。\n\n长大了才读懂这句话。', isPublic: false, reviewStatus: 'pending', createdAt: '2026-09-08' },
]

// ========== 书单数据 ==========
const shelfTab = ref('all') // all 全部 / reading 在读 / wantToRead 想读 / read 已读
const shelfTabs = [
  { key: 'all', label: '全部' },
  { key: 'reading', label: '在读' },
  { key: 'wantToRead', label: '想读' },
  { key: 'read', label: '已读' },
]
const statusText = { reading: '在读', wantToRead: '想读', read: '已读' }
const shelfBooks = ref([])
const shelfLoading = ref(false)

async function loadShelf() {
  shelfLoading.value = true
  try {
    const json = await request('/api/me/books?pageSize=100')
    if (json.code === 200) {
      shelfBooks.value = (json.data.list || []).map((item) => ({
        ...item.book,
        readingStatus: item.readingStatus,
      }))
    } else if (PREVIEW_MODE) {
      shelfBooks.value = [...previewBooks]
    }
  } catch (e) {
    if (PREVIEW_MODE) {
      shelfBooks.value = [...previewBooks]
    } else {
      alert(e.message || '加载书单失败')
    }
  } finally {
    shelfLoading.value = false
  }
}
const searchQuery = ref('')
const filteredBooks = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  return shelfBooks.value.filter((b) => {
    const matchStatus = shelfTab.value === 'all' || b.readingStatus === shelfTab.value
    const matchQuery =
      !q || b.title.toLowerCase().includes(q) || b.author.toLowerCase().includes(q)
    return matchStatus && matchQuery
  })
})
const shelfCounts = computed(() => {
  const c = { all: 0, reading: 0, wantToRead: 0, read: 0 }
  shelfBooks.value.forEach((b) => {
    c[b.readingStatus]++
    c.all++
  })
  return c
})

// 书单管理态：管理按钮开关 + 待确认移除的书籍
const shelfManage = ref(false)
const removingId = ref(null)
const detailBook = ref(null)

function toggleManage() {
  shelfManage.value = !shelfManage.value
  removingId.value = null
}

function removeBook(book) {
  if (removingId.value === book.bookId) {
    confirmRemoveBook(book)
  } else {
    removingId.value = book.bookId
  }
}

async function confirmRemoveBook(book) {
  try {
    const json = await request(`/api/me/books/${book.bookId}`, { method: 'DELETE' })
    if (json.code === 200) {
      shelfBooks.value = shelfBooks.value.filter((b) => b.bookId !== book.bookId)
      removingId.value = null
    } else {
      alert(json.message || '移除失败')
    }
  } catch (e) {
    alert(e.message || '移除失败')
  }
}

// 点开一本书，进入它的详情页（拉完整详情，含 intro/isbn）
async function openBookDetail(book) {
  if (shelfManage.value) return
  detailBook.value = book
  currentPage.value = 'bookDetail'
  const json = await request(`/api/books/${book.bookId}`)
  if (json.code === 200) {
    detailBook.value = json.data
  }
}

// 从详情页「记笔记」跳上传，并预选这本书
function goNoteForBook(book) {
  selectedBook.value = book
  noteForm.value.bookId = book.bookId
  bookSearch.value = book.title + ' · ' + book.author
  currentPage.value = 'note'
}

function notesForBook(bookId) {
  return myNotes.value.filter((n) => n.bookId === bookId)
}

// 把合并的 content 拆回「原文 / 评价」
function splitNote(content) {
  const idx = (content || '').indexOf('\n\n')
  if (idx === -1) return { quote: content || '', comment: '' }
  return { quote: content.slice(0, idx), comment: content.slice(idx + 2) }
}

// ========== 笔记数据 ==========
const noteForm = ref({ bookId: '', quote: '', comment: '', isPublic: true })
const noteLoading = ref(false)
const lastAiResult = ref(null) // 上传成功后 AI 返回 { topics, keywords, sentiment }
const sentimentText = { pos: '积极', neu: '中性', neg: '消极' }

// 选择书籍：搜索上架书，可下拉选择
const bookSearch = ref('')
const bookOpen = ref(false)
const bookOptions = ref([])
const selectedBook = ref(null)

async function searchBooks() {
  const q = bookSearch.value.trim()
  if (!q) {
    bookOptions.value = PREVIEW_MODE ? [...previewBooks] : []
    return
  }
  const json = await request(`/api/books?keyword=${encodeURIComponent(q)}&pageSize=20`)
  if (json.code === 200) {
    bookOptions.value = json.data.list || []
  } else if (PREVIEW_MODE) {
    bookOptions.value = previewBooks.filter(
      (b) => b.title.includes(q) || b.author.includes(q)
    )
  }
}

function pickBook(book) {
  selectedBook.value = book
  noteForm.value.bookId = book.bookId
  bookSearch.value = book.title + ' · ' + book.author
  bookOpen.value = false
}

function onBookFocus() {
  bookSearch.value = ''
  bookOpen.value = true
  bookOptions.value = PREVIEW_MODE ? [...previewBooks] : []
}

function onBookInput() {
  bookOpen.value = true
  searchBooks()
}

function onBookBlur() {
  bookOpen.value = false
  if (noteForm.value.bookId && selectedBook.value) {
    bookSearch.value = selectedBook.value.title + ' · ' + selectedBook.value.author
  }
}

const myNotes = ref([])

async function loadMyNotes() {
  const json = await request('/api/me/notes?pageSize=100')
  if (json.code === 200) {
    myNotes.value = (json.data.list || []).map((n) => ({
      noteId: n.noteId,
      bookId: n.book?.bookId,
      bookTitle: n.book?.title,
      content: n.content,
      isPublic: n.isPublic,
      reviewStatus: n.reviewStatus,
      reviewReason: n.reviewReason,
      createdAt: n.createdAt,
    }))
  } else if (PREVIEW_MODE) {
    myNotes.value = [...previewNotes]
  }
}

// 笔记审核状态显示文案
const reviewStatusText = { pending: '待审核', approved: '已通过', rejected: '未通过' }

// 上传笔记页：搜索自己的笔记
const noteSearchQuery = ref('')
const filteredMyNotes = computed(() => {
  const q = noteSearchQuery.value.trim().toLowerCase()
  if (!q) return myNotes.value
  return myNotes.value.filter(
    (n) => n.bookTitle.toLowerCase().includes(q) || n.content.toLowerCase().includes(q)
  )
})

async function submitNote() {
  const quote = noteForm.value.quote.trim()
  const comment = noteForm.value.comment.trim()
  if (!noteForm.value.bookId || (!quote && !comment)) {
    alert('请选择书籍，并至少填写「摘录原文」或「我的评价」中的一项')
    return
  }
  const content = quote + '\n\n' + comment
  noteLoading.value = true
  try {
    const json = await request('/api/notes', {
      method: 'POST',
      body: JSON.stringify({
        bookId: noteForm.value.bookId,
        content,
        isPublic: noteForm.value.isPublic,
      }),
    })
    if (json.code === 200) {
      lastAiResult.value = {
        topics: json.data.topics || [],
        keywords: json.data.keywords || [],
        sentiment: json.data.sentiment || 'neu',
      }
      alert(json.message || '笔记已保存，待审核')
      noteForm.value.quote = ''
      noteForm.value.comment = ''
      await loadMyNotes()
    } else if (PREVIEW_MODE) {
      // 预览模式：后端没接口，伪造成功 + 假 AI 结果，方便看效果
      lastAiResult.value = previewAiResult(content)
      myNotes.value.unshift({
        noteId: Date.now(),
        bookId: noteForm.value.bookId,
        bookTitle: selectedBook.value?.title || '',
        content,
        isPublic: noteForm.value.isPublic,
        reviewStatus: 'pending',
        createdAt: '刚刚',
      })
      noteForm.value.quote = ''
      noteForm.value.comment = ''
      alert('（预览）笔记已保存，AI 提取如下')
    } else {
      alert(json.message || '上传失败')
    }
  } catch (e) {
    alert(e.message || '上传失败')
  } finally {
    noteLoading.value = false
  }
}

// 预览模式临时造一份 AI 结果（后端接口好了后删掉）
function previewAiResult(content) {
  const words = (content || '')
    .split(/[\n，。！？、\s]+/)
    .filter(Boolean)
    .slice(0, 3)
  const sentiment = /(孤独|痛苦|悲伤|难过|绝望|失去|死)/.test(content)
    ? 'neg'
    : /(喜欢|感动|希望|美好|温暖|爱)/.test(content)
      ? 'pos'
      : 'neu'
  return { topics: ['文学', '感悟'], keywords: words, sentiment }
}

// ========== 页面跳转 ==========
function go(page) {
  currentPage.value = page
}

// （临时）预览主页用，等后端登录接口做好后删除
function previewHome() {
  const role = loginRole.value
  currentUser.value = { id: 1, username: 'test', nickname: '测试用户', role }
  if (role === 'admin') {
    currentPage.value = 'admin'
    loadAdminNotes()
    loadAdminBooks()
  } else {
    currentPage.value = 'home'
    loadShelf()
    loadMyNotes()
  }
}

// ========== 页面一加载就做两件事 ==========
onMounted(async () => {
  // 有 token 就尝试恢复登录态，失效会自动跳回登录页
  if (token.value) {
    try {
      await loadMe()
    } catch (e) {
      // request 已处理 401，这里不用额外操作
    }
  }
})

// ========== 登录 ==========
async function handleLogin() {
  try {
    const json = await request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(loginForm.value),
    })
    if (json.code === 200) {
      token.value = json.data.token
      localStorage.setItem('token', json.data.token)
      await loadMe()
    } else if (PREVIEW_MODE) {
      await loadMe()
    } else {
      alert(json.message || '登录失败')
    }
  } catch (e) {
    if (PREVIEW_MODE) {
      await loadMe()
    } else {
      alert(e.message || '登录失败')
    }
  }
}

// 用 token 拉取我的资料，拿到 role 后分流
async function loadMe() {
  const json = await request('/api/me')
  if (json.code === 200) {
    currentUser.value = json.data
    currentPage.value = json.data.role === 'admin' ? 'admin' : 'home'
    if (json.data.role === 'admin') {
      loadAdminNotes()
      loadAdminBooks()
    } else {
      loadShelf()
      loadMyNotes()
    }
  } else if (PREVIEW_MODE) {
    // 后端接口没做，预览模式直接伪造登录态进对应界面
    const role = loginRole.value
    currentUser.value = { userId: 1, username: 'yulan', nickname: '书友小A', role }
    if (role === 'admin') {
      currentPage.value = 'admin'
      loadAdminNotes()
      loadAdminBooks()
    } else {
      currentPage.value = 'home'
      loadShelf()
      loadMyNotes()
      refreshFriendBadge()
    }
  }
}

// ========== 注册 ==========
async function handleRegister() {
  try {
    if (!avatarFile.value) {
      alert('请先选择头像')
      return
    }
    const avatarPath = await uploadAvatar()
    const json = await request('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ ...registerForm.value, avatarPath }),
    })
    if (json.code === 200) {
      alert('注册成功，请登录')
      isRegister.value = false
      loginForm.value.email = registerForm.value.email
    } else {
      alert(json.message || '注册失败')
    }
  } catch (e) {
    alert(e.message || '注册失败')
  }
}

// 先上传头像，拿到 filePath 再注册
async function uploadAvatar() {
  const fd = new FormData()
  fd.append('file', avatarFile.value)
  fd.append('purpose', 'avatar')
  const res = await fetch('/api/uploads', { method: 'POST', body: fd })
  const json = await res.json()
  if (json.code === 200) return json.data.filePath
  throw new Error(json.message || '头像上传失败')
}

function onAvatarChange(e) {
  avatarFile.value = e.target.files[0] || null
}

// ========== 退出登录 ==========
function logout() {
  token.value = ''
  localStorage.removeItem('token')
  currentUser.value = null
  currentPage.value = 'login'
}

// ========== 管理员界面 ==========
const adminTab = ref('notes') // notes 审核笔记 / books 管理书籍

// 审核笔记
const adminNoteFilter = ref('pending')
const adminNoteFilters = [
  { key: 'pending', label: '待审核' },
  { key: 'approved', label: '已通过' },
  { key: 'rejected', label: '已拒绝' },
  { key: 'all', label: '全部' },
]
const adminNotes = ref([])
const rejectingNoteId = ref(null)
const rejectReason = ref('')

// 管理书籍
const adminBookStatus = ref('all')
const adminBooks = ref([])
const adminBookSearch = ref('')
const editingBookId = ref(null)
const editBookForm = ref({ title: '', author: '', isbn: '', intro: '', status: 'active' })

const previewAdminNotes = [
  { noteId: 201, author: { userId: 2, nickname: '山间读者' }, book: { bookId: 1, title: '百年孤独' }, content: '许多年之后，面对行刑队，奥雷里亚诺·布恩迪亚上校将会回想起父亲带他去见识冰块的那个遥远的下午。\n\n开头就把过去、现在、未来折叠在一起。', isPublic: true, reviewStatus: 'pending', reviewReason: null, createdAt: '2026-09-07' },
  { noteId: 202, author: { userId: 3, nickname: '云端旅人' }, book: { bookId: 2, title: '三体' }, content: '给岁月以文明，而不是给文明以岁月。\n\n', isPublic: true, reviewStatus: 'pending', reviewReason: null, createdAt: '2026-09-07' },
  { noteId: 203, author: { userId: 4, nickname: '林间书虫' }, book: { bookId: 3, title: '活着' }, content: '人是为了活着本身而活着，而不是为了活着之外的任何事物而活着。\n\n这句话回答了整本书的题眼。', isPublic: true, reviewStatus: 'approved', reviewReason: null, createdAt: '2026-09-05' },
  { noteId: 204, author: { userId: 5, nickname: '夜读人' }, book: { bookId: 1, title: '百年孤独' }, content: '家族的第一个人被捆在树上，最后一个人正被蚂蚁吃掉。\n\n宿命的循环感扑面而来。', isPublic: true, reviewStatus: 'rejected', reviewReason: '请补充自己的读书感受，删除无关广告。', createdAt: '2026-09-04' },
]

const previewAdminBooks = [
  { bookId: 1, title: '百年孤独', author: '加西亚·马尔克斯', isbn: '9787544253994', intro: '魔幻现实主义代表作，布恩迪亚家族七代人的传奇。', status: 'active' },
  { bookId: 2, title: '三体', author: '刘慈欣', isbn: '9787536692930', intro: '中国科幻里程碑，人类文明与三体文明的生死博弈。', status: 'active' },
  { bookId: 3, title: '活着', author: '余华', isbn: '9787506365437', intro: '一个人和他命运之间的友情，讲述苦难中的坚韧。', status: 'active' },
  { bookId: 4, title: '追风筝的人', author: '卡勒德·胡赛尼', isbn: '', intro: '', status: 'inactive' },
]

async function loadAdminNotes() {
  const json = await request('/api/admin/notes?pageSize=100')
  if (json.code === 200) {
    adminNotes.value = json.data.list || []
  } else if (PREVIEW_MODE) {
    adminNotes.value = [...previewAdminNotes]
  }
}

const filteredAdminNotes = computed(() => {
  if (adminNoteFilter.value === 'all') return adminNotes.value
  return adminNotes.value.filter((n) => n.reviewStatus === adminNoteFilter.value)
})

const adminNoteStats = computed(() => ({
  pending: adminNotes.value.filter((n) => n.reviewStatus === 'pending').length,
  approved: adminNotes.value.filter((n) => n.reviewStatus === 'approved').length,
  rejected: adminNotes.value.filter((n) => n.reviewStatus === 'rejected').length,
}))

const adminBookStats = computed(() => ({
  active: adminBooks.value.filter((b) => b.status === 'active').length,
  inactive: adminBooks.value.filter((b) => b.status === 'inactive').length,
}))

async function loadAdminBooks() {
  const json = await request('/api/admin/books?pageSize=100')
  if (json.code === 200) {
    adminBooks.value = json.data.list || []
  } else if (PREVIEW_MODE) {
    adminBooks.value = [...previewAdminBooks]
  }
}

function setAdminNoteFilter(key) {
  adminNoteFilter.value = key
}

const filteredAdminBooks = computed(() => {
  const q = adminBookSearch.value.trim().toLowerCase()
  return adminBooks.value.filter((b) => {
    const matchStatus = adminBookStatus.value === 'all' || b.status === adminBookStatus.value
    const matchQuery = !q || b.title.toLowerCase().includes(q) || b.author.toLowerCase().includes(q)
    return matchStatus && matchQuery
  })
})

async function approveNote(note) {
  const json = await request(`/api/admin/notes/${note.noteId}/review`, {
    method: 'PATCH',
    body: JSON.stringify({ reviewStatus: 'approved' }),
  })
  if (json.code === 200) {
    note.reviewStatus = 'approved'
    note.reviewReason = null
  } else if (PREVIEW_MODE) {
    note.reviewStatus = 'approved'
    note.reviewReason = null
  } else {
    alert(json.message || '操作失败')
  }
}

function startReject(note) {
  rejectingNoteId.value = note.noteId
  rejectReason.value = ''
}

async function confirmReject(note) {
  const reason = rejectReason.value.trim()
  if (!reason) {
    alert('请填写拒绝原因')
    return
  }
  const json = await request(`/api/admin/notes/${note.noteId}/review`, {
    method: 'PATCH',
    body: JSON.stringify({ reviewStatus: 'rejected', reviewReason: reason }),
  })
  if (json.code === 200) {
    note.reviewStatus = 'rejected'
    note.reviewReason = reason
  } else if (PREVIEW_MODE) {
    note.reviewStatus = 'rejected'
    note.reviewReason = reason
  } else {
    alert(json.message || '操作失败')
  }
  rejectingNoteId.value = null
  rejectReason.value = ''
}

function startEditBook(book) {
  editingBookId.value = book.bookId
  editBookForm.value = {
    title: book.title,
    author: book.author,
    isbn: book.isbn || '',
    intro: book.intro || '',
    status: book.status,
  }
}

async function saveBook(book) {
  const json = await request(`/api/admin/books/${book.bookId}`, {
    method: 'PATCH',
    body: JSON.stringify(editBookForm.value),
  })
  if (json.code === 200) {
    Object.assign(book, json.data)
  } else if (PREVIEW_MODE) {
    Object.assign(book, editBookForm.value)
  } else {
    alert(json.message || '保存失败')
  }
  editingBookId.value = null
}

async function toggleBookStatus(book) {
  const newStatus = book.status === 'active' ? 'inactive' : 'active'
  const json = await request(`/api/admin/books/${book.bookId}`, {
    method: 'PATCH',
    body: JSON.stringify({ status: newStatus }),
  })
  if (json.code === 200) {
    book.status = json.data.status
  } else if (PREVIEW_MODE) {
    book.status = newStatus
  } else {
    alert(json.message || '操作失败')
  }
}

// ========== 漂流瓶匹配（B1） ==========
const matchStep = ref('select') // select 选笔记 / result 看结果
const matchNotes = ref([]) // 可选的本人公开已过审笔记
const matchNotesLoading = ref(false)
const selectedMatchNote = ref(null)
const matchItems = ref([])
const matchTotal = ref(0)
const matchLoading = ref(false)
const matchPage = ref(1)
const matchPageSize = 3 // 每批 Top-N = 3
const openedMatch = ref(null) // 点开的候选卡片（看匹配度）
const acquiringId = ref(null) // 正在「交书友」的 bottleId
const acquiredInteraction = ref({}) // bottleId -> interactionId 缓存
const requestedBottles = ref({}) // bottleId -> true 已发申请

const previewMatches = [
  { bottleId: 501, author: { nickname: '晚风读者', avatarPath: '' }, book: { title: '百年孤独', author: '加西亚·马尔克斯' }, contentPreview: '我们总在回忆中重新理解时间。', recommendation: '你们都在时间里打捞记忆。', matchScore: 86.5, noteId: 202 },
  { bottleId: 502, author: { nickname: '云端旅人', avatarPath: '' }, book: { title: '百年孤独', author: '加西亚·马尔克斯' }, contentPreview: '孤独是布恩迪亚家族逃不掉的宿命。', recommendation: '你们都在思考孤独与宿命。', matchScore: 78.0, noteId: 203 },
  { bottleId: 503, author: { nickname: '林间书虫', avatarPath: '' }, book: { title: '活着', author: '余华' }, contentPreview: '苦难中的人，反而活得最用力。', recommendation: '你们对「活着」有相近的理解。', matchScore: 64.2, noteId: 204 },
  { bottleId: 504, author: { nickname: '夜读人', avatarPath: '' }, book: { title: '三体', author: '刘慈欣' }, contentPreview: '给岁月以文明，而不是给文明以岁月。', recommendation: '你们都向往宏大的文明尺度。', matchScore: 51.8, noteId: 205 },
  { bottleId: 505, author: { nickname: '晨雾书友', avatarPath: '' }, book: { title: '活着', author: '余华' }, contentPreview: '命运再苦，也要把日子过下去。', recommendation: '你们都看重人在苦难里的韧劲。', matchScore: 45.3, noteId: 206 },
  { bottleId: 506, author: { nickname: '星河读者', avatarPath: '' }, book: { title: '三体', author: '刘慈欣' }, contentPreview: '宇宙很大，人类很渺小。', recommendation: '你们都习惯把视角拉到宇宙尺度。', matchScore: 38.6, noteId: 207 },
]

async function enterMatch() {
  currentPage.value = 'match'
  matchStep.value = 'select'
  openedMatch.value = null
  selectedMatchNote.value = null
  await loadMatchNotes()
}

async function loadMatchNotes() {
  matchNotesLoading.value = true
  try {
    const json = await request('/api/me/notes?isPublic=true&reviewStatus=approved&pageSize=100')
    if (json.code === 200) {
      matchNotes.value = (json.data.list || []).map((n) => ({
        noteId: n.noteId,
        bookId: n.book?.bookId,
        bookTitle: n.book?.title,
        content: n.content,
      }))
    } else if (PREVIEW_MODE) {
      matchNotes.value = previewNotes.filter((n) => n.isPublic && n.reviewStatus === 'approved')
    }
  } catch (e) {
    if (PREVIEW_MODE) {
      matchNotes.value = previewNotes.filter((n) => n.isPublic && n.reviewStatus === 'approved')
    }
  } finally {
    matchNotesLoading.value = false
  }
}

function chooseMatchNote(note) {
  selectedMatchNote.value = note
  matchStep.value = 'result'
  matchPage.value = 1
  matchItems.value = []
  loadMatches()
}

async function loadMatches() {
  matchLoading.value = true
  try {
    const json = await request(
      `/api/bottles/matches?noteId=${selectedMatchNote.value.noteId}&pageNum=${matchPage.value}&pageSize=${matchPageSize}`
    )
    if (json.code === 200) {
      matchItems.value = json.data.list || []
      matchTotal.value = json.data.total || 0
    } else if (PREVIEW_MODE) {
      const start = (matchPage.value - 1) * matchPageSize
      matchItems.value = previewMatches.slice(start, start + matchPageSize)
      matchTotal.value = previewMatches.length
    }
  } catch (e) {
    if (PREVIEW_MODE) {
      const start = (matchPage.value - 1) * matchPageSize
      matchItems.value = previewMatches.slice(start, start + matchPageSize)
      matchTotal.value = previewMatches.length
    }
  } finally {
    matchLoading.value = false
  }
}

const hasMoreMatches = computed(() => matchPage.value * matchPageSize < matchTotal.value)

function nextBatch() {
  matchPage.value += 1
  loadMatches()
}

// 匹配度分档：高/中/低，用于徽章与环形进度配色 + 等级文案
function matchLevel(score) {
  if (score >= 80) return { label: '灵魂共振', cls: 'high', color: '#c98a5a' }
  if (score >= 60) return { label: '很有共鸣', cls: 'mid', color: '#b98a5e' }
  return { label: '可以聊聊', cls: 'low', color: '#b8a992' }
}

function openMatch(item) {
  openedMatch.value = item
}

function closeMatch() {
  openedMatch.value = null
}

async function sendFriendRequest(item) {
  acquiringId.value = item.bottleId
  try {
    let interactionId = acquiredInteraction.value[item.bottleId]
    if (!interactionId) {
      const acq = await request(`/api/bottles/${item.bottleId}/acquire`, { method: 'POST' })
      if (acq.code === 200) {
        interactionId = acq.data.myInteraction?.interactionId
      } else if (PREVIEW_MODE) {
        interactionId = Date.now()
      } else {
        alert(acq.message || '获取漂流瓶失败')
        return
      }
      acquiredInteraction.value[item.bottleId] = interactionId
    }
    const fr = await request('/api/friend-requests', {
      method: 'POST',
      body: JSON.stringify({ interactionId }),
    })
    if (fr.code === 200) {
      requestedBottles.value[item.bottleId] = true
      alert('书友申请已发出，等待对方回应')
    } else if (PREVIEW_MODE) {
      requestedBottles.value[item.bottleId] = true
      alert('（预览）书友申请已发出，等待对方回应')
    } else {
      alert(fr.message || '申请失败')
    }
  } catch (e) {
    if (PREVIEW_MODE) {
      requestedBottles.value[item.bottleId] = true
      alert('（预览）书友申请已发出，等待对方回应')
    } else {
      alert(e.message || '操作失败')
    }
  } finally {
    acquiringId.value = null
  }
}

// ========== 读书墙（B2） ==========
const wallNotes = ref([])
const wallLoading = ref(false)
const wallPage = ref(1)
const wallPageSize = 10
const wallTotal = ref(0)
const expandingComments = ref(null) // 当前展开评论的 noteId
const wallComments = ref({}) // noteId -> Comment[]
const wallCommentsLoading = ref(false)
const commentText = ref({}) // noteId -> 输入框文本
const wallTab = ref('all') // all=全部公开笔记 / favorites=我的收藏

const previewWallNotes = [
  { noteId: 301, author: { nickname: '晚风读者', avatarPath: '' }, book: { title: '百年孤独' }, content: '许多年之后，面对行刑队，奥雷里亚诺·布恩迪亚上校将会回想起父亲带他去见识冰块的那个遥远的下午。\n\n开头就把过去、现在、未来折叠在一起。', likeCount: 12, favoriteCount: 5, commentCount: 2, isLiked: false, isFavorited: false, createdAt: '2026-09-07' },
  { noteId: 302, author: { nickname: '云端旅人', avatarPath: '' }, book: { title: '三体' }, content: '给岁月以文明，而不是给文明以岁月。\n\n把文明的尺度拉到宇宙级别。', likeCount: 8, favoriteCount: 3, commentCount: 1, isLiked: true, isFavorited: false, createdAt: '2026-09-06' },
  { noteId: 303, author: { nickname: '林间书虫', avatarPath: '' }, book: { title: '活着' }, content: '人是为了活着本身而活着，而不是为了活着之外的任何事物而活着。\n\n这句话回答了整本书的题眼。', likeCount: 20, favoriteCount: 9, commentCount: 3, isLiked: false, isFavorited: true, createdAt: '2026-09-05' },
  { noteId: 304, author: { nickname: '山间读者', avatarPath: '' }, book: { title: '围城' }, content: '婚姻是一座围城，城外的人想进去，城里的人想出来。\n\n不止婚姻，人生处处是围城。', likeCount: 6, favoriteCount: 2, commentCount: 1, isLiked: false, isFavorited: false, createdAt: '2026-09-07' },
  { noteId: 305, author: { nickname: '星河读者', avatarPath: '' }, book: { title: '平凡的世界' }, content: '生活不能等待别人来安排，要自己去争取和奋斗。\n\n孙少平让我看到平凡人身上的光。', likeCount: 15, favoriteCount: 7, commentCount: 2, isLiked: true, isFavorited: false, createdAt: '2026-09-08' },
  { noteId: 306, author: { nickname: '晨雾书友', avatarPath: '' }, book: { title: '小王子' }, content: '真正重要的东西，用眼睛是看不见的，要用心去看。\n\n长大了才读懂这句话。', likeCount: 9, favoriteCount: 4, commentCount: 1, isLiked: false, isFavorited: false, createdAt: '2026-09-08' },
]

const previewWallComments = {
  301: [
    { commentId: 701, noteId: 301, author: { nickname: '星河读者', avatarPath: '' }, content: '这段关于时间的理解很有意思。', createdAt: '2026-09-08', canDelete: false },
    { commentId: 702, noteId: 301, author: { nickname: '晨雾书友', avatarPath: '' }, content: '我也是被这个开头震撼到了。', createdAt: '2026-09-08', canDelete: false },
  ],
  302: [
    { commentId: 703, noteId: 302, author: { nickname: '夜读人', avatarPath: '' }, content: '这句真的是全书的灵魂。', createdAt: '2026-09-07', canDelete: false },
  ],
  303: [
    { commentId: 704, noteId: 303, author: { nickname: '晚风读者', avatarPath: '' }, content: '读完久久不能平静。', createdAt: '2026-09-06', canDelete: false },
    { commentId: 705, noteId: 303, author: { nickname: '山间读者', avatarPath: '' }, content: '余华写得太狠了。', createdAt: '2026-09-06', canDelete: false },
    { commentId: 706, noteId: 303, author: { nickname: '云端旅人', avatarPath: '' }, content: '活着本身就是意义。', createdAt: '2026-09-05', canDelete: false },
  ],
  304: [
    { commentId: 707, noteId: 304, author: { nickname: '林间书虫', avatarPath: '' }, content: '围城这个比喻太精妙了。', createdAt: '2026-09-08', canDelete: false },
  ],
  305: [
    { commentId: 708, noteId: 305, author: { nickname: '晚风读者', avatarPath: '' }, content: '孙少平真的是平凡人的英雄。', createdAt: '2026-09-08', canDelete: false },
    { commentId: 709, noteId: 305, author: { nickname: '云端旅人', avatarPath: '' }, content: '路遥的文字很有力量。', createdAt: '2026-09-08', canDelete: false },
  ],
  306: [
    { commentId: 710, noteId: 306, author: { nickname: '星河读者', avatarPath: '' }, content: '小王子永远是我的治愈之书。', createdAt: '2026-09-08', canDelete: false },
  ],
}

async function enterWall() {
  currentPage.value = 'wall'
  wallTab.value = 'all'
  wallPage.value = 1
  expandingComments.value = null
  wallComments.value = {}
  await loadWall()
}

function switchWallTab(tab) {
  if (wallTab.value === tab) return
  wallTab.value = tab
  wallPage.value = 1
  expandingComments.value = null
  wallComments.value = {}
  loadWall()
}

async function loadWall() {
  wallLoading.value = true
  try {
    if (wallTab.value === 'favorites') {
      const json = await request(`/api/me/favorites?pageNum=${wallPage.value}&pageSize=${wallPageSize}`)
      if (json.code === 200) {
        wallNotes.value = json.data.list || []
        wallTotal.value = json.data.total || 0
      } else if (PREVIEW_MODE) {
        wallNotes.value = previewWallNotes.filter(n => n.isFavorited)
        wallTotal.value = wallNotes.value.length
      }
    } else {
      const json = await request(`/api/wall/notes?pageNum=${wallPage.value}&pageSize=${wallPageSize}`)
      if (json.code === 200) {
        wallNotes.value = json.data.list || []
        wallTotal.value = json.data.total || 0
      } else if (PREVIEW_MODE) {
        wallNotes.value = [...previewWallNotes]
        wallTotal.value = previewWallNotes.length
      }
    }
  } catch (e) {
    if (PREVIEW_MODE) {
      if (wallTab.value === 'favorites') {
        wallNotes.value = previewWallNotes.filter(n => n.isFavorited)
      } else {
        wallNotes.value = [...previewWallNotes]
      }
      wallTotal.value = wallNotes.value.length
    }
  } finally {
    wallLoading.value = false
  }
}

function applySocial(note, social) {
  if (!social) return
  note.likeCount = social.likeCount
  note.favoriteCount = social.favoriteCount
  note.commentCount = social.commentCount
  note.isLiked = social.isLiked
  note.isFavorited = social.isFavorited
}

async function toggleLike(note) {
  const method = note.isLiked ? 'DELETE' : 'PUT'
  try {
    const json = await request(`/api/notes/${note.noteId}/like`, { method })
    if (json.code === 200) {
      applySocial(note, json.data)
    } else if (PREVIEW_MODE) {
      note.isLiked = !note.isLiked
      note.likeCount += note.isLiked ? 1 : -1
    } else {
      alert(json.message || '操作失败')
    }
  } catch (e) {
    if (PREVIEW_MODE) {
      note.isLiked = !note.isLiked
      note.likeCount += note.isLiked ? 1 : -1
    } else {
      alert(e.message || '操作失败')
    }
  }
}

async function toggleFavorite(note) {
  const method = note.isFavorited ? 'DELETE' : 'PUT'
  try {
    const json = await request(`/api/notes/${note.noteId}/favorite`, { method })
    if (json.code === 200) {
      applySocial(note, json.data)
    } else if (PREVIEW_MODE) {
      note.isFavorited = !note.isFavorited
      note.favoriteCount += note.isFavorited ? 1 : -1
    } else {
      alert(json.message || '操作失败')
    }
  } catch (e) {
    if (PREVIEW_MODE) {
      note.isFavorited = !note.isFavorited
      note.favoriteCount += note.isFavorited ? 1 : -1
    } else {
      alert(e.message || '操作失败')
    }
  }
  pruneFavorites()
}

function pruneFavorites() {
  if (wallTab.value === 'favorites') {
    wallNotes.value = wallNotes.value.filter(n => n.isFavorited)
  }
}

async function toggleComments(note) {
  if (expandingComments.value === note.noteId) {
    expandingComments.value = null
    return
  }
  expandingComments.value = note.noteId
  wallCommentsLoading.value = true
  try {
    const json = await request(`/api/notes/${note.noteId}/comments?pageSize=100`)
    if (json.code === 200) {
      wallComments.value[note.noteId] = json.data.list || []
    } else if (PREVIEW_MODE) {
      wallComments.value[note.noteId] = [...(previewWallComments[note.noteId] || [])]
    }
  } catch (e) {
    if (PREVIEW_MODE) {
      wallComments.value[note.noteId] = [...(previewWallComments[note.noteId] || [])]
    }
  } finally {
    wallCommentsLoading.value = false
  }
}

async function submitComment(note) {
  const text = (commentText.value[note.noteId] || '').trim()
  if (!text) {
    alert('请输入评论内容')
    return
  }
  try {
    const json = await request(`/api/notes/${note.noteId}/comments`, {
      method: 'POST',
      body: JSON.stringify({ content: text }),
    })
    if (json.code === 200) {
      commentText.value[note.noteId] = ''
      note.commentCount += 1
      if (wallComments.value[note.noteId]) {
        wallComments.value[note.noteId].unshift(json.data)
      }
    } else if (PREVIEW_MODE) {
      commentText.value[note.noteId] = ''
      note.commentCount += 1
      if (!wallComments.value[note.noteId]) wallComments.value[note.noteId] = []
      wallComments.value[note.noteId].unshift({
        commentId: Date.now(),
        noteId: note.noteId,
        author: { nickname: currentUser?.nickname || '我', avatarPath: '' },
        content: text,
        createdAt: '刚刚',
        canDelete: true,
      })
    } else {
      alert(json.message || '评论失败')
    }
  } catch (e) {
    alert(e.message || '评论失败')
  }
}

async function deleteComment(note, comment) {
  try {
    const json = await request(`/api/comments/${comment.commentId}`, { method: 'DELETE' })
    if (json.code === 200 || PREVIEW_MODE) {
      note.commentCount -= 1
      wallComments.value[note.noteId] = (wallComments.value[note.noteId] || []).filter(
        (c) => c.commentId !== comment.commentId
      )
    } else {
      alert(json.message || '删除失败')
    }
  } catch (e) {
    if (PREVIEW_MODE) {
      note.commentCount -= 1
      wallComments.value[note.noteId] = (wallComments.value[note.noteId] || []).filter(
        (c) => c.commentId !== comment.commentId
      )
    } else {
      alert(e.message || '删除失败')
    }
  }
}

// ========== 书友（B6） ==========
const friendTab = ref('friends') // friends 我的书友 / requests 收到的申请
const friendsList = ref([])
const friendsLoading = ref(false)
const friendRequests = ref([])
const friendRequestsLoading = ref(false)
const friendPendingCount = ref(0) // 待处理的「收到的申请」数，用于顶栏红点
const friendActionId = ref(null) // 正在 accept/reject 的 requestId

const previewFriends = [
  { user: { userId: 2, nickname: '晚风读者', avatarPath: '' }, becameFriendsAt: '2026-09-07' },
  { user: { userId: 3, nickname: '云端旅人', avatarPath: '' }, becameFriendsAt: '2026-09-05' },
]

const previewFriendRequests = [
  { requestId: 601, requester: { userId: 4, nickname: '山间读者', avatarPath: '' }, receiver: { userId: 1 }, bottleId: 501, status: 'pending', createdAt: '2026-09-08', handledAt: null },
  { requestId: 602, requester: { userId: 5, nickname: '晨雾书友', avatarPath: '' }, receiver: { userId: 1 }, bottleId: 502, status: 'pending', createdAt: '2026-09-08', handledAt: null },
]

async function enterFriends() {
  currentPage.value = 'friends'
  friendTab.value = 'friends'
  friendsList.value = []
  friendRequests.value = []
  await loadFriends()
  await loadFriendRequests()
}

function switchFriendTab(tab) {
  if (friendTab.value === tab) return
  friendTab.value = tab
  if (tab === 'friends') loadFriends()
  else loadFriendRequests()
}

async function loadFriends() {
  friendsLoading.value = true
  try {
    const json = await request('/api/me/friends?pageNum=1&pageSize=100')
    if (json.code === 200) {
      friendsList.value = json.data.list || []
    } else if (PREVIEW_MODE) {
      friendsList.value = [...previewFriends]
    }
  } catch (e) {
    if (PREVIEW_MODE) friendsList.value = [...previewFriends]
  } finally {
    friendsLoading.value = false
  }
}

async function loadFriendRequests() {
  friendRequestsLoading.value = true
  try {
    const json = await request('/api/me/friend-requests?direction=received&status=pending&pageNum=1&pageSize=100')
    if (json.code === 200) {
      friendRequests.value = json.data.list || []
      friendPendingCount.value = json.data.total || friendRequests.value.length
    } else if (PREVIEW_MODE) {
      friendRequests.value = [...previewFriendRequests]
      friendPendingCount.value = friendRequests.value.length
    }
  } catch (e) {
    if (PREVIEW_MODE) {
      friendRequests.value = [...previewFriendRequests]
      friendPendingCount.value = friendRequests.value.length
    }
  } finally {
    friendRequestsLoading.value = false
  }
}

// 仅刷新顶栏红点数量（登录后调用，不拉完整列表）
async function refreshFriendBadge() {
  try {
    const json = await request('/api/me/friend-requests?direction=received&status=pending&pageSize=1')
    if (json.code === 200) {
      friendPendingCount.value = json.data.total || 0
    } else if (PREVIEW_MODE) {
      friendPendingCount.value = previewFriendRequests.length
    }
  } catch (e) {
    if (PREVIEW_MODE) friendPendingCount.value = previewFriendRequests.length
  }
}

async function handleFriendRequest(item, status) {
  friendActionId.value = item.requestId
  try {
    const json = await request(`/api/friend-requests/${item.requestId}`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    })
    if (json.code === 200) {
      friendRequests.value = friendRequests.value.filter((r) => r.requestId !== item.requestId)
      friendPendingCount.value = friendRequests.value.length
      if (status === 'accepted') {
        alert('已接受，你们成为书友了')
        loadFriends()
      } else {
        alert('已拒绝')
      }
    } else if (PREVIEW_MODE) {
      friendRequests.value = friendRequests.value.filter((r) => r.requestId !== item.requestId)
      friendPendingCount.value = friendRequests.value.length
      if (status === 'accepted') loadFriends()
    } else {
      alert(json.message || '操作失败')
    }
  } catch (e) {
    if (PREVIEW_MODE) {
      friendRequests.value = friendRequests.value.filter((r) => r.requestId !== item.requestId)
      friendPendingCount.value = friendRequests.value.length
      if (status === 'accepted') loadFriends()
    } else {
      alert(e.message || '操作失败')
    }
  } finally {
    friendActionId.value = null
  }
}

async function removeFriend(item) {
  if (!confirm(`确定解除与「${item.user.nickname}」的书友关系？`)) return
  try {
    const json = await request(`/api/me/friends/${item.user.userId}`, { method: 'DELETE' })
    if (json.code === 200 || PREVIEW_MODE) {
      friendsList.value = friendsList.value.filter((f) => f.user.userId !== item.user.userId)
    } else {
      alert(json.message || '操作失败')
    }
  } catch (e) {
    if (PREVIEW_MODE) {
      friendsList.value = friendsList.value.filter((f) => f.user.userId !== item.user.userId)
    } else {
      alert(e.message || '操作失败')
    }
  }
}
</script>

<template>
  <!-- 登录 / 注册页 -->
  <div v-if="currentPage === 'login'" class="auth-page">
    <div class="auth-box">
      <div class="quote-mark">“</div>
      <h1 class="logo">书遇</h1>
      <p class="slogan">读过同一页，就是见过面</p>

      <div class="role-toggle">
        <button class="role-opt" :class="{ active: loginRole === 'user' }" @click="switchRole('user')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
            <circle cx="12" cy="7" r="4"></circle>
          </svg>
          用户登录
        </button>
        <button class="role-opt" :class="{ active: loginRole === 'admin' }" @click="switchRole('admin')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
          </svg>
          管理员登录
        </button>
      </div>

      <!-- 登录表单 -->
      <form v-if="!isRegister" class="form" @submit.prevent="handleLogin">
        <input v-model="loginForm.email" type="email" placeholder="邮箱" required />
        <input v-model="loginForm.password" type="password" placeholder="密码" required />
        <button type="submit">登 录</button>
      </form>

      <!-- 注册表单 -->
      <form v-else class="form" @submit.prevent="handleRegister">
        <input v-model="registerForm.nickname" placeholder="昵称" required />
        <input v-model="registerForm.email" type="email" placeholder="邮箱" required />
        <input v-model="registerForm.password" type="password" placeholder="密码" required />
        <div class="avatar-field">
          <label class="avatar-label">头像（必填，先上传再注册）</label>
          <input type="file" accept="image/jpeg,image/png,image/webp" @change="onAvatarChange" required />
        </div>
        <select v-model="registerForm.gender">
          <option value="unspecified">性别：未设置</option>
          <option value="male">性别：男</option>
          <option value="female">性别：女</option>
        </select>
        <button type="submit">注 册</button>
      </form>

      <p v-if="loginRole === 'user'" class="switch" @click="isRegister = !isRegister">
        {{ isRegister ? '已有账号？去登录' : '没有账号？去注册' }}
      </p>
      <p class="preview-link" @click="previewHome">（临时）离线预览{{ loginRole === 'admin' ? '管理员界面' : '主页' }}</p>
    </div>
  </div>

  <!-- 主页 -->
  <div v-else-if="currentPage === 'home'" class="home-page">
    <header class="topbar">
      <div class="brand">书遇</div>
      <div class="user-area">
        <span class="user-avatar">{{ (currentUser?.nickname || currentUser?.username || '书').slice(0, 1) }}</span>
        <span class="username">{{ currentUser?.nickname || currentUser?.username }}</span>
        <button class="friend-btn" @click="enterFriends()">
          <svg class="friend-btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
            <circle cx="9" cy="7" r="4"></circle>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
          </svg>
          <span>书友</span>
          <span v-if="friendPendingCount > 0" class="friend-dot">{{ friendPendingCount }}</span>
        </button>
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
        <div class="card card-primary" @click="enterMatch()">
          <span class="card-icon icon-match">遇</span>
          <h2>交个书友</h2>
          <p>让摘录找到懂你的人</p>
        </div>
        <div class="card" @click="enterWall()">
          <span class="card-icon icon-wall">墙</span>
          <h2>读书墙</h2>
          <p>看大家此刻在读什么</p>
        </div>
      </section>
    </main>
  </div>

  <!-- 书单页 -->
  <div v-else-if="currentPage === 'shelf'" class="shelf-page">
    <header class="topbar">
      <div class="brand">书遇</div>
      <div class="user-area">
        <span class="user-avatar">{{ (currentUser?.nickname || currentUser?.username || '书').slice(0, 1) }}</span>
        <span class="username">{{ currentUser?.nickname || currentUser?.username }}</span>
        <button class="friend-btn" @click="enterFriends()">
          <svg class="friend-btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
            <circle cx="9" cy="7" r="4"></circle>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
          </svg>
          <span>书友</span>
          <span v-if="friendPendingCount > 0" class="friend-dot">{{ friendPendingCount }}</span>
        </button>
        <button class="logout-btn" @click="logout">退出</button>
      </div>
    </header>

    <main class="shelf-content">
      <button class="back-link" @click="go('home')">← 返回主页</button>

      <div class="shelf-head">
        <div>
          <h1 class="page-title">我的书单</h1>
          <p class="page-subtitle">共 {{ shelfBooks.length }} 本 · 记录你的阅读轨迹</p>
        </div>
        <div class="head-actions">
          <div class="search-box">
            <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
              <circle cx="11" cy="11" r="7"></circle>
              <line x1="21" y1="21" x2="16.5" y2="16.5"></line>
            </svg>
            <input v-model="searchQuery" type="text" placeholder="搜索书名或作者" />
          </div>
          <button class="manage-btn" :class="{ active: shelfManage }" @click="toggleManage">
            {{ shelfManage ? '完成' : '管理' }}
          </button>
        </div>
      </div>

      <div class="tabs">
        <button
          v-for="t in shelfTabs"
          :key="t.key"
          class="tab"
          :class="{ active: shelfTab === t.key }"
          @click="shelfTab = t.key"
        >
          {{ t.label }}<span class="tab-count">{{ shelfCounts[t.key] }}</span>
        </button>
      </div>

      <div class="book-list">
        <div
          v-for="book in filteredBooks"
          :key="book.bookId"
          class="book-card"
          :class="'card-' + book.readingStatus"
          @click="openBookDetail(book)"
        >
          <span class="book-cover">{{ book.title[0] }}</span>
          <div class="book-info">
            <h3>{{ book.title }}</h3>
            <p>{{ book.author }}</p>
          </div>
          <span v-if="!shelfManage" class="book-status" :class="'status-' + book.readingStatus">{{ statusText[book.readingStatus] }}</span>
          <button v-else class="remove-btn" :class="{ confirm: removingId === book.bookId }" @click.stop="removeBook(book)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="3 6 5 6 21 6"></polyline>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
              <line x1="10" y1="11" x2="10" y2="17"></line>
              <line x1="14" y1="11" x2="14" y2="17"></line>
            </svg>
            {{ removingId === book.bookId ? '确认移除？' : '移除' }}
          </button>
          <svg
            v-if="!shelfManage"
            class="expand-arrow"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <polyline points="9 6 15 12 9 18"></polyline>
          </svg>
        </div>
        <div v-if="filteredBooks.length === 0" class="empty-tip">
          <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
            <circle cx="11" cy="11" r="7"></circle>
            <line x1="21" y1="21" x2="16.5" y2="16.5"></line>
          </svg>
          <p>没有找到相关书籍</p>
        </div>
      </div>

      <p class="shelf-footer">“读过同一页，就是见过面”</p>
    </main>
  </div>

  <!-- 书籍详情页 -->
  <div v-else-if="currentPage === 'bookDetail'" class="book-detail-page">
    <header class="topbar">
      <div class="brand">书遇</div>
      <div class="user-area">
        <span class="user-avatar">{{ (currentUser?.nickname || currentUser?.username || '书').slice(0, 1) }}</span>
        <span class="username">{{ currentUser?.nickname || currentUser?.username }}</span>
        <button class="friend-btn" @click="enterFriends()">
          <svg class="friend-btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
            <circle cx="9" cy="7" r="4"></circle>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
          </svg>
          <span>书友</span>
          <span v-if="friendPendingCount > 0" class="friend-dot">{{ friendPendingCount }}</span>
        </button>
        <button class="logout-btn" @click="logout">退出</button>
      </div>
    </header>

    <main class="book-detail-content">
      <button class="back-link" @click="go('shelf')">← 返回书单</button>

      <div class="book-detail-head">
        <span class="book-cover book-cover-lg">{{ detailBook.title[0] }}</span>
        <div class="book-detail-info">
          <h1 class="page-title">{{ detailBook.title }}</h1>
          <p class="page-subtitle">{{ detailBook.author }}</p>
          <p v-if="detailBook.intro" class="book-intro">{{ detailBook.intro }}</p>
          <p v-if="detailBook.isbn" class="book-isbn">ISBN：{{ detailBook.isbn }}</p>
        </div>
      </div>

      <button class="submit-btn detail-note-btn" @click="goNoteForBook(detailBook)">在这本书下记笔记</button>

      <div class="my-notes">
        <div class="notes-head">
          <h2 class="notes-title">我的摘录</h2>
          <span class="notes-count">{{ notesForBook(detailBook.bookId).length }} 条</span>
        </div>

        <div v-if="notesForBook(detailBook.bookId).length === 0" class="notes-empty">还没有摘录，点上面「记笔记」写第一条吧</div>
        <div v-for="n in notesForBook(detailBook.bookId)" :key="n.noteId" class="note-card">
          <p v-if="splitNote(n.content).quote" class="note-quote">“{{ splitNote(n.content).quote }}”</p>
          <p v-if="splitNote(n.content).comment" class="note-comment">{{ splitNote(n.content).comment }}</p>
          <div class="note-card-bottom">
            <span class="note-visibility" :class="n.isPublic ? 'public' : 'private'">{{ n.isPublic ? '公开' : '私密' }}</span>
            <span class="note-status" :class="'ns-' + n.reviewStatus">{{ reviewStatusText[n.reviewStatus] }}</span>
            <span class="note-date">{{ n.createdAt }}</span>
          </div>
        </div>
      </div>
    </main>
  </div>

  <!-- 上传笔记页 -->
  <div v-else-if="currentPage === 'note'" class="note-page">
    <header class="topbar">
      <div class="brand">书遇</div>
      <div class="user-area">
        <span class="user-avatar">{{ (currentUser?.nickname || currentUser?.username || '书').slice(0, 1) }}</span>
        <span class="username">{{ currentUser?.nickname || currentUser?.username }}</span>
        <button class="friend-btn" @click="enterFriends()">
          <svg class="friend-btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
            <circle cx="9" cy="7" r="4"></circle>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
          </svg>
          <span>书友</span>
          <span v-if="friendPendingCount > 0" class="friend-dot">{{ friendPendingCount }}</span>
        </button>
        <button class="logout-btn" @click="logout">退出</button>
      </div>
    </header>

    <main class="note-content">
      <button class="back-link" @click="go('home')">← 返回主页</button>
      <h1 class="page-title">上传笔记</h1>
      <p class="page-subtitle">记下你的摘录与感悟，AI 帮你提炼</p>

      <div class="note-form">
        <div class="form-quote">“</div>

        <label class="field-label">选择书籍</label>
        <div class="book-picker">
          <div class="book-picker-input" :class="{ open: bookOpen }">
            <input
              v-model="bookSearch"
              type="text"
              placeholder="搜索或选择一本书"
              @click="onBookFocus"
              @focus="onBookFocus"
              @input="onBookInput"
              @blur="onBookBlur"
            />
            <svg class="picker-chevron" :class="{ open: bookOpen }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          </div>
          <div v-if="bookOpen" class="book-picker-list">
            <div
              v-for="b in bookOptions"
              :key="b.bookId"
              class="book-picker-item"
              :class="{ active: String(b.bookId) === String(noteForm.bookId) }"
              @mousedown.prevent="pickBook(b)"
            >
              <span class="picker-title">{{ b.title }}</span>
              <span class="picker-author">{{ b.author }}</span>
            </div>
            <div v-if="bookOptions.length === 0" class="book-picker-empty">没有匹配的书籍</div>
          </div>
        </div>

        <label class="field-label">可见范围</label>
        <div class="visibility-toggle">
          <button type="button" class="vis-option" :class="{ active: noteForm.isPublic === true }" @click="noteForm.isPublic = true">
            <span v-if="noteForm.isPublic === true" class="vis-check">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
            </span>
            <svg class="vis-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M22 2L11 13"></path>
              <path d="M22 2l-7 20-4-9-9-4z"></path>
            </svg>
            <span class="vis-label">公开</span>
            <span class="vis-hint">会漂流出去交朋友</span>
          </button>
          <button type="button" class="vis-option" :class="{ active: noteForm.isPublic === false }" @click="noteForm.isPublic = false">
            <span v-if="noteForm.isPublic === false" class="vis-check">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
            </span>
            <svg class="vis-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
            </svg>
            <span class="vis-label">私密</span>
            <span class="vis-hint">仅自己可见</span>
          </button>
        </div>

        <label class="field-label">摘录原文</label>
        <textarea
          v-model="noteForm.quote"
          class="note-textarea"
          placeholder="摘录触动你的那段话..."
        ></textarea>
        <div class="char-count">{{ noteForm.quote.length }} 字</div>

        <label class="field-label">我的评价</label>
        <textarea
          v-model="noteForm.comment"
          class="note-textarea"
          placeholder="写下这一刻的想法..."
        ></textarea>
        <div class="char-count">{{ noteForm.comment.length }} 字</div>

        <button class="submit-btn" :disabled="noteLoading" @click="submitNote">
          <svg v-if="!noteLoading" class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 2L11 13"></path>
            <path d="M22 2l-7 20-4-9-9-4z"></path>
          </svg>
          <span v-else class="spinner"></span>
          {{ noteLoading ? '分析中…' : '上传笔记' }}
        </button>

        <div v-if="lastAiResult" class="ai-result">
          <h3 class="ai-result-title">AI 提取结果</h3>
          <div class="ai-row">
            <span class="ai-label">主题</span>
            <div class="ai-tags">
              <span v-for="t in lastAiResult.topics" :key="t" class="ai-tag">{{ t }}</span>
              <span v-if="lastAiResult.topics.length === 0" class="ai-empty">暂无</span>
            </div>
          </div>
          <div class="ai-row">
            <span class="ai-label">关键词</span>
            <div class="ai-tags">
              <span v-for="k in lastAiResult.keywords" :key="k" class="ai-tag">{{ k }}</span>
              <span v-if="lastAiResult.keywords.length === 0" class="ai-empty">暂无</span>
            </div>
          </div>
          <div class="ai-row">
            <span class="ai-label">情绪</span>
            <span class="ai-sentiment" :class="'sent-' + lastAiResult.sentiment">{{ sentimentText[lastAiResult.sentiment] || lastAiResult.sentiment }}</span>
          </div>
        </div>
      </div>

      <div class="my-notes">
        <div class="notes-head">
          <h2 class="notes-title">我的笔记</h2>
          <span class="notes-count">{{ myNotes.length }} 条</span>
        </div>

        <div class="notes-search">
          <svg class="notes-search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
            <circle cx="11" cy="11" r="7"></circle>
            <line x1="21" y1="21" x2="16.5" y2="16.5"></line>
          </svg>
          <input v-model="noteSearchQuery" type="text" placeholder="搜索我的笔记（书名或内容）" />
        </div>

        <div v-if="myNotes.length === 0" class="notes-empty">还没有笔记，写下第一条吧</div>
        <div v-else-if="filteredMyNotes.length === 0" class="notes-empty">没有找到匹配的笔记</div>

        <div v-for="n in filteredMyNotes" :key="n.noteId" class="note-card">
          <div class="note-card-top">
            <span class="note-book">{{ n.bookTitle }}</span>
            <span class="note-visibility" :class="n.isPublic ? 'public' : 'private'">{{ n.isPublic ? '公开' : '私密' }}</span>
          </div>
          <p v-if="splitNote(n.content).quote" class="note-quote">“{{ splitNote(n.content).quote }}”</p>
          <p v-if="splitNote(n.content).comment" class="note-comment">{{ splitNote(n.content).comment }}</p>
          <div class="note-card-bottom">
            <span class="note-status" :class="'ns-' + n.reviewStatus">{{ reviewStatusText[n.reviewStatus] }}</span>
            <span class="note-date">{{ n.createdAt }}</span>
          </div>
        </div>
      </div>
    </main>
  </div>

  <!-- 漂流瓶匹配页 -->
  <div v-else-if="currentPage === 'match'" class="match-page">
    <header class="topbar">
      <div class="brand">书遇</div>
      <div class="user-area">
        <span class="user-avatar">{{ (currentUser?.nickname || currentUser?.username || '书').slice(0, 1) }}</span>
        <span class="username">{{ currentUser?.nickname || currentUser?.username }}</span>
        <button class="friend-btn" @click="enterFriends()">
          <svg class="friend-btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
            <circle cx="9" cy="7" r="4"></circle>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
          </svg>
          <span>书友</span>
          <span v-if="friendPendingCount > 0" class="friend-dot">{{ friendPendingCount }}</span>
        </button>
        <button class="logout-btn" @click="logout">退出</button>
      </div>
    </header>

    <main class="match-content">
      <button class="back-link" @click="go('home')">← 返回主页</button>

      <!-- 步骤一：选一篇公开笔记 -->
      <section v-if="matchStep === 'select'" class="match-select">
        <h1 class="page-title">找同频的人</h1>
        <p class="match-subtitle">选一篇你已公开的笔记，系统会从文字里找到与你最相近的书友。</p>

        <div v-if="matchNotesLoading" class="match-empty"><span class="loading-dot"></span>加载中…</div>
        <div v-else-if="matchNotes.length === 0" class="match-empty">
          <p>你还没有公开且已过审的笔记。</p>
          <button class="submit-btn" @click="go('note')">去上传一篇</button>
        </div>
        <div v-else class="match-note-list">
          <button
            v-for="(n, index) in matchNotes"
            :key="n.noteId"
            class="match-note-item"
            @click="chooseMatchNote(n)"
          >
            <span class="match-note-index">{{ index + 1 }}</span>
            <div class="match-note-body">
              <span class="match-note-book">{{ n.bookTitle }}</span>
              <span class="match-note-quote">“{{ splitNote(n.content).quote || splitNote(n.content).comment }}”</span>
            </div>
            <span class="match-note-go">开始匹配 →</span>
          </button>
        </div>
      </section>

      <!-- 步骤二：看匹配结果 -->
      <section v-else class="match-result">
        <div class="match-result-head">
          <button class="text-btn" @click="matchStep = 'select'">← 换一篇</button>
          <div class="match-source">
            <span class="match-source-label">当前笔记 · {{ selectedMatchNote?.bookTitle }}</span>
            <span class="match-source-quote">“{{ splitNote(selectedMatchNote?.content).quote || splitNote(selectedMatchNote?.content).comment }}”</span>
          </div>
        </div>

        <div v-if="matchLoading" class="match-empty"><span class="loading-dot"></span>正在匹配…</div>
        <div v-else-if="matchItems.length === 0" class="match-empty">
          <p>暂时没有匹配到书友，换个笔记试试。</p>
        </div>
        <div v-else class="match-list">
          <p class="match-count">为你找到 {{ matchTotal }} 位相近书友 · 第 {{ matchPage }} 批</p>
          <button
            v-for="(item, index) in matchItems"
            :key="item.bottleId"
            class="match-card"
            :style="{ animationDelay: index * 0.06 + 's' }"
            @click="openMatch(item)"
          >
            <span class="match-score-badge" :class="matchLevel(item.matchScore).cls">{{ item.matchScore }}%</span>
            <div class="match-card-top">
              <span class="match-avatar">{{ (item.author?.nickname || '书').slice(0, 1) }}</span>
              <div class="match-card-info">
                <span class="match-card-name">{{ item.author?.nickname || '匿名书友' }}</span>
                <span class="match-card-book">{{ item.book?.title }}</span>
              </div>
            </div>
            <p class="match-card-preview">{{ item.contentPreview }}</p>
            <p v-if="item.recommendation" class="match-card-rec"><span class="match-rec-tag">推荐语</span>{{ item.recommendation }}</p>
          </button>

          <button v-if="hasMoreMatches" class="match-refresh-btn" @click="nextBatch">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 12a9 9 0 1 1-2.64-6.36"></path>
              <polyline points="21 3 21 9 15 9"></polyline>
            </svg>
            换一批书友
          </button>
          <p v-else class="match-no-more">没有更多书友了，换个笔记试试</p>
        </div>
      </section>
    </main>

    <!-- 匹配详情弹层 -->
    <div v-if="openedMatch" class="match-modal" @click.self="closeMatch">
      <div class="match-modal-card">
        <button class="modal-close" @click="closeMatch">×</button>
        <div class="match-modal-head">
          <span class="match-avatar big">{{ (openedMatch.author?.nickname || '书').slice(0, 1) }}</span>
          <div>
            <div class="match-modal-name">{{ openedMatch.author?.nickname || '匿名书友' }}</div>
            <div class="match-modal-book">{{ openedMatch.book?.title }}</div>
          </div>
        </div>
        <p class="match-modal-preview">{{ openedMatch.contentPreview }}</p>
        <p v-if="openedMatch.recommendation" class="match-modal-rec">“{{ openedMatch.recommendation }}”</p>

        <div class="match-score-block">
          <div
            class="match-score-ring"
            :style="'background: conic-gradient(' + matchLevel(openedMatch.matchScore).color + ' 0 ' + openedMatch.matchScore + '%, #efe6d8 ' + openedMatch.matchScore + '% 100%)'"
          >
            <div class="match-score-ring-inner">
              <div class="match-score-num">{{ openedMatch.matchScore }}<span class="match-score-unit">%</span></div>
              <div class="match-score-level" :class="matchLevel(openedMatch.matchScore).cls">{{ matchLevel(openedMatch.matchScore).label }}</div>
            </div>
          </div>
        </div>

        <button
          v-if="requestedBottles[openedMatch.bottleId]"
          class="submit-btn match-cta"
          disabled
        >已发出申请</button>
        <button
          v-else
          class="submit-btn match-cta"
          :disabled="acquiringId === openedMatch.bottleId"
          @click="sendFriendRequest(openedMatch)"
        >{{ acquiringId === openedMatch.bottleId ? '发送中…' : '交个书友' }}</button>
      </div>
    </div>
  </div>

  <!-- 读书墙 -->
  <div v-else-if="currentPage === 'wall'" class="wall-page">
    <header class="topbar">
      <div class="brand">书遇</div>
      <div class="user-area">
        <span class="user-avatar">{{ (currentUser?.nickname || currentUser?.username || '书').slice(0, 1) }}</span>
        <span class="username">{{ currentUser?.nickname || currentUser?.username }}</span>
        <button class="friend-btn" @click="enterFriends()">
          <svg class="friend-btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
            <circle cx="9" cy="7" r="4"></circle>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
          </svg>
          <span>书友</span>
          <span v-if="friendPendingCount > 0" class="friend-dot">{{ friendPendingCount }}</span>
        </button>
        <button class="logout-btn" @click="logout">退出</button>
      </div>
    </header>

    <main class="wall-content">
      <button class="back-link" @click="go('home')">← 返回主页</button>
      <h1 class="page-title">读书墙</h1>
      <p class="page-subtitle">看看你的书友们此刻在读什么、在想什么</p>

      <div class="wall-tabs">
        <button class="wall-tab" :class="{ active: wallTab === 'all' }" @click="switchWallTab('all')">全部笔记</button>
        <button class="wall-tab" :class="{ active: wallTab === 'favorites' }" @click="switchWallTab('favorites')">我的收藏</button>
      </div>

      <div v-if="wallLoading" class="wall-empty"><span class="loading-dot"></span>加载中…</div>
      <div v-else-if="wallNotes.length === 0" class="wall-empty">
        <p>{{ wallTab === 'favorites' ? '还没有收藏任何笔记。' : '还没有书友发布笔记，先去交个书友吧。' }}</p>
        <button class="submit-btn" @click="wallTab === 'favorites' ? switchWallTab('all') : enterMatch()">
          {{ wallTab === 'favorites' ? '去墙上看看' : '去交个书友' }}
        </button>
      </div>
      <div v-else class="wall-list">
        <article v-for="n in wallNotes" :key="n.noteId" class="wall-card">
          <div class="wall-card-head">
            <span class="wall-avatar">{{ (n.author?.nickname || '书').slice(0, 1) }}</span>
            <div class="wall-author">
              <span class="wall-nickname">{{ n.author?.nickname || '匿名书友' }}</span>
              <span class="wall-meta">{{ n.book?.title }} · {{ n.createdAt }}</span>
            </div>
          </div>

          <p v-if="splitNote(n.content).quote" class="wall-quote">“{{ splitNote(n.content).quote }}”</p>
          <p v-if="splitNote(n.content).comment" class="wall-review">{{ splitNote(n.content).comment }}</p>

          <div class="wall-actions">
            <button class="wall-action" :class="{ active: n.isLiked }" @click="toggleLike(n)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
              </svg>
              <span>{{ n.likeCount }}</span>
            </button>
            <button class="wall-action" :class="{ active: n.isFavorited }" @click="toggleFavorite(n)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
              </svg>
              <span>{{ n.favoriteCount }}</span>
            </button>
            <button class="wall-action" @click="toggleComments(n)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
              </svg>
              <span>{{ n.commentCount }}</span>
            </button>
          </div>

          <!-- 评论区 -->
          <div v-if="expandingComments === n.noteId" class="wall-comments">
            <div v-if="wallCommentsLoading" class="wall-comments-empty"><span class="loading-dot"></span>加载评论…</div>
            <div v-else-if="!(wallComments[n.noteId] || []).length" class="wall-comments-empty">还没有评论，来抢沙发</div>
            <div v-else class="wall-comment-list">
              <div v-for="c in wallComments[n.noteId]" :key="c.commentId" class="wall-comment-item">
                <span class="wall-comment-avatar">{{ (c.author?.nickname || '书').slice(0, 1) }}</span>
                <div class="wall-comment-body">
                  <div class="wall-comment-head">
                    <span class="wall-comment-name">{{ c.author?.nickname || '匿名' }}</span>
                    <span class="wall-comment-time">{{ c.createdAt }}</span>
                  </div>
                  <p class="wall-comment-text">{{ c.content }}</p>
                </div>
                <button v-if="c.canDelete" class="wall-comment-del" @click="deleteComment(n, c)">删除</button>
              </div>
            </div>
            <div class="wall-comment-input">
              <input
                v-model="commentText[n.noteId]"
                placeholder="写下你的评论…"
                @keyup.enter="submitComment(n)"
              />
              <button class="wall-comment-send" @click="submitComment(n)">发送</button>
            </div>
          </div>
        </article>
      </div>
    </main>
  </div>

  <!-- 书友 -->
  <div v-else-if="currentPage === 'friends'" class="friends-page">
    <header class="topbar">
      <div class="brand">书遇</div>
      <div class="user-area">
        <span class="user-avatar">{{ (currentUser?.nickname || currentUser?.username || '书').slice(0, 1) }}</span>
        <span class="username">{{ currentUser?.nickname || currentUser?.username }}</span>
        <button class="friend-btn" @click="enterFriends()">
          <svg class="friend-btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
            <circle cx="9" cy="7" r="4"></circle>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
          </svg>
          <span>书友</span>
          <span v-if="friendPendingCount > 0" class="friend-dot">{{ friendPendingCount }}</span>
        </button>
        <button class="logout-btn" @click="logout">退出</button>
      </div>
    </header>

    <main class="friends-content">
      <button class="back-link" @click="go('home')">← 返回主页</button>
      <h1 class="page-title">书友</h1>
      <p class="page-subtitle">与你读过同一页的人</p>

      <div class="friend-tabs">
        <button class="friend-tab" :class="{ active: friendTab === 'friends' }" @click="switchFriendTab('friends')">
          <svg class="friend-tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
            <circle cx="9" cy="7" r="4"></circle>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
          </svg>
          我的书友
        </button>
        <button class="friend-tab" :class="{ active: friendTab === 'requests' }" @click="switchFriendTab('requests')">
          <svg class="friend-tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="2" y="4" width="20" height="16" rx="2"></rect>
            <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"></path>
          </svg>
          收到的申请
          <span v-if="friendPendingCount > 0" class="friend-dot friend-dot-inline">{{ friendPendingCount }}</span>
        </button>
      </div>

      <div v-if="friendTab === 'friends'">
        <div v-if="friendsLoading" class="friends-empty"><span class="loading-dot"></span>加载中…</div>
        <div v-else-if="friendsList.length === 0" class="friends-empty">
          <span class="friends-empty-icon">缘</span>
          <p>还没有书友，去「交个书友」认识一位吧。</p>
          <button class="submit-btn" @click="enterMatch()">去交个书友</button>
        </div>
        <div v-else class="friends-list">
          <div v-for="f in friendsList" :key="f.user.userId" class="friend-card">
            <span class="friend-avatar">{{ (f.user.nickname || '书').slice(0, 1) }}</span>
            <div class="friend-info">
              <span class="friend-name">{{ f.user.nickname }}</span>
              <span class="friend-meta">{{ f.becameFriendsAt }} 成为书友</span>
            </div>
            <button class="friend-remove" @click="removeFriend(f)">解除</button>
          </div>
        </div>
      </div>

      <div v-else>
        <div v-if="friendRequestsLoading" class="friends-empty"><span class="loading-dot"></span>加载中…</div>
        <div v-else-if="friendRequests.length === 0" class="friends-empty">
          <span class="friends-empty-icon">静</span>
          <p>没有待处理的书友申请。</p>
        </div>
        <div v-else class="friends-list">
          <div v-for="r in friendRequests" :key="r.requestId" class="friend-card">
            <span class="friend-avatar">{{ (r.requester.nickname || '书').slice(0, 1) }}</span>
            <div class="friend-info">
              <span class="friend-name">{{ r.requester.nickname }}</span>
              <span class="friend-meta">{{ r.createdAt }} 想与你成为书友</span>
            </div>
            <div class="friend-req-actions">
              <button class="friend-accept" :disabled="friendActionId === r.requestId" @click="handleFriendRequest(r, 'accepted')">接受</button>
              <button class="friend-reject" :disabled="friendActionId === r.requestId" @click="handleFriendRequest(r, 'rejected')">拒绝</button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>

  <!-- 管理员界面 -->
  <div v-else-if="currentPage === 'admin'" class="admin-page">
    <header class="topbar">
      <div class="brand">书遇</div>
      <div class="user-area">
        <span class="user-avatar">{{ (currentUser?.nickname || currentUser?.username || '书').slice(0, 1) }}</span>
        <span class="username">{{ currentUser?.nickname || currentUser?.username }}</span>
        <button class="logout-btn" @click="logout">退出</button>
      </div>
    </header>

    <main class="admin-content">
      <div class="admin-head">
        <div>
          <h1 class="page-title">管理员界面</h1>
          <p class="page-subtitle">审核公开笔记 · 管理上架书籍</p>
        </div>
        <div class="admin-tabs">
          <button class="admin-tab" :class="{ active: adminTab === 'notes' }" @click="adminTab = 'notes'">
            审核笔记
            <span v-if="adminNoteStats.pending > 0" class="tab-badge">{{ adminNoteStats.pending }}</span>
          </button>
          <button class="admin-tab" :class="{ active: adminTab === 'books' }" @click="adminTab = 'books'">管理书籍</button>
        </div>
      </div>

      <div class="admin-stats">
        <template v-if="adminTab === 'notes'">
          <div class="stat-card"><span class="stat-num">{{ adminNoteStats.pending }}</span><span class="stat-label">待审核</span></div>
          <div class="stat-card"><span class="stat-num">{{ adminNoteStats.approved }}</span><span class="stat-label">已通过</span></div>
          <div class="stat-card"><span class="stat-num">{{ adminNoteStats.rejected }}</span><span class="stat-label">已拒绝</span></div>
        </template>
        <template v-else>
          <div class="stat-card"><span class="stat-num">{{ adminBookStats.active }}</span><span class="stat-label">上架书籍</span></div>
          <div class="stat-card"><span class="stat-num">{{ adminBookStats.inactive }}</span><span class="stat-label">下架书籍</span></div>
        </template>
      </div>

      <!-- 审核笔记 -->
      <section v-if="adminTab === 'notes'">
        <div class="admin-filter">
          <button
            v-for="f in adminNoteFilters"
            :key="f.key"
            class="filter-chip"
            :class="{ active: adminNoteFilter === f.key }"
            @click="setAdminNoteFilter(f.key)"
          >{{ f.label }}</button>
        </div>

        <div v-if="filteredAdminNotes.length === 0" class="notes-empty">没有相关笔记</div>
        <div v-for="n in filteredAdminNotes" :key="n.noteId" class="admin-note-card" :class="'status-' + n.reviewStatus">
          <div class="note-card-top">
            <span class="note-book">{{ n.book?.title }}</span>
            <span class="admin-note-author">{{ n.author?.nickname }}</span>
          </div>
          <p v-if="splitNote(n.content).quote" class="note-quote">“{{ splitNote(n.content).quote }}”</p>
          <p v-if="splitNote(n.content).comment" class="note-comment">{{ splitNote(n.content).comment }}</p>
          <div class="admin-note-meta">
            <span class="note-visibility" :class="n.isPublic ? 'public' : 'private'">{{ n.isPublic ? '公开' : '私密' }}</span>
            <span class="note-status" :class="'ns-' + n.reviewStatus">{{ reviewStatusText[n.reviewStatus] }}</span>
            <span v-if="n.reviewReason" class="admin-reject-reason">拒因：{{ n.reviewReason }}</span>
            <span class="note-date">{{ n.createdAt }}</span>
          </div>
          <div v-if="n.reviewStatus === 'pending'" class="admin-note-actions">
            <button class="admin-approve-btn" @click="approveNote(n)">通过</button>
            <template v-if="rejectingNoteId !== n.noteId">
              <button class="admin-reject-btn" @click="startReject(n)">拒绝</button>
            </template>
            <template v-else>
              <input v-model="rejectReason" class="admin-reject-input" placeholder="填写拒绝原因（1-500 字）" />
              <button class="admin-approve-btn" @click="confirmReject(n)">确认拒绝</button>
              <button class="admin-cancel-btn" @click="rejectingNoteId = null">取消</button>
            </template>
          </div>
        </div>
      </section>

      <!-- 管理书籍 -->
      <section v-else>
        <div class="admin-book-toolbar">
          <div class="notes-search">
            <svg class="notes-search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
              <circle cx="11" cy="11" r="7"></circle>
              <line x1="21" y1="21" x2="16.5" y2="16.5"></line>
            </svg>
            <input v-model="adminBookSearch" type="text" placeholder="搜索书名或作者" />
          </div>
          <div class="admin-filter">
            <button
              v-for="s in [['all', '全部'], ['active', '上架'], ['inactive', '下架']]"
              :key="s[0]"
              class="filter-chip"
              :class="{ active: adminBookStatus === s[0] }"
              @click="adminBookStatus = s[0]"
            >{{ s[1] }}</button>
          </div>
        </div>

        <div v-if="filteredAdminBooks.length === 0" class="notes-empty">没有匹配的书籍</div>
        <div v-for="b in filteredAdminBooks" :key="b.bookId" class="admin-book-card">
          <span class="book-cover">{{ (b.title || '书')[0] }}</span>
          <div class="admin-book-info">
            <template v-if="editingBookId !== b.bookId">
              <h3 class="admin-book-title">
                {{ b.title }}
                <span class="book-status" :class="b.status">{{ b.status === 'active' ? '上架' : '下架' }}</span>
              </h3>
              <p class="admin-book-meta">{{ b.author }}<span v-if="b.isbn"> · ISBN {{ b.isbn }}</span></p>
              <p class="admin-book-intro">{{ b.intro || '暂无简介' }}</p>
            </template>
            <template v-else>
              <input v-model="editBookForm.title" class="admin-edit-input" placeholder="书名" />
              <input v-model="editBookForm.author" class="admin-edit-input" placeholder="作者" />
              <input v-model="editBookForm.isbn" class="admin-edit-input" placeholder="ISBN" />
              <textarea v-model="editBookForm.intro" class="admin-edit-input" placeholder="简介"></textarea>
            </template>
          </div>
          <div class="admin-book-actions">
            <template v-if="editingBookId !== b.bookId">
              <button class="admin-edit-btn" @click="startEditBook(b)">编辑</button>
              <button class="admin-approve-btn" @click="toggleBookStatus(b)">{{ b.status === 'active' ? '下架' : '上架' }}</button>
            </template>
            <template v-else>
              <button class="admin-approve-btn" @click="saveBook(b)">保存</button>
              <button class="admin-cancel-btn" @click="editingBookId = null">取消</button>
            </template>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
/* ===== 登录页 ===== */
.auth-page {
  position: relative;
  overflow: hidden;
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
  margin: 0 0 22px;
}
.role-toggle {
  display: inline-flex;
  gap: 4px;
  padding: 4px;
  margin: 0 0 26px;
  background: #f6efe4;
  border: 1px solid #efe6d8;
  border-radius: 24px;
}
.role-opt {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 18px;
  border: none;
  border-radius: 20px;
  background: transparent;
  color: #8a7a68;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}
.role-opt svg {
  width: 15px;
  height: 15px;
}
.role-opt:hover {
  color: #7d5233;
}
.role-opt.active {
  background: linear-gradient(135deg, #9a6a45, #7d5233);
  color: #fff;
  box-shadow: 0 4px 12px rgba(139, 94, 60, 0.25);
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
  font-family: inherit;
  color: #4a3a2a;
  background: #fdfaf6;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.form select {
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC',
    'Microsoft YaHei', sans-serif;
  color: #4a3a2a;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23a58a6e' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 14px center;
  padding-right: 38px;
  cursor: pointer;
}
.form select option {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC',
    'Microsoft YaHei', sans-serif;
  color: #4a3a2a;
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
.avatar-field {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
  text-align: left;
}
.avatar-label {
  font-size: 13px;
  color: #a58a6e;
}
.avatar-field input[type='file'] {
  width: 100%;
  padding: 9px;
  border: 1px dashed #d9b98a;
  border-radius: 10px;
  font-size: 13px;
  color: #8a7a68;
  background: #fdfaf6;
  cursor: pointer;
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
  position: relative;
  overflow: hidden;
  min-height: 100vh;
  background:
    radial-gradient(circle at 18% 18%, rgba(185, 138, 94, 0.07), transparent 45%),
    radial-gradient(circle at 82% 82%, rgba(185, 138, 94, 0.06), transparent 45%),
    linear-gradient(160deg, #fbf8f2 0%, #f5ecdd 100%);
}
.topbar {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 40px;
  background: rgba(255, 255, 255, 0.65);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}
.topbar::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(185, 138, 94, 0.35), transparent);
}
.brand {
  font-family: 'Songti SC', 'STSong', 'SimSun', 'Noto Serif SC', serif;
  font-size: 24px;
  letter-spacing: 8px;
  background: linear-gradient(135deg, #8a5c3a, #b98a5e);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}
.user-area {
  display: flex;
  align-items: center;
  gap: 12px;
}
.user-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: linear-gradient(135deg, #d9b98a, #b98a5e);
  color: #fff;
  font-size: 15px;
  flex-shrink: 0;
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
.friend-btn {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 16px;
  border: 1px solid #e5ddd3;
  border-radius: 20px;
  background: linear-gradient(135deg, #ffffff, #fdfaf6);
  color: #7d5233;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(139, 94, 60, 0.06);
  transition: all 0.2s;
}
.friend-btn:hover {
  border-color: #b98a5e;
  box-shadow: 0 4px 14px rgba(139, 94, 60, 0.16);
  transform: translateY(-1px);
}
.friend-btn-icon {
  width: 15px;
  height: 15px;
  color: #b98a5e;
  transition: color 0.2s;
}
.friend-btn:hover .friend-btn-icon {
  color: #7d5233;
}
.friend-dot {
  position: absolute;
  top: -7px;
  right: -7px;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  border-radius: 9px;
  background: #c96a5a;
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  line-height: 18px;
  text-align: center;
  box-shadow: 0 2px 6px rgba(201, 106, 90, 0.4);
}
.friend-dot-inline {
  position: static;
  margin-left: 6px;
  box-shadow: none;
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
  border-radius: 16px;
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

/* ===== 书单页 ===== */
.shelf-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at 18% 18%, rgba(185, 138, 94, 0.07), transparent 45%),
    radial-gradient(circle at 82% 82%, rgba(185, 138, 94, 0.06), transparent 45%),
    linear-gradient(160deg, #fbf8f2 0%, #f5ecdd 100%);
}
.shelf-content {
  max-width: 760px;
  margin: 0 auto;
  padding: 40px 24px 60px;
}
.back-link {
  display: inline-block;
  margin-bottom: 18px;
  background: none;
  border: none;
  padding: 0;
  color: #a58a6e;
  font-size: 14px;
  cursor: pointer;
  transition: color 0.2s;
}
.back-link:hover {
  color: #7d5233;
}
.page-title {
  position: relative;
  font-family: 'Songti SC', 'STSong', 'SimSun', 'Noto Serif SC', serif;
  font-size: 28px;
  color: #4a3a2a;
  margin: 0 0 6px;
  padding-bottom: 14px;
}
.page-title::after {
  content: '';
  position: absolute;
  left: 2px;
  bottom: 0;
  width: 44px;
  height: 3px;
  border-radius: 2px;
  background: linear-gradient(90deg, #b98a5e, rgba(217, 185, 138, 0.2));
}
.page-subtitle {
  margin: 0;
  font-size: 14px;
  color: #a58a6e;
}
.shelf-head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 24px;
}
.head-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}
.manage-btn {
  padding: 9px 16px;
  border: 1px solid #e8ddd0;
  border-radius: 20px;
  background: #fff;
  color: #8a7a68;
  font-size: 14px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
}
.manage-btn:hover {
  color: #7d5233;
  border-color: #b98a5e;
}
.manage-btn.active {
  background: linear-gradient(135deg, #9a6a45, #7d5233);
  color: #fff;
  border-color: transparent;
  box-shadow: 0 4px 12px rgba(139, 94, 60, 0.25);
}
.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 14px;
  background: #fff;
  border: 1px solid #e8ddd0;
  border-radius: 20px;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.search-box:hover {
  border-color: #d9b98a;
}
.search-box:focus-within {
  border-color: #b98a5e;
  box-shadow: 0 0 0 3px rgba(185, 138, 94, 0.12);
}
.search-icon {
  width: 16px;
  height: 16px;
  color: #b98a5e;
  flex-shrink: 0;
}
.search-box input {
  border: none;
  outline: none;
  background: transparent;
  width: 180px;
  font-size: 14px;
  color: #4a3a2a;
}
.search-box input::placeholder {
  color: #c5b8a6;
}
.tabs {
  display: inline-flex;
  gap: 4px;
  padding: 4px;
  margin-bottom: 26px;
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid #efe6d8;
  border-radius: 24px;
}
.tab {
  padding: 8px 20px;
  border: none;
  border-radius: 20px;
  background: transparent;
  color: #8a7a68;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}
.tab:hover {
  color: #7d5233;
  background: rgba(185, 138, 94, 0.08);
}
.tab.active {
  background: linear-gradient(135deg, #9a6a45, #7d5233);
  color: #fff;
  box-shadow: 0 4px 12px rgba(139, 94, 60, 0.25);
}
.tab-count {
  display: inline-block;
  margin-left: 6px;
  min-width: 18px;
  padding: 0 5px;
  border-radius: 10px;
  background: rgba(0, 0, 0, 0.05);
  font-size: 12px;
  line-height: 18px;
}
.tab.active .tab-count {
  background: rgba(255, 255, 255, 0.25);
}
.book-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.book-card {
  position: relative;
  overflow: hidden;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 16px 18px;
  background: #fff;
  border: 1px solid #efe6d8;
  border-radius: 16px;
  padding: 18px 22px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
  animation: card-in 0.4s ease backwards;
}
.book-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 28px rgba(139, 94, 60, 0.12);
  border-color: #e0c9a8;
}
.book-card:hover .book-cover {
  transform: rotate(-3deg) translateY(-2px);
}
.book-card:hover .book-info h3 {
  color: #7d5233;
}
.book-card:nth-child(1) { animation-delay: 0s; }
.book-card:nth-child(2) { animation-delay: 0.06s; }
.book-card:nth-child(3) { animation-delay: 0.12s; }
.book-card:nth-child(4) { animation-delay: 0.18s; }
.book-card:nth-child(5) { animation-delay: 0.24s; }
.book-card:nth-child(6) { animation-delay: 0.3s; }
.book-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: #b98a5e;
}
.card-wantToRead::before {
  background: #d9b98a;
}
.card-read::before {
  background: #a08f7a;
}
.book-cover {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 46px;
  height: 58px;
  border-radius: 6px;
  overflow: hidden;
  font-family: 'Songti SC', 'STSong', 'SimSun', 'Noto Serif SC', serif;
  font-size: 22px;
  color: #fff;
  background: linear-gradient(160deg, #b98a5e, #8a5c3a);
  box-shadow: 0 4px 12px rgba(139, 94, 60, 0.18);
  transition: transform 0.2s ease;
}
.book-cover::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 5px;
  background: rgba(0, 0, 0, 0.18);
  border-radius: 6px 0 0 6px;
}
.book-cover::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 4px;
  background: rgba(255, 255, 255, 0.25);
}
.book-info {
  flex: 1;
}
.book-info h3 {
  margin: 0 0 4px;
  font-size: 16px;
  color: #5f4a33;
  transition: color 0.2s;
}
.book-info p {
  margin: 0;
  font-size: 13px;
  color: #a58a6e;
}
.book-status {
  margin-left: auto;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  white-space: nowrap;
}
.status-reading {
  background: #f3e9db;
  color: #b98a5e;
}
.status-wantToRead {
  background: #f7e8d8;
  color: #c98a5a;
}
.status-read {
  background: #f0ece6;
  color: #a08f7a;
}
.remove-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  margin-left: auto;
  padding: 7px 14px;
  border: 1px solid #e8c9c0;
  border-radius: 14px;
  background: #fdf6f3;
  color: #c98a7a;
  font-size: 13px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
}
.remove-btn svg {
  width: 14px;
  height: 14px;
}
.remove-btn:hover {
  background: #c96a5a;
  border-color: #c96a5a;
  color: #fff;
  box-shadow: 0 4px 12px rgba(201, 106, 90, 0.25);
}
.remove-btn.confirm {
  background: #c96a5a;
  border-color: #c96a5a;
  color: #fff;
  box-shadow: 0 4px 12px rgba(201, 106, 90, 0.3);
}
.expand-arrow {
  width: 16px;
  height: 16px;
  color: #c9bfb2;
  flex-shrink: 0;
}
.empty-tip {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  margin: 40px 0;
  color: #c9bfb2;
  font-size: 14px;
}
.empty-tip p {
  margin: 0;
}
.empty-icon {
  width: 28px;
  height: 28px;
  color: #ddd2c2;
}
.shelf-footer {
  margin: 40px auto 0;
  padding-top: 18px;
  max-width: 260px;
  border-top: 1px solid #ece2d4;
  text-align: center;
  font-family: 'Songti SC', 'STSong', 'SimSun', 'Noto Serif SC', serif;
  font-style: italic;
  font-size: 13px;
  letter-spacing: 2px;
  color: #b08a5e;
}

/* ===== 上传笔记页 ===== */
.note-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at 18% 18%, rgba(185, 138, 94, 0.07), transparent 45%),
    radial-gradient(circle at 82% 82%, rgba(185, 138, 94, 0.06), transparent 45%),
    linear-gradient(160deg, #fbf8f2 0%, #f5ecdd 100%);
}
.note-content {
  max-width: 760px;
  margin: 0 auto;
  padding: 40px 24px 60px;
}
.note-form {
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 24px;
  background: #fff;
  border: 1px solid #efe6d8;
  border-radius: 18px;
  padding: 28px;
  box-shadow: 0 12px 32px rgba(139, 94, 60, 0.08);
}
.note-form::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #d9b98a, #b98a5e, #d9b98a);
}
.form-quote {
  font-family: Georgia, 'Times New Roman', serif;
  font-size: 42px;
  line-height: 1;
  color: #e4d5c0;
  margin: -4px 0 0;
}
.field-label {
  margin-top: 6px;
  font-size: 14px;
  color: #8a7a68;
}
.visibility-toggle {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.vis-option {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  padding: 13px 10px 11px;
  border: 1px solid #e8ddd0;
  border-radius: 12px;
  background: #fdfaf6;
  cursor: pointer;
  transition: all 0.2s;
}
.vis-option:hover {
  border-color: #d9b98a;
}
.vis-icon {
  width: 18px;
  height: 18px;
  color: #b98a5e;
  margin-bottom: 2px;
}
.vis-label {
  font-size: 14px;
  color: #5f4a33;
}
.vis-hint {
  font-size: 12px;
  color: #c5b8a6;
}
.vis-option.active {
  border-color: #b98a5e;
  background: #f7efe4;
  box-shadow: 0 0 0 3px rgba(185, 138, 94, 0.1);
  transform: translateY(-1px) scale(1.02);
}
.vis-option.active .vis-label {
  color: #7d5233;
}
.vis-option.active .vis-icon {
  color: #9a6a45;
}
.vis-option.active .vis-hint {
  color: #a58a6e;
}
.vis-check {
  position: absolute;
  top: 8px;
  right: 8px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: linear-gradient(135deg, #9a6a45, #7d5233);
  color: #fff;
  animation: fade-in 0.15s ease;
}
.vis-check svg {
  width: 12px;
  height: 12px;
}
.char-count {
  align-self: flex-end;
  margin-top: -4px;
  font-size: 12px;
  color: #c5b8a6;
}
.note-textarea {
  width: 100%;
  padding: 13px 15px;
  border: 1px solid #e8ddd0;
  border-radius: 12px;
  font-size: 15px;
  font-family: inherit;
  background: #fdfaf6;
  color: #4a3a2a;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.note-textarea:focus {
  border-color: #b98a5e;
  box-shadow: 0 0 0 3px rgba(185, 138, 94, 0.12);
}
.note-textarea:hover {
  border-color: #d9b98a;
}
.book-picker {
  position: relative;
}
.book-picker-input {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 14px;
  border: 1px solid #e8ddd0;
  border-radius: 12px;
  background: #fdfaf6;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.book-picker-input:hover {
  border-color: #d9b98a;
}
.book-picker-input.open {
  border-color: #b98a5e;
  box-shadow: 0 0 0 3px rgba(185, 138, 94, 0.12);
}
.book-picker-input input {
  flex: 1;
  padding: 13px 0;
  border: none;
  outline: none;
  background: transparent;
  font-size: 15px;
  color: #4a3a2a;
}
.book-picker-input input::placeholder {
  color: #c5b8a6;
}
.picker-chevron {
  width: 16px;
  height: 16px;
  color: #b98a5e;
  flex-shrink: 0;
  transition: transform 0.2s;
}
.picker-chevron.open {
  transform: rotate(180deg);
}
.book-picker-list {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  z-index: 20;
  max-height: 240px;
  overflow-y: auto;
  background: #fff;
  border: 1px solid #efe6d8;
  border-radius: 12px;
  box-shadow: 0 12px 32px rgba(139, 94, 60, 0.16);
  padding: 6px;
}
.book-picker-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s;
}
.book-picker-item:hover {
  background: #f7efe4;
}
.book-picker-item.active {
  background: #f3e9db;
}
.picker-title {
  font-size: 14px;
  color: #4a3a2a;
}
.book-picker-item.active .picker-title {
  color: #7d5233;
}
.picker-author {
  font-size: 12px;
  color: #a58a6e;
}
.book-picker-empty {
  padding: 14px;
  text-align: center;
  font-size: 13px;
  color: #c9bfb2;
}
.note-textarea {
  min-height: 140px;
  resize: vertical;
  line-height: 1.7;
}
.submit-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 8px;
  padding: 13px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #9a6a45, #7d5233);
  color: #fff;
  font-size: 16px;
  letter-spacing: 4px;
  cursor: pointer;
  transition: background 0.2s, transform 0.1s, opacity 0.2s;
}
.btn-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}
.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
.submit-btn:hover {
  background: #7d5233;
}
.submit-btn:active {
  transform: scale(0.98);
}
.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.ai-result {
  margin-top: 20px;
  padding: 18px 20px;
  border: 1px solid #e6d8c4;
  border-radius: 16px;
  background: linear-gradient(160deg, #fdf8ef, #f7eedd);
  animation: card-in 0.4s ease;
}
.ai-result-title {
  margin: 0 0 14px;
  font-family: 'Songti SC', 'STSong', 'SimSun', 'Noto Serif SC', serif;
  font-size: 15px;
  color: #7d5233;
}
.ai-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 10px;
}
.ai-row:last-child {
  margin-bottom: 0;
}
.ai-label {
  flex-shrink: 0;
  width: 44px;
  font-size: 13px;
  color: #a58a6e;
  line-height: 24px;
}
.ai-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.ai-tag {
  padding: 4px 12px;
  border-radius: 12px;
  background: #fff;
  border: 1px solid #e8ddd0;
  font-size: 13px;
  color: #6a5a48;
}
.ai-empty {
  font-size: 13px;
  color: #c9bfb2;
  line-height: 24px;
}
.ai-sentiment {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 13px;
  line-height: 16px;
}
.sent-pos {
  background: #eef2e4;
  color: #7f9062;
}
.sent-neu {
  background: #f0ece6;
  color: #a08f7a;
}
.sent-neg {
  background: #f6e6e4;
  color: #c9867a;
}
.my-notes {
  margin-top: 28px;
}
.notes-head {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 14px;
}
.notes-title {
  font-family: 'Songti SC', 'STSong', 'SimSun', 'Noto Serif SC', serif;
  font-size: 20px;
  color: #4a3a2a;
  margin: 0;
}
.notes-count {
  font-size: 13px;
  color: #c5b8a6;
}
.notes-search {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 14px;
  margin-bottom: 14px;
  background: #fff;
  border: 1px solid #e8ddd0;
  border-radius: 20px;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.notes-search:focus-within {
  border-color: #b98a5e;
  box-shadow: 0 0 0 3px rgba(185, 138, 94, 0.12);
}
.notes-search-icon {
  width: 16px;
  height: 16px;
  color: #b98a5e;
  flex-shrink: 0;
}
.notes-search input {
  border: none;
  outline: none;
  background: transparent;
  width: 100%;
  font-size: 14px;
  color: #4a3a2a;
}
.notes-search input::placeholder {
  color: #c5b8a6;
}
.notes-empty {
  padding: 30px 0;
  text-align: center;
  color: #c9bfb2;
  font-size: 14px;
}
.note-card {
  display: flex;
  flex-direction: column;
  gap: 10px;
  background: #fff;
  border: 1px solid #efe6d8;
  border-radius: 16px;
  padding: 18px 20px;
  margin-bottom: 12px;
  transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
  animation: card-in 0.4s ease backwards;
}
.note-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 28px rgba(139, 94, 60, 0.12);
  border-color: #e0c9a8;
}
.note-card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.note-book {
  font-size: 14px;
  color: #7d5233;
  font-family: 'Songti SC', 'STSong', 'SimSun', 'Noto Serif SC', serif;
}
.note-visibility {
  padding: 3px 10px;
  border-radius: 10px;
  font-size: 12px;
}
.note-visibility.public {
  background: #f3e9db;
  color: #b98a5e;
}
.note-visibility.private {
  background: #f0ece6;
  color: #a08f7a;
}
.note-card-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.note-status {
  padding: 3px 10px;
  border-radius: 10px;
  font-size: 12px;
}
.ns-approved {
  background: #eef2e4;
  color: #7f9062;
}
.ns-pending {
  background: #f7e8d8;
  color: #c98a5a;
}
.ns-rejected {
  background: #f6e6e4;
  color: #c9867a;
}
.note-date {
  font-size: 12px;
  color: #c9bfb2;
}

/* ===== 书籍详情页 ===== */
.book-detail-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at 18% 18%, rgba(185, 138, 94, 0.07), transparent 45%),
    radial-gradient(circle at 82% 82%, rgba(185, 138, 94, 0.06), transparent 45%),
    linear-gradient(160deg, #fbf8f2 0%, #f5ecdd 100%);
}
.book-detail-content {
  max-width: 760px;
  margin: 0 auto;
  padding: 40px 24px 60px;
}
.book-detail-head {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}
.book-cover-lg {
  width: 88px;
  height: 112px;
  font-size: 40px;
}
.book-detail-info {
  flex: 1;
  min-width: 0;
}
.book-detail-info .page-title {
  font-size: 26px;
  margin-bottom: 4px;
}
.book-detail-info .page-subtitle {
  margin-bottom: 12px;
}
.book-intro {
  margin: 0 0 8px;
  font-size: 14px;
  line-height: 1.8;
  color: #6a5a48;
}
.book-isbn {
  margin: 0;
  font-size: 12px;
  color: #c9bfb2;
  letter-spacing: 0.5px;
}
.detail-note-btn {
  width: 100%;
  margin: 24px 0 0;
}
.note-quote {
  margin: 0;
  font-family: 'Songti SC', 'STSong', 'SimSun', 'Noto Serif SC', serif;
  font-size: 15px;
  line-height: 1.8;
  color: #4a3a2a;
}
.note-quote::before,
.note-quote::after {
  color: #c9bfb2;
}
.note-comment {
  margin: 0;
  padding-left: 12px;
  border-left: 3px solid #e0c9a8;
  font-size: 14px;
  line-height: 1.7;
  color: #6a5a48;
}

/* ===== 管理员界面 ===== */
.admin-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at 18% 18%, rgba(185, 138, 94, 0.07), transparent 45%),
    radial-gradient(circle at 82% 82%, rgba(185, 138, 94, 0.06), transparent 45%),
    linear-gradient(160deg, #fbf8f2 0%, #f5ecdd 100%);
}
.admin-content {
  max-width: 760px;
  margin: 0 auto;
  padding: 40px 24px 60px;
}
.admin-head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 22px;
}
.admin-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 20px;
}
.stat-card {
  flex: 1;
  min-width: 110px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 16px 12px;
  background: #fff;
  border: 1px solid #efe6d8;
  border-radius: 16px;
  transition: transform 0.2s, box-shadow 0.2s;
}
.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(139, 94, 60, 0.1);
}
.stat-num {
  font-family: 'Songti SC', 'STSong', 'SimSun', 'Noto Serif SC', serif;
  font-size: 26px;
  color: #7d5233;
  line-height: 1;
}
.stat-label {
  font-size: 12px;
  color: #a58a6e;
}
.tab-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-left: 6px;
  min-width: 18px;
  height: 18px;
  padding: 0 6px;
  border-radius: 9px;
  background: #c98a5a;
  color: #fff;
  font-size: 12px;
  line-height: 1;
}
.admin-tabs {
  display: flex;
  gap: 8px;
  padding: 4px;
  background: #fff;
  border: 1px solid #e8ddd0;
  border-radius: 20px;
}
.admin-tab {
  padding: 8px 18px;
  border: none;
  border-radius: 16px;
  background: transparent;
  color: #8a7a68;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}
.admin-tab.active {
  background: linear-gradient(135deg, #9a6a45, #7d5233);
  color: #fff;
  box-shadow: 0 4px 12px rgba(139, 94, 60, 0.25);
}
.admin-filter {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}
.filter-chip {
  padding: 7px 16px;
  border: 1px solid #e8ddd0;
  border-radius: 18px;
  background: #fff;
  color: #8a7a68;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}
.filter-chip.active {
  background: linear-gradient(135deg, #9a6a45, #7d5233);
  border-color: transparent;
  color: #fff;
  box-shadow: 0 4px 12px rgba(139, 94, 60, 0.25);
}
.admin-note-card {
  position: relative;
  overflow: hidden;
  background: #fff;
  border: 1px solid #efe6d8;
  border-radius: 16px;
  padding: 18px 20px;
  margin-bottom: 12px;
  animation: card-in 0.4s ease backwards;
  transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
}
.admin-note-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: #d9b98a;
}
.admin-note-card.status-approved::before {
  background: #a3b18a;
}
.admin-note-card.status-rejected::before {
  background: #c9867a;
}
.admin-note-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 28px rgba(139, 94, 60, 0.12);
  border-color: #e0c9a8;
}
.admin-note-author {
  font-size: 13px;
  color: #a58a6e;
}
.admin-note-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}
.admin-reject-reason {
  font-size: 12px;
  color: #c9867a;
}
.admin-note-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px dashed #ece2d4;
}
.admin-approve-btn,
.admin-reject-btn,
.admin-cancel-btn,
.admin-edit-btn {
  padding: 7px 16px;
  border-radius: 16px;
  border: 1px solid #e8ddd0;
  background: #fff;
  color: #6a5a48;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}
.admin-approve-btn {
  background: linear-gradient(135deg, #9a6a45, #7d5233);
  border-color: transparent;
  color: #fff;
}
.admin-approve-btn:hover {
  background: #7d5233;
}
.admin-reject-btn:hover {
  border-color: #c9867a;
  color: #c9867a;
}
.admin-cancel-btn:hover,
.admin-edit-btn:hover {
  border-color: #b98a5e;
  color: #7d5233;
}
.admin-reject-input {
  flex: 1;
  min-width: 200px;
  padding: 8px 12px;
  border: 1px solid #e8ddd0;
  border-radius: 12px;
  font-size: 13px;
  background: #fdfaf6;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.admin-reject-input:focus {
  border-color: #b98a5e;
  box-shadow: 0 0 0 3px rgba(185, 138, 94, 0.12);
}
.admin-book-toolbar {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}
.admin-book-card {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  background: #fff;
  border: 1px solid #efe6d8;
  border-radius: 16px;
  padding: 18px 20px;
  margin-bottom: 12px;
  animation: card-in 0.4s ease backwards;
  transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
}
.admin-book-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 28px rgba(139, 94, 60, 0.12);
  border-color: #e0c9a8;
}
.admin-book-info {
  flex: 1;
  min-width: 0;
}
.admin-book-title {
  margin: 0 0 4px;
  font-size: 16px;
  color: #5f4a33;
}
.book-status {
  margin-left: 8px;
  padding: 2px 10px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: normal;
}
.book-status.active {
  background: #eef2e4;
  color: #7f9062;
}
.book-status.inactive {
  background: #f0ece6;
  color: #a08f7a;
}
.admin-book-meta {
  margin: 0 0 6px;
  font-size: 13px;
  color: #a58a6e;
}
.admin-book-intro {
  margin: 0;
  font-size: 13px;
  line-height: 1.7;
  color: #6a5a48;
}
.admin-book-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex-shrink: 0;
}
.admin-edit-input {
  display: block;
  width: 100%;
  margin-bottom: 8px;
  padding: 9px 12px;
  border: 1px solid #e8ddd0;
  border-radius: 10px;
  font-size: 13px;
  background: #fdfaf6;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.admin-edit-input:focus {
  border-color: #b98a5e;
  box-shadow: 0 0 0 3px rgba(185, 138, 94, 0.12);
}

/* ===== 漂流瓶匹配页 ===== */
.match-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at 18% 18%, rgba(185, 138, 94, 0.07), transparent 45%),
    radial-gradient(circle at 82% 82%, rgba(185, 138, 94, 0.06), transparent 45%),
    linear-gradient(160deg, #fbf8f2 0%, #f5ecdd 100%);
}
.match-content {
  max-width: 760px;
  margin: 0 auto;
  padding: 40px 24px 60px;
}
.match-subtitle {
  margin: 0 0 24px;
  color: #a58a6e;
  font-size: 14px;
}
.match-note-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.match-note-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 18px;
  text-align: left;
  background: #fff;
  border: 1px solid #efe6d8;
  border-radius: 16px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
}
.match-note-item:hover {
  transform: translateY(-2px);
  border-color: #d9b98a;
  box-shadow: 0 8px 20px rgba(139, 94, 60, 0.1);
}
.match-note-index {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #f6ead9;
  color: #a97b50;
  font-family: 'Songti SC', 'STSong', 'SimSun', 'Noto Serif SC', serif;
  font-size: 15px;
  flex-shrink: 0;
}
.match-note-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.match-note-book {
  font-family: 'Songti SC', 'STSong', 'SimSun', 'Noto Serif SC', serif;
  color: #7d5233;
  font-size: 15px;
}
.match-note-quote {
  color: #8a7a68;
  font-size: 13px;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.match-note-go {
  flex-shrink: 0;
  color: #b98a5e;
  font-size: 13px;
  white-space: nowrap;
  transition: transform 0.2s;
}
.match-note-item:hover .match-note-go {
  transform: translateX(3px);
}
.match-empty {
  padding: 48px 20px;
  text-align: center;
  color: #a58a6e;
  font-size: 14px;
  background: rgba(255, 255, 255, 0.6);
  border: 1px dashed #e0d3c0;
  border-radius: 16px;
}
.match-empty p {
  margin: 0 0 16px;
}
.match-result-head {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
}
.text-btn {
  align-self: flex-start;
  background: none;
  border: none;
  padding: 0;
  color: #a58a6e;
  font-size: 14px;
  cursor: pointer;
  transition: color 0.2s;
}
.text-btn:hover {
  color: #7d5233;
}
.match-source {
  padding: 14px 16px;
  background: linear-gradient(160deg, #fdf8ef, #f7eedd);
  border: 1px solid #e6d8c4;
  border-radius: 14px;
}
.match-source-label {
  display: block;
  margin-bottom: 6px;
  color: #7d5233;
  font-size: 13px;
}
.match-source-quote {
  color: #8a7a68;
  font-size: 13px;
  line-height: 1.6;
}
.match-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.match-count {
  margin: 0;
  color: #a58a6e;
  font-size: 13px;
}
.match-card {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 16px 18px;
  text-align: left;
  background: #fff;
  border: 1px solid #efe6d8;
  border-radius: 16px;
  cursor: pointer;
  animation: card-in 0.4s ease backwards;
  transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
}
.match-card:hover {
  transform: translateY(-2px);
  border-color: #d9b98a;
  box-shadow: 0 8px 20px rgba(139, 94, 60, 0.1);
}
.match-score-badge {
  position: absolute;
  top: 14px;
  right: 16px;
  padding: 4px 10px;
  border-radius: 12px;
  background: linear-gradient(135deg, #d9b98a, #b98a5e);
  color: #fff;
  font-family: 'Songti SC', 'STSong', 'SimSun', 'Noto Serif SC', serif;
  font-size: 14px;
  letter-spacing: 0.5px;
}
.match-score-badge.high {
  background: linear-gradient(135deg, #e0a566, #c98a5a);
}
.match-score-badge.mid {
  background: linear-gradient(135deg, #d9b98a, #b98a5e);
}
.match-score-badge.low {
  background: linear-gradient(135deg, #cbbca8, #b8a992);
}
.match-card-top {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-right: 64px;
}
.match-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #d9b98a, #b98a5e);
  color: #fff;
  font-size: 18px;
  flex-shrink: 0;
}
.match-avatar.big {
  width: 52px;
  height: 52px;
  font-size: 22px;
}
.match-card-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.match-card-name {
  color: #4a3a2a;
  font-size: 15px;
}
.match-card-book {
  color: #a58a6e;
  font-size: 13px;
}
.match-card-preview {
  margin: 0;
  color: #8a7a68;
  font-size: 14px;
  line-height: 1.7;
}
.match-card-rec {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin: 0;
  color: #8a7a68;
  font-size: 13px;
  line-height: 1.5;
}
.match-rec-tag {
  flex-shrink: 0;
  padding: 2px 8px;
  border-radius: 6px;
  background: #f6ead9;
  color: #a97b50;
  font-size: 12px;
}
.match-modal {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: rgba(74, 58, 42, 0.35);
  animation: fade-in 0.2s ease;
}
.match-modal-card {
  position: relative;
  width: 100%;
  max-width: 420px;
  max-height: 90vh;
  overflow-y: auto;
  padding: 28px 24px 24px;
  background: #fff;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(74, 58, 42, 0.3);
  animation: card-in 0.3s ease;
}
.modal-close {
  position: absolute;
  top: 14px;
  right: 16px;
  background: none;
  border: none;
  color: #c0b4a4;
  font-size: 24px;
  line-height: 1;
  cursor: pointer;
  transition: color 0.2s;
}
.modal-close:hover {
  color: #7d5233;
}
.match-modal-head {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 16px;
}
.match-modal-name {
  color: #4a3a2a;
  font-size: 18px;
  font-family: 'Songti SC', 'STSong', 'SimSun', 'Noto Serif SC', serif;
}
.match-modal-book {
  color: #a58a6e;
  font-size: 13px;
  margin-top: 2px;
}
.match-modal-preview {
  margin: 0 0 12px;
  color: #8a7a68;
  font-size: 15px;
  line-height: 1.8;
}
.match-modal-rec {
  margin: 0 0 20px;
  padding: 12px 14px;
  color: #b98a5e;
  font-size: 13px;
  background: #fdf8ef;
  border-left: 3px solid #d9b98a;
  border-radius: 8px;
}
.match-score-block {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 22px;
  padding: 20px;
  background: linear-gradient(160deg, #fdf8ef, #f7eedd);
  border-radius: 16px;
}
.match-score-ring {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 150px;
  height: 150px;
  border-radius: 50%;
}
.match-score-ring-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  width: 118px;
  height: 118px;
  border-radius: 50%;
  background: #fff;
}
.match-score-num {
  font-family: 'Songti SC', 'STSong', 'SimSun', 'Noto Serif SC', serif;
  font-size: 38px;
  color: #7d5233;
  line-height: 1;
}
.match-score-unit {
  font-size: 18px;
  margin-left: 2px;
}
.match-score-level {
  font-size: 13px;
  letter-spacing: 1px;
}
.match-score-level.high {
  color: #c98a5a;
}
.match-score-level.mid {
  color: #b98a5e;
}
.match-score-level.low {
  color: #b8a992;
}
.match-cta {
  width: 100%;
  letter-spacing: 2px;
}
.match-refresh-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 8px;
  padding: 12px;
  border: 1px solid #d9b98a;
  border-radius: 12px;
  background: #fff;
  color: #7d5233;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.2s;
}
.match-refresh-btn svg {
  width: 16px;
  height: 16px;
}
.match-refresh-btn:hover {
  background: #fdf8ef;
  border-color: #b98a5e;
}
.match-no-more {
  margin: 8px 0 0;
  text-align: center;
  color: #b8a992;
  font-size: 13px;
}

/* ===== 读书墙 ===== */
.wall-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at 18% 18%, rgba(185, 138, 94, 0.07), transparent 45%),
    radial-gradient(circle at 82% 82%, rgba(185, 138, 94, 0.06), transparent 45%),
    linear-gradient(160deg, #fbf8f2 0%, #f5ecdd 100%);
}
.wall-content {
  max-width: 760px;
  margin: 0 auto;
  padding: 40px 24px 60px;
}
.wall-content .page-subtitle {
  margin-bottom: 24px;
}
.wall-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}
.wall-tab {
  padding: 8px 18px;
  border: 1px solid #e8ddd0;
  border-radius: 20px;
  background: #fff;
  color: #8a7a68;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}
.wall-tab:hover {
  color: #7d5233;
  border-color: #b98a5e;
}
.wall-tab.active {
  background: linear-gradient(135deg, #9a6a45, #7d5233);
  color: #fff;
  border-color: transparent;
  box-shadow: 0 4px 12px rgba(139, 94, 60, 0.25);
}
.wall-empty {
  padding: 48px 20px;
  text-align: center;
  color: #a58a6e;
  font-size: 14px;
  background: rgba(255, 255, 255, 0.6);
  border: 1px dashed #e0d3c0;
  border-radius: 16px;
}
.wall-empty p {
  margin: 0 0 16px;
}
.wall-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.wall-card {
  background: #fff;
  border: 1px solid #efe6d8;
  border-radius: 16px;
  padding: 20px 22px;
  transition: transform 0.2s, box-shadow 0.2s;
}
.wall-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 28px rgba(139, 94, 60, 0.1);
}
.wall-card-head {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}
.wall-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: linear-gradient(135deg, #d9b98a, #b98a5e);
  color: #fff;
  font-size: 20px;
  flex-shrink: 0;
}
.wall-author {
  display: flex;
  flex-direction: column;
  gap: 3px;
}
.wall-nickname {
  color: #4a3a2a;
  font-size: 15px;
}
.wall-meta {
  color: #a58a6e;
  font-size: 12px;
}
.wall-quote {
  margin: 0 0 8px;
  padding: 12px 16px;
  color: #7d5233;
  font-family: 'Songti SC', 'STSong', 'SimSun', 'Noto Serif SC', serif;
  font-size: 15px;
  line-height: 1.8;
  background: linear-gradient(160deg, #fdf8ef, #f7eedd);
  border-left: 3px solid #d9b98a;
  border-radius: 8px;
}
.wall-review {
  margin: 0;
  color: #8a7a68;
  font-size: 14px;
  line-height: 1.7;
}
.wall-actions {
  display: flex;
  gap: 18px;
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px solid #f3ead9;
}
.wall-action {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 6px;
  border: none;
  background: none;
  color: #a58a6e;
  font-size: 13px;
  cursor: pointer;
  transition: color 0.2s, transform 0.1s;
}
.wall-action svg {
  width: 18px;
  height: 18px;
}
.wall-action:hover {
  color: #7d5233;
}
.wall-action:active {
  transform: scale(0.92);
}
.wall-action.active {
  color: #c9867a;
}
.wall-action.active svg {
  fill: currentColor;
}
.wall-comments {
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px solid #f3ead9;
}
.wall-comments-empty {
  padding: 16px 0;
  text-align: center;
  color: #b8a992;
  font-size: 13px;
}
.wall-comment-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 14px;
}
.wall-comment-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}
.wall-comment-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #f6ead9;
  color: #a97b50;
  font-size: 14px;
  flex-shrink: 0;
}
.wall-comment-body {
  flex: 1;
}
.wall-comment-head {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 3px;
}
.wall-comment-name {
  color: #5f4a33;
  font-size: 13px;
}
.wall-comment-time {
  color: #b8a992;
  font-size: 11px;
}
.wall-comment-text {
  margin: 0;
  color: #8a7a68;
  font-size: 13px;
  line-height: 1.6;
}
.wall-comment-del {
  flex-shrink: 0;
  background: none;
  border: none;
  padding: 2px;
  color: #c0b4a4;
  font-size: 12px;
  cursor: pointer;
  transition: color 0.2s;
}
.wall-comment-del:hover {
  color: #c9867a;
}
.wall-comment-input {
  display: flex;
  gap: 8px;
}
.wall-comment-input input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid #e6d8c4;
  border-radius: 10px;
  background: #fdfaf5;
  font-size: 14px;
  color: #5f4a33;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.wall-comment-input input:focus {
  border-color: #b98a5e;
  box-shadow: 0 0 0 3px rgba(185, 138, 94, 0.12);
}
.wall-comment-input input::placeholder {
  color: #c0b4a4;
}
.wall-comment-send {
  padding: 10px 18px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #9a6a45, #7d5233);
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  transition: opacity 0.2s;
}
.wall-comment-send:hover {
  opacity: 0.9;
}

/* ===== 书友 ===== */
.friends-content {
  max-width: 760px;
  margin: 0 auto;
  padding: 40px 24px 60px;
}
.friends-content .page-subtitle {
  margin-bottom: 24px;
}
.friend-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}
.friend-tab {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 18px;
  border: 1px solid #e8ddd0;
  border-radius: 20px;
  background: #fff;
  color: #8a7a68;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}
.friend-tab-icon {
  width: 15px;
  height: 15px;
}
.friend-tab:hover {
  color: #7d5233;
  border-color: #b98a5e;
}
.friend-tab.active {
  background: linear-gradient(135deg, #9a6a45, #7d5233);
  color: #fff;
  border-color: transparent;
  box-shadow: 0 4px 12px rgba(139, 94, 60, 0.25);
}
.friends-empty {
  padding: 48px 20px;
  text-align: center;
  color: #a58a6e;
  font-size: 14px;
  background: rgba(255, 255, 255, 0.6);
  border: 1px dashed #e0d3c0;
  border-radius: 16px;
}
.friends-empty p {
  margin: 0 0 16px;
}
.friends-empty-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
  border-radius: 50%;
  background: linear-gradient(135deg, #f3e9db, #e8d8c2);
  color: #c0a67f;
  font-family: 'Songti SC', 'STSong', 'SimSun', 'Noto Serif SC', serif;
  font-size: 28px;
}
.friends-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.friend-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 14px;
  background: #fff;
  border: 1px solid #efe6d8;
  border-radius: 16px;
  padding: 16px 20px;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
}
.friend-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: linear-gradient(180deg, #b98a5e, #d9b98a);
  opacity: 0;
  transition: opacity 0.2s;
}
.friend-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 28px rgba(139, 94, 60, 0.1);
}
.friend-card:hover::before {
  opacity: 1;
}
.friend-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 46px;
  height: 46px;
  border-radius: 50%;
  background: linear-gradient(135deg, #d9b98a, #b98a5e);
  color: #fff;
  font-size: 18px;
  flex-shrink: 0;
  box-shadow: 0 0 0 3px #f3e9db, 0 4px 10px rgba(139, 94, 60, 0.18);
}
.friend-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.friend-name {
  font-size: 15px;
  font-weight: 600;
  color: #4a3a2a;
}
.friend-meta {
  font-size: 13px;
  color: #a58a6e;
}
.friend-remove {
  padding: 6px 14px;
  border: 1px solid #e8c9c0;
  border-radius: 14px;
  background: #fdf6f3;
  color: #c9867a;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}
.friend-remove:hover {
  background: #c96a5a;
  border-color: #c96a5a;
  color: #fff;
}
.friend-req-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}
.friend-accept {
  padding: 6px 16px;
  border: 1px solid transparent;
  border-radius: 14px;
  background: linear-gradient(135deg, #9a6a45, #7d5233);
  color: #fff;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}
.friend-accept:hover {
  box-shadow: 0 4px 12px rgba(139, 94, 60, 0.25);
}
.friend-accept:disabled {
  opacity: 0.5;
  cursor: default;
}
.friend-reject {
  padding: 6px 16px;
  border: 1px solid #e8c9c0;
  border-radius: 14px;
  background: #fff;
  color: #c9867a;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}
.friend-reject:hover {
  background: #fdf6f3;
  border-color: #c9867a;
}
.friend-reject:disabled {
  opacity: 0.5;
  cursor: default;
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
/* 页面切换过渡 */
.auth-page,
.home-page,
.shelf-page,
.note-page,
.book-detail-page,
.match-page,
.wall-page,
.friends-page,
.admin-page {
  animation: page-in 0.35s ease;
}
@keyframes page-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
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
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
.loading-dot {
  display: inline-block;
  width: 14px;
  height: 14px;
  margin-right: 8px;
  border: 2px solid #e6d8c4;
  border-top-color: #b98a5e;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  vertical-align: -2px;
}
.auth-page::before,
.home-page::before {
  content: '';
  position: absolute;
  width: 320px;
  height: 320px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(185, 138, 94, 0.14), transparent 70%);
  top: 6%;
  left: -6%;
  animation: float-a 13s ease-in-out infinite;
}
.auth-page::after,
.home-page::after {
  content: '';
  position: absolute;
  width: 280px;
  height: 280px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(201, 138, 90, 0.12), transparent 70%);
  bottom: 5%;
  right: -5%;
  animation: float-b 16s ease-in-out infinite;
}
@keyframes float-a {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  50% {
    transform: translate(32px, -24px) scale(1.08);
  }
}
@keyframes float-b {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  50% {
    transform: translate(-28px, 20px) scale(1.06);
  }
}
</style>
