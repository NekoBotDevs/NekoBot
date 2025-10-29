"""
NekoBot - 主入口文件
多平台智能聊天机器人框架

使用方法:
    uv run main.py
    或
    python main.py
"""

import asyncio
import sys
from pathlib import Path

# 确保项目根目录在 Python 路径中
sys.path.insert(0, str(Path(__file__).parent))

from nekobot.core.bot import run_bot
from nekobot.utils.logger import setup_logger
from nekobot import __version__, __description__


def main():
    """主函数"""
    # 设置日志
    logger = setup_logger("nekobot", level="INFO")

    logger.info("=" * 60)
    logger.info(f"NekoBot v{__version__}")
    logger.info(__description__)
    logger.info("=" * 60)

    # 运行机器人
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info("程序已停止")
    except Exception as e:
        logger.error(f"程序运行出错: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

