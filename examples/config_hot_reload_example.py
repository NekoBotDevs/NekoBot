"""
配置热重载示例

演示如何使用配置热重载功能
"""

import asyncio
from nekobot.config.manager import get_config_manager
from nekobot.utils.logger import setup_logger

logger = setup_logger("example")


async def my_config_change_handler(old_config, new_config):
    """自定义配置变更处理器"""
    logger.info("=== 配置已变更 ===")
    logger.info(f"旧配置: {old_config.get('bot', {}).get('command_prefix')}")
    logger.info(f"新配置: {new_config.get('bot', {}).get('command_prefix')}")


async def main():
    """主函数"""
    # 获取配置管理器（会自动启动文件监控）
    config_manager = get_config_manager()

    # 注册配置变更回调
    config_manager.on_config_change(my_config_change_handler)

    logger.info("配置管理器已初始化，正在监控配置文件...")
    logger.info(f"配置文件路径: {config_manager.config_file}")
    logger.info("\n请手动编辑配置文件来测试热重载功能")
    logger.info("例如：修改 bot.command_prefix 的值\n")

    # 显示当前配置
    current_prefix = config_manager.get("bot.command_prefix", "/")
    logger.info(f"当前命令前缀: {current_prefix}")

    # 保持运行
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("程序已停止")
        config_manager.stop_watching()


if __name__ == "__main__":
    asyncio.run(main())

