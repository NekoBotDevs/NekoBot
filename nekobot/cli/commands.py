"""
CLI 命令实现
"""

import sys
import asyncio
import getpass
import click
import requests
from pathlib import Path

from nekobot import __version__
from nekobot.database.engine import DatabaseManager
from nekobot.database.models import User
from nekobot.auth.jwt_auth import JWTAuth
from nekobot.config.manager import NekoConfigManager
from sqlmodel import select


@click.group()
def cli():
    """NekoBot CLI 工具"""
    pass


@cli.command("version")
@click.option("-v", "--verbose", is_flag=True, help="显示详细信息")
def version(verbose):
    """显示当前版本"""
    click.echo(f"当前版本为 {__version__}")
    if verbose:
        click.echo(f"Python 版本: {sys.version}")


@cli.command("check")
def check():
    """检查是否有新版本"""
    try:
        click.echo(f"当前版本为 {__version__}")
        click.echo("正在检查更新...")

        response = requests.get(
            "https://api.github.com/repos/NekoBotDevs/NekoBot/releases/latest",
            timeout=10,
        )

        if response.status_code == 200:
            latest_version = response.json().get("tag_name", "").lstrip("v")
            click.echo(f"最新版本为 {latest_version}")

            if latest_version > __version__:
                click.echo("发现新版本！请使用 'nekobot-cli update' 更新")
            else:
                click.echo("已是最新版本")
        else:
            click.echo("检查更新失败，请稍后重试")

    except Exception as e:
        click.echo(f"检查更新时出错: {e}", err=True)


@cli.command("update")
@click.argument("version", required=False)
def update(version):
    """更新到指定版本或最新版本"""
    target_version = version or "latest"
    click.echo(f"正在更新到 {target_version} 版本...")
    click.echo("此功能需要配合 GitHub Actions 和包管理器实现")
    click.echo("请访问 https://github.com/NekoBotDevs/NekoBot/releases 手动下载")


@cli.command("reset-passwd")
def reset_password():
    """重置用户密码"""

    async def _reset_password():
        try:
            click.echo("密码重置工具")
            click.echo("-" * 50)

            # 初始化数据库
            db_manager = DatabaseManager()

            async with db_manager.async_session_maker() as session:
                # 获取所有用户
                result = await session.execute(select(User))
                users = result.scalars().all()

                if not users:
                    click.echo("数据库中没有用户，请先运行主程序进行初始化")
                    return

                # 显示用户列表
                click.echo("\n用户列表:")
                for idx, user in enumerate(users, 1):
                    click.echo(f"{idx}. {user.username}")

                # 选择用户
                if len(users) == 1:
                    user = users[0]
                    click.echo(f"\n已选择用户: {user.username}")
                else:
                    user_idx = click.prompt("请选择用户（输入序号）", type=int)
                    if user_idx < 1 or user_idx > len(users):
                        click.echo("无效的序号")
                        return
                    user = users[user_idx - 1]

                # 输入新密码
                new_password = getpass.getpass("请输入新密码: ")
                confirm_password = getpass.getpass("请再次输入新密码: ")

                if new_password != confirm_password:
                    click.echo("两次输入的密码不一致")
                    return

                if len(new_password) < 6:
                    click.echo("密码长度至少为 6 位")
                    return

                # 更新密码
                jwt_auth = JWTAuth()
                user.password_hash = jwt_auth.hash_password(new_password)
                user.must_change_password = False
                session.add(user)
                await session.commit()

                # 使所有 Token 失效
                jwt_auth.invalidate_all_tokens()

                click.echo("\n密码重置成功！所有旧登录令牌已失效")

        except Exception as e:
            click.echo(f"重置密码时出错: {e}", err=True)

    asyncio.run(_reset_password())


@cli.command("init")
def init():
    """初始化 NekoBot（创建默认配置和数据库）"""

    async def _init():
        try:
            click.echo("正在初始化 NekoBot...")

            # 创建数据目录
            data_dir = Path("./data")
            data_dir.mkdir(parents=True, exist_ok=True)
            click.echo("数据目录已创建")

            # 初始化配置
            NekoConfigManager()
            click.echo("配置文件已创建")

            # 初始化数据库
            db_manager = DatabaseManager()
            await db_manager.create_db_and_tables_async()
            click.echo("数据库已创建")

            # 创建默认用户
            async with db_manager.async_session_maker() as session:
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
                    click.echo("默认用户已创建（用户名: nekobot, 密码: nekobot）")
                else:
                    click.echo("默认用户已存在")

            click.echo("\nNekoBot 初始化完成！")
            click.echo("请使用 'uv run main.py' 或 'python main.py' 启动")

        except Exception as e:
            click.echo(f"初始化时出错: {e}", err=True)

    asyncio.run(_init())


if __name__ == "__main__":
    cli()

