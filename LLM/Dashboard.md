# Dashboard Tips

这篇文章为了Dashboard的开发规范而写，目的是让LLM更好的理解并以Next.js的方式来开发NekoBot的前端仪表盘

## 安全

/dashboard/app
/dashboard/auth/login/page.tsx(登录页面) 且登录成功后跳转到 /dashboard
/dashboard/dashboard/page.tsx(仪表盘首页)
/dashboard/layout.tsx(仪表盘布局文件，包含侧边栏和顶部导航，也负责路由守卫) 如果未登录则跳转到 /auth/login

## 项目要求

使用侧边栏布局+顶部导航栏布局

侧边栏包含以下菜单项:

* 仪表盘(Dashboard) /dashboard
* 消息平台适配器(Chat Platforms) /dashboard/platforms
* 机器人基础配置(Bot Settings) /dashboard/bot
* 插件管理(Plugins) /dashboard/plugins
* LLM/TTL 服务提供商配置 /dashboard/llm
* 人设/提示词(Personalities/Prompts) /dashboard/personalities
* MCP 配置(MCP Settings) /dashboard/mcp
* 日志管理(Logs) /dashboard/logs
* 更多设置(Settings) /dashboard/settings

### 顶部组件

* Logo
* 检查更新\[自动检查框架更新状态(如有更新就显示提醒并闪烁)] 可在此处查看更新切换分支或者下载最新版本
* 用户信息 [显示用户名 点击后显示下拉菜单 修改密码] 修改密码时弹出小卡片 包含 旧密码 新密码 确认新密码 和 提交按钮
* 明暗模式切换
* 语言切换（CN/EN）
* 退出按钮

### 侧边栏布局

* **仪表盘**：当前系统CPU与内存占用、插件数量、消息适配器数量、消息统计(可显示列表数据)
* **消息平台适配器**：消息平台适配器设定
* **机器人基础配置**：设定命令前缀、配置CORS跨域、bot对话黑白名单(群聊、群聊用户、私信)、bot主人设置(可以设置多个主人)
* **插件**：本地插件()与在线插件市场(后续添加Api实现)
* **LLM/TTL 服务商配置**：配置LLM/TTL服务商信息
* **MCP 配置**：配置MCP工具
* **日志**：运行日志，支持过滤日志类型
* **更多配置**：服务重启

## 部分页面说明

### 插件

插件页面包含两个按钮切换并管理本地插件和在线插件市场安装

* **本地插件**

    *   用户可上传本地插件
    *   插件安装后需重启服务才能生效

* **在线插件**

    *   调用远程 API 获取插件仓库列表解析后在前端渲染成小卡片或者列表(可使用按钮切换)\[里边包含插件仓库"按钮"、插件版本、以及插件名称、插件描述]
    *   支持浏览和安装插件
    *   支持使用预设 GitHub 代理、自定义代理或直连
* **插件安装方式**

    *   上传 `*.zip` 压缩包
    *   输入插件压缩包直链 URL或者插件的插件仓库的地址来进行安装

#### 插件安装后显示

*   当前插件的自带的Readme文件（Markdown 格式）并在插件安装后显示（以小卡片形式显示自述文档，用户可以从卡片的右上角关闭）(由后端Api提供,具体查看API-Doc.md)

---

