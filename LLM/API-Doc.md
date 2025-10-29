# NekoBot API 文档

本文档提供了 **NekoBot** 的完整 API 接口说明，以便前端仪表盘（Dashboard）调用。

## 基础信息

- **基础路径**: `/api`
- **认证方式**: JWT (Bearer Token)
- **数据格式**: JSON
- **字符编码**: UTF-8

### 认证说明

除登录和版本查询接口外，所有 API 均需要在 HTTP 请求头中携带 JWT Token：

```
Authorization: Bearer <your_jwt_token>
```

## WebSocket 实时日志

### 连接地址

```
ws://<host>:<port>/ws
```

### 连接说明

- 连接后会立即推送最近 100 条历史日志
- 之后实时推送所有新日志
- 支持心跳检测（客户端发送 "ping"，服务端返回 {"type": "pong"}）

### 日志格式

```json
{
  "timestamp": "2025-10-29T12:34:56.789",
  "level": "INFO",
  "message": "日志消息内容",
  "module": "模块名称",
  "line": 123
}
```

---

## API 端点列表

### 1. 认证相关 (`/api/auth`)

#### 1.1 用户登录

**接口**: `POST /api/auth/login`

**请求体**:
```json
{
  "username": "nekobot",
  "password": "your_password"
}
```

**响应**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "username": "nekobot",
  "must_change_password": false
}
```

**状态码**:
- 200: 登录成功
- 400: 参数错误
- 401: 用户名或密码错误
- 403: 用户已被禁用

---

#### 1.2 修改密码

**接口**: `POST /api/auth/change-password`

**认证**: 需要

**请求体**:
```json
{
  "old_password": "old_password",
  "new_password": "new_password"
}
```

**响应**:
```json
{
  "message": "密码修改成功，请重新登录"
}
```

**状态码**:
- 200: 修改成功
- 400: 参数错误
- 401: 旧密码错误

**注意**: 修改密码后所有旧 Token 将失效，需要重新登录。

---

#### 1.3 获取用户信息

**接口**: `GET /api/auth/profile`

**认证**: 需要

**响应**:
```json
{
  "username": "nekobot",
  "is_active": true,
  "must_change_password": false,
  "created_at": "2025-10-29T12:00:00"
}
```

---

### 2. 插件管理 (`/api/plugins`)

#### 2.1 获取插件列表

**接口**: `GET /api/plugins/list`

**认证**: 需要

**响应**:
```json
{
  "plugins": [
    {
      "name": "NekoBot_Plugins_Example",
      "version": "1.0.0",
      "description": "示例插件",
      "author": "NekoBotDevs",
      "repository": "https://github.com/NekoBotDevs/NekoBot_Plugins_Example",
      "is_enabled": true
    }
  ]
}
```

---

#### 2.2 启用插件

**接口**: `POST /api/plugins/<plugin_name>/enable`

**认证**: 需要

**响应**:
```json
{
  "message": "插件已启用"
}
```

---

#### 2.3 禁用插件

**接口**: `POST /api/plugins/<plugin_name>/disable`

**认证**: 需要

**响应**:
```json
{
  "message": "插件已禁用"
}
```

---

#### 2.4 重载插件

**接口**: `POST /api/plugins/<plugin_name>/reload`

**认证**: 需要

**响应**:
```json
{
  "message": "插件已重载"
}
```

---

#### 2.5 卸载插件

**接口**: `DELETE /api/plugins/<plugin_name>/uninstall`

**认证**: 需要

**响应**:
```json
{
  "message": "插件已卸载"
}
```

---

#### 2.6 上传插件

**接口**: `POST /api/plugins/upload`

**认证**: 需要

**请求类型**: `multipart/form-data`

**参数**:
- `file`: ZIP 格式插件压缩包

**响应**:
```json
{
  "message": "插件安装成功"
}
```

---

### 3. LLM 管理 (`/api/llm`)

#### 3.1 获取服务商列表

**接口**: `GET /api/llm/providers`

**认证**: 需要

**响应**:
```json
{
  "providers": [
    {
      "name": "openai-gpt4",
      "model": "gpt-4",
      "base_url": "https://api.openai.com/v1",
      "api_key_count": 2
    }
  ]
}
```

---

#### 3.2 添加服务商

**接口**: `POST /api/llm/providers`

**认证**: 需要

**请求体**:
```json
{
  "name": "openai-gpt4",
  "provider_type": "openai",
  "api_keys": ["sk-..."],
  "model": "gpt-4",
  "base_url": "https://api.openai.com/v1",
  "config": {
    "temperature": 0.7,
    "max_tokens": 2000
  }
}
```

**provider_type** 支持的值:
- `openai`: OpenAI 格式
- `anthropic`: Anthropic (Claude)
- `google`: Google (Gemini)
- `custom`: 自定义（兼容 OpenAI 格式）

**响应**:
```json
{
  "message": "服务商添加成功"
}
```

---

#### 3.3 删除服务商

**接口**: `DELETE /api/llm/providers/<provider_name>`

**认证**: 需要

**响应**:
```json
{
  "message": "服务商已移除"
}
```

---

#### 3.4 测试服务商连接

**接口**: `POST /api/llm/providers/<provider_name>/test`

**认证**: 需要

**响应**:
```json
{
  "message": "连接测试成功"
}
```

---

#### 3.5 与 LLM 对话

**接口**: `POST /api/llm/chat`

**认证**: 需要

**请求体**:
```json
{
  "provider": "openai-gpt4",
  "messages": [
    {
      "role": "system",
      "content": "你是一个有帮助的助手"
    },
    {
      "role": "user",
      "content": "你好"
    }
  ]
}
```

**响应**:
```json
{
  "content": "你好！有什么我可以帮助你的吗？",
  "model": "gpt-4",
  "usage": {
    "prompt_tokens": 20,
    "completion_tokens": 15,
    "total_tokens": 35
  }
}
```

---

### 4. 配置管理 (`/api/config`)

#### 4.1 获取配置

**接口**: `GET /api/config/`

**认证**: 需要

**响应**:
```json
{
  "config": {
    "server": {
      "host": "0.0.0.0",
      "port": 6285,
      "cors_origins": ["*"]
    },
    "security": {
      "jwt_secret": "***",
      "jwt_algorithm": "***"
    },
    "bot": {
      "command_prefix": "/"
    }
  }
}
```

**注意**: 安全相关配置会被脱敏显示。

---

#### 4.2 更新配置

**接口**: `PUT /api/config/`

**认证**: 需要

**请求体**:
```json
{
  "key": "bot.command_prefix",
  "value": "!"
}
```

**响应**:
```json
{
  "message": "配置已更新"
}
```

---

#### 4.3 重新加载配置

**接口**: `POST /api/config/reload`

**认证**: 需要

**响应**:
```json
{
  "message": "配置已重新加载"
}
```

---

### 5. 系统信息 (`/api/system`)

#### 5.1 获取系统信息

**接口**: `GET /api/system/info`

**认证**: 需要

**响应**:
```json
{
  "version": "1.0.0",
  "cpu_percent": 15.2,
  "memory_percent": 45.8,
  "memory_total_gb": 16.0,
  "memory_used_gb": 7.3,
  "disk_percent": 62.5,
  "disk_total_gb": 500.0,
  "disk_used_gb": 312.5
}
```

---

#### 5.2 获取版本信息

**接口**: `GET /api/system/version`

**认证**: 不需要

**响应**:
```json
{
  "version": "1.0.0"
}
```

---

## 错误响应格式

所有错误响应都遵循以下格式：

```json
{
  "error": "错误描述信息"
}
```

常见状态码：
- `400`: 请求参数错误
- `401`: 未授权或认证失败
- `403`: 禁止访问
- `404`: 资源不存在
- `500`: 服务器内部错误

---

## 使用示例

### JavaScript (Fetch API)

```javascript
// 登录
const loginResponse = await fetch('http://localhost:6285/api/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    username: 'nekobot',
    password: 'nekobot'
  })
});

const { token } = await loginResponse.json();

// 使用 Token 调用其他 API
const pluginsResponse = await fetch('http://localhost:6285/api/plugins/list', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const { plugins } = await pluginsResponse.json();
console.log(plugins);
```

### Python (requests)

```python
import requests

# 登录
login_response = requests.post(
    'http://localhost:6285/api/auth/login',
    json={'username': 'nekobot', 'password': 'nekobot'}
)

token = login_response.json()['token']

# 使用 Token 调用其他 API
plugins_response = requests.get(
    'http://localhost:6285/api/plugins/list',
    headers={'Authorization': f'Bearer {token}'}
)

plugins = plugins_response.json()['plugins']
print(plugins)
```

---

## WebSocket 使用示例

### JavaScript

```javascript
const ws = new WebSocket('ws://localhost:6285/ws');

ws.onopen = () => {
  console.log('WebSocket 已连接');
  
  // 发送心跳
  setInterval(() => {
    ws.send('ping');
  }, 30000);
};

ws.onmessage = (event) => {
  const log = JSON.parse(event.data);
  console.log(`[${log.level}] ${log.message}`);
};

ws.onerror = (error) => {
  console.error('WebSocket 错误:', error);
};

ws.onclose = () => {
  console.log('WebSocket 已断开');
};
```

---

## 注意事项

1. **默认账户**: 首次启动后，默认用户名和密码均为 `nekobot`，登录后会强制要求修改密码
2. **Token 过期**: JWT Token 默认 24 小时过期，需要重新登录
3. **CORS**: 默认允许所有域名访问，生产环境请在配置中限制 `cors_origins`
4. **端口**: 默认端口为 6285，可在配置文件中修改
5. **安全**: 生产环境请使用 HTTPS 和强密码

---

## 更新日志

### v1.0.0 (2025-10-29)

- 初始版本发布
- 完整的 REST API 实现
- WebSocket 实时日志推送
- JWT 认证系统
- 插件管理系统
- LLM 服务商管理
