"""CLI命令实现"""
import asyncio
import click
import getpass
from pathlib import Path
from nekobot.core.config import NekoConfigManager
from nekobot.core.db import DatabaseManager, User
from nekobot.core.auth import AuthManager


@click.group()
def cli():
    """NekoBot CLI工具"""
    pass


@cli.command()
def reset_passwd():
    """重置用户密码"""
    click.echo("=== NekoBot 密码重置 ===")
    
    password = getpass.getpass("请输入新密码: ")
    if len(password) < 6:
        click.echo("错误: 密码长度不能少于6位")
        return
    
    password_confirm = getpass.getpass("请再次输入新密码: ")
    if password != password_confirm:
        click.echo("错误: 两次输入的密码不一致")
        return
    
    async def reset():
        db_manager = DatabaseManager("./data/nekobot.db")
        await db_manager.init_db()
        
        users = await db_manager.get_all(User, limit=1)
        if not users:
            click.echo("错误: 未找到用户,请先初始化系统")
            return
        
        user = users[0]
        config_manager = NekoConfigManager("./data")
        auth_manager = AuthManager(config_manager)
        
        user.password_hash = auth_manager.hash_password(password)
        await db_manager.update(user)
        
        click.echo("密码重置成功！")
        
        await db_manager.close()
    
    asyncio.run(reset())


@cli.command()
@click.option("-h", "--help", is_flag=True, help="显示帮助信息")
def help(help):
    """显示帮助信息"""
    if help:
        click.echo(cli.get_help(click.Context(cli)))
    else:
        click.echo("可用命令如下：")
        click.echo("  nekobot-cli reset-passwd  : 重置用户密码")
        click.echo("  nekobot-cli help/-h       : 显示帮助信息")
        click.echo("  nekobot-cli version/-v    : 显示当前版本")
        click.echo("  nekobot-cli check/-c      : 检查是否有新版本")
        click.echo("  nekobot-cli update/-up    : 更新到最新版本")


@cli.command()
@click.option("-v", "--version", is_flag=True, help="显示版本")
def version(version):
    """显示当前版本"""
    click.echo("当前版本为 1.0.0")


@cli.command()
@click.option("-c", "--check", is_flag=True, help="检查更新")
def check(check):
    """检查是否有新版本"""
    import requests
    
    try:
        click.echo("正在检查更新...")
        resp = requests.get(
            "https://api.github.com/repos/NekoBotDevs/NekoBot/releases/latest",
            timeout=10,
        )
        
        if resp.status_code == 200:
            data = resp.json()
            latest_version = data.get("tag_name", "").lstrip("v")
            current_version = "1.0.0"
            
            if latest_version != current_version:
                click.echo(f"当前版本为 {current_version}，最新版本为 {latest_version}")
                click.echo("可以使用 'nekobot-cli update' 进行更新")
            else:
                click.echo(f"当前版本为 {current_version}，已是最新版本")
        else:
            click.echo("检查更新失败，请稍后重试")
    
    except Exception as e:
        click.echo(f"检查更新失败: {str(e)}")


@cli.command()
@click.option("-up", "--update", is_flag=True, help="更新版本")
def update(update):
    """更新到最新版本"""
    import subprocess
    
    project_root = Path(__file__).parent.parent.parent
    
    if not (project_root / ".git").exists():
        click.echo("错误: 当前不是git仓库,无法使用git更新")
        return
    
    try:
        click.echo("正在更新到最新版本...")
        
        result = subprocess.run(
            ["git", "fetch", "origin", "main"],
            cwd=project_root,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            click.echo(f"更新失败: {result.stderr}")
            return
        
        result = subprocess.run(
            ["git", "pull", "origin", "main"],
            cwd=project_root,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            click.echo(f"更新失败: {result.stderr}")
            return
        
        click.echo("更新成功！请重启应用以应用更新")
    
    except Exception as e:
        click.echo(f"更新失败: {str(e)}")


if __name__ == "__main__":
    cli()