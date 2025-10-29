# NapCat 平台适配器

用于对接 QQ 个人号的 NapCat 适配器，基于 OneBot V11 协议。

## 功能特性

- ✅ 发送群消息和私聊消息
- ✅ 接收消息事件
- ✅ 群管理功能（禁言、踢人、设置名片等）
- ✅ 获取群列表、好友列表
- ✅ 消息撤回
- ✅ 支持多种消息类型（文本、图片、@、回复等）
- ✅ WebSocket 事件监听

## 配置说明

### HTTP API 配置

```python
config = {
    "host": "localhost",        # NapCat HTTP API 地址
    "port": 3000,               # NapCat HTTP API 端口
    "access_token": "your_token"  # 访问令牌（可选）
}
```

### WebSocket 配置

```python
config = {
    "ws_host": "0.0.0.0",      # WebSocket 服务器地址
    "ws_port": 6299,            # WebSocket 服务器端口
    "access_token": "your_token"  # 访问令牌（需与 NapCat 配置一致）
}
```

## 使用示例

### 1. 初始化适配器

```python
from nekobot.core.platform.sources.napcat.napcat_adapter import NapCatAdapter

# 创建适配器
adapter = NapCatAdapter({
    "host": "localhost",
    "port": 3000,
    "access_token": "your_token"
})

# 连接
await adapter.connect()
```

### 2. 发送消息

#### 发送文本消息

```python
# 发送群消息
message = adapter.build_text_message("Hello, World!")
await adapter.send_group_msg(group_id=123456789, message=message)

# 发送私聊消息
await adapter.send_private_msg(user_id=987654321, message=message)
```

#### 发送图片消息

```python
# 通过文件路径
image_msg = adapter.build_image_message("file:///path/to/image.jpg")

# 通过 URL
image_msg = adapter.build_image_message("https://example.com/image.png")

await adapter.send_group_msg(group_id=123456789, message=image_msg)
```

#### 发送混合消息

```python
# 发送 @ + 文本
message = adapter.build_mixed_message(
    adapter.build_at_message(qq=987654321),
    adapter.build_text_message(" 你好！")
)
await adapter.send_group_msg(group_id=123456789, message=message)

# 发送回复 + 文本 + 图片
message = adapter.build_mixed_message(
    adapter.build_reply_message(message_id=123456),
    adapter.build_text_message("这是一张图片："),
    adapter.build_image_message("https://example.com/image.png")
)
await adapter.send_group_msg(group_id=123456789, message=message)
```

### 3. 接收消息

#### 启动 WebSocket 服务器

```python
from nekobot.core.platform.sources.napcat.napcat_server import NapCatWebSocketServer

# 创建服务器
server = NapCatWebSocketServer(
    host="0.0.0.0",
    port=6299,
    access_token="your_token"
)

# 注册消息处理器
@server.on_message
async def handle_message(event):
    print(f"收到消息: {event.get_plain_text()}")
    
    # 群消息
    if event.is_group_message():
        print(f"来自群: {event.group_id}")
        
    # 私聊消息
    elif event.is_private_message():
        print(f"来自用户: {event.user_id}")

# 启动服务器
await server.run()
```

### 4. 群管理

#### 禁言

```python
# 禁言 10 分钟
await adapter.set_group_ban(
    group_id=123456789,
    user_id=987654321,
    duration=600
)

# 解除禁言
await adapter.set_group_ban(
    group_id=123456789,
    user_id=987654321,
    duration=0
)
```

#### 踢出群成员

```python
await adapter.set_group_kick(
    group_id=123456789,
    user_id=987654321,
    reject_add_request=False  # 是否拒绝再次加群
)
```

#### 设置群名片

```python
await adapter.set_group_card(
    group_id=123456789,
    user_id=987654321,
    card="新名片"
)
```

### 5. 获取信息

#### 获取登录信息

```python
info = await adapter.get_login_info()
print(f"QQ: {info['user_id']}, 昵称: {info['nickname']}")
```

#### 获取群列表

```python
groups = await adapter.get_group_list()
for group in groups:
    print(f"群号: {group['group_id']}, 群名: {group['group_name']}")
```

#### 获取好友列表

```python
friends = await adapter.get_friend_list()
for friend in friends:
    print(f"QQ: {friend['user_id']}, 昵称: {friend['nickname']}")
```

## 消息事件结构

### 群消息事件

```python
{
    "post_type": "message",
    "message_type": "group",
    "sub_type": "normal",
    "message_id": 123456,
    "group_id": 123456789,
    "user_id": 987654321,
    "anonymous": None,
    "message": [
        {"type": "text", "data": {"text": "Hello"}}
    ],
    "raw_message": "Hello",
    "font": 0,
    "sender": {
        "user_id": 987654321,
        "nickname": "张三",
        "card": "群名片",
        "sex": "male",
        "age": 25,
        "area": "地区",
        "level": "等级",
        "role": "member",
        "title": "头衔"
    }
}
```

### 私聊消息事件

```python
{
    "post_type": "message",
    "message_type": "private",
    "sub_type": "friend",
    "message_id": 123456,
    "user_id": 987654321,
    "message": [
        {"type": "text", "data": {"text": "Hello"}}
    ],
    "raw_message": "Hello",
    "font": 0,
    "sender": {
        "user_id": 987654321,
        "nickname": "张三",
        "sex": "male",
        "age": 25
    }
}
```

## NapCat 配置

在 NapCat 的配置文件中，需要配置反向 WebSocket：

```json
{
  "http": {
    "enable": true,
    "host": "0.0.0.0",
    "port": 3000,
    "secret": "",
    "enableHeart": true,
    "enablePost": false
  },
  "ws": {
    "enable": false
  },
  "reverseWs": {
    "enable": true,
    "urls": [
      "ws://127.0.0.1:6299/"
    ]
  }
}
```

## 注意事项

1. **端口配置**: 确保 NapCat 的 HTTP API 端口和 WebSocket 端口与适配器配置一致
2. **访问令牌**: 如果设置了 access_token，需要在 NapCat 和适配器中保持一致
3. **消息格式**: 使用 OneBot V11 消息段格式，详见 [OneBot V11 文档](https://github.com/botuniverse/onebot-11)
4. **权限**: 部分 API 需要管理员或群主权限

## API 参考

完整的 API 列表请参考 [NapCat API 文档](https://napneko.github.io/zh-CN/)

## 故障排查

### 无法连接到 NapCat

1. 检查 NapCat 是否已启动
2. 检查 host 和 port 配置是否正确
3. 检查防火墙设置

### 收不到消息事件

1. 检查 WebSocket 服务器是否已启动
2. 检查 NapCat 的反向 WebSocket 配置
3. 检查 access_token 是否正确
4. 查看日志输出

### 发送消息失败

1. 检查消息格式是否正确
2. 检查 API 返回的错误信息
3. 确认机器人账号是否有发送权限

## 更新日志

### v1.0.0 (2025-10-29)
- 初始版本
- 支持基本的消息收发
- 支持群管理功能
- 支持 WebSocket 事件监听

