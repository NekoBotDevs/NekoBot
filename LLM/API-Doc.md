# API 文档

本文档提供了 **NekoBot** 的 API 接口 以及示例,以便更好的帮助LLM开发Dashboard。

## API 端口列举

### 主服务端口

- **6285** - 主服务端口,提供 Web 仪表盘和 API 接口
  - `/` - Web 仪表盘服务(静态文件)
  - `/api` - API 接口服务

### 适配器端口

以下是默认适配器端口,用于连接不同的聊天平台:

- **6294** - 企业微信(WeCom) Webhook 服务端口
- **6295** - 企业微信(WeCom) 反向 WebSocket 服务端口
- **6296** - QQ 官方接口(QQ Official API) Webhook 服务端口
- **6297** - Slack Webhook 服务端口
- **6299** - QQ(OneBot V11) 反向 WebSocket 服务端口

**注意**: 适配器端口根据配置可能会有所不同,以上为默认端口配置。各适配器端口主要用于:
- Webhook 端口: 接收来自第三方平台的消息推送
- WebSocket 端口: 建立与第三方平台的双向通信连接

## API 基础架构

### 认证方式

所有 API 接口均需要 JWT 认证:

- **认证方式**: Bearer Token
- **Token 类型**: JWT
- **Token 位置**: HTTP Header `Authorization: Bearer <token>`

### 响应格式

所有 API 接口均返回 JSON 格式数据:

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

### 错误码

| 错误码 | 说明 |
|------|------|
| 0 | 成功 |
| 401 | 未授权/Token无效 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## API 端点

### 认证相关

#### 用户登录

**POST** `/api/auth/login`

请求体:
```json
{
  "username": "nekobot",
  "password": "password"
}
```

响应:
```json
{
  "code": 0,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "username": "nekobot"
    }
  }
}
```

#### 修改密码

**POST** `/api/auth/change-password`

请求头:
```
Authorization: Bearer <token>
```

请求体:
```json
{
  "old_password": "old_password",
  "new_password": "new_password"
}
```

响应:
```json
{
  "code": 0,
  "message": "密码修改成功"
}
```

#### 初始化用户

**POST** `/api/auth/init`

用于首次使用时创建默认用户

请求体:
```json
{
  "username": "nekobot",
  "password": "new_password"
}
```

响应:
```json
{
  "code": 0,
  "message": "初始化成功"
}
```

### 插件管理

#### 获取插件列表

**GET** `/api/plugins`

请求头:
```
Authorization: Bearer <token>
```

响应:
```json
{
  "code": 0,
  "data": {
    "plugins": [
      {
        "name": "插件名称",
        "version": "1.0.0",
        "description": "插件描述",
        "author": "作者",
        "enabled": true,
        "is_official": false
      }
    ]
  }
}
```

#### 上传插件

**POST** `/api/plugins/upload`

请求头:
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

请求体:
- `file`: 插件 zip 文件

响应:
```json
{
  "code": 0,
  "message": "插件上传成功",
  "data": {
    "plugin_name": "plugin_name"
  }
}
```

#### 启用/禁用插件

**POST** `/api/plugins/{plugin_name}/toggle`

请求头:
```
Authorization: Bearer <token>
```

请求体:
```json
{
  "enabled": true
}
```

响应:
```json
{
  "code": 0,
  "message": "插件状态更新成功"
}
```

#### 卸载插件

**DELETE** `/api/plugins/{plugin_name}`

请求头:
```
Authorization: Bearer <token>
```

响应:
```json
{
  "code": 0,
  "message": "插件卸载成功"
}
```

#### 更新插件

**POST** `/api/plugins/{plugin_name}/update`

请求头:
```
Authorization: Bearer <token>
```

响应:
```json
{
  "code": 0,
  "message": "插件更新成功",
  "data": {
    "old_version": "1.0.0",
    "new_version": "1.0.1"
  }
}
```

### LLM/TTL 配置

#### 获取 LLM 配置列表

**GET** `/api/llm/providers`

请求头:
```
Authorization: Bearer <token>
```

响应:
```json
{
  "code": 0,
  "data": {
    "providers": [
      {
        "id": "provider_id",
        "name": "OpenAI",
        "type": "openai",
        "api_keys": ["sk-***"],
        "model": "gpt-4",
        "enabled": true
      }
    ]
  }
}
```

#### 添加 LLM 提供商

**POST** `/api/llm/providers`

请求头:
```
Authorization: Bearer <token>
```

请求体:
```json
{
  "name": "OpenAI",
  "type": "openai",
  "api_keys": ["sk-xxxxx"],
  "model": "gpt-4",
  "base_url": "https://api.openai.com/v1",
  "timeout": 60
}
```

响应:
```json
{
  "code": 0,
  "message": "LLM 提供商添加成功",
  "data": {
    "id": "provider_id"
  }
}
```

#### 更新 LLM 提供商

**PUT** `/api/llm/providers/{provider_id}`

请求头:
```
Authorization: Bearer <token>
```

请求体: (同添加接口)

响应:
```json
{
  "code": 0,
  "message": "LLM 提供商更新成功"
}
```

#### 删除 LLM 提供商

**DELETE** `/api/llm/providers/{provider_id}`

请求头:
```
Authorization: Bearer <token>
```

响应:
```json
{
  "code": 0,
  "message": "LLM 提供商删除成功"
}
```

### 提示词/人设配置

#### 获取提示词列表

**GET** `/api/prompts`

请求头:
```
Authorization: Bearer <token>
```

响应:
```json
{
  "code": 0,
  "data": {
    "prompts": [
      {
        "id": "prompt_id",
        "name": "默认提示词",
        "content": "你是一个友好的助手...",
        "created_at": "2025-01-01T00:00:00Z"
      }
    ]
  }
}
```

#### 创建提示词

**POST** `/api/prompts`

请求头:
```
Authorization: Bearer <token>
```

请求体:
```json
{
  "name": "提示词名称",
  "content": "提示词内容"
}
```

响应:
```json
{
  "code": 0,
  "message": "提示词创建成功",
  "data": {
    "id": "prompt_id"
  }
}
```

#### 上传提示词文件

**POST** `/api/prompts/upload`

请求头:
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

请求体:
- `file`: Markdown 或 txt 文件

响应:
```json
{
  "code": 0,
  "message": "提示词上传成功",
  "data": {
    "id": "prompt_id"
  }
}
```

### 日志管理

#### 获取日志

**GET** `/api/logs`

请求头:
```
Authorization: Bearer <token>
```

查询参数:
- `level`: 日志级别 (DEBUG/INFO/WARNING/ERROR/CRITICAL)
- `limit`: 返回条数 (默认 100)
- `search`: 搜索关键词

响应:
```json
{
  "code": 0,
  "data": {
    "logs": [
      {
        "timestamp": "2025-01-01T00:00:00Z",
        "level": "INFO",
        "message": "日志消息",
        "module": "nekobot.core"
      }
    ]
  }
}
```

#### 清除日志

**POST** `/api/logs/clear`

请求头:
```
Authorization: Bearer <token>
```

请求体:
```json
{
  "before_date": "2025-01-01T00:00:00Z"
}
```

响应:
```json
{
  "code": 0,
  "message": "日志清除成功",
  "data": {
    "deleted_count": 100
  }
}
```

#### 日志 WebSocket 实时推送

**WebSocket** `/api/logs/stream`

连接参数:
```
ws://localhost:6285/api/logs/stream?token=<jwt_token>
```

推送消息格式:
```json
{
  "timestamp": "2025-01-01T00:00:00Z",
  "level": "INFO",
  "message": "日志消息",
  "module": "nekobot.core"
}
```

### 系统管理

#### 获取系统状态

**GET** `/api/system/status`

请求头:
```
Authorization: Bearer <token>
```

响应:
```json
{
  "code": 0,
  "data": {
    "version": "1.0.0",
    "uptime": 3600,
    "cpu_usage": 25.5,
    "memory_usage": 512,
    "plugin_count": 5,
    "platform_count": 3
  }
}
```

#### 检查更新

**GET** `/api/system/check-update`

请求头:
```
Authorization: Bearer <token>
```

响应:
```json
{
  "code": 0,
  "data": {
    "current_version": "1.0.0",
    "latest_version": "1.0.1",
    "has_update": true,
    "changelog": "更新说明"
  }
}
```

#### 执行更新

**POST** `/api/system/update`

请求头:
```
Authorization: Bearer <token>
```

请求体:
```json
{
  "version": "1.0.1",
  "branch": "main"
}
```

响应:
```json
{
  "code": 0,
  "message": "更新任务已启动"
}
```

#### 重启系统

**POST** `/api/system/restart`

请求头:
```
Authorization: Bearer <token>
```

响应:
```json
{
  "code": 0,
  "message": "系统将在3秒后重启"
}
```

### MCP 服务配置

#### 获取 MCP 服务器列表

**GET** `/api/mcp/servers`

请求头:
```
Authorization: Bearer <token>
```

响应:
```json
{
  "code": 0,
  "data": {
    "servers": [
      {
        "name": "sequentialthinking",
        "enabled": true,
        "config": {}
      }
    ]
  }
}
```

#### 添加 MCP 服务器

**POST** `/api/mcp/servers`

请求头:
```
Authorization: Bearer <token>
```

请求体:
```json
{
  "name": "server_name",
  "enabled": true,
  "config": {
    "key": "value"
  }
}
```

响应:
```json
{
  "code": 0,
  "message": "MCP服务器添加成功"
}
```

#### 更新 MCP 服务器配置

**PUT** `/api/mcp/servers/{server_name}`

请求头:
```
Authorization: Bearer <token>
```

请求体:
```json
{
  "enabled": true,
  "config": {
    "key": "value"
  }
}
```

响应:
```json
{
  "code": 0,
  "message": "MCP 服务器配置更新成功"
}
```

#### 删除 MCP 服务器

**DELETE** `/api/mcp/servers/{server_name}`

请求头:
```
Authorization: Bearer <token>
```

响应:
```json
{
  "code": 0,
  "message": "MCP服务器删除成功"
}
```

### 平台适配器管理

#### 获取适配器列表

**GET** `/api/adapters`

请求头:
```
Authorization: Bearer <token>
```

响应:
```json
{
  "code": 0,
  "data": {
    "adapters": [
      {
        "name": "wecom",
        "running": true,
        "platform": "wecom",
        "config": {}
      }
    ]
  }
}
```

#### 启动适配器

**POST** `/api/adapters/{adapter_name}/start`

请求头:
```
Authorization: Bearer <token>
```

响应:
```json
{
  "code": 0,
  "message": "适配器启动成功"
}
```

#### 停止适配器

**POST** `/api/adapters/{adapter_name}/stop`

请求头:
```
Authorization: Bearer <token>
```

响应:
```json
{
  "code": 0,
  "message": "适配器停止成功"
}
```

#### 更新适配器配置

**PUT** `/api/adapters/{adapter_name}/config`

请求头:
```
Authorization: Bearer <token>
```

请求体:
```json
{
  "config": {
    "key": "value"
  }
}
```

响应:
```json
{
  "code": 0,
  "message": "配置更新成功"
}
```

## 支持的平台适配器

| 适配器名称 | 平台 | 协议类型 | 默认端口 |
|----------|------|---------|---------|
| wecom | 企业微信 | Webhook | 6294 |
| aiocqhttp | QQ | WebSocket (OneBot V11) | 6299 |
| qqofficial | QQ官方接口 | Webhook | 6296 |
| slack | Slack | Webhook | 6297 |

## 注意事项

1. 所有 API 接口均需要通过 JWT 认证
2. JWT Token 有效期为 24 小时
3. 初次登录需使用默认账户密码(均为 `nekobot`),并强制修改密码
4. 文件上传接口支持的最大文件大小为 50MB
5. WebSocket 连接需要在 URL 参数中传递 JWT Token
6. 所有时间戳均使用 ISO 8601 UTC 格式
7. API 接口遵循 RESTful 设计规范
8. 平台适配器需要在配置文件中正确设置相关参数才能启动
9. 每个适配器监听独立的端口,确保端口不冲突
