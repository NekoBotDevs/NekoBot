"""
NekoBot 设置验证脚本
"""

import sys
import importlib.util


def check_module(module_name):
    """检查模块是否可导入"""
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is not None:
            print(f"[OK] {module_name}")
            return True
        else:
            print(f"[FAIL] {module_name} - 未安装")
            return False
    except Exception as e:
        print(f"[ERROR] {module_name} - 错误: {e}")
        return False


def main():
    print("=" * 60)
    print("NekoBot 环境检查")
    print("=" * 60)

    print("\n检查核心依赖...")
    modules = [
        "quart",
        "sqlmodel",
        "sqlalchemy",
        "aiosqlite",
        "bcrypt",
        "pyjwt",
        "click",
        "filelock",
        "httpx",
        "watchfiles",
        "ruff",
    ]

    all_ok = True
    for module in modules:
        if not check_module(module):
            all_ok = False

    print("\n检查 NekoBot 模块...")
    nekobot_modules = [
        "nekobot",
        "nekobot.config",
        "nekobot.database",
        "nekobot.auth",
        "nekobot.plugin",
        "nekobot.llm",
        "nekobot.web",
        "nekobot.cli",
        "nekobot.utils",
        "nekobot.core",
    ]

    for module in nekobot_modules:
        if not check_module(module):
            all_ok = False

    print("\n" + "=" * 60)
    if all_ok:
        print("[SUCCESS] 所有检查通过！NekoBot 已准备就绪")
        print("\n启动命令:")
        print("  uv run main.py")
        print("  或")
        print("  python main.py")
    else:
        print("[WARN] 部分检查未通过，请安装缺失的依赖")
        print("\n安装命令:")
        print("  uv pip install -r requirements.txt")
    print("=" * 60)

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
