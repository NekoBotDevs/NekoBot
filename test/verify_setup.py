"""
NekoBot 安装验证脚本

运行此脚本以验证 NekoBot 是否正确安装和配置
"""

import sys
import io
from pathlib import Path

# 修复 Windows 控制台编码问题
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


def check_python_version():
    """检查 Python 版本"""
    print("检查 Python 版本...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"✓ Python 版本: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python 版本过低: {version.major}.{version.minor}.{version.micro}")
        print("  需要 Python 3.10 或更高版本")
        return False


def check_dependencies():
    """检查依赖包"""
    print("\n检查依赖包...")
    required_packages = [
        "quart",
        "sqlmodel",
        "pydantic",
        "bcrypt",
        "jwt",
        "colorlog",
        "click",
        "psutil",
        "aiohttp",
    ]

    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package}")
            missing.append(package)

    if missing:
        print(f"\n缺少依赖包: {', '.join(missing)}")
        print("请运行: pip install -r requirements.txt")
        return False

    return True


def check_project_structure():
    """检查项目结构"""
    print("\n检查项目结构...")
    required_dirs = [
        "nekobot",
        "nekobot/auth",
        "nekobot/config",
        "nekobot/database",
        "nekobot/llm",
        "nekobot/plugin",
        "nekobot/web",
        "nekobot/cli",
        "nekobot/core",
        "nekobot/utils",
    ]

    missing = []
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✓ {dir_path}/")
        else:
            print(f"✗ {dir_path}/")
            missing.append(dir_path)

    if missing:
        print(f"\n缺少目录: {', '.join(missing)}")
        return False

    return True


def check_main_file():
    """检查主文件"""
    print("\n检查主文件...")
    if Path("main.py").exists():
        print("✓ main.py")
        return True
    else:
        print("✗ main.py")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("NekoBot 安装验证")
    print("=" * 60)

    checks = [
        check_python_version(),
        check_dependencies(),
        check_project_structure(),
        check_main_file(),
    ]

    print("\n" + "=" * 60)
    if all(checks):
        print("✓ 所有检查通过！")
        print("\n您可以运行以下命令启动 NekoBot:")
        print("  uv run main.py")
        print("  或")
        print("  python main.py")
    else:
        print("✗ 部分检查未通过，请先解决上述问题")
        sys.exit(1)
    print("=" * 60)


if __name__ == "__main__":
    main()

