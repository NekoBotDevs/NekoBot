"""
机器人核心
"""

from nekobot.config.manager import get_config_manager
from nekobot.config.hot_reload import get_hot_reload_manager
from nekobot.database.engine import get_db_manager
from nekobot.database.models import User
from nekobot.auth.jwt_auth import JWTAuth
from nekobot.plugin.manager import get_plugin_manager
from nekobot.llm.manager import get_llm_manager
from nekobot.web.app import create_app
from nekobot.utils.logger import get_logger
from sqlmodel import select

logger = get_logger("bot")


class NekoBotCore:
    """NekoBot 核心控制器"""

    def __init__(self):
        self.config_manager = get_config_manager()
        self.hot_reload_manager = get_hot_reload_manager()
        self.db_manager = get_db_manager()
        self.plugin_manager = get_plugin_manager()
        self.llm_manager = get_llm_manager()
        self.app = None

        logger.info("NekoBot 核心初始化完成")
        logger.info("配置热重载已启用")

    async def initialize(self):
        """初始化所有组件"""
        logger.info("开始初始化 NekoBot...")

        # 创建数据库表
        await self.db_manager.create_db_and_tables_async()

        # 初始化默认用户
        await self._init_default_user()

        # 加载插件
        await self.plugin_manager.load_all_plugins()

        # 加载 LLM 服务商
        await self.llm_manager.load_providers_from_db()

        # 创建 Web 应用
        self.app = create_app()

        logger.info("NekoBot 初始化完成")

    async def _init_default_user(self):
        """初始化默认用户"""
        async with self.db_manager.async_session_maker() as session:
            result = await session.execute(
                select(User).where(User.username == "nekobot")
            )
            existing_user = result.scalar_one_or_none()

            if not existing_user:
                jwt_auth = JWTAuth()
                default_user = User(
                    username="nekobot",
                    password_hash=jwt_auth.hash_password("nekobot"),
                    must_change_password=True,
                )
                session.add(default_user)
                await session.commit()
                logger.warning(
                    "已创建默认用户 (用户名: nekobot, 密码: nekobot)，请尽快修改密码"
                )

    async def start(self):
        """启动 NekoBot"""
        await self.initialize()

        host = self.config_manager.get("server.host", "0.0.0.0")
        port = self.config_manager.get("server.port", 6285)

        logger.info(f"NekoBot 启动中... http://{host}:{port}")

        try:
            await self.app.run_task(host=host, port=port)
        except KeyboardInterrupt:
            logger.info("收到停止信号，正在关闭...")
        finally:
            await self.shutdown()

    async def shutdown(self):
        """关闭 NekoBot"""
        logger.info("正在关闭 NekoBot...")

        # 停止配置文件监控
        self.config_manager.stop_watching()

        # 卸载所有插件
        for plugin_name in list(self.plugin_manager.plugins.keys()):
            await self.plugin_manager.unload_plugin(plugin_name)

        # 关闭数据库连接
        await self.db_manager.close()

        logger.info("NekoBot 已关闭")


async def run_bot():
    """运行机器人"""
    bot = NekoBotCore()
    await bot.start()

