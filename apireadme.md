---
title: 书遇接口文档
language_tabs:
  - shell: Shell
  - http: HTTP
  - javascript: JavaScript
  - ruby: Ruby
  - python: Python
  - php: PHP
  - java: Java
  - go: Go
toc_footers: []
includes: []
search: true
code_clipboard: true
highlight_theme: darkula
headingLevel: 2
generator: "@tarslib/widdershins v4.0.30"

---

# 书遇接口文档

40 个 HTTP 接口，按模块分组。所有业务 HTTP 响应均为 200；业务 code 仅 200（成功）、400（失败）、401（需要登录）。先上传头像，再以 avatarPath 注册；头像必有且不可清空。除注册、登录和头像上传外使用 Bearer Token。WebSocket /api/ws 的首帧及事件见 Apifox导入说明.md，不将它作为 HTTP 接口导入。

Base URLs:

# Authentication

- HTTP Authentication, scheme: bearer<br/>登录返回的 token。Apifox Bearer Token 中只填写 token 值，不再手写 Bearer 前缀。

# 01 认证与用户

<a id="opIdloginUser"></a>

## POST 用户与管理员统一登录

POST /api/auth/login

无需 Token。邮箱或密码错误返回 code=400。登录成功后只持久缓存 token，再调用 /api/me 获取用户资料及角色；Token 默认有效期 7 天。

> Body 请求参数

```json
{
    "email": "reader@example.com",
    "password": "ReadTogether2026"
}
```

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|body|body|[LoginRequest](#schemaloginrequest)| 是 |none|

> 返回示例

> HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。

```json
{
    "code": 200,
    "data": {
        "token": "example-jwt-token",
        "expiresAt": "2026-09-14T12:00:00Z"
    },
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|code|400|
|code|401|
|data|null|

<a id="opIdregisterUser"></a>

## POST 注册账号

POST /api/auth/register

无需 Token。先上传头像，再将 data.filePath 作为 avatarPath 提交 JSON。头像必填，不允许 null 或空字符串；不提供默认头像。邮箱规范化后查重，注册角色固定为普通用户，成功后调用登录。

> Body 请求参数

```json
{
    "avatarPath": "/uploads/avatars/9c1a2c77.png",
    "nickname": "山间读者",
    "email": "reader@example.com",
    "password": "ReadTogether2026",
    "gender": "female"
}
```

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|body|body|[RegisterRequest](#schemaregisterrequest)| 是 |none|

> 返回示例

> HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。

```json
{
    "code": 200,
    "data": {
        "userId": 1
    },
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|code|400|
|code|401|
|data|null|

<a id="opIdgetCurrentUser"></a>

## GET 获取我的资料

GET /api/me

根据 Token 查询本人资料，不接受 userId。返回真实角色及当前阅读，头像始终为非空路径。

> 返回示例

> HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。

```json
{
    "code": 200,
    "data": {
        "userId": 1,
        "nickname": "山间读者",
        "avatarPath": "/uploads/avatars/9c1a2c77.png",
        "gender": "female",
        "email": "reader@example.com",
        "role": "user",
        "currentReading": {
            "book": {
                "bookId": 101,
                "title": "百年孤独",
                "author": "加西亚·马尔克斯",
                "coverPath": "/uploads/covers/6d28c990.png",
                "status": "active"
            },
            "updatedAt": "2026-09-08T08:00:00Z"
        },
        "createdAt": "2026-09-07T12:00:00Z"
    },
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|gender|male|
|gender|female|
|gender|unspecified|
|role|user|
|role|admin|
|status|active|
|status|inactive|
|*anonymous*|null|
|code|400|
|code|401|
|data|null|

<a id="opIdupdateCurrentUser"></a>

## PATCH 修改我的资料

PATCH /api/me

至少提交一个字段，未提交则保留原值。gender：male 男、female 女、unspecified 未设置。头像只能保留或替换，不可清空；更换前调用上传接口。不能修改邮箱、密码和角色。

> Body 请求参数

```json
{
    "nickname": "山间读者",
    "gender": "female",
    "avatarPath": "/uploads/avatars/9c1a2c77.png"
}
```

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|body|body|[UpdateProfileRequest](#schemaupdateprofilerequest)| 是 |none|

> 返回示例

> HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。

```json
{
    "code": 200,
    "data": {
        "userId": 1,
        "nickname": "山间读者",
        "avatarPath": "/uploads/avatars/9c1a2c77.png",
        "gender": "female",
        "email": "reader@example.com",
        "role": "user",
        "currentReading": {
            "book": {
                "bookId": 101,
                "title": "百年孤独",
                "author": "加西亚·马尔克斯",
                "coverPath": "/uploads/covers/6d28c990.png",
                "status": "active"
            },
            "updatedAt": "2026-09-08T08:00:00Z"
        },
        "createdAt": "2026-09-07T12:00:00Z"
    },
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|gender|male|
|gender|female|
|gender|unspecified|
|role|user|
|role|admin|
|status|active|
|status|inactive|
|*anonymous*|null|
|code|400|
|code|401|
|data|null|

<a id="opIdgetUserCard"></a>

## GET 查看用户公开名片

GET /api/users/{userId}

仅返回公开摘要、当前阅读和书友状态，不返回邮箱、性别、私人书单或私人笔记。用户不存在返回 code=400。

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|userId|path|integer| 是 |目标用户 ID，正整数。|

> 返回示例

> HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。

```json
{
    "code": 200,
    "data": {
        "user": {
            "userId": 1,
            "nickname": "山间读者",
            "avatarPath": "/uploads/avatars/9c1a2c77.png"
        },
        "currentReading": {
            "book": {
                "bookId": 101,
                "title": "百年孤独",
                "author": "加西亚·马尔克斯",
                "coverPath": "/uploads/covers/6d28c990.png",
                "status": "active"
            },
            "updatedAt": "2026-09-08T08:00:00Z"
        },
        "isFriend": false
    },
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|status|active|
|status|inactive|
|*anonymous*|null|
|code|400|
|code|401|
|data|null|

# 02 文件上传

<a id="opIduploadImage"></a>

## POST 上传头像或书籍封面

POST /api/uploads

multipart/form-data 上传单张 JPEG、PNG、WebP，不超过 5 MiB。purpose=avatar 时无需 Token，注册前可用；purpose=cover 时必须携带管理员 Token。返回 data.filePath，注册或修改时原样提交为 avatarPath/coverPath。后端检查实际文件及用途，不接受手填站外地址。

> Body 请求参数

```yaml
file: ""
purpose: avatar

```

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|body|body|object| 是 |none|
|» file|body|string(binary)| 是 |文件选择器选中的图片；JPEG、PNG、WebP，最多 5 MiB。|
|» purpose|body|string| 是 |上传用途：avatar（头像，无需 Token）、cover（书籍封面，需要管理员 Token）。|

#### 枚举值

|属性|值|
|---|---|
|» purpose|avatar|
|» purpose|cover|

> 返回示例

> HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。

```json
{
    "code": 200,
    "data": {
        "filePath": "/uploads/avatars/9c1a2c77.png"
    },
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|code|400|
|code|401|
|data|null|

# 03 书籍与书单

<a id="opIdlistBooks"></a>

## GET 搜索上架书籍

GET /api/books

仅查询上架书籍，按 bookId 倒序。

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|pageNum|query|integer| 否 |页码，从 1 开始，默认 1。|
|pageSize|query|integer| 否 |每页条数，1～100，默认 10。|
|keyword|query|string| 否 |搜索书名或作者，去除首尾空白后 1～100 字符；不传则不筛选。|

> 返回示例

> HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。

```json
{
    "code": 200,
    "data": {
        "list": [
            {
                "bookId": 101,
                "title": "百年孤独",
                "author": "加西亚·马尔克斯",
                "coverPath": "/uploads/covers/6d28c990.png",
                "status": "active"
            }
        ],
        "total": 1,
        "pageNum": 1,
        "pageSize": 10
    },
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|status|active|
|status|inactive|
|code|400|
|code|401|
|data|null|

<a id="opIdcreateOrReuseBook"></a>

## POST 创建或复用书籍

POST /api/books

书名和作者转纯文字、统一空白与全半角、去掉外层书名号，按书名加作者查重。已存在返回 reused=true，不覆盖原资料；同名不同作者不合并。新书默认上架，封面等暂为空。复用下架书不自动上架。创建后需另外加入书单。

> Body 请求参数

```json
{
    "title": "百年孤独",
    "author": "加西亚·马尔克斯"
}
```

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|body|body|[CreateBookRequest](#schemacreatebookrequest)| 是 |none|

> 返回示例

> HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。

```json
{
    "code": 200,
    "data": {
        "book": {
            "bookId": 101,
            "title": "百年孤独",
            "author": "加西亚·马尔克斯",
            "coverPath": null,
            "status": "active",
            "isbn": null,
            "intro": null,
            "createdAt": "2026-09-07T12:00:00Z",
            "updatedAt": "2026-09-07T12:00:00Z"
        },
        "reused": false
    },
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|status|active|
|status|inactive|
|code|400|
|code|401|
|data|null|

<a id="opIdgetBook"></a>

## GET 获取书籍详情

GET /api/books/{bookId}

下架书仍可查看，返回 status=inactive；书籍不存在返回 code=400。

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|bookId|path|integer| 是 |书籍 ID，正整数。|

> 返回示例

> HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。

```json
{
    "code": 200,
    "data": {
        "bookId": 101,
        "title": "百年孤独",
        "author": "加西亚·马尔克斯",
        "coverPath": "/uploads/covers/6d28c990.png",
        "status": "active",
        "isbn": "9780307474728",
        "intro": "一部围绕家族、时间与记忆展开的小说。",
        "createdAt": "2026-09-07T12:00:00Z",
        "updatedAt": "2026-09-07T12:00:00Z"
    },
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|status|active|
|status|inactive|
|code|400|
|code|401|
|data|null|

<a id="opIdlistMyBooks"></a>

## GET 获取我的书单

GET /api/me/books

只查询本人书单，包含已有的下架书，按 updatedAt、bookId 倒序。

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|pageNum|query|integer| 否 |页码，从 1 开始，默认 1。|
|pageSize|query|integer| 否 |每页条数，1～100，默认 10。|
|readingStatus|query|string| 否 |wantToRead（想读）、reading（在读）、read（已读）；不传则查询全部。|

#### 枚举值

|属性|值|
|---|---|
|readingStatus|wantToRead|
|readingStatus|reading|
|readingStatus|read|

> 返回示例

> HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。

```json
{
    "code": 200,
    "data": {
        "list": [
            {
                "book": {
                    "bookId": 101,
                    "title": "百年孤独",
                    "author": "加西亚·马尔克斯",
                    "coverPath": "/uploads/covers/6d28c990.png",
                    "status": "active"
                },
                "readingStatus": "reading",
                "createdAt": "2026-09-07T12:00:00Z",
                "updatedAt": "2026-09-07T12:00:00Z"
            }
        ],
        "total": 1,
        "pageNum": 1,
        "pageSize": 10
    },
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|status|active|
|status|inactive|
|readingStatus|wantToRead|
|readingStatus|reading|
|readingStatus|read|
|code|400|
|code|401|
|data|null|

<a id="opIdsetMyBook"></a>

## PUT 加入书单或修改阅读状态

PUT /api/me/books/{bookId}

同一书只有一条书单记录。下架书不能新加入，已有记录可修改。设置 reading 不自动设为当前阅读；当前阅读书改为想读或已读时清空当前阅读。

> Body 请求参数

```json
{
    "readingStatus": "reading"
}
```

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|bookId|path|integer| 是 |书籍 ID，正整数。|
|body|body|[SetUserBookRequest](#schemasetuserbookrequest)| 是 |none|

> 返回示例

> HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。

```json
{
    "code": 200,
    "data": {
        "book": {
            "bookId": 101,
            "title": "百年孤独",
            "author": "加西亚·马尔克斯",
            "coverPath": "/uploads/covers/6d28c990.png",
            "status": "active"
        },
        "readingStatus": "reading",
        "createdAt": "2026-09-07T12:00:00Z",
        "updatedAt": "2026-09-07T12:00:00Z"
    },
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|status|active|
|status|inactive|
|readingStatus|wantToRead|
|readingStatus|reading|
|readingStatus|read|
|code|400|
|code|401|
|data|null|

<a id="opIdremoveMyBook"></a>

## DELETE 移出我的书单

DELETE /api/me/books/{bookId}

无请求体。不删除笔记或系统书籍，移除当前阅读书时清空当前阅读。重复移除成功。

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|bookId|path|integer| 是 |书籍 ID，正整数。|

> 返回示例

> HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。

```json
{
    "code": 200,
    "data": null,
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|data|null|
|code|400|
|code|401|
|data|null|

# 04 文本笔记

<a id="opIdlistMyNotes"></a>

## GET 获取我的笔记

GET /api/me/notes

返回：Page<Note>，本人未删除笔记，按 createdAt、noteId 倒序。

匹配页选择笔记时传 isPublic=true、reviewStatus=approved，直接使用返回的 noteId，无需新增上传或选择接口。

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|pageNum|query|integer| 否 |页码，从 1 开始，默认 1。|
|pageSize|query|integer| 否 |每页条数，1～100，默认 10。|
|bookId|query|integer| 否 |按关联书籍 ID 筛选，不传则不限。|
|isPublic|query|boolean| 否 |true申请公开、false私密，不代表审核结果，不传不限。|
|reviewStatus|query|string| 否 |pending待审核、approved通过、rejected拒绝；不传不限。|

#### 枚举值

|属性|值|
|---|---|
|reviewStatus|pending|
|reviewStatus|approved|
|reviewStatus|rejected|

> 返回示例

> HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。

```json
{
    "code": 200,
    "data": {
        "list": [
            {
                "noteId": 201,
                "author": {
                    "userId": 1,
                    "nickname": "山间读者",
                    "avatarPath": "/uploads/avatars/9c1a2c77.png"
                },
                "book": {
                    "bookId": 101,
                    "title": "百年孤独",
                    "author": "加西亚·马尔克斯",
                    "coverPath": "/uploads/covers/6d28c990.png",
                    "status": "active"
                },
                "content": "读到时间和记忆的段落，想起了童年的夏天。",
                "isPublic": true,
                "createdAt": "2026-09-07T12:00:00Z",
                "updatedAt": "2026-09-08T08:00:00Z",
                "deletedAt": null,
                "likeCount": 0,
                "favoriteCount": 0,
                "commentCount": 0,
                "isLiked": false,
                "isFavorited": false,
                "reviewStatus": "approved",
                "reviewReason": null
            }
        ],
        "total": 1,
        "pageNum": 1,
        "pageSize": 10
    },
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

```json
{
    "code": 200,
    "data": {
        "list": [
            {
                "noteId": 201,
                "author": {
                    "userId": 1,
                    "nickname": "山间读者",
                    "avatarPath": "/uploads/avatars/9c1a2c77.png"
                },
                "book": {
                    "bookId": 101,
                    "title": "百年孤独",
                    "author": "加西亚·马尔克斯",
                    "coverPath": "/uploads/covers/6d28c990.png",
                    "status": "active"
                },
                "content": "读到时间和记忆的段落，想起了童年的夏天。",
                "isPublic": true,
                "createdAt": "2026-09-07T12:00:00Z",
                "updatedAt": "2026-09-08T08:00:00Z",
                "deletedAt": null,
                "likeCount": 0,
                "favoriteCount": 0,
                "commentCount": 0,
                "isLiked": false,
                "isFavorited": false,
                "reviewStatus": "pending",
                "reviewReason": null
            }
        ],
        "total": 1,
        "pageNum": 1,
        "pageSize": 10
    },
    "message": "操作成功"
}
```

```json
{
    "code": 200,
    "data": {
        "list": [
            {
                "noteId": 201,
                "author": {
                    "userId": 1,
                    "nickname": "山间读者",
                    "avatarPath": "/uploads/avatars/9c1a2c77.png"
                },
                "book": {
                    "bookId": 101,
                    "title": "百年孤独",
                    "author": "加西亚·马尔克斯",
                    "coverPath": "/uploads/covers/6d28c990.png",
                    "status": "active"
                },
                "content": "读到时间和记忆的段落，想起了童年的夏天。",
                "isPublic": true,
                "createdAt": "2026-09-07T12:00:00Z",
                "updatedAt": "2026-09-08T08:00:00Z",
                "deletedAt": null,
                "likeCount": 0,
                "favoriteCount": 0,
                "commentCount": 0,
                "isLiked": false,
                "isFavorited": false,
                "reviewStatus": "rejected",
                "reviewReason": "请补充自己的读书感受，删除无关广告。"
            }
        ],
        "total": 1,
        "pageNum": 1,
        "pageSize": 10
    },
    "message": "操作成功"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|status|active|
|status|inactive|
|reviewStatus|pending|
|reviewStatus|approved|
|reviewStatus|rejected|
|reviewStatus|pending|
|reviewStatus|approved|
|reviewReason|null|
|reviewStatus|rejected|
|code|400|
|code|401|
|data|null|

<a id="opIdcreateNote"></a>

## POST 创建文本笔记

POST /api/notes

创建自己的笔记。

返回：Note，reviewStatus=pending、reviewReason=null。保存成功的 code=200 不代表审核通过。所有新笔记都待审核，包括私密笔记和管理员自己的笔记，不能提交 reviewStatus 或 reviewReason。

审核通过且公开后才出现在阅读墙、自动创建漂流瓶并启动 AI 分析；7 天从实际入池开始计算，阅读墙不等待 AI 就绪。待审核、被拒绝或私密的笔记仅本人和管理员可看。

> Body 请求参数

```json
{
    "bookId": 101,
    "content": "读到时间和记忆的段落，想起了童年的夏天。",
    "isPublic": true
}
```

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|body|body|[CreateNoteRequest](#schemacreatenoterequest)| 是 |none|

> 返回示例

> HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。

```json
{
    "code": 200,
    "data": {
        "noteId": 201,
        "author": {
            "userId": 1,
            "nickname": "山间读者",
            "avatarPath": "/uploads/avatars/9c1a2c77.png"
        },
        "book": {
            "bookId": 101,
            "title": "百年孤独",
            "author": "加西亚·马尔克斯",
            "coverPath": "/uploads/covers/6d28c990.png",
            "status": "active"
        },
        "content": "读到时间和记忆的段落，想起了童年的夏天。",
        "isPublic": true,
        "createdAt": "2026-09-07T12:00:00Z",
        "updatedAt": "2026-09-07T12:00:00Z",
        "deletedAt": null,
        "likeCount": 0,
        "favoriteCount": 0,
        "commentCount": 0,
        "isLiked": false,
        "isFavorited": false,
        "reviewStatus": "pending",
        "reviewReason": null
    },
    "message": "笔记已保存，待审核"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|status|active|
|status|inactive|
|reviewStatus|pending|
|reviewStatus|approved|
|reviewStatus|rejected|
|reviewStatus|pending|
|reviewStatus|approved|
|reviewReason|null|
|reviewStatus|rejected|
|code|400|
|code|401|
|data|null|

<a id="opIdgetNote"></a>

## GET 查看笔记详情

GET /api/notes/{noteId}

返回：Note。本人可查看自己所有未删除笔记及审核结果；其他登录用户只可查看审核通过、公开且未删除的笔记；管理员可查看全部笔记和软删除记录。

无权限时 code=400。书友、收藏、评论和漂流获取记录都不能绕过审核与公开权限。本接口只查看笔记，不产生漂流瓶获取记录。

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|noteId|path|integer| 是 |笔记 ID，正整数。|

> 返回示例

> HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。

```json
{
    "code": 200,
    "data": {
        "noteId": 201,
        "author": {
            "userId": 1,
            "nickname": "山间读者",
            "avatarPath": "/uploads/avatars/9c1a2c77.png"
        },
        "book": {
            "bookId": 101,
            "title": "百年孤独",
            "author": "加西亚·马尔克斯",
            "coverPath": "/uploads/covers/6d28c990.png",
            "status": "active"
        },
        "content": "读到时间和记忆的段落，想起了童年的夏天。",
        "isPublic": false,
        "createdAt": "2026-09-07T12:00:00Z",
        "updatedAt": "2026-09-07T12:00:00Z",
        "deletedAt": null,
        "likeCount": 0,
        "favoriteCount": 0,
        "commentCount": 0,
        "isLiked": false,
        "isFavorited": false,
        "reviewStatus": "pending",
        "reviewReason": null
    },
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|status|active|
|status|inactive|
|reviewStatus|pending|
|reviewStatus|approved|
|reviewStatus|rejected|
|reviewStatus|pending|
|reviewStatus|approved|
|reviewReason|null|
|reviewStatus|rejected|
|code|400|
|code|401|
|data|null|

<a id="opIdupdateNote"></a>

## PATCH 修改文本笔记

PATCH /api/notes/{noteId}

作者或管理员修改笔记。

至少提交一个字段，返回 Note。不能改作者、书籍、reviewStatus 或 reviewReason；审核使用管理员专用接口。管理员不能代他人公开私密笔记；已删除笔记不能修改。

- 正文去除首尾空白后实际变化：重置为 pending、reviewReason=null，并撤回全部关联漂流瓶；作者和管理员修改都要重新审核。审核期间从阅读墙、匹配和其他用户收藏列表隐藏，不能继续查看原文、评论或旧漂流副本。
- 重新审核通过且公开：以新正文创建新瓶子，重新计算 7 天；旧瓶保持撤回，不恢复旧获取记录的访问权。原有点赞、收藏、评论仍关联同一 noteId。
- 仅私密改公开：关联书籍需上架；已 approved 时创建新瓶子，pending/rejected 时不展示、不入池，也不改变审核结果。
- 仅公开改私密：不改变审核结果，但撤回全部关联漂流瓶并收回其他用户访问权。
- 同时改正文和公开状态：先按正文变化重置审核，不能因为提交 isPublic=true 直接入池。提交相同正文或重复公开不重新审核、不创建瓶子、不续期。
- 被拒绝后修改正文即可重新提交审核，不提供单独重提接口。漂流瓶过期不改变笔记审核结果，也不自动续期。

> Body 请求参数

```json
{
    "content": "重新读这段文字，我更关注记忆如何改变我们对时间的理解。",
    "isPublic": true
}
```

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|noteId|path|integer| 是 |笔记 ID，正整数。|
|body|body|[UpdateNoteRequest](#schemaupdatenoterequest)| 是 |none|

> 返回示例

> HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。

```json
{
    "code": 200,
    "data": {
        "noteId": 201,
        "author": {
            "userId": 1,
            "nickname": "山间读者",
            "avatarPath": "/uploads/avatars/9c1a2c77.png"
        },
        "book": {
            "bookId": 101,
            "title": "百年孤独",
            "author": "加西亚·马尔克斯",
            "coverPath": "/uploads/covers/6d28c990.png",
            "status": "active"
        },
        "content": "重新读这段文字，我更关注记忆如何改变我们对时间的理解。",
        "isPublic": true,
        "createdAt": "2026-09-07T12:00:00Z",
        "updatedAt": "2026-09-08T08:40:00Z",
        "deletedAt": null,
        "likeCount": 0,
        "favoriteCount": 0,
        "commentCount": 0,
        "isLiked": false,
        "isFavorited": false,
        "reviewStatus": "pending",
        "reviewReason": null
    },
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|status|active|
|status|inactive|
|reviewStatus|pending|
|reviewStatus|approved|
|reviewStatus|rejected|
|reviewStatus|pending|
|reviewStatus|approved|
|reviewReason|null|
|reviewStatus|rejected|
|code|400|
|code|401|
|data|null|

<a id="opIddeleteNote"></a>

## DELETE 软删除笔记

DELETE /api/notes/{noteId}

作者或管理员软删除，无 body，返回 null。重复删除仍成功。

删除后关联漂流瓶全部撤回，其他用户不能通过收藏、评论、通知或已获取记录继续访问。点赞、收藏和评论记录不转移到其他笔记。

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|noteId|path|integer| 是 |笔记 ID，正整数。|

> 返回示例

> HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。

```json
{
    "code": 200,
    "data": null,
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|data|null|
|code|400|
|code|401|
|data|null|

<a id="opIdlistUserPublicNotes"></a>

## GET 获取用户公开笔记

GET /api/users/{userId}/notes

query：分页参数。返回：Page<Note>，仅该用户已审核通过、公开且未删除的笔记，按 createdAt、noteId 倒序。

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|userId|path|integer| 是 |目标用户 ID，正整数。|
|pageNum|query|integer| 否 |页码，从 1 开始，默认 1。|
|pageSize|query|integer| 否 |每页条数，1～100，默认 10。|

> 返回示例

> HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。

```json
{
    "code": 200,
    "data": {
        "list": [
            {
                "noteId": 201,
                "author": {
                    "userId": 1,
                    "nickname": "山间读者",
                    "avatarPath": "/uploads/avatars/9c1a2c77.png"
                },
                "book": {
                    "bookId": 101,
                    "title": "百年孤独",
                    "author": "加西亚·马尔克斯",
                    "coverPath": "/uploads/covers/6d28c990.png",
                    "status": "active"
                },
                "content": "读到时间和记忆的段落，想起了童年的夏天。",
                "isPublic": true,
                "createdAt": "2026-09-07T12:00:00Z",
                "updatedAt": "2026-09-07T12:00:00Z",
                "deletedAt": null,
                "likeCount": 0,
                "favoriteCount": 0,
                "commentCount": 0,
                "isLiked": false,
                "isFavorited": false,
                "reviewStatus": "approved",
                "reviewReason": null
            }
        ],
        "total": 1,
        "pageNum": 1,
        "pageSize": 10
    },
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|status|active|
|status|inactive|
|reviewStatus|pending|
|reviewStatus|approved|
|reviewStatus|rejected|
|reviewStatus|pending|
|reviewStatus|approved|
|reviewReason|null|
|reviewStatus|rejected|
|code|400|
|code|401|
|data|null|

# 05 漂流瓶与匹配

<a id="opIdreplyStickyNote"></a>

## PUT 作者回贴便签

PUT /api/bottle-interactions/{interactionId}/reply

原作者回贴。body：content 必填，1～200 字符。返回 Interaction。

必须已有便签且瓶子未过期、未撤回、原笔记审核通过、公开且未删除。每张便签回贴一次，重复规则同上。成功通知获取者，管理员不可代替作者回贴。

> Body 请求参数

```json
{
    "content": "谢谢你的便签，很高兴遇到同样的感受。"
}
```

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|interactionId|path|integer| 是 |获取记录 ID，正整数。|
|body|body|[StickyRequest](#schemastickyrequest)| 是 |none|

> 返回示例

> HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。

```json
{
    "code": 200,
    "data": {
        "interactionId": 301,
        "bottleId": 501,
        "receiver": {
            "userId": 1,
            "nickname": "山间读者",
            "avatarPath": "/uploads/avatars/9c1a2c77.png"
        },
        "acquiredAt": "2026-09-08T08:05:00Z",
        "stickyText": "我也很喜欢你对记忆的理解。",
        "stickyAt": "2026-09-08T08:10:00Z",
        "replyText": "谢谢你的便签，很高兴遇到同样的感受。",
        "repliedAt": "2026-09-08T08:20:00Z"
    },
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|code|400|
|code|401|
|data|null|

<a id="opIdlistBottleMatches"></a>

## GET 按选中笔记智能匹配漂流瓶

GET /api/bottles/matches

无 body。选择列表复用 `GET /api/me/notes?isPublic=true&reviewStatus=approved`；这里只提交 noteId，不重新上传正文。

返回：Page<MatchItem>。只根据选中的一篇笔记，从整个有效池按内容匹配度降序排序后分页，分数相同按 bottleId 倒序；不是先随机取一批再评分，也不使用其他笔记或私密笔记。

- 来源必须属于本人、审核通过、公开且未删除；来源自己的漂流瓶是否过期、AI 是否就绪不影响选择。来源不符合条件、noteId 缺失或 AI 不可用时 code=400。
- 排除本人、已获取、过期、撤回、原笔记未审核通过或不再公开、已删除、AI 未就绪的候选。
- 不设置最低分门槛，total 为整个合格候选池数量，不是本页长度。翻页时保留同一个来源 noteId；切换笔记或获取后从第 1 页重新查询。
- 合格池为空时 code=200，data.list=[]、total=0；页码超界时 list=[]，保留实际 total。
- 每条都有 matchScore；仅推荐语失败时 recommendation=null，不影响分数与排序。匹配计算失败不返回虚构分数。
- 返回前若来源或候选的审核、公开或有效状态变化，返回 code=400，提示重新匹配，不返回失效内容。
- 查询不会创建获取记录、建立书友关系或发送便签。

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|noteId|query|integer| 是 |本人选中的已审核通过、公开且未删除笔记ID；只传ID，不重新上传正文，不要求其自身瓶子有效或AI就绪。|
|pageNum|query|integer| 否 |页码，从 1 开始，默认 1。|
|pageSize|query|integer| 否 |每页条数，1～100，默认 10。|

> 返回示例

> HTTP始终200；code=200成功，400失败，401需要登录；失败data=null。

```json
{
    "code": 200,
    "data": {
        "list": [
            {
                "bottleId": 501,
                "author": {
                    "userId": 2,
                    "nickname": "晚风读者",
                    "avatarPath": "/uploads/avatars/72d50b11.png"
                },
                "book": {
                    "bookId": 101,
                    "title": "百年孤独",
                    "author": "加西亚·马尔克斯",
                    "coverPath": "/uploads/covers/6d28c990.png",
                    "status": "active"
                },
                "status": "active",
                "aiStatus": "ready",
                "createdAt": "2026-09-08T08:00:00Z",
                "expiresAt": "2026-09-15T08:00:00Z",
                "contentPreview": "我们总在回忆中重新理解时间。",
                "noteId": 202,
                "recommendation": "你们的文字都关注时间与记忆。",
                "matchScore": 86.5
            }
        ],
        "total": 1,
        "pageNum": 1,
        "pageSize": 10
    },
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

```json
{
    "code": 200,
    "data": {
        "list": [],
        "total": 0,
        "pageNum": 1,
        "pageSize": 10
    },
    "message": "暂无匹配"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "请选择本人已审核通过的公开笔记"
}
```

```json
{
    "code": 200,
    "data": {
        "list": [],
        "total": 12,
        "pageNum": 3,
        "pageSize": 10
    },
    "message": "暂无匹配"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP始终200；code=200成功，400失败，401需要登录；失败data=null。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|status|active|
|status|inactive|
|status|active|
|status|expired|
|status|withdrawn|
|aiStatus|pending|
|aiStatus|processing|
|aiStatus|ready|
|aiStatus|failed|
|code|400|
|code|401|
|data|null|

<a id="opIdgetBottle"></a>

## GET 查看漂流瓶详情

GET /api/bottles/{bottleId}

返回 BottleDetail。作者、管理员或合法已获取者可查询，不创建获取记录。

作者和管理员可看撤回历史；其他用户必须持有获取记录，且原笔记仍审核通过、公开、未删除、瓶子未撤回。首次打开使用 acquire 接口。

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|bottleId|path|integer| 是 |漂流瓶 ID，正整数。|

> 返回示例

> HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。

```json
{
    "code": 200,
    "data": {
        "bottleId": 501,
        "author": {
            "userId": 2,
            "nickname": "晚风读者",
            "avatarPath": "/uploads/avatars/72d50b11.png"
        },
        "book": {
            "bookId": 101,
            "title": "百年孤独",
            "author": "加西亚·马尔克斯",
            "coverPath": "/uploads/covers/6d28c990.png",
            "status": "active"
        },
        "status": "active",
        "aiStatus": "ready",
        "createdAt": "2026-09-08T08:00:00Z",
        "expiresAt": "2026-09-15T08:00:00Z",
        "content": "读到时间和记忆的段落，想起了童年的夏天。",
        "topics": [
            "记忆"
        ],
        "keywords": [
            "童年"
        ],
        "emotion": "reflective",
        "aiMessage": null,
        "myInteraction": {
            "interactionId": 301,
            "bottleId": 501,
            "receiver": {
                "userId": 1,
                "nickname": "山间读者",
                "avatarPath": "/uploads/avatars/9c1a2c77.png"
            },
            "acquiredAt": "2026-09-08T08:05:00Z",
            "stickyText": null,
            "stickyAt": null,
            "replyText": null,
            "repliedAt": null
        },
        "noteId": 202
    },
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|status|active|
|status|inactive|
|status|active|
|status|expired|
|status|withdrawn|
|aiStatus|pending|
|aiStatus|processing|
|aiStatus|ready|
|aiStatus|failed|
|emotion|calm|
|emotion|joyful|
|emotion|sad|
|emotion|reflective|
|emotion|mixed|
|emotion|neutral|
|emotion|null|
|*anonymous*|null|
|code|400|
|code|401|
|data|null|

<a id="opIdacquireBottle"></a>

## POST 点开并获取漂流瓶

POST /api/bottles/{bottleId}/acquire

用户主动点开匹配项时调用，无 body。返回 BottleDetail，myInteraction 为本人获取记录。

只能新获取他人的 active、AI ready、原笔记审核通过、公开且未删除的瓶子。不存在、无权访问或不可获取时 code=400。

重复打开不重复生成获取记录。已有记录且瓶子过期时可返回历史；原笔记不再审核通过、转私密、删除或瓶子撤回后不可访问。获取成功后可贴便签或用 interactionId 申请书友。

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|bottleId|path|integer| 是 |漂流瓶ID，正整数。|

> 返回示例

> HTTP始终200；code=200成功，400失败，401需要登录；失败data=null。

```json
{
    "code": 200,
    "data": {
        "bottleId": 501,
        "author": {
            "userId": 2,
            "nickname": "晚风读者",
            "avatarPath": "/uploads/avatars/72d50b11.png"
        },
        "book": {
            "bookId": 101,
            "title": "百年孤独",
            "author": "加西亚·马尔克斯",
            "coverPath": "/uploads/covers/6d28c990.png",
            "status": "active"
        },
        "status": "active",
        "aiStatus": "ready",
        "createdAt": "2026-09-08T08:00:00Z",
        "expiresAt": "2026-09-15T08:00:00Z",
        "content": "读到时间和记忆的段落，想起了童年的夏天。",
        "topics": [
            "记忆"
        ],
        "keywords": [
            "童年"
        ],
        "emotion": "reflective",
        "aiMessage": null,
        "myInteraction": {
            "interactionId": 301,
            "bottleId": 501,
            "receiver": {
                "userId": 1,
                "nickname": "山间读者",
                "avatarPath": "/uploads/avatars/9c1a2c77.png"
            },
            "acquiredAt": "2026-09-08T08:05:00Z",
            "stickyText": null,
            "stickyAt": null,
            "replyText": null,
            "repliedAt": null
        },
        "noteId": 202
    },
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP始终200；code=200成功，400失败，401需要登录；失败data=null。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|status|active|
|status|inactive|
|status|active|
|status|expired|
|status|withdrawn|
|aiStatus|pending|
|aiStatus|processing|
|aiStatus|ready|
|aiStatus|failed|
|emotion|calm|
|emotion|joyful|
|emotion|sad|
|emotion|reflective|
|emotion|mixed|
|emotion|neutral|
|emotion|null|
|*anonymous*|null|
|code|400|
|code|401|
|data|null|

<a id="opIdlistBottleInteractions"></a>

## GET 查看漂流瓶便签列表

GET /api/bottles/{bottleId}/interactions

作者或管理员查询该瓶便签列表。query：通用分页。返回 Page<Interaction>，只包含已贴便签记录，按 stickyAt、interactionId 倒序。

获取者只能通过详情的 myInteraction 看自己的便签，不能看其他获取者的互动。此列表与公开评论列表相互独立。

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|bottleId|path|integer| 是 |漂流瓶 ID，正整数。|
|pageNum|query|integer| 否 |页码，从 1 开始，默认 1。|
|pageSize|query|integer| 否 |每页条数，1～100，默认 10。|

> 返回示例

> HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。

```json
{
    "code": 200,
    "data": {
        "list": [
            {
                "interactionId": 301,
                "bottleId": 501,
                "receiver": {
                    "userId": 1,
                    "nickname": "山间读者",
                    "avatarPath": "/uploads/avatars/9c1a2c77.png"
                },
                "acquiredAt": "2026-09-08T08:05:00Z",
                "stickyText": "我也很喜欢你对记忆的理解。",
                "stickyAt": "2026-09-08T08:10:00Z",
                "replyText": null,
                "repliedAt": null
            }
        ],
        "total": 1,
        "pageNum": 1,
        "pageSize": 10
    },
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|code|400|
|code|401|
|data|null|

<a id="opIdcreateStickyNote"></a>

## PUT 给漂流瓶贴便签

PUT /api/bottles/{bottleId}/sticky-note

获取者给作者贴一张便签。

content 必填，去除首尾空白后 1～200 字符。返回 Interaction。必须已获取且瓶子有效、原笔记审核通过、公开且未删除。

同一获取记录只能贴一次，相同文本重复返回原记录，不同文本再次提交时 code=400。成功通知作者，便签不会显示在公开评论区。

> Body 请求参数

```json
{
    "content": "我也很喜欢你对记忆的理解。"
}
```

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|bottleId|path|integer| 是 |漂流瓶 ID，正整数。|
|body|body|[StickyRequest](#schemastickyrequest)| 是 |none|

> 返回示例

> HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。

```json
{
    "code": 200,
    "data": {
        "interactionId": 301,
        "bottleId": 501,
        "receiver": {
            "userId": 1,
            "nickname": "山间读者",
            "avatarPath": "/uploads/avatars/9c1a2c77.png"
        },
        "acquiredAt": "2026-09-08T08:05:00Z",
        "stickyText": "我也很喜欢你对记忆的理解。",
        "stickyAt": "2026-09-08T08:10:00Z",
        "replyText": null,
        "repliedAt": null
    },
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|code|400|
|code|401|
|data|null|

<a id="opIdlistMyBottles"></a>

## GET 查询我的漂流记录

GET /api/me/bottles

返回 Page<BottleSummary>。sent 按入池时间倒序，received 按获取时间倒序，同时间按 bottleId 倒序。received 不返回原笔记未审核通过、已私密、已删除或瓶子已撤回的记录。

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|pageNum|query|integer| 否 |页码，从 1 开始，默认 1。|
|pageSize|query|integer| 否 |每页条数，1～100，默认 10。|
|direction|query|string| 是 |sent本人审核通过且公开后产生的漂流记录；received已获取且原笔记仍审核通过、公开未删除、瓶子未撤回的记录。|
|status|query|string| 否 |active（有效）、expired（过期）、withdrawn（撤回）；不传不限。|

#### 枚举值

|属性|值|
|---|---|
|direction|sent|
|direction|received|
|status|active|
|status|expired|
|status|withdrawn|

> 返回示例

> HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。

```json
{
    "code": 200,
    "data": {
        "list": [
            {
                "bottleId": 501,
                "author": {
                    "userId": 2,
                    "nickname": "晚风读者",
                    "avatarPath": "/uploads/avatars/72d50b11.png"
                },
                "book": {
                    "bookId": 101,
                    "title": "百年孤独",
                    "author": "加西亚·马尔克斯",
                    "coverPath": "/uploads/covers/6d28c990.png",
                    "status": "active"
                },
                "status": "active",
                "aiStatus": "ready",
                "createdAt": "2026-09-08T08:00:00Z",
                "expiresAt": "2026-09-15T08:00:00Z",
                "contentPreview": "我们总在回忆中重新理解时间。",
                "noteId": 202
            }
        ],
        "total": 1,
        "pageNum": 1,
        "pageSize": 10
    },
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|status|active|
|status|inactive|
|status|active|
|status|expired|
|status|withdrawn|
|aiStatus|pending|
|aiStatus|processing|
|aiStatus|ready|
|aiStatus|failed|
|code|400|
|code|401|
|data|null|

# 06 书友关系

<a id="opIdcreateFriendRequest"></a>

## POST 发起书友申请

POST /api/friend-requests

interactionId 必填，来自主动点开后 acquire 接口返回的 myInteraction.interactionId。获取者申请作者，或作者申请该记录的获取者；无需先贴便签。返回：FriendRequest。只浏览匹配列表还没有获取记录，不能直接申请。

- 已是书友时 code=400。
- 同方向已有待处理申请时返回原申请；反方向已有待处理申请时 code=400，先处理收到的申请。
- 已过期但未撤回且原笔记仍审核通过、公开、未删除的瓶子仍可发起申请。原笔记未审核通过、私密、已删除、瓶子撤回或记录无权使用时 code=400。
- 新申请会通知接收者。

> Body 请求参数

```json
{
    "interactionId": 301
}
```

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|body|body|[CreateFriendRequest](#schemacreatefriendrequest)| 是 |none|

> 返回示例

> HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。

```json
{
    "code": 200,
    "data": {
        "requestId": 601,
        "requester": {
            "userId": 1,
            "nickname": "山间读者",
            "avatarPath": "/uploads/avatars/9c1a2c77.png"
        },
        "receiver": {
            "userId": 2,
            "nickname": "晚风读者",
            "avatarPath": "/uploads/avatars/72d50b11.png"
        },
        "bottleId": 501,
        "status": "pending",
        "createdAt": "2026-09-08T08:25:00Z",
        "handledAt": null
    },
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|status|pending|
|status|accepted|
|status|rejected|
|code|400|
|code|401|
|data|null|

<a id="opIdhandleFriendRequest"></a>

## PATCH 接受或拒绝书友申请

PATCH /api/friend-requests/{requestId}

仅接收者可操作。

status 必填，只能 accepted（接受）或 rejected（拒绝）。返回：FriendRequest。

接受后建立书友关系并通知申请者，拒绝则不建立关系。重复相同处理返回原结果，不能更改已处理结果。笔记后续重新审核、转私密或删除，以及瓶子过期或撤回，不影响处理已有申请，也不解除已建立的书友关系；但不能因此继续读取失效内容。

> Body 请求参数

```json
{
    "status": "accepted"
}
```

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|requestId|path|integer| 是 |书友申请 ID，正整数。|
|body|body|[HandleFriendRequest](#schemahandlefriendrequest)| 是 |none|

> 返回示例

> HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。

```json
{
    "code": 200,
    "data": {
        "requestId": 601,
        "requester": {
            "userId": 1,
            "nickname": "山间读者",
            "avatarPath": "/uploads/avatars/9c1a2c77.png"
        },
        "receiver": {
            "userId": 2,
            "nickname": "晚风读者",
            "avatarPath": "/uploads/avatars/72d50b11.png"
        },
        "bottleId": 501,
        "status": "accepted",
        "createdAt": "2026-09-08T08:25:00Z",
        "handledAt": "2026-09-08T08:30:00Z"
    },
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|status|pending|
|status|accepted|
|status|rejected|
|code|400|
|code|401|
|data|null|

<a id="opIdlistMyFriendRequests"></a>

## GET 查询我的书友申请

GET /api/me/friend-requests

返回：Page<FriendRequest>，按 createdAt、requestId 倒序。

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|pageNum|query|integer| 否 |页码，从 1 开始，默认 1。|
|pageSize|query|integer| 否 |每页条数，1～100，默认 10。|
|direction|query|string| 是 |sent（已发送）、received（已收到），必填。|
|status|query|string| 否 |pending（待处理）、accepted（已接受）、rejected（已拒绝）；不传不限。|
|requestId|query|integer| 否 |按通知中的申请 ID 精确筛选，仅限本人申请。|

#### 枚举值

|属性|值|
|---|---|
|direction|sent|
|direction|received|
|status|pending|
|status|accepted|
|status|rejected|

> 返回示例

> HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。

```json
{
    "code": 200,
    "data": {
        "list": [
            {
                "requestId": 601,
                "requester": {
                    "userId": 1,
                    "nickname": "山间读者",
                    "avatarPath": "/uploads/avatars/9c1a2c77.png"
                },
                "receiver": {
                    "userId": 2,
                    "nickname": "晚风读者",
                    "avatarPath": "/uploads/avatars/72d50b11.png"
                },
                "bottleId": 501,
                "status": "pending",
                "createdAt": "2026-09-08T08:25:00Z",
                "handledAt": null
            }
        ],
        "total": 1,
        "pageNum": 1,
        "pageSize": 10
    },
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|status|pending|
|status|accepted|
|status|rejected|
|code|400|
|code|401|
|data|null|

<a id="opIdlistMyFriends"></a>

## GET 查询我的书友

GET /api/me/friends

query：分页参数。返回：Page<Friend>，按 becameFriendsAt、对方 userId 倒序。

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|pageNum|query|integer| 否 |页码，从 1 开始，默认 1。|
|pageSize|query|integer| 否 |每页条数，1～100，默认 10。|

> 返回示例

> HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。

```json
{
    "code": 200,
    "data": {
        "list": [
            {
                "user": {
                    "userId": 1,
                    "nickname": "山间读者",
                    "avatarPath": "/uploads/avatars/9c1a2c77.png"
                },
                "becameFriendsAt": "2026-09-07T12:00:00Z"
            }
        ],
        "total": 1,
        "pageNum": 1,
        "pageSize": 10
    },
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|code|400|
|code|401|
|data|null|

<a id="opIdremoveFriend"></a>

## DELETE 解除书友关系

DELETE /api/me/friends/{userId}

解除与指定用户的书友关系，无 body。返回：null。任一方可解除，重复解除仍成功。

解除后需要重新申请才能再次成为书友，不能通过重复接受旧申请恢复关系。

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|userId|path|integer| 是 |目标用户 ID，正整数。|

> 返回示例

> HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。

```json
{
    "code": 200,
    "data": null,
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|data|null|
|code|400|
|code|401|
|data|null|

# 07 阅读墙与通知

<a id="opIdlistMyNotifications"></a>

## GET 查询我的通知

GET /api/me/notifications

query：分页参数；可选 isRead 布尔值，true 查询已读、false 查询未读，不传则查询全部通知。

返回：Page<Notification>，data 额外包含 unreadCount: integer，表示本人全部未读数量。按 createdAt、notificationId 倒序。

通知不包含私人正文，点击后查询对应内容；申请使用 requestId 筛选申请列表。内容已撤回时 code=400。

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|pageNum|query|integer| 否 |页码，从 1 开始，默认 1。|
|pageSize|query|integer| 否 |每页条数，1～100，默认 10。|
|isRead|query|boolean| 否 |true（已读）、false（未读），不传查询全部。|

> 返回示例

> HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。

```json
{
    "code": 200,
    "data": {
        "list": [
            {
                "notificationId": 401,
                "type": "stickyNote",
                "actor": {
                    "userId": 1,
                    "nickname": "山间读者",
                    "avatarPath": "/uploads/avatars/9c1a2c77.png"
                },
                "content": "收到一张便签",
                "resourceType": "bottle",
                "resourceId": 501,
                "isRead": false,
                "createdAt": "2026-09-07T12:00:00Z"
            }
        ],
        "total": 1,
        "pageNum": 1,
        "pageSize": 10,
        "unreadCount": 1
    },
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|type|stickyNote|
|type|stickyReply|
|type|friendRequest|
|type|friendAccepted|
|resourceType|bottle|
|resourceType|friendRequest|
|code|400|
|code|401|
|data|null|

<a id="opIdreadNotifications"></a>

## PATCH 标记通知已读

PATCH /api/me/notifications

标记已读。

notificationIds 必填，1～100 个不重复的正整数。返回：null。只允许本人通知，存在他人或无效 ID 时整批返回 code=400；已读记录再次提交仍成功。

> Body 请求参数

```json
{
    "notificationIds": [
        401,
        402
    ]
}
```

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|body|body|[ReadNotificationsRequest](#schemareadnotificationsrequest)| 是 |none|

> 返回示例

> HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。

```json
{
    "code": 200,
    "data": null,
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|data|null|
|code|400|
|code|401|
|data|null|

<a id="opIdsetCurrentReading"></a>

## PUT 设置或停止当前阅读

PUT /api/me/reading

设置当前阅读书籍。

bookId 必填，传 null 表示停止阅读。返回：ReadingState。

书籍需要已上架、已加入本人书单且状态为 reading，否则 code=400。一次只能设置一本，不自动修改书单。查询当前阅读使用 `/api/me`。

> Body 请求参数

```json
{
    "bookId": 101
}
```

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|body|body|[SetReadingRequest](#schemasetreadingrequest)| 是 |none|

> 返回示例

> HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。

```json
{
    "code": 200,
    "data": {
        "book": {
            "bookId": 101,
            "title": "百年孤独",
            "author": "加西亚·马尔克斯",
            "coverPath": "/uploads/covers/6d28c990.png",
            "status": "active"
        },
        "updatedAt": "2026-09-08T08:00:00Z"
    },
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|status|active|
|status|inactive|
|*anonymous*|null|
|code|400|
|code|401|
|data|null|

<a id="opIdlistWallNotes"></a>

## GET 查看最新公开笔记

GET /api/wall/notes

query：分页参数。返回：Page<Note>，按 createdAt、noteId 倒序。

仅展示全站审核通过、公开且未删除的笔记，作者不必在线。发布后待审核，不立即展示；审核通过且公开后展示，不等待 AI 就绪。正文修改后重新待审核，会从墙上隐藏。漂流瓶入池 7 天后，仍符合展示条件的原笔记可以继续显示。

每条 Note 自带 likeCount、favoriteCount、commentCount、isLiked、isFavorited。点赞、收藏和评论使用 noteId，接口见 `09-点赞收藏与评论.md`。操作后刷新该条及评论列表，不增加互动数量的实时广播。

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|pageNum|query|integer| 否 |页码，从 1 开始，默认 1。|
|pageSize|query|integer| 否 |每页条数，1～100，默认 10。|

> 返回示例

> HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。

```json
{
    "code": 200,
    "data": {
        "list": [
            {
                "noteId": 201,
                "author": {
                    "userId": 1,
                    "nickname": "山间读者",
                    "avatarPath": "/uploads/avatars/9c1a2c77.png"
                },
                "book": {
                    "bookId": 101,
                    "title": "百年孤独",
                    "author": "加西亚·马尔克斯",
                    "coverPath": "/uploads/covers/6d28c990.png",
                    "status": "active"
                },
                "content": "读到时间和记忆的段落，想起了童年的夏天。",
                "isPublic": true,
                "createdAt": "2026-09-07T12:00:00Z",
                "updatedAt": "2026-09-07T12:00:00Z",
                "deletedAt": null,
                "likeCount": 0,
                "favoriteCount": 0,
                "commentCount": 0,
                "isLiked": false,
                "isFavorited": false,
                "reviewStatus": "approved",
                "reviewReason": null
            }
        ],
        "total": 1,
        "pageNum": 1,
        "pageSize": 10
    },
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|status|active|
|status|inactive|
|reviewStatus|pending|
|reviewStatus|approved|
|reviewStatus|rejected|
|reviewStatus|pending|
|reviewStatus|approved|
|reviewReason|null|
|reviewStatus|rejected|
|code|400|
|code|401|
|data|null|

<a id="opIdlistOnlineReaders"></a>

## GET 查看在线阅读墙

GET /api/wall/readers

query：分页参数。返回：Page<OnlineReader>，按 userId 倒序。

在线状态以服务端 WebSocket 连接状态为准。

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|pageNum|query|integer| 否 |页码，从 1 开始，默认 1。|
|pageSize|query|integer| 否 |每页条数，1～100，默认 10。|

> 返回示例

> HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。

```json
{
    "code": 200,
    "data": {
        "list": [
            {
                "user": {
                    "userId": 1,
                    "nickname": "山间读者",
                    "avatarPath": "/uploads/avatars/9c1a2c77.png"
                },
                "currentReading": {
                    "book": {
                        "bookId": 101,
                        "title": "百年孤独",
                        "author": "加西亚·马尔克斯",
                        "coverPath": "/uploads/covers/6d28c990.png",
                        "status": "active"
                    },
                    "updatedAt": "2026-09-08T08:00:00Z"
                }
            }
        ],
        "total": 1,
        "pageNum": 1,
        "pageSize": 10
    },
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|status|active|
|status|inactive|
|*anonymous*|null|
|code|400|
|code|401|
|data|null|

# 08 后台管理

<a id="opIdadminListBooks"></a>

## GET 管理书籍列表

GET /api/admin/books

仅管理员 Token。

返回：Page<Book>，按 bookId 倒序，包含下架书籍。

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|pageNum|query|integer| 否 |页码，从 1 开始，默认 1。|
|pageSize|query|integer| 否 |每页条数，1～100，默认 10。|
|keyword|query|string| 否 |搜索书名或作者，去除首尾空白后 1～100 字符；不传则不筛选。|
|status|query|string| 否 |active（上架）、inactive（下架），不传查询全部。|
|needsCompletion|query|boolean| 否 |true：缺封面或简介；false：两者均已完善；不传不限。|

#### 枚举值

|属性|值|
|---|---|
|status|active|
|status|inactive|

> 返回示例

> HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。

```json
{
    "code": 200,
    "data": {
        "list": [
            {
                "bookId": 101,
                "title": "百年孤独",
                "author": "加西亚·马尔克斯",
                "coverPath": "/uploads/covers/6d28c990.png",
                "status": "active",
                "isbn": null,
                "intro": null,
                "createdAt": "2026-09-07T12:00:00Z",
                "updatedAt": "2026-09-07T12:00:00Z"
            }
        ],
        "total": 1,
        "pageNum": 1,
        "pageSize": 10
    },
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|status|active|
|status|inactive|
|code|400|
|code|401|
|data|null|

<a id="opIdadminUpdateBook"></a>

## PATCH 修改书籍或上下架

PATCH /api/admin/books/{bookId}

仅管理员 Token。

至少提交一个字段，返回：Book。书名和作者按创建时的规则查重；与其他书重复或 ISBN 重复时 code=400。

更换封面先调用 `POST /api/uploads`，上传 file 并设置 purpose=cover，再将返回的 data.filePath 填入 coverPath。不接受空字符串、头像路径或站外图片地址。

请求示例：

下架提交 status=inactive，重新上架提交 status=active。下架不删除已有书单、笔记和漂流瓶，但不能新增相关内容。

> Body 请求参数

```json
{
    "title": "百年孤独",
    "author": "加西亚·马尔克斯",
    "isbn": "9780307474728",
    "coverPath": "/uploads/covers/6d28c990.png",
    "intro": "一部围绕家族、时间与记忆展开的小说。",
    "status": "active"
}
```

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|bookId|path|integer| 是 |书籍 ID，正整数。|
|body|body|[UpdateBookRequest](#schemaupdatebookrequest)| 是 |none|

> 返回示例

> HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。

```json
{
    "code": 200,
    "data": {
        "bookId": 101,
        "title": "百年孤独",
        "author": "加西亚·马尔克斯",
        "coverPath": "/uploads/covers/6d28c990.png",
        "status": "active",
        "isbn": null,
        "intro": null,
        "createdAt": "2026-09-07T12:00:00Z",
        "updatedAt": "2026-09-07T12:00:00Z"
    },
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|status|active|
|status|inactive|
|code|400|
|code|401|
|data|null|

<a id="opIdadminListNotes"></a>

## GET 管理笔记列表

GET /api/admin/notes

仅管理员 Token。

返回：Page<Note>，按 createdAt、noteId 倒序。

审核列表复用此接口，传 reviewStatus=pending；笔记详情仍使用 `GET /api/notes/{noteId}`。

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|pageNum|query|integer| 否 |页码，从 1 开始，默认 1。|
|pageSize|query|integer| 否 |每页条数，1～100，默认 10。|
|authorId|query|integer| 否 |按作者用户 ID 筛选，不传不限。|
|bookId|query|integer| 否 |按书籍 ID 筛选，不传不限。|
|isPublic|query|boolean| 否 |true申请公开、false私密，不代表审核结果，不传不限。|
|includeDeleted|query|boolean| 否 |true 包含软删除记录，false 仅未删除；默认 false。|
|reviewStatus|query|string| 否 |pending待审核、approved通过、rejected拒绝；不传不限。|

#### 枚举值

|属性|值|
|---|---|
|reviewStatus|pending|
|reviewStatus|approved|
|reviewStatus|rejected|

> 返回示例

> HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。

```json
{
    "code": 200,
    "data": {
        "list": [
            {
                "noteId": 201,
                "author": {
                    "userId": 1,
                    "nickname": "山间读者",
                    "avatarPath": "/uploads/avatars/9c1a2c77.png"
                },
                "book": {
                    "bookId": 101,
                    "title": "百年孤独",
                    "author": "加西亚·马尔克斯",
                    "coverPath": "/uploads/covers/6d28c990.png",
                    "status": "active"
                },
                "content": "读到时间和记忆的段落，想起了童年的夏天。",
                "isPublic": false,
                "createdAt": "2026-09-07T12:00:00Z",
                "updatedAt": "2026-09-07T12:00:00Z",
                "deletedAt": null,
                "likeCount": 0,
                "favoriteCount": 0,
                "commentCount": 0,
                "isLiked": false,
                "isFavorited": false,
                "reviewStatus": "pending",
                "reviewReason": null
            }
        ],
        "total": 1,
        "pageNum": 1,
        "pageSize": 10
    },
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|status|active|
|status|inactive|
|reviewStatus|pending|
|reviewStatus|approved|
|reviewStatus|rejected|
|reviewStatus|pending|
|reviewStatus|approved|
|reviewReason|null|
|reviewStatus|rejected|
|code|400|
|code|401|
|data|null|

<a id="opIdadminReviewNote"></a>

## PATCH 审核笔记

PATCH /api/admin/notes/{noteId}/review

仅管理员 Token。

审核一篇待审核笔记，不修改正文或公开状态。

返回 Note，reviewStatus、reviewReason、updatedAt 更新为本次结果。

- 仅管理员可以操作，普通用户 code=400；已删除或不存在的笔记不可审核。
- 只处理 pending 笔记。已处理后提交相同结果及相同原因返回现有 Note，不再次入池；不同结果或原因 code=400。修改正文后会重新待审核。
- approved 且 isPublic=true：关联书籍需上架，自动创建新瓶并启动 AI，阅读墙立即显示；7 天从实际入池开始计算。AI 处理失败不改变审核结果。
- approved 且 isPublic=false：仍为私密，不展示、不入池。拒绝时同样不展示、不入池，作者可以查看原因并修改后重审。
- 新建或修改正文不会因为操作者是管理员而跳过审核；只改变公开状态也不会改变审核结果。

> Body 请求参数

```json
{
    "reviewStatus": "approved"
}
```

```json
{
    "reviewStatus": "rejected",
    "reviewReason": "请补充自己的读书感受，删除无关广告。"
}
```

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|noteId|path|integer| 是 |笔记 ID，正整数。|
|body|body|[ReviewNoteRequest](#schemareviewnoterequest)| 是 |none|

> 返回示例

> HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。

```json
{
    "code": 200,
    "data": {
        "noteId": 201,
        "author": {
            "userId": 1,
            "nickname": "山间读者",
            "avatarPath": "/uploads/avatars/9c1a2c77.png"
        },
        "book": {
            "bookId": 101,
            "title": "百年孤独",
            "author": "加西亚·马尔克斯",
            "coverPath": "/uploads/covers/6d28c990.png",
            "status": "active"
        },
        "content": "读到时间和记忆的段落，想起了童年的夏天。",
        "isPublic": true,
        "createdAt": "2026-09-07T12:00:00Z",
        "updatedAt": "2026-09-08T08:00:00Z",
        "deletedAt": null,
        "likeCount": 0,
        "favoriteCount": 0,
        "commentCount": 0,
        "isLiked": false,
        "isFavorited": false,
        "reviewStatus": "approved",
        "reviewReason": null
    },
    "message": "审核通过"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

```json
{
    "code": 200,
    "data": {
        "noteId": 201,
        "author": {
            "userId": 1,
            "nickname": "山间读者",
            "avatarPath": "/uploads/avatars/9c1a2c77.png"
        },
        "book": {
            "bookId": 101,
            "title": "百年孤独",
            "author": "加西亚·马尔克斯",
            "coverPath": "/uploads/covers/6d28c990.png",
            "status": "active"
        },
        "content": "读到时间和记忆的段落，想起了童年的夏天。",
        "isPublic": true,
        "createdAt": "2026-09-07T12:00:00Z",
        "updatedAt": "2026-09-08T08:00:00Z",
        "deletedAt": null,
        "likeCount": 0,
        "favoriteCount": 0,
        "commentCount": 0,
        "isLiked": false,
        "isFavorited": false,
        "reviewStatus": "rejected",
        "reviewReason": "请补充自己的读书感受，删除无关广告。"
    },
    "message": "审核已拒绝"
}
```

```json
{
    "code": 200,
    "data": {
        "noteId": 201,
        "author": {
            "userId": 1,
            "nickname": "山间读者",
            "avatarPath": "/uploads/avatars/9c1a2c77.png"
        },
        "book": {
            "bookId": 101,
            "title": "百年孤独",
            "author": "加西亚·马尔克斯",
            "coverPath": "/uploads/covers/6d28c990.png",
            "status": "active"
        },
        "content": "读到时间和记忆的段落，想起了童年的夏天。",
        "isPublic": false,
        "createdAt": "2026-09-07T12:00:00Z",
        "updatedAt": "2026-09-08T08:00:00Z",
        "deletedAt": null,
        "likeCount": 0,
        "favoriteCount": 0,
        "commentCount": 0,
        "isLiked": false,
        "isFavorited": false,
        "reviewStatus": "approved",
        "reviewReason": null
    },
    "message": "审核通过"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP 始终为 200。code=200 成功，400 操作失败，401 需要登录；失败时 data=null，提示 message。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|status|active|
|status|inactive|
|reviewStatus|pending|
|reviewStatus|approved|
|reviewStatus|rejected|
|reviewStatus|pending|
|reviewStatus|approved|
|reviewReason|null|
|reviewStatus|rejected|
|code|400|
|code|401|
|data|null|

# 09 点赞收藏与评论

<a id="opIddeleteComment"></a>

## DELETE 删除评论

DELETE /api/comments/{commentId}

删除评论，无 body，返回 null。评论作者、笔记作者或管理员可删除；其他人 code=400。重复删除已删除评论仍成功。

即使原笔记重新待审核、被拒绝、已私密或删除，评论作者仍可删除自己的评论，但不能通过此操作获取原文或评论列表。删除后 commentCount 减少，不影响漂流便签。

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|commentId|path|integer| 是 |评论ID，正整数。|

> 返回示例

> HTTP始终200；code=200成功，400失败，401需要登录；失败data=null。

```json
{
    "code": 200,
    "data": null,
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP始终200；code=200成功，400失败，401需要登录；失败data=null。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|data|null|
|code|400|
|code|401|
|data|null|

<a id="opIdlistMyFavorites"></a>

## GET 我的收藏

GET /api/me/favorites

query：通用分页。返回 Page<Note>，按本人收藏时间倒序，同时间按 noteId 倒序。

只显示本人收藏且当前仍审核通过、公开、未删除的笔记，total 也按可见内容计算。重新待审核、被拒绝或转私密后隐藏，恢复通过且公开后未取消的收藏可重新显示；原有点赞、收藏、评论仍关联原 noteId。没有其他用户的收藏列表接口。

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|pageNum|query|integer| 否 |页码，从 1 开始，默认 1。|
|pageSize|query|integer| 否 |每页条数，1～100，默认 10。|

> 返回示例

> HTTP始终200；code=200成功，400失败，401需要登录；失败data=null。

```json
{
    "code": 200,
    "data": {
        "list": [
            {
                "noteId": 201,
                "author": {
                    "userId": 1,
                    "nickname": "山间读者",
                    "avatarPath": "/uploads/avatars/9c1a2c77.png"
                },
                "book": {
                    "bookId": 101,
                    "title": "百年孤独",
                    "author": "加西亚·马尔克斯",
                    "coverPath": "/uploads/covers/6d28c990.png",
                    "status": "active"
                },
                "content": "读到时间和记忆的段落，想起了童年的夏天。",
                "isPublic": true,
                "createdAt": "2026-09-07T12:00:00Z",
                "updatedAt": "2026-09-07T12:00:00Z",
                "deletedAt": null,
                "likeCount": 0,
                "favoriteCount": 1,
                "commentCount": 0,
                "isLiked": false,
                "isFavorited": true,
                "reviewStatus": "approved",
                "reviewReason": null
            }
        ],
        "total": 1,
        "pageNum": 1,
        "pageSize": 10
    },
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP始终200；code=200成功，400失败，401需要登录；失败data=null。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|status|active|
|status|inactive|
|reviewStatus|pending|
|reviewStatus|approved|
|reviewStatus|rejected|
|reviewStatus|pending|
|reviewStatus|approved|
|reviewReason|null|
|reviewStatus|rejected|
|code|400|
|code|401|
|data|null|

<a id="opIdlistNoteComments"></a>

## GET 查询公开评论

GET /api/notes/{noteId}/comments

query：通用分页。返回 Page<Comment>，按 createdAt、commentId 倒序，只返回未删除评论。

审核通过、公开且未删除笔记的评论对所有登录用户可见；重新待审核、被拒绝或转私密后仅笔记作者和管理员可查，历史评论者不能绕过审核和公开权限。原笔记删除后仅管理员可查；其他情况 code=400。

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|noteId|path|integer| 是 |原笔记ID，正整数。|
|pageNum|query|integer| 否 |页码，从 1 开始，默认 1。|
|pageSize|query|integer| 否 |每页条数，1～100，默认 10。|

> 返回示例

> HTTP始终200；code=200成功，400失败，401需要登录；失败data=null。

```json
{
    "code": 200,
    "data": {
        "list": [
            {
                "commentId": 701,
                "noteId": 201,
                "author": {
                    "userId": 1,
                    "nickname": "山间读者",
                    "avatarPath": "/uploads/avatars/9c1a2c77.png"
                },
                "content": "这段关于时间的理解很有意思。",
                "createdAt": "2026-09-08T08:00:00Z",
                "canDelete": true
            }
        ],
        "total": 1,
        "pageNum": 1,
        "pageSize": 10
    },
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP始终200；code=200成功，400失败，401需要登录；失败data=null。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|code|400|
|code|401|
|data|null|

<a id="opIdcreateNoteComment"></a>

## POST 发表评论

POST /api/notes/{noteId}/comments

发布评论。

content 必填，纯文本，去除首尾空白后 1～500 字符。返回 Comment。仅可评论审核通过、公开且未删除笔记；允许同一用户发表多条评论，不支持回复、楼中楼或评论点赞。

成功后刷新评论列表及笔记 commentCount。不增加评论专用通知或实时广播。

> Body 请求参数

```json
{
    "content": "这段关于时间的理解很有意思。"
}
```

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|noteId|path|integer| 是 |原笔记ID，正整数。|
|body|body|[CreateCommentRequest](#schemacreatecommentrequest)| 是 |none|

> 返回示例

> HTTP始终200；code=200成功，400失败，401需要登录；失败data=null。

```json
{
    "code": 200,
    "data": {
        "commentId": 701,
        "noteId": 201,
        "author": {
            "userId": 1,
            "nickname": "山间读者",
            "avatarPath": "/uploads/avatars/9c1a2c77.png"
        },
        "content": "这段关于时间的理解很有意思。",
        "createdAt": "2026-09-08T08:00:00Z",
        "canDelete": true
    },
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP始终200；code=200成功，400失败，401需要登录；失败data=null。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|code|400|
|code|401|
|data|null|

<a id="opIdfavoriteNote"></a>

## PUT 收藏笔记

PUT /api/notes/{noteId}/favorite

收藏，无 body，返回 NoteSocial。同一人对同一笔记只保留一条收藏，重复提交不增加数量。

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|noteId|path|integer| 是 |原笔记ID，正整数。|

> 返回示例

> HTTP始终200；code=200成功，400失败，401需要登录；失败data=null。

```json
{
    "code": 200,
    "data": {
        "noteId": 201,
        "likeCount": 0,
        "favoriteCount": 1,
        "commentCount": 0,
        "isLiked": false,
        "isFavorited": true
    },
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP始终200；code=200成功，400失败，401需要登录；失败data=null。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|code|400|
|code|401|
|data|null|

<a id="opIdunfavoriteNote"></a>

## DELETE 取消收藏

DELETE /api/notes/{noteId}/favorite

取消收藏，无 body。笔记仍审核通过、公开且未删除时返回 NoteSocial；其他情况仅清除本人收藏并返回 null。不曾收藏或已取消也成功。

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|noteId|path|integer| 是 |原笔记ID，正整数。|

> 返回示例

> HTTP始终200；code=200成功，400失败，401需要登录；失败data=null。

```json
{
    "code": 200,
    "data": {
        "noteId": 201,
        "likeCount": 0,
        "favoriteCount": 0,
        "commentCount": 0,
        "isLiked": false,
        "isFavorited": false
    },
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

```json
{
    "code": 200,
    "data": null,
    "message": "已取消"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP始终200；code=200成功，400失败，401需要登录；失败data=null。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|*anonymous*|null|
|code|400|
|code|401|
|data|null|

<a id="opIdlikeNote"></a>

## PUT 点赞笔记

PUT /api/notes/{noteId}/like

点赞，无 body，返回 NoteSocial。每人对同一笔记只点一次，重复提交不增加数量；成功后前端用返回值更新按钮与计数。

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|noteId|path|integer| 是 |原笔记ID，正整数。|

> 返回示例

> HTTP始终200；code=200成功，400失败，401需要登录；失败data=null。

```json
{
    "code": 200,
    "data": {
        "noteId": 201,
        "likeCount": 1,
        "favoriteCount": 0,
        "commentCount": 0,
        "isLiked": true,
        "isFavorited": false
    },
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP始终200；code=200成功，400失败，401需要登录；失败data=null。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|code|400|
|code|401|
|data|null|

<a id="opIdunlikeNote"></a>

## DELETE 取消点赞

DELETE /api/notes/{noteId}/like

取消点赞，无 body。笔记仍审核通过、公开且未删除时返回 NoteSocial；其他情况仅清除本人点赞并返回 null，不返回计数。不曾点赞或已取消也成功。

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|noteId|path|integer| 是 |原笔记ID，正整数。|

> 返回示例

> HTTP始终200；code=200成功，400失败，401需要登录；失败data=null。

```json
{
    "code": 200,
    "data": {
        "noteId": 201,
        "likeCount": 0,
        "favoriteCount": 0,
        "commentCount": 0,
        "isLiked": false,
        "isFavorited": false
    },
    "message": "操作成功"
}
```

```json
{
    "code": 400,
    "data": null,
    "message": "操作失败，请检查参数或当前状态"
}
```

```json
{
    "code": 401,
    "data": null,
    "message": "请先登录或重新登录"
}
```

```json
{
    "code": 200,
    "data": null,
    "message": "已取消"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|HTTP始终200；code=200成功，400失败，401需要登录；失败data=null。|Inline|

### 返回数据结构

#### 枚举值

|属性|值|
|---|---|
|code|200|
|*anonymous*|null|
|code|400|
|code|401|
|data|null|

# 数据模型

<h2 id="tocS_UserSummary">UserSummary</h2>

<a id="schemausersummary"></a>
<a id="schema_UserSummary"></a>
<a id="tocSusersummary"></a>
<a id="tocsusersummary"></a>

```json
{
  "userId": 1,
  "nickname": "山间读者",
  "avatarPath": "/uploads/avatars/9c1a2c77.png"
}

```

对外用户摘要，不含邮箱和私人资料。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|userId|integer|true|none||用户 ID。|
|nickname|string|true|none||昵称，去除首尾空白后 1～30 字符。|
|avatarPath|string|true|none||头像图片路径：先以 purpose=avatar 上传，取 data.filePath。必有头像，不允许空字符串或 null。|

<h2 id="tocS_BookSummary">BookSummary</h2>

<a id="schemabooksummary"></a>
<a id="schema_BookSummary"></a>
<a id="tocSbooksummary"></a>
<a id="tocsbooksummary"></a>

```json
{
  "bookId": 101,
  "title": "百年孤独",
  "author": "加西亚·马尔克斯",
  "coverPath": "/uploads/covers/6d28c990.png",
  "status": "active"
}

```

书籍摘要。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|bookId|integer|true|none||书籍 ID。|
|title|string|true|none||书名，规范化后 1～200 字符。|
|author|string|true|none||作者，规范化后 1～100 字符。|
|coverPath|string¦null|true|none||封面图片路径：先以 purpose=cover 上传，取 data.filePath；null 表示没有封面。|
|status|string|true|none||书籍状态：active（上架）、inactive（下架）。|

#### 枚举值

|属性|值|
|---|---|
|status|active|
|status|inactive|

<h2 id="tocS_ReadingState">ReadingState</h2>

<a id="schemareadingstate"></a>
<a id="schema_ReadingState"></a>
<a id="tocSreadingstate"></a>
<a id="tocsreadingstate"></a>

```json
{
  "book": {
    "bookId": 101,
    "title": "百年孤独",
    "author": "加西亚·马尔克斯",
    "coverPath": "/uploads/covers/6d28c990.png",
    "status": "active"
  },
  "updatedAt": null
}

```

当前正在阅读的一本书。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|book|any|true|none||当前阅读书籍，停止阅读或未设置时为 null。|

oneOf

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» *anonymous*|[BookSummary](#schemabooksummary)|false|none||书籍摘要。|

xor

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» *anonymous*|object¦null|false|none||无内容，返回 null|

continued

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|updatedAt|string(date-time)¦null|true|none||最近设置时间，从未设置时为 null。|

#### 枚举值

|属性|值|
|---|---|
|*anonymous*|null|

<h2 id="tocS_CurrentUser">CurrentUser</h2>

<a id="schemacurrentuser"></a>
<a id="schema_CurrentUser"></a>
<a id="tocScurrentuser"></a>
<a id="tocscurrentuser"></a>

```json
{
  "userId": 1,
  "nickname": "山间读者",
  "avatarPath": "/uploads/avatars/9c1a2c77.png",
  "gender": "female",
  "email": "reader@example.com",
  "role": "user",
  "currentReading": {
    "book": {
      "bookId": 101,
      "title": "百年孤独",
      "author": "加西亚·马尔克斯",
      "coverPath": "/uploads/covers/6d28c990.png",
      "status": "active"
    },
    "updatedAt": null
  },
  "createdAt": "2026-09-07T12:00:00Z"
}

```

当前登录用户的完整资料。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|userId|integer|true|none||用户 ID。|
|nickname|string|true|none||昵称，去除首尾空白后 1～30 字符。|
|avatarPath|string|true|none||头像图片路径：先以 purpose=avatar 上传，取 data.filePath。必有头像，不允许空字符串或 null。|
|gender|string|true|none||性别：male（男）、female（女）、unspecified（未设置）。|
|email|string(email)|true|none||登录邮箱，去除首尾空白并转小写后查重。|
|role|string|true|none||账号身份：user（普通用户）、admin（管理员）。|
|currentReading|[ReadingState](#schemareadingstate)|true|none||当前正在阅读的一本书。|
|createdAt|string(date-time)|true|none||注册时间，UTC。|

#### 枚举值

|属性|值|
|---|---|
|gender|male|
|gender|female|
|gender|unspecified|
|role|user|
|role|admin|

<h2 id="tocS_UserCard">UserCard</h2>

<a id="schemausercard"></a>
<a id="schema_UserCard"></a>
<a id="tocSusercard"></a>
<a id="tocsusercard"></a>

```json
{
  "user": {
    "userId": 1,
    "nickname": "山间读者",
    "avatarPath": "/uploads/avatars/9c1a2c77.png"
  },
  "currentReading": {
    "book": {
      "bookId": 101,
      "title": "百年孤独",
      "author": "加西亚·马尔克斯",
      "coverPath": "/uploads/covers/6d28c990.png",
      "status": "active"
    },
    "updatedAt": null
  },
  "isFriend": false
}

```

用户公开名片。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|user|[UserSummary](#schemausersummary)|true|none||对外用户摘要，不含邮箱和私人资料。|
|currentReading|[ReadingState](#schemareadingstate)|true|none||当前正在阅读的一本书。|
|isFriend|boolean|true|none||是否已经与当前登录用户建立书友关系。|

<h2 id="tocS_Book">Book</h2>

<a id="schemabook"></a>
<a id="schema_Book"></a>
<a id="tocSbook"></a>
<a id="tocsbook"></a>

```json
{
  "bookId": 101,
  "title": "百年孤独",
  "author": "加西亚·马尔克斯",
  "coverPath": "/uploads/covers/6d28c990.png",
  "status": "active",
  "isbn": null,
  "intro": null,
  "createdAt": "2026-09-07T12:00:00Z",
  "updatedAt": "2026-09-07T12:00:00Z"
}

```

书籍详情。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|bookId|integer|true|none||书籍 ID。|
|title|string|true|none||书名，规范化后 1～200 字符。|
|author|string|true|none||作者，规范化后 1～100 字符。|
|coverPath|string¦null|true|none||封面图片路径：先以 purpose=cover 上传，取 data.filePath；null 表示没有封面。|
|status|string|true|none||书籍状态：active（上架）、inactive（下架）。|
|isbn|string¦null|true|none||ISBN，尚未补全时为 null。|
|intro|string¦null|true|none||书籍简介，尚未补全时为 null。|
|createdAt|string(date-time)|true|none||创建时间，UTC。|
|updatedAt|string(date-time)|true|none||更新时间，UTC。|

#### 枚举值

|属性|值|
|---|---|
|status|active|
|status|inactive|

<h2 id="tocS_UserBook">UserBook</h2>

<a id="schemauserbook"></a>
<a id="schema_UserBook"></a>
<a id="tocSuserbook"></a>
<a id="tocsuserbook"></a>

```json
{
  "book": {
    "bookId": 101,
    "title": "百年孤独",
    "author": "加西亚·马尔克斯",
    "coverPath": "/uploads/covers/6d28c990.png",
    "status": "active"
  },
  "readingStatus": "reading",
  "createdAt": "2026-09-07T12:00:00Z",
  "updatedAt": "2026-09-07T12:00:00Z"
}

```

个人书单条目。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|book|[BookSummary](#schemabooksummary)|true|none||书籍摘要。|
|readingStatus|string|true|none||阅读状态：wantToRead（想读）、reading（在读）、read（已读）。|
|createdAt|string(date-time)|true|none||加入书单的时间，UTC。|
|updatedAt|string(date-time)|true|none||最近修改书单状态的时间，UTC。|

#### 枚举值

|属性|值|
|---|---|
|readingStatus|wantToRead|
|readingStatus|reading|
|readingStatus|read|

<h2 id="tocS_Note">Note</h2>

<a id="schemanote"></a>
<a id="schema_Note"></a>
<a id="tocSnote"></a>
<a id="tocsnote"></a>

```json
{
  "noteId": 201,
  "author": {
    "userId": 1,
    "nickname": "山间读者",
    "avatarPath": "/uploads/avatars/9c1a2c77.png"
  },
  "book": {
    "bookId": 101,
    "title": "百年孤独",
    "author": "加西亚·马尔克斯",
    "coverPath": "/uploads/covers/6d28c990.png",
    "status": "active"
  },
  "content": "读到时间和记忆的段落，想起了童年的夏天。",
  "isPublic": false,
  "reviewStatus": "pending",
  "reviewReason": null,
  "createdAt": "2026-09-07T12:00:00Z",
  "updatedAt": "2026-09-07T12:00:00Z",
  "deletedAt": null,
  "likeCount": 0,
  "favoriteCount": 0,
  "commentCount": 0,
  "isLiked": false,
  "isFavorited": false
}

```

当前文本笔记。新建或实际修改正文后均待审核；只有审核通过、公开且未删除才对他人可见。审核状态与AI状态分开，互动按noteId计算。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|noteId|integer|true|none||笔记 ID。|
|author|[UserSummary](#schemausersummary)|true|none||对外用户摘要，不含邮箱和私人资料。|
|book|[BookSummary](#schemabooksummary)|true|none||书籍摘要。|
|content|string|true|none||当前笔记纯文本正文；不是历史漂流副本。去除首尾空白后1～10000字符。|
|isPublic|boolean|true|none||true申请公开，false私密；true仍须reviewStatus=approved且未删除才对他人可见。|
|reviewStatus|string|true|read-only||内容审核：pending待审核、approved通过、rejected拒绝；由服务端设置，不是漂流瓶aiStatus。|
|reviewReason|string¦null|true|read-only||拒绝原因，rejected时为1～500字符；pending或approved时为null。只能由审核接口设置。|
|createdAt|string(date-time)|true|none||创建时间，UTC。|
|updatedAt|string(date-time)|true|none||正文、公开状态或审核结果的最近更新时间，UTC。|
|deletedAt|string(date-time)¦null|true|none||软删除时间，未删除时为 null。|
|likeCount|integer|true|none||笔记点赞人数；同一人只计一次。|
|favoriteCount|integer|true|none||笔记收藏人数，不返回收藏者列表。|
|commentCount|integer|true|none||未删除公开评论数，与漂流便签分开。|
|isLiked|boolean|true|none||当前登录用户是否已点赞：true 已点赞，false 未点赞。|
|isFavorited|boolean|true|none||当前登录用户是否已收藏：true 已收藏，false 未收藏。|

oneOf

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|*anonymous*|object|false|none||none|
|» reviewStatus|any|false|none||none|
|» reviewReason|[NullData](#schemanulldata)|false|none||无内容，返回 null|

xor

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|*anonymous*|object|false|none||none|
|» reviewStatus|string|false|none||none|
|» reviewReason|string|false|none||none|

#### 枚举值

|属性|值|
|---|---|
|reviewStatus|pending|
|reviewStatus|approved|
|reviewStatus|rejected|
|reviewStatus|pending|
|reviewStatus|approved|
|reviewStatus|rejected|

<h2 id="tocS_Interaction">Interaction</h2>

<a id="schemainteraction"></a>
<a id="schema_Interaction"></a>
<a id="tocSinteraction"></a>
<a id="tocsinteraction"></a>

```json
{
  "interactionId": 301,
  "bottleId": 501,
  "receiver": {
    "userId": 1,
    "nickname": "山间读者",
    "avatarPath": "/uploads/avatars/9c1a2c77.png"
  },
  "acquiredAt": "2026-09-08T08:05:00Z",
  "stickyText": null,
  "stickyAt": null,
  "replyText": null,
  "repliedAt": null
}

```

用户点开并获取漂流瓶后产生的记录及一对一便签，不含推荐语。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|interactionId|integer|true|none||获取记录 ID，可用于书友申请及作者回贴。|
|bottleId|integer|true|none||漂流瓶 ID。|
|receiver|[UserSummary](#schemausersummary)|true|none||对外用户摘要，不含邮箱和私人资料。|
|acquiredAt|string(date-time)|true|none||获取时间，UTC。|
|stickyText|string¦null|true|none||获取者便签，尚未提交时为 null。|
|stickyAt|string(date-time)¦null|true|none||便签提交时间，尚未提交时为 null。|
|replyText|string¦null|true|none||作者回贴，尚未回复时为 null。|
|repliedAt|string(date-time)¦null|true|none||回贴时间，尚未回复时为 null。|

<h2 id="tocS_BottleSummary">BottleSummary</h2>

<a id="schemabottlesummary"></a>
<a id="schema_BottleSummary"></a>
<a id="tocSbottlesummary"></a>
<a id="tocsbottlesummary"></a>

```json
{
  "bottleId": 501,
  "author": {
    "userId": 2,
    "nickname": "晚风读者",
    "avatarPath": "/uploads/avatars/72d50b11.png"
  },
  "book": {
    "bookId": 101,
    "title": "百年孤独",
    "author": "加西亚·马尔克斯",
    "coverPath": "/uploads/covers/6d28c990.png",
    "status": "active"
  },
  "status": "active",
  "aiStatus": "ready",
  "createdAt": "2026-09-08T08:00:00Z",
  "expiresAt": "2026-09-15T08:00:00Z",
  "contentPreview": "我们总在回忆中重新理解时间。",
  "noteId": 202
}

```

公开笔记自动入池的漂流记录摘要。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|bottleId|integer|true|none||漂流瓶 ID。|
|author|[UserSummary](#schemausersummary)|true|none||公开笔记作者。|
|book|[BookSummary](#schemabooksummary)|true|none||书籍摘要。|
|status|string|true|none||漂流瓶状态：active（有效）、expired（过期）、withdrawn（已撤回）。|
|aiStatus|string|true|none||AI处理状态：pending待处理、processing处理中、ready就绪、failed失败；不是笔记reviewStatus审核结果。|
|createdAt|string(date-time)|true|none||审核通过且公开后，本次实际入池时间，UTC；不是提交审核时间。|
|expiresAt|string(date-time)|true|none||实际入池后7天，UTC。修改正文撤回旧瓶，新内容通过且公开后新建瓶子；AI重试不续期。|
|contentPreview|string|true|none||正文前 100 字符。|
|noteId|integer|true|none||该瓶原笔记ID，用于点赞、收藏、评论；不是匹配请求所选来源笔记ID。|

#### 枚举值

|属性|值|
|---|---|
|status|active|
|status|expired|
|status|withdrawn|
|aiStatus|pending|
|aiStatus|processing|
|aiStatus|ready|
|aiStatus|failed|

<h2 id="tocS_BottleDetail">BottleDetail</h2>

<a id="schemabottledetail"></a>
<a id="schema_BottleDetail"></a>
<a id="tocSbottledetail"></a>
<a id="tocsbottledetail"></a>

```json
{
  "bottleId": 501,
  "author": {
    "userId": 2,
    "nickname": "晚风读者",
    "avatarPath": "/uploads/avatars/72d50b11.png"
  },
  "book": {
    "bookId": 101,
    "title": "百年孤独",
    "author": "加西亚·马尔克斯",
    "coverPath": "/uploads/covers/6d28c990.png",
    "status": "active"
  },
  "status": "active",
  "aiStatus": "ready",
  "createdAt": "2026-09-08T08:00:00Z",
  "expiresAt": "2026-09-15T08:00:00Z",
  "content": "读到时间和记忆的段落，想起了童年的夏天。",
  "topics": [
    "记忆"
  ],
  "keywords": [
    "童年"
  ],
  "emotion": "reflective",
  "aiMessage": null,
  "myInteraction": {
    "interactionId": 301,
    "bottleId": 501,
    "receiver": {
      "userId": 1,
      "nickname": "山间读者",
      "avatarPath": "/uploads/avatars/9c1a2c77.png"
    },
    "acquiredAt": "2026-09-08T08:05:00Z",
    "stickyText": null,
    "stickyAt": null,
    "replyText": null,
    "repliedAt": null
  },
  "noteId": 202
}

```

漂流瓶正文副本；原笔记转私密或删除后，获取者也无权查看。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|bottleId|integer|true|none||漂流瓶 ID。|
|author|[UserSummary](#schemausersummary)|true|none||公开笔记作者。|
|book|[BookSummary](#schemabooksummary)|true|none||书籍摘要。|
|status|string|true|none||漂流瓶状态：active（有效）、expired（过期）、withdrawn（已撤回）。|
|aiStatus|string|true|none||AI处理状态：pending待处理、processing处理中、ready就绪、failed失败；不是笔记reviewStatus审核结果。|
|createdAt|string(date-time)|true|none||审核通过且公开后，本次实际入池时间，UTC；不是提交审核时间。|
|expiresAt|string(date-time)|true|none||实际入池后7天，UTC。修改正文撤回旧瓶，新内容通过且公开后新建瓶子；AI重试不续期。|
|content|string|true|none||本次入池时已审核通过的正文副本；不覆盖为后续编辑内容，正文修改后此瓶撤回。|
|topics|[string]|true|none||主题，尚未生成时为空数组。|
|keywords|[string]|true|none||关键词，尚未生成时为空数组。|
|emotion|string¦null|true|none||文字情绪：calm（平静）、joyful（愉悦）、sad（低落）、reflective（感慨）、mixed（复杂）、neutral（中性）；未生成时为 null。|
|aiMessage|string¦null|true|none||AI 处理提示，没有提示时为 null。|
|myInteraction|any|true|none||当前登录用户的获取记录；作者或未获取的管理员查看时为null。|

oneOf

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» *anonymous*|[Interaction](#schemainteraction)|false|none||用户点开并获取漂流瓶后产生的记录及一对一便签，不含推荐语。|

xor

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» *anonymous*|object¦null|false|none||无内容，返回 null|

continued

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|noteId|integer|true|none||该瓶原笔记ID，用于点赞、收藏、评论；不是匹配请求所选来源笔记ID。|

#### 枚举值

|属性|值|
|---|---|
|status|active|
|status|expired|
|status|withdrawn|
|aiStatus|pending|
|aiStatus|processing|
|aiStatus|ready|
|aiStatus|failed|
|emotion|calm|
|emotion|joyful|
|emotion|sad|
|emotion|reflective|
|emotion|mixed|
|emotion|neutral|
|emotion|null|
|*anonymous*|null|

<h2 id="tocS_FriendRequest">FriendRequest</h2>

<a id="schemafriendrequest"></a>
<a id="schema_FriendRequest"></a>
<a id="tocSfriendrequest"></a>
<a id="tocsfriendrequest"></a>

```json
{
  "requestId": 601,
  "requester": {
    "userId": 1,
    "nickname": "山间读者",
    "avatarPath": "/uploads/avatars/9c1a2c77.png"
  },
  "receiver": {
    "userId": 2,
    "nickname": "晚风读者",
    "avatarPath": "/uploads/avatars/72d50b11.png"
  },
  "bottleId": 501,
  "status": "pending",
  "createdAt": "2026-09-07T12:00:00Z",
  "handledAt": null
}

```

书友申请。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|requestId|integer|true|none||申请 ID。|
|requester|[UserSummary](#schemausersummary)|true|none||对外用户摘要，不含邮箱和私人资料。|
|receiver|[UserSummary](#schemausersummary)|true|none||接收申请的用户。|
|bottleId|integer|true|none||相关漂流瓶 ID。|
|status|string|true|none||申请状态：pending（待处理）、accepted（已接受）、rejected（已拒绝）。|
|createdAt|string(date-time)|true|none||申请时间，UTC。|
|handledAt|string(date-time)¦null|true|none||处理时间，待处理时为 null。|

#### 枚举值

|属性|值|
|---|---|
|status|pending|
|status|accepted|
|status|rejected|

<h2 id="tocS_Friend">Friend</h2>

<a id="schemafriend"></a>
<a id="schema_Friend"></a>
<a id="tocSfriend"></a>
<a id="tocsfriend"></a>

```json
{
  "user": {
    "userId": 1,
    "nickname": "山间读者",
    "avatarPath": "/uploads/avatars/9c1a2c77.png"
  },
  "becameFriendsAt": "2026-09-07T12:00:00Z"
}

```

已经建立的书友关系。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|user|[UserSummary](#schemausersummary)|true|none||对外用户摘要，不含邮箱和私人资料。|
|becameFriendsAt|string(date-time)|true|none||本次书友关系建立时间，UTC。|

<h2 id="tocS_OnlineReader">OnlineReader</h2>

<a id="schemaonlinereader"></a>
<a id="schema_OnlineReader"></a>
<a id="tocSonlinereader"></a>
<a id="tocsonlinereader"></a>

```json
{
  "user": {
    "userId": 1,
    "nickname": "山间读者",
    "avatarPath": "/uploads/avatars/9c1a2c77.png"
  },
  "currentReading": {
    "book": {
      "bookId": 101,
      "title": "百年孤独",
      "author": "加西亚·马尔克斯",
      "coverPath": "/uploads/covers/6d28c990.png",
      "status": "active"
    },
    "updatedAt": null
  }
}

```

全站在线用户及当前阅读。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|user|[UserSummary](#schemausersummary)|true|none||对外用户摘要，不含邮箱和私人资料。|
|currentReading|[ReadingState](#schemareadingstate)|true|none||当前正在阅读的一本书。|

<h2 id="tocS_Notification">Notification</h2>

<a id="schemanotification"></a>
<a id="schema_Notification"></a>
<a id="tocSnotification"></a>
<a id="tocsnotification"></a>

```json
{
  "notificationId": 401,
  "type": "stickyNote",
  "actor": {
    "userId": 1,
    "nickname": "山间读者",
    "avatarPath": "/uploads/avatars/9c1a2c77.png"
  },
  "content": "收到一张便签",
  "resourceType": "bottle",
  "resourceId": 501,
  "isRead": false,
  "createdAt": "2026-09-07T12:00:00Z"
}

```

个人通知。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|notificationId|integer|true|none||通知 ID。|
|type|string|true|none||通知类型：stickyNote（收到便签）、stickyReply（收到回贴）、friendRequest（收到书友申请）、friendAccepted（申请被接受）。|
|actor|[UserSummary](#schemausersummary)|true|none||对外用户摘要，不含邮箱和私人资料。|
|content|string|true|none||简短通知提示，不包含私人正文。|
|resourceType|string|true|none||关联资源：bottle（漂流瓶）、friendRequest（书友申请）。|
|resourceId|integer|true|none||对应的 bottleId 或 requestId。|
|isRead|boolean|true|none||是否已读：true 已读，false 未读。|
|createdAt|string(date-time)|true|none||创建时间，UTC。|

#### 枚举值

|属性|值|
|---|---|
|type|stickyNote|
|type|stickyReply|
|type|friendRequest|
|type|friendAccepted|
|resourceType|bottle|
|resourceType|friendRequest|

<h2 id="tocS_PageBookSummary">PageBookSummary</h2>

<a id="schemapagebooksummary"></a>
<a id="schema_PageBookSummary"></a>
<a id="tocSpagebooksummary"></a>
<a id="tocspagebooksummary"></a>

```json
{
  "list": [
    {
      "bookId": 101,
      "title": "百年孤独",
      "author": "加西亚·马尔克斯",
      "coverPath": "/uploads/covers/6d28c990.png",
      "status": "active"
    }
  ],
  "total": 1,
  "pageNum": 1,
  "pageSize": 10
}

```

分页列表：BookSummary

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|list|[[BookSummary](#schemabooksummary)]|true|none||当前页记录，无记录时返回空数组。|
|total|integer|true|none||筛选后的总条数。|
|pageNum|integer|true|none||当前页码。|
|pageSize|integer|true|none||每页条数。|

<h2 id="tocS_PageBook">PageBook</h2>

<a id="schemapagebook"></a>
<a id="schema_PageBook"></a>
<a id="tocSpagebook"></a>
<a id="tocspagebook"></a>

```json
{
  "list": [
    {
      "bookId": 101,
      "title": "百年孤独",
      "author": "加西亚·马尔克斯",
      "coverPath": "/uploads/covers/6d28c990.png",
      "status": "active",
      "isbn": null,
      "intro": null,
      "createdAt": "2026-09-07T12:00:00Z",
      "updatedAt": "2026-09-07T12:00:00Z"
    }
  ],
  "total": 1,
  "pageNum": 1,
  "pageSize": 10
}

```

分页列表：Book

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|list|[[Book](#schemabook)]|true|none||当前页记录，无记录时返回空数组。|
|total|integer|true|none||筛选后的总条数。|
|pageNum|integer|true|none||当前页码。|
|pageSize|integer|true|none||每页条数。|

<h2 id="tocS_PageUserBook">PageUserBook</h2>

<a id="schemapageuserbook"></a>
<a id="schema_PageUserBook"></a>
<a id="tocSpageuserbook"></a>
<a id="tocspageuserbook"></a>

```json
{
  "list": [
    {
      "book": {
        "bookId": 101,
        "title": "百年孤独",
        "author": "加西亚·马尔克斯",
        "coverPath": "/uploads/covers/6d28c990.png",
        "status": "active"
      },
      "readingStatus": "reading",
      "createdAt": "2026-09-07T12:00:00Z",
      "updatedAt": "2026-09-07T12:00:00Z"
    }
  ],
  "total": 1,
  "pageNum": 1,
  "pageSize": 10
}

```

分页列表：UserBook

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|list|[[UserBook](#schemauserbook)]|true|none||当前页记录，无记录时返回空数组。|
|total|integer|true|none||筛选后的总条数。|
|pageNum|integer|true|none||当前页码。|
|pageSize|integer|true|none||每页条数。|

<h2 id="tocS_PageNote">PageNote</h2>

<a id="schemapagenote"></a>
<a id="schema_PageNote"></a>
<a id="tocSpagenote"></a>
<a id="tocspagenote"></a>

```json
{
  "list": [
    {
      "noteId": 201,
      "author": {
        "userId": 1,
        "nickname": "山间读者",
        "avatarPath": "/uploads/avatars/9c1a2c77.png"
      },
      "book": {
        "bookId": 101,
        "title": "百年孤独",
        "author": "加西亚·马尔克斯",
        "coverPath": "/uploads/covers/6d28c990.png",
        "status": "active"
      },
      "content": "读到时间和记忆的段落，想起了童年的夏天。",
      "isPublic": false,
      "reviewStatus": "pending",
      "reviewReason": null,
      "createdAt": "2026-09-07T12:00:00Z",
      "updatedAt": "2026-09-07T12:00:00Z",
      "deletedAt": null,
      "likeCount": 0,
      "favoriteCount": 0,
      "commentCount": 0,
      "isLiked": false,
      "isFavorited": false
    }
  ],
  "total": 1,
  "pageNum": 1,
  "pageSize": 10
}

```

分页列表：Note

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|list|[[Note](#schemanote)]|true|none||当前页记录，无记录时返回空数组。|
|total|integer|true|none||筛选后的总条数。|
|pageNum|integer|true|none||当前页码。|
|pageSize|integer|true|none||每页条数。|

<h2 id="tocS_PageBottleSummary">PageBottleSummary</h2>

<a id="schemapagebottlesummary"></a>
<a id="schema_PageBottleSummary"></a>
<a id="tocSpagebottlesummary"></a>
<a id="tocspagebottlesummary"></a>

```json
{
  "list": [
    {
      "bottleId": 501,
      "author": {
        "userId": 2,
        "nickname": "晚风读者",
        "avatarPath": "/uploads/avatars/72d50b11.png"
      },
      "book": {
        "bookId": 101,
        "title": "百年孤独",
        "author": "加西亚·马尔克斯",
        "coverPath": "/uploads/covers/6d28c990.png",
        "status": "active"
      },
      "status": "active",
      "aiStatus": "ready",
      "createdAt": "2026-09-08T08:00:00Z",
      "expiresAt": "2026-09-15T08:00:00Z",
      "contentPreview": "我们总在回忆中重新理解时间。",
      "noteId": 202
    }
  ],
  "total": 1,
  "pageNum": 1,
  "pageSize": 10
}

```

分页列表：BottleSummary

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|list|[[BottleSummary](#schemabottlesummary)]|true|none||当前页记录，无记录时返回空数组。|
|total|integer|true|none||筛选后的总条数。|
|pageNum|integer|true|none||当前页码。|
|pageSize|integer|true|none||每页条数。|

<h2 id="tocS_PageInteraction">PageInteraction</h2>

<a id="schemapageinteraction"></a>
<a id="schema_PageInteraction"></a>
<a id="tocSpageinteraction"></a>
<a id="tocspageinteraction"></a>

```json
{
  "list": [
    {
      "interactionId": 301,
      "bottleId": 501,
      "receiver": {
        "userId": 1,
        "nickname": "山间读者",
        "avatarPath": "/uploads/avatars/9c1a2c77.png"
      },
      "acquiredAt": "2026-09-08T08:05:00Z",
      "stickyText": null,
      "stickyAt": null,
      "replyText": null,
      "repliedAt": null
    }
  ],
  "total": 1,
  "pageNum": 1,
  "pageSize": 10
}

```

分页列表：Interaction

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|list|[[Interaction](#schemainteraction)]|true|none||当前页记录，无记录时返回空数组。|
|total|integer|true|none||筛选后的总条数。|
|pageNum|integer|true|none||当前页码。|
|pageSize|integer|true|none||每页条数。|

<h2 id="tocS_PageFriendRequest">PageFriendRequest</h2>

<a id="schemapagefriendrequest"></a>
<a id="schema_PageFriendRequest"></a>
<a id="tocSpagefriendrequest"></a>
<a id="tocspagefriendrequest"></a>

```json
{
  "list": [
    {
      "requestId": 601,
      "requester": {
        "userId": 1,
        "nickname": "山间读者",
        "avatarPath": "/uploads/avatars/9c1a2c77.png"
      },
      "receiver": {
        "userId": 2,
        "nickname": "晚风读者",
        "avatarPath": "/uploads/avatars/72d50b11.png"
      },
      "bottleId": 501,
      "status": "pending",
      "createdAt": "2026-09-07T12:00:00Z",
      "handledAt": null
    }
  ],
  "total": 1,
  "pageNum": 1,
  "pageSize": 10
}

```

分页列表：FriendRequest

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|list|[[FriendRequest](#schemafriendrequest)]|true|none||当前页记录，无记录时返回空数组。|
|total|integer|true|none||筛选后的总条数。|
|pageNum|integer|true|none||当前页码。|
|pageSize|integer|true|none||每页条数。|

<h2 id="tocS_PageFriend">PageFriend</h2>

<a id="schemapagefriend"></a>
<a id="schema_PageFriend"></a>
<a id="tocSpagefriend"></a>
<a id="tocspagefriend"></a>

```json
{
  "list": [
    {
      "user": {
        "userId": 1,
        "nickname": "山间读者",
        "avatarPath": "/uploads/avatars/9c1a2c77.png"
      },
      "becameFriendsAt": "2026-09-07T12:00:00Z"
    }
  ],
  "total": 1,
  "pageNum": 1,
  "pageSize": 10
}

```

分页列表：Friend

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|list|[[Friend](#schemafriend)]|true|none||当前页记录，无记录时返回空数组。|
|total|integer|true|none||筛选后的总条数。|
|pageNum|integer|true|none||当前页码。|
|pageSize|integer|true|none||每页条数。|

<h2 id="tocS_PageOnlineReader">PageOnlineReader</h2>

<a id="schemapageonlinereader"></a>
<a id="schema_PageOnlineReader"></a>
<a id="tocSpageonlinereader"></a>
<a id="tocspageonlinereader"></a>

```json
{
  "list": [
    {
      "user": {
        "userId": 1,
        "nickname": "山间读者",
        "avatarPath": "/uploads/avatars/9c1a2c77.png"
      },
      "currentReading": {
        "book": {},
        "updatedAt": null
      }
    }
  ],
  "total": 1,
  "pageNum": 1,
  "pageSize": 10
}

```

分页列表：OnlineReader

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|list|[[OnlineReader](#schemaonlinereader)]|true|none||当前页记录，无记录时返回空数组。|
|total|integer|true|none||筛选后的总条数。|
|pageNum|integer|true|none||当前页码。|
|pageSize|integer|true|none||每页条数。|

<h2 id="tocS_PageNotification">PageNotification</h2>

<a id="schemapagenotification"></a>
<a id="schema_PageNotification"></a>
<a id="tocSpagenotification"></a>
<a id="tocspagenotification"></a>

```json
{
  "list": [
    {
      "notificationId": 401,
      "type": "stickyNote",
      "actor": {
        "userId": 1,
        "nickname": "山间读者",
        "avatarPath": "/uploads/avatars/9c1a2c77.png"
      },
      "content": "收到一张便签",
      "resourceType": "bottle",
      "resourceId": 501,
      "isRead": false,
      "createdAt": "2026-09-07T12:00:00Z"
    }
  ],
  "total": 1,
  "pageNum": 1,
  "pageSize": 10,
  "unreadCount": 1
}

```

分页列表：Notification

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|list|[[Notification](#schemanotification)]|true|none||当前页记录，无记录时返回空数组。|
|total|integer|true|none||筛选后的总条数。|
|pageNum|integer|true|none||当前页码。|
|pageSize|integer|true|none||每页条数。|
|unreadCount|integer|true|none||全部未读数量，不受本页和 isRead 筛选影响。|

<h2 id="tocS_RegisterRequest">RegisterRequest</h2>

<a id="schemaregisterrequest"></a>
<a id="schema_RegisterRequest"></a>
<a id="tocSregisterrequest"></a>
<a id="tocsregisterrequest"></a>

```json
{
  "avatarPath": "/uploads/avatars/9c1a2c77.png",
  "nickname": "山间读者",
  "email": "reader@example.com",
  "password": "ReadTogether2026",
  "gender": "female"
}

```

注册资料。先上传头像，再提交返回路径；不提供默认头像。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|avatarPath|string|true|none||头像图片路径：先以 purpose=avatar 上传，取 data.filePath。必有头像，不允许空字符串或 null。|
|nickname|string|true|none||昵称，去除首尾空白后 1～30 字符。|
|email|string(email)|true|none||登录邮箱，去除首尾空白并转小写后查重。|
|password|string(password)|true|write-only||登录密码，8～72 字符，不去除首尾空白。|
|gender|string|false|none||性别：male（男）、female（女）、unspecified（未设置）。|

#### 枚举值

|属性|值|
|---|---|
|gender|male|
|gender|female|
|gender|unspecified|

<h2 id="tocS_RegisterResult">RegisterResult</h2>

<a id="schemaregisterresult"></a>
<a id="schema_RegisterResult"></a>
<a id="tocSregisterresult"></a>
<a id="tocsregisterresult"></a>

```json
{
  "userId": 1
}

```

注册成功。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|userId|integer|true|none||新用户 ID。|

<h2 id="tocS_LoginRequest">LoginRequest</h2>

<a id="schemaloginrequest"></a>
<a id="schema_LoginRequest"></a>
<a id="tocSloginrequest"></a>
<a id="tocsloginrequest"></a>

```json
{
  "email": "reader@example.com",
  "password": "ReadTogether2026"
}

```

登录参数。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|email|string(email)|true|none||登录邮箱，去除首尾空白并转小写后查重。|
|password|string(password)|true|write-only||登录密码，8～72 字符，不去除首尾空白。|

<h2 id="tocS_LoginResult">LoginResult</h2>

<a id="schemaloginresult"></a>
<a id="schema_LoginResult"></a>
<a id="tocSloginresult"></a>
<a id="tocsloginresult"></a>

```json
{
  "token": "example-jwt-token",
  "expiresAt": "2026-09-14T12:00:00Z"
}

```

登录结果。只持久缓存 token。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|token|string|true|none||登录令牌，后续请求通过 Authorization: Bearer <token> 携带。|
|expiresAt|string(date-time)|true|none||Token 到期时间，UTC；默认有效期 7 天。|

<h2 id="tocS_UpdateProfileRequest">UpdateProfileRequest</h2>

<a id="schemaupdateprofilerequest"></a>
<a id="schema_UpdateProfileRequest"></a>
<a id="tocSupdateprofilerequest"></a>
<a id="tocsupdateprofilerequest"></a>

```json
{
  "nickname": "山间读者",
  "gender": "female",
  "avatarPath": "/uploads/avatars/9c1a2c77.png"
}

```

修改个人资料。未提交的字段保持原值，头像不能清空。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|nickname|string|false|none||昵称，去除首尾空白后 1～30 字符。|
|gender|string|false|none||性别：male（男）、female（女）、unspecified（未设置）。不传保留原值。|
|avatarPath|string|false|none||头像图片路径：先以 purpose=avatar 上传，取 data.filePath。必有头像，不允许空字符串或 null。修改时不传保留已上传的原头像。|

#### 枚举值

|属性|值|
|---|---|
|gender|male|
|gender|female|
|gender|unspecified|

<h2 id="tocS_UploadRequest">UploadRequest</h2>

<a id="schemauploadrequest"></a>
<a id="schema_UploadRequest"></a>
<a id="tocSuploadrequest"></a>
<a id="tocsuploadrequest"></a>

```json
{
  "file": "string",
  "purpose": "avatar"
}

```

上传单张图片。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|file|string(binary)|true|none||文件选择器选中的图片；JPEG、PNG、WebP，最多 5 MiB。|
|purpose|string|true|none||上传用途：avatar（头像，无需 Token）、cover（书籍封面，需要管理员 Token）。|

#### 枚举值

|属性|值|
|---|---|
|purpose|avatar|
|purpose|cover|

<h2 id="tocS_UploadResult">UploadResult</h2>

<a id="schemauploadresult"></a>
<a id="schema_UploadResult"></a>
<a id="tocSuploadresult"></a>
<a id="tocsuploadresult"></a>

```json
{
  "filePath": "/uploads/avatars/9c1a2c77.png"
}

```

上传返回路径。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|filePath|string|true|none||图片相对路径，原样提交为 avatarPath 或 coverPath；预览时才拼接后端地址。|

<h2 id="tocS_CreateBookRequest">CreateBookRequest</h2>

<a id="schemacreatebookrequest"></a>
<a id="schema_CreateBookRequest"></a>
<a id="tocScreatebookrequest"></a>
<a id="tocscreatebookrequest"></a>

```json
{
  "title": "百年孤独",
  "author": "加西亚·马尔克斯"
}

```

创建或复用书籍，按规范化书名加作者去重。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|title|string|true|none||书名，规范化后 1～200 字符。|
|author|string|true|none||作者，规范化后 1～100 字符。|

<h2 id="tocS_CreateBookResult">CreateBookResult</h2>

<a id="schemacreatebookresult"></a>
<a id="schema_CreateBookResult"></a>
<a id="tocScreatebookresult"></a>
<a id="tocscreatebookresult"></a>

```json
{
  "book": {
    "bookId": 101,
    "title": "百年孤独",
    "author": "加西亚·马尔克斯",
    "coverPath": "/uploads/covers/6d28c990.png",
    "status": "active",
    "isbn": null,
    "intro": null,
    "createdAt": "2026-09-07T12:00:00Z",
    "updatedAt": "2026-09-07T12:00:00Z"
  },
  "reused": false
}

```

创建或复用结果。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|book|[Book](#schemabook)|true|none||书籍详情。|
|reused|boolean|true|none||true 表示复用已有书籍，false 表示新建。|

<h2 id="tocS_SetUserBookRequest">SetUserBookRequest</h2>

<a id="schemasetuserbookrequest"></a>
<a id="schema_SetUserBookRequest"></a>
<a id="tocSsetuserbookrequest"></a>
<a id="tocssetuserbookrequest"></a>

```json
{
  "readingStatus": "reading"
}

```

加入书单或修改书单阅读状态。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|readingStatus|string|true|none||阅读状态：wantToRead（想读）、reading（在读）、read（已读）。|

#### 枚举值

|属性|值|
|---|---|
|readingStatus|wantToRead|
|readingStatus|reading|
|readingStatus|read|

<h2 id="tocS_CreateNoteRequest">CreateNoteRequest</h2>

<a id="schemacreatenoterequest"></a>
<a id="schema_CreateNoteRequest"></a>
<a id="tocScreatenoterequest"></a>
<a id="tocscreatenoterequest"></a>

```json
{
  "bookId": 101,
  "content": "读到时间和记忆的段落，想起了童年的夏天。",
  "isPublic": false
}

```

创建本人待审核笔记，包括私密及管理员笔记，不能提交审核字段。通过且公开后才创建漂流瓶和AI任务。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|bookId|integer|true|none||关联上架书籍 ID。|
|content|string|true|none||笔记纯文本正文，去除首尾空白后 1～10000 字符。|
|isPublic|boolean|false|none||true申请通过审核后公开并自动入池；false私密、不入池。默认false，两者新建时均为pending。|

<h2 id="tocS_UpdateNoteRequest">UpdateNoteRequest</h2>

<a id="schemaupdatenoterequest"></a>
<a id="schema_UpdateNoteRequest"></a>
<a id="tocSupdatenoterequest"></a>
<a id="tocsupdatenoterequest"></a>

```json
{
  "content": "读到时间和记忆的段落，想起了童年的夏天。",
  "isPublic": false
}

```

至少一个字段，不能提交审核字段。正文实际变化重置pending、清空原因并撤回全部旧瓶；再次通过且公开才新建瓶子。仅改变公开状态不改变审核结果。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|content|string|false|none||去除首尾空白后1～10000字符。实际变化才重新待审、撤回旧瓶；相同正文不重审、不续期。|
|isPublic|boolean|false|none||true申请公开，false私密；不传保留。仅改公开且已approved时新建瓶子，pending/rejected不展示不入池；转私密撤回全部旧瓶。|

<h2 id="tocS_ThrowBottleRequest">ThrowBottleRequest</h2>

<a id="schemathrowbottlerequest"></a>
<a id="schema_ThrowBottleRequest"></a>
<a id="tocSthrowbottlerequest"></a>
<a id="tocsthrowbottlerequest"></a>

```json
{
  "noteId": 201
}

```

从本人未删除笔记抛出。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|noteId|integer|true|none||本人笔记 ID；同笔记最多一个有效漂流瓶。|

<h2 id="tocS_StickyRequest">StickyRequest</h2>

<a id="schemastickyrequest"></a>
<a id="schema_StickyRequest"></a>
<a id="tocSstickyrequest"></a>
<a id="tocsstickyrequest"></a>

```json
{
  "content": "我也很喜欢你对记忆的理解。"
}

```

提交一张便签或作者回贴。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|content|string|true|none||便签或回贴的纯文本内容，去除首尾空白后 1～200 字符。|

<h2 id="tocS_CreateFriendRequest">CreateFriendRequest</h2>

<a id="schemacreatefriendrequest"></a>
<a id="schema_CreateFriendRequest"></a>
<a id="tocScreatefriendrequest"></a>
<a id="tocscreatefriendrequest"></a>

```json
{
  "interactionId": 301
}

```

根据获取记录发起书友申请。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|interactionId|integer|true|none||主动点开acquire返回的myInteraction.interactionId；列表浏览不产生此ID。|

<h2 id="tocS_HandleFriendRequest">HandleFriendRequest</h2>

<a id="schemahandlefriendrequest"></a>
<a id="schema_HandleFriendRequest"></a>
<a id="tocShandlefriendrequest"></a>
<a id="tocshandlefriendrequest"></a>

```json
{
  "status": "accepted"
}

```

接收方处理申请。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|status|string|true|none||处理结果：accepted（接受并成为书友）、rejected（拒绝）。|

#### 枚举值

|属性|值|
|---|---|
|status|accepted|
|status|rejected|

<h2 id="tocS_SetReadingRequest">SetReadingRequest</h2>

<a id="schemasetreadingrequest"></a>
<a id="schema_SetReadingRequest"></a>
<a id="tocSsetreadingrequest"></a>
<a id="tocssetreadingrequest"></a>

```json
{
  "bookId": 101
}

```

设置当前阅读。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|bookId|integer¦null|true|none||当前阅读书籍 ID，必须在本人书单且为 reading；null 表示停止阅读。|

<h2 id="tocS_ReadNotificationsRequest">ReadNotificationsRequest</h2>

<a id="schemareadnotificationsrequest"></a>
<a id="schema_ReadNotificationsRequest"></a>
<a id="tocSreadnotificationsrequest"></a>
<a id="tocsreadnotificationsrequest"></a>

```json
{
  "notificationIds": [
    401,
    402
  ]
}

```

将指定本人通知标为已读。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|notificationIds|[integer]|true|none||通知 ID 数组，1～100 个，不重复；单条也使用数组。|

<h2 id="tocS_UpdateBookRequest">UpdateBookRequest</h2>

<a id="schemaupdatebookrequest"></a>
<a id="schema_UpdateBookRequest"></a>
<a id="tocSupdatebookrequest"></a>
<a id="tocsupdatebookrequest"></a>

```json
{
  "title": "百年孤独",
  "author": "加西亚·马尔克斯",
  "isbn": "9780307474728",
  "coverPath": "/uploads/covers/6d28c990.png",
  "intro": "一部围绕家族、时间与记忆展开的小说。",
  "status": "active"
}

```

管理员维护书籍；未提交字段保持不变。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|title|string|false|none||书名，规范化后 1～200 字符。|
|author|string|false|none||作者，规范化后 1～100 字符。|
|isbn|string¦null|false|none||有效 ISBN-10 或 ISBN-13，去除空格及连字符后校验；null 清空。|
|coverPath|string¦null|false|none||封面图片路径：先以 purpose=cover 上传，取 data.filePath；null 表示没有封面。|
|intro|string¦null|false|none||简介，去除首尾空白后 1～2000 字符；null 清空。|
|status|string|false|none||书籍状态：active（上架）、inactive（下架）。|

#### 枚举值

|属性|值|
|---|---|
|status|active|
|status|inactive|

<h2 id="tocS_NullData">NullData</h2>

<a id="schemanulldata"></a>
<a id="schema_NullData"></a>
<a id="tocSnulldata"></a>
<a id="tocsnulldata"></a>

```json
null

```

无内容，返回 null

### 属性

*None*

<h2 id="tocS_ErrorResponse">ErrorResponse</h2>

<a id="schemaerrorresponse"></a>
<a id="schema_ErrorResponse"></a>
<a id="tocSerrorresponse"></a>
<a id="tocserrorresponse"></a>

```json
{
  "code": 400,
  "data": null,
  "message": "操作失败"
}

```

业务失败。HTTP 仍为 200，按 code 和 message 处理。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|code|integer|true|none||400：操作失败，提示 message；401：未登录或 Token 无效、过期，重新登录。|
|data|[NullData](#schemanulldata)|true|none||无内容，返回 null|
|message|string|true|none||可直接展示的失败原因。|

#### 枚举值

|属性|值|
|---|---|
|code|400|
|code|401|

<h2 id="tocS_NoteSocial">NoteSocial</h2>

<a id="schemanotesocial"></a>
<a id="schema_NoteSocial"></a>
<a id="tocSnotesocial"></a>
<a id="tocsnotesocial"></a>

```json
{
  "noteId": 201,
  "likeCount": 0,
  "favoriteCount": 0,
  "commentCount": 0,
  "isLiked": false,
  "isFavorited": false
}

```

原笔记的点赞、收藏和评论状态，所有入口共用。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|noteId|integer|true|none||原笔记ID，不是漂流瓶ID。|
|likeCount|integer|true|none||笔记点赞人数；同一人只计一次。|
|favoriteCount|integer|true|none||笔记收藏人数，不返回收藏者列表。|
|commentCount|integer|true|none||未删除公开评论数，与漂流便签分开。|
|isLiked|boolean|true|none||当前登录用户是否已点赞：true 已点赞，false 未点赞。|
|isFavorited|boolean|true|none||当前登录用户是否已收藏：true 已收藏，false 未收藏。|

<h2 id="tocS_MatchItem">MatchItem</h2>

<a id="schemamatchitem"></a>
<a id="schema_MatchItem"></a>
<a id="tocSmatchitem"></a>
<a id="tocsmatchitem"></a>

```json
{
  "bottleId": 501,
  "author": {
    "userId": 2,
    "nickname": "晚风读者",
    "avatarPath": "/uploads/avatars/72d50b11.png"
  },
  "book": {
    "bookId": 101,
    "title": "百年孤独",
    "author": "加西亚·马尔克斯",
    "coverPath": "/uploads/covers/6d28c990.png",
    "status": "active"
  },
  "status": "active",
  "aiStatus": "ready",
  "createdAt": "2026-09-08T08:00:00Z",
  "expiresAt": "2026-09-15T08:00:00Z",
  "contentPreview": "我们总在回忆中重新理解时间。",
  "noteId": 202,
  "recommendation": "你们的文字都关注时间与记忆。",
  "matchScore": 86.5
}

```

所选单篇笔记的全池智能匹配结果，返回匹配度和推荐语，不表示已获取。二者随来源变化，不是瓶子固定属性。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|bottleId|integer|true|none||漂流瓶 ID。|
|author|[UserSummary](#schemausersummary)|true|none||公开笔记作者。|
|book|[BookSummary](#schemabooksummary)|true|none||书籍摘要。|
|status|string|true|none||漂流瓶状态：active（有效）、expired（过期）、withdrawn（已撤回）。|
|aiStatus|string|true|none||AI处理状态：pending待处理、processing处理中、ready就绪、failed失败；不是笔记reviewStatus审核结果。|
|createdAt|string(date-time)|true|none||审核通过且公开后，本次实际入池时间，UTC；不是提交审核时间。|
|expiresAt|string(date-time)|true|none||实际入池后7天，UTC。修改正文撤回旧瓶，新内容通过且公开后新建瓶子；AI重试不续期。|
|contentPreview|string|true|none||正文前 100 字符。|
|noteId|integer|true|none||该瓶原笔记ID，用于点赞、收藏、评论；不是匹配请求所选来源笔记ID。|
|recommendation|string¦null|true|none||AI概括来源笔记与本条候选共同主题的推荐语，1～100字符；生成失败为null，使用data.list[].recommendation。|
|matchScore|number|true|none||笔记内容匹配度，0～100，越高越相近；86.5前端显示86.5%，不是原始向量距离或交友成功概率。|

#### 枚举值

|属性|值|
|---|---|
|status|active|
|status|expired|
|status|withdrawn|
|aiStatus|pending|
|aiStatus|processing|
|aiStatus|ready|
|aiStatus|failed|

<h2 id="tocS_PageMatchItem">PageMatchItem</h2>

<a id="schemapagematchitem"></a>
<a id="schema_PageMatchItem"></a>
<a id="tocSpagematchitem"></a>
<a id="tocspagematchitem"></a>

```json
{
  "list": [
    {
      "bottleId": 501,
      "author": {
        "userId": 2,
        "nickname": "晚风读者",
        "avatarPath": "/uploads/avatars/72d50b11.png"
      },
      "book": {
        "bookId": 101,
        "title": "百年孤独",
        "author": "加西亚·马尔克斯",
        "coverPath": "/uploads/covers/6d28c990.png",
        "status": "active"
      },
      "status": "active",
      "aiStatus": "ready",
      "createdAt": "2026-09-08T08:00:00Z",
      "expiresAt": "2026-09-15T08:00:00Z",
      "contentPreview": "我们总在回忆中重新理解时间。",
      "noteId": 202,
      "recommendation": "你们的文字都关注时间与记忆。",
      "matchScore": 86.5
    }
  ],
  "total": 1,
  "pageNum": 1,
  "pageSize": 10
}

```

仅根据所选一篇笔记，在整个合格池按matchScore降序、同分bottleId降序后分页，不随机抽取；列表不产生获取记录。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|list|[[MatchItem](#schemamatchitem)]|true|none||当前页记录，没有结果时为空数组。|
|total|integer|true|none||完整合格候选池数量，不设最低分门槛，不是本页长度；页码超界保留实际total。|
|pageNum|integer|true|none||当前页码。|
|pageSize|integer|true|none||每页条数，默认10，范围1～100。|

<h2 id="tocS_Comment">Comment</h2>

<a id="schemacomment"></a>
<a id="schema_Comment"></a>
<a id="tocScomment"></a>
<a id="tocscomment"></a>

```json
{
  "commentId": 701,
  "noteId": 201,
  "author": {
    "userId": 1,
    "nickname": "山间读者",
    "avatarPath": "/uploads/avatars/9c1a2c77.png"
  },
  "content": "这段关于时间的理解很有意思。",
  "createdAt": "2026-09-08T08:00:00Z",
  "canDelete": true
}

```

原笔记的单层公开评论，不是漂流便签。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|commentId|integer|true|none||评论ID。|
|noteId|integer|true|none||原笔记ID。|
|author|[UserSummary](#schemausersummary)|true|none||对外用户摘要，不含邮箱和私人资料。|
|content|string|true|none||公开评论正文，纯文本，去除首尾空白后1～500字符。|
|createdAt|string(date-time)|true|none||评论发表时间，UTC。|
|canDelete|boolean|true|none||当前用户是否可删除：评论作者、笔记作者或管理员为true。|

<h2 id="tocS_PageComment">PageComment</h2>

<a id="schemapagecomment"></a>
<a id="schema_PageComment"></a>
<a id="tocSpagecomment"></a>
<a id="tocspagecomment"></a>

```json
{
  "list": [
    {
      "commentId": 701,
      "noteId": 201,
      "author": {
        "userId": 1,
        "nickname": "山间读者",
        "avatarPath": "/uploads/avatars/9c1a2c77.png"
      },
      "content": "这段关于时间的理解很有意思。",
      "createdAt": "2026-09-08T08:00:00Z",
      "canDelete": true
    }
  ],
  "total": 1,
  "pageNum": 1,
  "pageSize": 10
}

```

未删除评论分页列表。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|list|[[Comment](#schemacomment)]|true|none||当前页记录，没有结果时为空数组。|
|total|integer|true|none||筛选后全部结果数量，不是本页数量。|
|pageNum|integer|true|none||当前页码。|
|pageSize|integer|true|none||每页条数，默认10，范围1～100。|

<h2 id="tocS_CreateCommentRequest">CreateCommentRequest</h2>

<a id="schemacreatecommentrequest"></a>
<a id="schema_CreateCommentRequest"></a>
<a id="tocScreatecommentrequest"></a>
<a id="tocscreatecommentrequest"></a>

```json
{
  "content": "这段关于时间的理解很有意思。"
}

```

发表单层评论，不支持回复或楼中楼。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|content|string|true|none||公开评论正文，纯文本，去除首尾空白后1～500字符。|

<h2 id="tocS_ReviewNoteRequest">ReviewNoteRequest</h2>

<a id="schemareviewnoterequest"></a>
<a id="schema_ReviewNoteRequest"></a>
<a id="tocSreviewnoterequest"></a>
<a id="tocsreviewnoterequest"></a>

```json
{
  "reviewStatus": "approved",
  "reviewReason": null
}

```

管理员审核pending笔记。同结果及同原因重复成功，不重复入池；不能直接改判，修改正文后重新审核。

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|reviewStatus|string|true|none||approved通过，rejected拒绝，不能传pending。|
|reviewReason|string¦null|false|none||拒绝时必填去除首尾空白后1～500字符原因；通过时省略或null，不接受非空原因。|

oneOf

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|*anonymous*|object|false|none||none|
|» reviewStatus|string|false|none||none|
|» reviewReason|[NullData](#schemanulldata)|false|none||无内容，返回 null|

xor

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|*anonymous*|object|false|none||none|
|» reviewStatus|string|false|none||none|
|» reviewReason|string|true|none||none|

#### 枚举值

|属性|值|
|---|---|
|reviewStatus|approved|
|reviewStatus|rejected|
|reviewStatus|approved|
|reviewStatus|rejected|

