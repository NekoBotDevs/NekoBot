# 项目

此项目为一个基于 Python 的架构，旨在构建一个支持接入多聊天平台大模型并且支持接入 LLM/TTL支持 的聊天机器人框架应用，并使用 Next.js 构建的前端仪表盘进行配置和展示。

## 项目规则

*   Always respond to me in **Chinese**.
*   使用 uv 来管理 Python 环境。
*   可编辑 **pyproject.toml**。

## 项目要求(前提条件)

你需要使用当前的项目架构完成一个机器人框架名为：*NekoBot*，且使用 Python + SQLite 作为数据库来完成一个机器人框架项目。你需要提供 API 接口并写入当前目录的LLM\API-Doc.md 以供前端仪表盘调用和提供 web 服务(由 Next.js 构建后的静态文件)：

```text
aiohttp
pydantic~=2.10.3
psutil>=5.8.0
openai
anthropic
qq-botpy
chardet~=5.1.0
Pillow
beautifulsoup4
googlesearch-python
readability-lxml
quart
lxml_html_clean
colorlog
aiocqhttp
pyjwt
bcrypt
apscheduler
docstring_parser
aiodocker
silk-python
lark-oapi
ormsgpack
cryptography
dashscope
python-telegram-bot
wechatpy
dingtalk-stream
defusedxml
mcp
certifi
pip
telegramify-markdown
google-genai
click
filelock
watchfiles
websockets
faiss-cpu
aiosqlite
py-cord>=2.6.1
slack-sdk
pydub
sqlmodel
deprecated
sqlalchemy[asyncio]
pyjson5
```

---

## 参考项目

[AstrBot项目仓库](https://github.com/AstrBotDevs/AstrBot)

[Astrbot 文档部分](https://docs.astrbot.app)

## 项目帮助

我们为你提供了mcp_router这个工具,方便你阅读多个项目文档

### 工具列表

## MCP Router 提供的8个管理工具

### 1. **mcp_router_list**
- **功能**：列出所有已注册的MCP客户端实例
- **用途**：查看当前所有配置的MCP实例及其状态信息

### 2. **mcp_router_help**
- **功能**：获取所有实例中可用工具的帮助信息
- **用途**：查看每个MCP实例提供的工具列表及其详细参数说明

### 3. **mcp_router_use**
- **功能**：使用特定的MCP实例并返回其可用工具
- **参数**：
  - `instance_name` (必需)：要使用的MCP实例名称

### 4. **mcp_router_add**
- **功能**：动态添加新的MCP配置
- **参数**：
  - `provider_name` (必需)：提供者名称（仅支持字母数字和下划线）
  - `config` (必需)：MCP配置对象，包含：
    - `name`：名称
    - `type`：类型（stdio/sse/http）
    - `command`：命令
    - `args`：参数数组（可选）
    - `env`：环境变量（可选）
    - `isActive`：是否激活（可选）

### 5. **mcp_router_remove**
- **功能**：移除MCP配置
- **参数**：
  - `instance_name` (必需)：要移除的实例名称

### 6. **mcp_router_disable**
- **功能**：禁用MCP实例但不删除其配置
- **参数**：
  - `instance_name` (必需)：要禁用的实例名称

### 7. **mcp_router_enable**
- **功能**：启用之前禁用的MCP实例
- **参数**：
  - `instance_name` (必需)：要启用的实例名称

### 8. **mcp_router_call**
- **功能**：在特定实例上调用工具
- **参数**：
  - `instance_name` (必需)：实例名称
  - `tool_name` (必需)：要调用的工具名称
  - `arguments` (必需)：工具参数对象

---

这8个工具提供了完整的MCP实例生命周期管理功能，包括查询、添加、删除、启用/禁用实例，以及调用实例中的工具。

### 提供的文档实例

* 钉钉API文档
* OpenAI文档
* 企业微信API文档
* 飞书API文档
* NapcatAPI文档

以下文档使用浏览器工具获取

QQBotAPI文档(官方)
[QQBotAPI文档](https://bot.q.qq.com/wiki/#%E7%AE%80%E4%BB%8B)
SlackAPI文档(官方)
[SlackAPI文档](https://docs.slack.dev/apis/)

## Web服务

检查项目的./data/dist是否包含index.html等前端文件如果没有则检查./data/tamp包含 **/dist.zip** 预编译的静态文件,如果包含则解压至项目的./data/dist,如果再没有则从 (https://github.com/NekoBotDevs/NekoBot/releases/latest/download/dist.zip)下载
对于指定版本则使用(https://github.com/NekoBotDevs/NekoBot/releases/download/{version}/dist.zip)

或者 尝试使用GitHub代理列表尝试下载

## 可用的Github代理列表(安装更新插件版本/更新项目/下载预编译的静态文件时使用)

```link
*   https://ghproxy.com
*   https://edgeone.gh-proxy.com
*   https://hk.gh-proxy.com
*   https://gh.llkk.cc
*   (直连)
*   (自定义)
```

## 可用的pip源列表(安装更新依赖/更新项目时使用)

```link
*   https://pypi.tuna.tsinghua.edu.cn/simple
*   https://pypi.mirrors.ustc.edu.cn/simple
*   https://pypi.mirrors.aliyun.com/simple
*   (官方源)
*   (自定义)
```

## 功能特点

### 整体架构

*   **前端 (Next.js):** 负责用户界面和交互，展示配置信息和数据，以及与聊天机器人进行交互。
*   **后端 (Python):** 作为 Web 服务，处理 API 请求，与插件管理模块和聊天机器人核心模块通信。
*   **插件管理 (Python):** 负责动态加载、禁用、卸载和更新插件，例如不同聊天平台的适配器。
*   **聊天机器人核心 (Python):** 负责处理用户消息，调用 LLM/TTL 模型，并生成回复。

### 插件系统

*   **本地插件**

    *   用户可上传本地插件
    *   插件安装后需重载插件服务才能生效
*   **在线插件**

    *   调用远程 API (后续支持)获取插件仓库列表解析后在前端渲染成小卡片或者列表\[里边包含插件仓库"按钮"、插件版本、以及插件名称、插件描述]
    *   支持浏览插件商店并安装插件
    *   支持使用预设 GitHub 代理(可在列表中ping)、自定义代理或直连
    *   支持直接输入仓库地址随后自动拉取至本地安装

*   **插件安装逻辑**

*   用户可自主拉取仓库,手动安装依赖

    ```bash
    cd /path/data/plugins (这里的*path*指NekoBot目录)
    git clone https://github.com/NekoBotDevs/NekoBot_Plugins_Example.git
    cd NekoBot_Plugins_Example
    pip install -r requirements.txt
    ```

*   由用户手动从前端仪表盘上传插件(必须要验证jwt密钥),然后后端开始处理zip插件,解压至./data/temp(如果没有则自动创建目录),随后解压至 **/data/plugins** 插件目录，如果有**_conf_schema.json**则会自动创建数据库表(如果没有则不创建)，随后安装依赖(如果有requirements.txt)并提示用户重载插件服务
*   **插件依赖管理**

    *   插件可附带 `requirements.txt`
    *   系统会在插件安装时自动运行(pip install -r requirements.txt)来自动安装依赖(前提是在插件目录发现requirements.txt) 如果需要安装其他依赖可以在插件的requirements.txt中添加,系统会自动安装依赖。
*   **插件管理功能**

    *   启用/禁用插件（支持热重载加载插件）
    *   查看插件的行为和功能说明（注册命令）
*   **插件安装方式**

    *   上传 `*.zip` 压缩包
    *   输入 GitHub 地址(可使用)
    *   输入插件压缩包直链 URL或者插件的插件仓库的地址

*   插件架构(必须包含)
    data/plugins/nekobot_plugin/
    metadata.yaml（插件元数据 包含名称 版本 描述 作者等信息）
    main.py（插件主程序包含注册插件命令 与版本等）
    requirements.txt(插件需要的依赖)
    README.md（插件自述文件）

*   **官方插件**
    *   官方插件会放在 `packages/` 目录下，用户无法删除官方插件，不可禁用
        main.py
        metadata.yaml
        requirements.txt

#### 插件管理器逻辑

因为我们想更好的管理插件系统，于是我们为开发者提供了装饰器用于管理插件生命周期:

#### 插件注册的前提条件

*   插件主程序必须集成一个基类名为'base'的类，如果没有这个类则无法不识别为插件
*   插件主程序可以包含以下装饰器(函数)用于管理插件生命周期，但是有些函数是必须的(如注册命令)否则无法识别为插件

*   @Neko.base.Register(用于在管理器注册命令)(必须，实现插件注册逻辑)
*   @Neko.base.Unregister(用于在管理器销毁命令)
*   @Neko.base.Reload(用于在管理器重载命令)
*   @Neko.base.Enable(用于在管理器启用命令)
*   @Neko.base.Disable(用于在管理器禁用命令)
*   @Neko.base.export_commands(作为给插件提供命令的API，用于给其他插件提供此插件以外的命令)(可选)
*   @Neko.base.Update(用于在管理器更新插件命令)

#### 插件元数据(metadata.yaml)格式

用于在插件管理页面显示信息与插件更新时使用,格式如下：

```yaml
name: 插件名称(NekoBot_Plugins_Example)
version: 1.0.0
description: 插件描述
author: 作者名称
repository: 插件的GitHub仓库地址(更新时需要)
#### 示例: repository: https://github.com/NekoBotDevs/NekoBot_Plugins_Example
```

### 插件安装后(前端显示)显示

*   当前插件的自带的Readme文件（Markdown 格式）并在插件安装后解析插件目录下的README.md文件并显示（以小卡片形式显示自述文档，用户可以从卡片的右上角关闭）

### 插件的数据管理

* 插件作者可以选择在插件目录中自定义存储方式，或者使用 **_conf_schema.json** 来配置插件的数据存储。  
* 如果使用 **_conf_schema.json** 配置，则数据会存放在 `./data/plugins_data/{plugin_name}_data.json` 目录下，并且可以在 webui 中进行配置。
*   插件可以在其代码中访问和管理自己的数据目录
*   插件的数据目录在插件卸载时不会被删除，如果webui中勾选了“删除数据”选项，则会删除插件的数据目录

#### 命令系统

*   用户可以自定义命令前缀，默认为"/"，可以修改为中英文前缀或者@此机器人
*   支持通过插件系统扩展机器人的功能
*   插件可以注册新的命令、消息处理器和事件监听器
*   权限管理(主人>群主>管理员>用户)跨平台一致性，不同平台的“群主/管理员”需要映射到统一的抽象角色

### 4. LLM/TTL 服务商配置

LLM/TTL 服务商配置存储在./data/cmd_config.json中,且支持动态加载(使用json 配置id 切换实现) 使用NekoConfigManager 进行加载配置 配置包含 API 密钥、模型设置和超时等参数。

*   支持在仪表盘中配置多个 LLM/TTL 服务商
*   用户可自定义 API 兼容 OpenAI/Anthropic/Google 风格
*   支持为同一服务商配置多个 APIKey(轮询使用)
*   支持动态增删服务商配置
*   支持对话黑白名单设置
*   支持给予LLM提供网络搜索接口
*   支持给予LLM工具接口(开关)
*   支持用户自定义提示词和角色设定
*   支持为不同场景配置不同的提示词和角色
*   支持导入导出(支持上传Markdown文件)提示词和角色配置
*   支持每个用户(消息适配器角色)分为不同对话
*   添加配置时使用api添加/移除/重命名/测试。(适配器需要实现openai/chatgpt/gemini/claude,openai为openai格式兼容)

## 日志

*   支持日志级别设置（如 DEBUG、INFO、WARNING、ERROR、CRITICAL）
*   支持日志搜索与过滤
*   实时日志流[(WebSocket 推送)(支持自动滚动开关)]
*   日志类型颜色(按照类型显示)

### LLM接入

使用NekoConfigManager方法进行动态配置注册,并动态加载，且支持动态销毁

## 消息适配器

使用NekoConfigManager方法进行动态配置注册,并动态加载，且支持动态销毁

*   支持多种聊天平台（如 Telegram、QQ、Slack、企业微信等）

### 服务部分

当访问"/"目录时提供前端仪表盘服务,"/api"则为前端仪表盘提供api服务
### 端口部分

*   6285 主服务端口，用于提供 Web 仪表盘和 API 接口

以下是默认适配器端口

*   6294 企业微信（WeCom）Webhook 服务的默认端口。
*   6295 企业微信（WeCom）反向 WebSocket 服务的默认端口。
*   6296 QQ 官方接口（QQ Official API）Webhook 服务的默认端口。
*   6297 Slack Webhook 服务的默认端口。
*   6299 QQ（OneBot V11）反向 WebSocket 服务的默认端口。

如果要作为WebSocket服务器需要提供/ws,连接时使用以下格式连接

```text
ws://<host>:<post>/ws
```

#### API基础架构

只给予仪表盘(Dashboard)API接口

*   所有API均在 后端端口/api
*   所有API均需JWT认证
*   所有API均返回JSON格式数据

##### JWT用户认证

*   使用 JWT 进行用户登录认证
*   用户的密码加盐哈希存储(bcrypt)至存储后端,且每次登录校验bcrypt加盐后结果,避免损失性能
*   初次登录需使用默认账户密码(均为nekobot)，并强制修改密码/[(用户也可一并修改)(用户名非必须)]
*   如没有JWT密钥则随机生成一个JWT密钥并存储在配置文件中
*   如果用户忘记密码可使用cli命令行重置密码

完成后请将api端点以及REST请求方式[API文档](/LLM/API-Doc.md)

###### CLI命令行示例

```bash
nekocli reset-passwd
系统回复：请输入新密码:
(用户输入强密码)
系统回复：请再次输入新密码:
(用户输入强密码)
系统回复：密码重置成功！

nekobot-cli help
系统回复：可用命令如下：
nekocli reset-passwd: 重置用户密码
nekocli help/-h: 显示帮助信息
nekocli version/-v: 显示当前版本
nekocli check/-c: 检查是否有新版本
nekocli update/-up: 更新到最新版本

```

###### 版本控制

```bash
nekocli -v
系统回复：当前版本为 1.0.0

nekocli -c
系统回复：当前版本为 1.0.0，最新版本为 1.0.1

nekocli -up <version>
系统回复：正在更新到<version>版本...

nekocli -up <latest-version>
系统回复：正在更新到最新版本...
```

> 需要编写github工作流,通过提交tag的版本号来控制版本号

或者使用前端的仪表盘来检查版本/切换分支/更新(前端发送请求到后端API)

---

## 项目格式化要求

使用 ruff 进行代码格式化和检查。

```bash
ruff check .
```

ruff格式要求

*   忽略：F403, F405, E501, ASYNC230
*   检查规则：Pyflakes (F)、Pycodestyle (W/E)、异步规范 (ASYNC)、列表推导优化 (C4)、引号规范 (Q)
*   最大行长：88
*   目标版本：Python 3.10
*   排除目录：.venv, venv, env, .git, __pycache__, build, dist, .eggs, *.egg-info, .mypy_cache, .pytest_cache, .ruff_cache
*   项目/参数命名不要过长

## 部署与安全

*   可使用 Docker Compose 一键部署，支持多操作系统
*   初次登录需使用默认账户密码(均为nekobot)，并强制修改密码/[(用户也可一并修改)(用户名非必须)]
*   用户密码加盐哈希存储(bcrypt),登录时校验数据库中加盐后的密码
*   使用 JWT 进行用户登录认证
*   可使用配置文件来控制cors跨域 来控制哪些域名可以访问webui(dashboard)接口
*   最大限度减少对外暴露的端口，只暴露webui端口和Fastapi端口
*   防止SQL、XSS注入攻击，防止文件上传漏洞和文件遍历攻击
*   直接使用*python main.py*启动 不需要任何脚本,如要测试,请写入 [test](/test/) 文件夹内
*   在重置密码后，将把当前的JWT密钥失效，以防止旧的JWT被继续使用，用户重新登录后生成新的JWT密钥。
*   在./data目录下存储所有数据和配置文件,且在./data/config.json存储cors跨域配置(方便用户手动更改),0.0.0.0 or 127.0.0.1 or 自定义域名,用户信息(均储存至sqlite数据库内)
*   不可以在程序中使用emoji,如果用户有在需求提到对应功能,则不再询问是否询问用户是否实现
*   请勿在程序中写入TODO类的字样,除非此功能在文档特意说明过,否则重写。
*   版本号不要写死,统一管理在pyproject.toml中,或者使用 **__init__.py** 来指定版本。
*   不要创建多余的文档只保留[Readme.md](/Releases.md) 和 [README.md](/Releases.md)
