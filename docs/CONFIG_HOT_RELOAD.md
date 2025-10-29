# 配置热重载使用指南

NekoBot 支持配置文件的热重载功能，可以在不重启服务的情况下动态更新配置。

## 功能特性

- ✅ **自动监控** - 自动监控配置文件变化
- ✅ **热重载** - 配置变更自动生效，无需重启
- ✅ **变更通知** - 配置变更时通知相关组件
- ✅ **回调机制** - 支持注册自定义配置变更处理器
- ✅ **线程安全** - 使用文件锁保证并发安全

---

## 基础使用

### 1. 获取配置管理器

```python
from nekobot.config.manager import get_config_manager

# 获取配置管理器（自动启动文件监控）
config_manager = get_config_manager()
```

### 2. 读取配置

```python
# 读取配置项（支持点号分隔的嵌套键）
host = config_manager.get("server.host")
port = config_manager.get("server.port", 6285)  # 带默认值

# 读取所有配置
all_config = config_manager.get_all()
```

### 3. 修改配置

```python
# 设置配置项
config_manager.set("bot.command_prefix", "!")

# 批量更新
config_manager.update({
    "bot": {
        "command_prefix": "!",
        "admin_users": [123456, 789012]
    }
})

# 删除配置项
config_manager.delete("bot.some_key")
```

### 4. 手动重载

```python
# 手动重新加载配置文件
config_manager.reload()
```

---

## 配置变更回调

### 注册回调函数

```python
from nekobot.config.manager import get_config_manager

config_manager = get_config_manager()

# 同步回调
def on_config_change(old_config, new_config):
    print("配置已变更")
    print(f"旧值: {old_config}")
    print(f"新值: {new_config}")

# 异步回调
async def async_on_config_change(old_config, new_config):
    print("配置已变更（异步）")
    # 执行异步操作
    await some_async_operation()

# 注册回调
config_manager.on_config_change(on_config_change)
config_manager.on_config_change(async_on_config_change)
```

### 移除回调

```python
config_manager.remove_callback(on_config_change)
```

---

## 文件监控

### 启动监控

```python
# 自动启动（初始化时自动启动）
config_manager = get_config_manager()

# 手动启动
config_manager.start_watching()
```

### 停止监控

```python
config_manager.stop_watching()
```

### 禁用自动监控

```python
from nekobot.config.manager import NekoConfigManager

# 创建配置管理器但不启动监控
config_manager = NekoConfigManager(auto_reload=False)
```

---

## 热重载管理器

NekoBot 内置了热重载管理器，自动处理常见配置的变更。

### 自动处理的配置

1. **服务器配置** (`server.*`)
   - 端口变更提示
   - CORS 配置更新

2. **日志配置** (`logging.*`)
   - 日志级别动态调整
   - 历史记录限制更新

3. **机器人配置** (`bot.*`)
   - 命令前缀更新
   - 管理员列表更新

### 使用示例

```python
from nekobot.config.hot_reload import get_hot_reload_manager

# 获取热重载管理器（自动注册内置处理器）
hot_reload_manager = get_hot_reload_manager()
```

---

## 完整示例

### 示例 1: 监控配置变更

```python
import asyncio
from nekobot.config.manager import get_config_manager
from nekobot.utils.logger import get_logger

logger = get_logger("example")

async def on_prefix_change(old_config, new_config):
    """监控命令前缀变更"""
    old_prefix = old_config.get("bot", {}).get("command_prefix")
    new_prefix = new_config.get("bot", {}).get("command_prefix")
    
    if old_prefix != new_prefix:
        logger.info(f"命令前缀已变更: {old_prefix} -> {new_prefix}")
        # 执行相关操作，如通知所有插件

async def main():
    config_manager = get_config_manager()
    config_manager.on_config_change(on_prefix_change)
    
    logger.info("配置监控已启动")
    logger.info(f"配置文件: {config_manager.config_file}")
    
    # 保持运行
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
```

### 示例 2: 动态调整日志级别

```python
import logging
from nekobot.config.manager import get_config_manager

config_manager = get_config_manager()

async def on_logging_change(old_config, new_config):
    """动态调整日志级别"""
    new_level = new_config.get("logging", {}).get("level", "INFO")
    
    # 更新日志级别
    logging.getLogger("nekobot").setLevel(
        getattr(logging, new_level.upper())
    )
    print(f"日志级别已调整为: {new_level}")

config_manager.on_config_change(on_logging_change)
```

### 示例 3: 自定义配置处理

```python
from nekobot.config.manager import get_config_manager

config_manager = get_config_manager()

class MyFeature:
    def __init__(self):
        self.enabled = config_manager.get("my_feature.enabled", False)
        
        # 注册配置变更监听
        config_manager.on_config_change(self.on_config_change)
    
    async def on_config_change(self, old_config, new_config):
        """处理配置变更"""
        old_enabled = old_config.get("my_feature", {}).get("enabled", False)
        new_enabled = new_config.get("my_feature", {}).get("enabled", False)
        
        if old_enabled != new_enabled:
            self.enabled = new_enabled
            
            if self.enabled:
                await self.start()
            else:
                await self.stop()
    
    async def start(self):
        print("功能已启用")
    
    async def stop(self):
        print("功能已禁用")
```

---

## 配置文件格式

配置文件位于 `./data/config.json`，使用 JSON 格式：

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 6285,
    "cors_origins": ["http://localhost:6285"]
  },
  "logging": {
    "level": "INFO",
    "max_history": 1000
  },
  "bot": {
    "command_prefix": "/",
    "admin_users": []
  },
  "security": {
    "jwt_secret": "...",
    "jwt_algorithm": "HS256",
    "jwt_expire_hours": 24
  }
}
```

---

## 注意事项

### 1. 需要重启的配置

某些配置变更需要重启服务才能生效：

- ✅ **无需重启**
  - 日志级别 (`logging.level`)
  - 命令前缀 (`bot.command_prefix`)
  - 管理员列表 (`bot.admin_users`)

- ⚠️ **需要重启**
  - 服务器端口 (`server.port`)
  - 服务器地址 (`server.host`)
  - JWT 密钥 (`security.jwt_secret`)

### 2. 文件锁

配置文件使用文件锁保证并发安全，避免多个进程同时写入。

### 3. 变更延迟

文件监控检测到变化后会延迟 0.1 秒再加载，避免文件未写入完成。

### 4. 回调异常

如果回调函数执行失败，不会影响其他回调和配置加载。

---

## API 参考

### NekoConfigManager

#### 方法

- `get(key, default=None)` - 获取配置值
- `set(key, value, save=True)` - 设置配置值
- `delete(key, save=True)` - 删除配置项
- `get_all()` - 获取所有配置
- `update(config, save=True)` - 批量更新配置
- `reload()` - 手动重载配置
- `reset_to_default()` - 重置为默认配置
- `on_config_change(callback)` - 注册变更回调
- `remove_callback(callback)` - 移除回调
- `start_watching()` - 启动文件监控
- `stop_watching()` - 停止文件监控

### ConfigHotReloadManager

#### 方法

自动处理内置配置的变更，无需手动调用。

---

## 故障排查

### 问题1: 配置变更未生效

**解决方案**:
1. 检查配置文件格式是否正确（JSON）
2. 查看日志是否有加载错误
3. 确认配置项路径正确
4. 某些配置需要重启服务

### 问题2: 文件监控未启动

**解决方案**:
1. 确认 `auto_reload=True`（默认）
2. 检查 `watchfiles` 是否已安装
3. 查看日志确认监控状态

### 问题3: 回调未执行

**解决方案**:
1. 确认回调已注册
2. 检查回调函数签名正确
3. 查看日志中的异常信息

---

## 更新日志

### v1.0.0
- 初始版本
- 支持基本的配置热重载
- 文件监控
- 回调通知机制

---

**配置热重载让您的 NekoBot 更加灵活！**

