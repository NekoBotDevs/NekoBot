# 配置热重载 - 快速开始

## 什么是配置热重载？

配置热重载允许您在**不重启服务**的情况下动态更新配置，系统会自动检测配置文件的变化并重新加载。

## 快速体验

### 1. 启动 NekoBot

```bash
python main.py
```

你会看到类似的日志：

```
2025-10-29 12:00:00 [INFO] config - 配置文件加载成功: ./data/config.json
2025-10-29 12:00:01 [INFO] config - 配置文件监控已启动: ./data/config.json
2025-10-29 12:00:02 [INFO] bot - 配置热重载已启用
```

### 2. 修改配置文件

打开 `./data/config.json`，修改任意配置项，例如：

```json
{
  "bot": {
    "command_prefix": "!"  // 从 "/" 改为 "!"
  }
}
```

### 3. 观察日志

保存文件后，你会立即看到：

```
2025-10-29 12:05:00 [INFO] config - 检测到配置文件变化
2025-10-29 12:05:00 [INFO] config - 配置已重新加载，检测到变更
2025-10-29 12:05:00 [INFO] hot_reload - 命令前缀已变更: / -> !
```

**不需要重启，配置已生效！**

## 主要功能

### ✅ 自动监控
- 系统自动监控 `./data/config.json` 文件
- 文件变化时自动重新加载
- 无需手动操作

### ✅ 变更通知
- 配置变更时自动通知相关组件
- 支持注册自定义回调函数
- 异步回调支持

### ✅ 动态生效
以下配置无需重启即可生效：

- 日志级别 (`logging.level`)
- 命令前缀 (`bot.command_prefix`)
- 管理员列表 (`bot.admin_users`)
- CORS 配置 (`server.cors_origins`)

### ⚠️ 需要重启的配置

- 服务器端口 (`server.port`)
- 服务器地址 (`server.host`)
- JWT 密钥 (`security.jwt_secret`)

## 实用示例

### 示例 1: 动态调整日志级别

1. 启动 NekoBot
2. 编辑 `./data/config.json`:

```json
{
  "logging": {
    "level": "DEBUG"  // 改为 DEBUG 查看更详细的日志
  }
}
```

3. 保存后日志级别立即生效，无需重启

### 示例 2: 更改命令前缀

1. 编辑配置:

```json
{
  "bot": {
    "command_prefix": "!"
  }
}
```

2. 保存后，机器人命令前缀从 `/` 变为 `!`
3. 现在使用 `!help` 而不是 `/help`

### 示例 3: 添加管理员

```json
{
  "bot": {
    "admin_users": [123456789, 987654321]
  }
}
```

保存后管理员列表立即更新。

## 自定义配置变更处理

如果你需要在配置变更时执行自定义操作：

```python
from nekobot.config.manager import get_config_manager

config_manager = get_config_manager()

# 注册回调
async def on_my_config_change(old_config, new_config):
    if old_config.get("my_feature") != new_config.get("my_feature"):
        print("我的功能配置已变更")
        # 执行相应操作

config_manager.on_config_change(on_my_config_change)
```

## 手动重载

如果需要手动触发配置重载：

```python
from nekobot.config.manager import get_config_manager

config_manager = get_config_manager()
config_manager.reload()
```

或通过 API：

```bash
curl -X POST http://localhost:6285/api/config/reload \
  -H "Authorization: Bearer <your_token>"
```

## 测试配置热重载

运行测试示例：

```bash
python examples/config_hot_reload_example.py
```

然后编辑 `./data/config.json` 观察效果。

## 故障排查

### 配置未自动重载？

1. 检查日志，确认监控已启动
2. 确认文件路径正确：`./data/config.json`
3. 检查 JSON 格式是否正确
4. 查看是否有错误日志

### 如何禁用自动监控？

编辑代码（不推荐）：

```python
from nekobot.config.manager import NekoConfigManager

config_manager = NekoConfigManager(auto_reload=False)
```

## 下一步

查看完整文档：[CONFIG_HOT_RELOAD.md](CONFIG_HOT_RELOAD.md)

---

**配置热重载让 NekoBot 更加灵活和易用！**

