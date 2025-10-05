"""NekoBot主程序入口"""
import asyncio
from nekobot.app import run_app


if __name__ == "__main__":
    try:
        asyncio.run(run_app())
    except KeyboardInterrupt:
        print("\n[NekoBot] 应用已停止")