# NekoBot 快速开始指南

## 安装步骤

### 1. 克隆仓库

```bash
git clone https://github.com/NekoBotDevs/NekoBot.git
cd NekoBot
```

### 2. 安装依赖

#### 使用 uv（推荐）

```bash
# 安装 uv（如果尚未安装）
pip install uv

# 安装依赖
uv pip install -r requirements.txt
```

#### 使用 pip

```bash
pip install -r requirements.txt
```

### 3. 初始化项目

```bash
# 方式1：使用 CLI 工具初始化
uv run -m nekobot.cli.commands init

# 方式2：直接运行（会自动初始化）
uv run main.py
```

## 启动 NekoBot

```bash
# 使用 uv
uv run main.py

# 或使用 Python
python main.py
```

启动成功后，您会看到类似的输出：

```
============================================================
NekoBot v1.0.0
智能聊天机器人框架
============================================================
2025-10-29 12:00:00 [INFO] nekobot - 数据库初始化完成
2025-10-29 12:00:01 [INFO] nekobot - NekoBot 核心初始化完成
2025-10-29 12:00:02 [INFO] nekobot - NekoBot 启动中... http://0.0.0.0:6285
```

## 访问 Web 界面

在浏览器中打开：

```
http://localhost:6285
```

## 默认登录信息

- **用户名**: `nekobot`
- **密码**: `nekobot`

**重要**: 首次登录后会强制要求修改密码，这是为了安全考虑。

## 基本使用

### 1. 修改密码

登录后，系统会提示您修改密码。或者手动访问：

```
设置 -> 修改密码
```

### 2. 添加 LLM 服务商

前往 `LLM 管理` -> `添加服务商`：

```json
{
  "name": "openai-gpt4",
  "provider_type": "openai",
  "api_keys": ["sk-your-api-key"],
  "model": "gpt-4",
  "base_url": "https://api.openai.com/v1"
}
```

### 3. 安装插件

#### 方式1：上传 ZIP 插件

前往 `插件管理` -> `上传插件`，选择 `.zip` 格式的插件包。

#### 方式2：手动安装

```bash
cd data/plugins
git clone https://github.com/YourName/YourPlugin.git
cd YourPlugin
pip install -r requirements.txt
```

然后在 Web 界面重载插件服务。

### 4. 配置平台适配器

根据您需要接入的聊天平台，配置相应的适配器。

例如配置 Telegram：

```json
{
  "name": "telegram-bot",
  "platform_type": "telegram",
  "config": {
    "token": "your-bot-token"
  }
}
```

## CLI 工具使用

### 查看版本

```bash
nekobot-cli version
```

### 检查更新

```bash
nekobot-cli check
```

### 重置密码

如果忘记密码：

```bash
nekobot-cli reset-passwd
```

### 初始化项目

```bash
nekobot-cli init
```

## 目录结构说明

```
NekoBot/
├── data/                    # 数据目录（自动创建）
│   ├── config.json         # 配置文件
│   ├── nekobot.db          # 数据库
│   ├── plugins/            # 插件目录
│   └── dist/               # 前端静态文件
├── nekobot/                # 核心代码
├── main.py                 # 主入口
└── requirements.txt        # 依赖列表
```

## 常见问题

### Q: 启动失败，提示端口被占用

A: 修改配置文件 `data/config.json` 中的端口号：

```json
{
  "server": {
    "port": 8080
  }
}
```

### Q: 如何查看日志？

A: 
1. 控制台会实时输出日志
2. Web 界面的"日志"页面可查看实时日志
3. WebSocket 连接 `ws://localhost:6285/ws` 获取实时日志流

### Q: 如何停止服务？

A: 在终端按 `Ctrl + C`

### Q: 数据存储在哪里？

A: 所有数据都存储在 `./data/` 目录下，包括：
- 配置文件：`config.json`
- 数据库：`nekobot.db`
- 插件数据：`plugins_data/`

## 下一步

- 阅读完整文档：[Readme.md](Readme.md)
- API 文档：[API-Doc.md](LLM/API-Doc.md)
- 项目详细说明：[Project.md](LLM/Project.md)
- 开发插件：参考 `data/plugins/NekoBot_Plugins_Example/`

## 获取帮助

- GitHub Issues: https://github.com/NekoBotDevs/NekoBot/issues
- 文档: https://github.com/NekoBotDevs/NekoBot/tree/main/LLM

---

祝您使用愉快！

