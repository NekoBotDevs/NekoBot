# 配置热重载实现说明

## 概述

为 NekoBot 实现了完整的配置热重载功能，支持配置文件的实时监控和自动更新，无需重启服务即可使配置变更生效。

---

## 实现的功能

### 1. 文件监控 (`nekobot/config/manager.py`)

使用 `watchfiles` 库实现配置文件的实时监控：

```python
async def _watch_config_file(self):
    """监控配置文件变化"""
    try:
        async for changes in awatch(str(self.config_file)):
            logger.info(f"检测到配置文件变化: {changes}")
            await asyncio.sleep(0.1)  # 延迟避免文件写入未完成
            self.reload()
    except asyncio.CancelledError:
        logger.info("配置文件监控已取消")
```

**特性:**
- 自动检测文件变化
- 异步实现，不阻塞主线程
- 延迟加载避免文件写入冲突
- 支持手动启动/停止监控

### 2. 热重载机制

配置变更时自动重新加载并通知订阅者：

```python
def reload(self):
    """重新加载配置"""
    old_config = self._config.copy()
    self._load_config()
    
    if old_config != self._config:
        logger.info("配置已重新加载，检测到变更")
        self._notify_callbacks(old_config, self._config)
```

**特性:**
- 检测配置差异
- 保存旧配置用于对比
- 自动通知所有订阅者

### 3. 回调通知系统

支持注册自定义回调函数处理配置变更：

```python
def on_config_change(self, callback: Callable):
    """注册配置变更回调函数"""
    if callback not in self._callbacks:
        self._callbacks.append(callback)

def _notify_callbacks(self, old_config: Dict, new_config: Dict):
    """通知所有回调函数"""
    for callback in self._callbacks:
        try:
            if asyncio.iscoroutinefunction(callback):
                asyncio.create_task(callback(old_config, new_config))
            else:
                callback(old_config, new_config)
        except Exception as e:
            logger.error(f"回调执行失败: {e}")
```

**特性:**
- 支持同步和异步回调
- 异常隔离，不影响其他回调
- 可注册多个回调函数

### 4. 内置配置处理器 (`nekobot/config/hot_reload.py`)

自动处理常见配置的变更：

```python
class ConfigHotReloadManager:
    """配置热重载管理器"""
    
    async def on_logging_config_change(self, old_config, new_config):
        """动态调整日志级别"""
        new_level = new_config.get("logging", {}).get("level", "INFO")
        logging.getLogger("nekobot").setLevel(
            getattr(logging, new_level.upper())
        )
```

**处理的配置:**
- 服务器配置（端口、CORS）
- 日志级别（动态调整）
- 机器人配置（命令前缀、管理员）

### 5. 核心集成 (`nekobot/core/bot.py`)

在主控制器中集成热重载管理器：

```python
class NekoBotCore:
    def __init__(self):
        self.config_manager = get_config_manager()
        self.hot_reload_manager = get_hot_reload_manager()  # 新增
        # ...
        logger.info("配置热重载已启用")
    
    async def shutdown(self):
        self.config_manager.stop_watching()  # 关闭时停止监控
```

---

## 技术实现

### 依赖库

```python
from watchfiles import awatch  # 文件监控
from filelock import FileLock   # 文件锁
import asyncio                  # 异步支持
```

### 核心类

#### NekoConfigManager

**主要方法:**

| 方法 | 说明 |
|------|------|
| `__init__(config_dir, auto_reload)` | 初始化配置管理器 |
| `get(key, default)` | 获取配置值 |
| `set(key, value, save)` | 设置配置值 |
| `reload()` | 手动重载配置 |
| `on_config_change(callback)` | 注册变更回调 |
| `start_watching()` | 启动文件监控 |
| `stop_watching()` | 停止文件监控 |

**新增属性:**

| 属性 | 类型 | 说明 |
|------|------|------|
| `_callbacks` | `List[Callable]` | 回调函数列表 |
| `_watch_task` | `Optional[asyncio.Task]` | 监控任务 |
| `_auto_reload` | `bool` | 是否自动重载 |

#### ConfigHotReloadManager

**回调处理器:**

- `on_server_config_change()` - 服务器配置变更
- `on_logging_config_change()` - 日志配置变更
- `on_bot_config_change()` - 机器人配置变更

---

## 使用示例

### 基础使用

```python
from nekobot.config.manager import get_config_manager

# 获取配置管理器（自动启动监控）
config_manager = get_config_manager()

# 读取配置
port = config_manager.get("server.port", 6285)

# 修改配置
config_manager.set("bot.command_prefix", "!")

# 手动重载
config_manager.reload()
```

### 注册自定义回调

```python
async def my_handler(old_config, new_config):
    """自定义配置变更处理"""
    if old_config.get("my_key") != new_config.get("my_key"):
        print("配置已变更")
        # 执行相应操作

config_manager.on_config_change(my_handler)
```

### 禁用自动监控

```python
from nekobot.config.manager import NekoConfigManager

# 创建配置管理器但不启动监控
config_manager = NekoConfigManager(auto_reload=False)

# 手动启动
config_manager.start_watching()

# 停止监控
config_manager.stop_watching()
```

---

## 配置文件格式

位置: `./data/config.json`

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

## 热重载支持的配置

### ✅ 无需重启即可生效

- `logging.level` - 日志级别
- `logging.max_history` - 日志历史记录限制
- `bot.command_prefix` - 命令前缀
- `bot.admin_users` - 管理员列表
- `server.cors_origins` - CORS 配置

### ⚠️ 需要重启服务

- `server.host` - 服务器地址
- `server.port` - 服务器端口
- `security.jwt_secret` - JWT 密钥
- `security.jwt_algorithm` - JWT 算法

---

## 工作流程

```
1. 用户编辑配置文件
   ↓
2. watchfiles 检测到文件变化
   ↓
3. 触发 _watch_config_file()
   ↓
4. 延迟 0.1 秒（避免文件未写完）
   ↓
5. 调用 reload()
   ↓
6. 加载新配置并对比
   ↓
7. 如果有变更，通知所有回调
   ↓
8. 回调处理器执行相应操作
   ↓
9. 配置生效（无需重启）
```

---

## 线程安全

使用 `filelock.FileLock` 确保多进程安全：

```python
with FileLock(str(self.lock_file)):
    with open(self.config_file, "r") as f:
        self._config = json.load(f)
```

**保证:**
- 多进程不会同时读写配置文件
- 避免数据损坏和竞态条件

---

## 异常处理

### 文件监控异常

```python
try:
    async for changes in awatch(...):
        # 处理变更
except asyncio.CancelledError:
    logger.info("监控已取消")
except Exception as e:
    logger.error(f"监控异常: {e}")
```

### 回调执行异常

```python
try:
    callback(old_config, new_config)
except Exception as e:
    logger.error(f"回调执行失败: {e}")
    # 不影响其他回调继续执行
```

---

## 性能优化

### 1. 延迟加载

避免文件写入未完成就加载：

```python
await asyncio.sleep(0.1)
```

### 2. 差异检测

只在配置真正变化时才通知：

```python
if old_config != self._config:
    self._notify_callbacks(old_config, self._config)
```

### 3. 异步回调

异步回调不阻塞主线程：

```python
if asyncio.iscoroutinefunction(callback):
    asyncio.create_task(callback(old_config, new_config))
```

---

## 测试示例

### 运行测试脚本

```bash
python examples/config_hot_reload_example.py
```

### 测试步骤

1. 启动测试脚本
2. 编辑 `./data/config.json`
3. 修改 `bot.command_prefix` 的值
4. 保存文件
5. 观察控制台输出

**预期输出:**

```
2025-10-29 12:00:00 [INFO] 配置管理器已初始化
2025-10-29 12:00:00 [INFO] 配置文件监控已启动
2025-10-29 12:00:00 [INFO] 当前命令前缀: /

# 编辑并保存文件后
2025-10-29 12:05:00 [INFO] 检测到配置文件变化
2025-10-29 12:05:00 [INFO] 配置已重新加载，检测到变更
2025-10-29 12:05:00 [INFO] === 配置已变更 ===
2025-10-29 12:05:00 [INFO] 旧配置: /
2025-10-29 12:05:00 [INFO] 新配置: !
```

---

## 文档

### 已创建的文档

1. **完整使用指南**
   - `docs/CONFIG_HOT_RELOAD.md`
   - API 参考
   - 完整示例
   - 故障排查

2. **快速开始**
   - `docs/CONFIG_HOT_RELOAD_QUICKSTART.md`
   - 快速体验
   - 常见用法
   - 测试方法

3. **示例代码**
   - `examples/config_hot_reload_example.py`
   - 实际可运行的示例

---

## 代码统计

### 新增代码

- `nekobot/config/manager.py` - 增强约 100 行
- `nekobot/config/hot_reload.py` - 新增约 100 行
- `nekobot/core/bot.py` - 增强约 10 行
- `examples/config_hot_reload_example.py` - 新增约 50 行

**总计:** 约 260 行新代码

### 文档

- `docs/CONFIG_HOT_RELOAD.md` - 约 600 行
- `docs/CONFIG_HOT_RELOAD_QUICKSTART.md` - 约 200 行

**总计:** 约 800 行文档

---

## 优势

### 1. 用户体验

- ✅ 无需重启服务
- ✅ 配置立即生效
- ✅ 减少服务中断时间

### 2. 开发体验

- ✅ 易于使用的 API
- ✅ 完整的文档和示例
- ✅ 灵活的回调机制

### 3. 系统性能

- ✅ 异步实现，不阻塞
- ✅ 差异检测，减少不必要的通知
- ✅ 线程安全，多进程友好

### 4. 可维护性

- ✅ 清晰的模块划分
- ✅ 完善的异常处理
- ✅ 详细的日志记录

---

## 未来扩展

### 可能的改进

1. **配置验证**
   - 添加配置 Schema 验证
   - 配置错误时回滚

2. **配置历史**
   - 记录配置变更历史
   - 支持回滚到历史版本

3. **远程配置**
   - 支持从远程加载配置
   - 分布式配置同步

4. **Web 界面**
   - 在线编辑配置
   - 实时预览效果

---

## 总结

配置热重载功能已完整实现，具备以下特点：

✅ **功能完整** - 文件监控、热重载、回调通知  
✅ **性能优秀** - 异步实现，不影响主线程  
✅ **易于使用** - 简单的 API，丰富的示例  
✅ **文档完善** - 详细的使用指南和参考  
✅ **代码质量** - 通过 Ruff 检查，符合规范  
✅ **生产就绪** - 异常处理、线程安全、日志记录  

**配置热重载让 NekoBot 更加灵活和易用！**

---

*实现日期: 2025-10-29*  
*版本: v1.0.0*

