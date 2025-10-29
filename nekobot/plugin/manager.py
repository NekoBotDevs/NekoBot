"""
插件管理器
"""

import sys
import zipfile
import shutil
import subprocess
import importlib.util
from pathlib import Path
from typing import Dict, Optional, List
import yaml

from nekobot.plugin.base import PluginBase
from nekobot.utils.logger import get_logger
from nekobot.database.engine import get_db_manager
from nekobot.database.models import Plugin
from sqlmodel import select

logger = get_logger("plugin")


class PluginManager:
    """插件管理器 - 负责加载、卸载、热重载插件"""

    def __init__(self, plugin_dir: Optional[Path] = None, packages_dir: Optional[Path] = None):
        self.plugin_dir = plugin_dir or Path("./data/plugins")
        self.packages_dir = packages_dir or Path("./packages")
        self.temp_dir = Path("./data/temp")

        # 确保目录存在
        self.plugin_dir.mkdir(parents=True, exist_ok=True)
        self.packages_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        self.plugins: Dict[str, PluginBase] = {}
        self.db_manager = get_db_manager()

        logger.info(f"插件管理器初始化完成 - 插件目录: {self.plugin_dir}")

    async def load_all_plugins(self):
        """加载所有插件"""
        # 加载官方插件
        await self._load_plugins_from_dir(self.packages_dir, is_official=True)

        # 加载用户插件
        await self._load_plugins_from_dir(self.plugin_dir, is_official=False)

        logger.info(f"已加载 {len(self.plugins)} 个插件")

    async def _load_plugins_from_dir(self, directory: Path, is_official: bool = False):
        """从目录加载插件"""
        if not directory.exists():
            return

        for plugin_path in directory.iterdir():
            if not plugin_path.is_dir():
                continue

            # 跳过特殊目录
            if plugin_path.name.startswith(".") or plugin_path.name == "__pycache__":
                continue

            try:
                await self.load_plugin(plugin_path, is_official)
            except Exception as e:
                logger.error(f"加载插件失败 {plugin_path.name}: {e}")

    async def load_plugin(self, plugin_path: Path, is_official: bool = False) -> bool:
        """加载单个插件"""
        metadata_file = plugin_path / "metadata.yaml"
        main_file = plugin_path / "main.py"

        if not metadata_file.exists() or not main_file.exists():
            logger.warning(f"插件 {plugin_path.name} 缺少必要文件")
            return False

        # 读取元数据
        try:
            with open(metadata_file, "r", encoding="utf-8") as f:
                metadata = yaml.safe_load(f)
        except Exception as e:
            logger.error(f"读取插件元数据失败 {plugin_path.name}: {e}")
            return False

        plugin_name = metadata.get("name", plugin_path.name)

        # 检查是否已加载
        if plugin_name in self.plugins:
            logger.warning(f"插件 {plugin_name} 已加载")
            return False

        # 动态导入插件
        try:
            spec = importlib.util.spec_from_file_location(plugin_name, main_file)
            if spec is None or spec.loader is None:
                raise ImportError(f"无法加载插件模块 {plugin_name}")

            module = importlib.util.module_from_spec(spec)
            sys.modules[plugin_name] = module
            spec.loader.exec_module(module)

            # 查找 PluginBase 子类
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, PluginBase)
                    and attr is not PluginBase
                ):
                    plugin_class = attr
                    break

            if plugin_class is None:
                logger.error(f"插件 {plugin_name} 未找到 PluginBase 子类")
                return False

            # 实例化插件
            plugin_instance = plugin_class()
            plugin_instance.name = metadata.get("name", plugin_name)
            plugin_instance.version = metadata.get("version", "1.0.0")
            plugin_instance.description = metadata.get("description", "")
            plugin_instance.author = metadata.get("author", "")
            plugin_instance.repository = metadata.get("repository", "")

            # 注册插件
            if await plugin_instance.register():
                self.plugins[plugin_name] = plugin_instance
                await self._save_plugin_to_db(
                    plugin_instance, str(plugin_path), is_official
                )
                logger.info(f"插件 {plugin_name} 加载成功")
                return True
            else:
                logger.error(f"插件 {plugin_name} 注册失败")
                return False

        except Exception as e:
            logger.error(f"加载插件失败 {plugin_name}: {e}")
            return False

    async def unload_plugin(self, plugin_name: str) -> bool:
        """卸载插件"""
        if plugin_name not in self.plugins:
            logger.warning(f"插件 {plugin_name} 未加载")
            return False

        plugin = self.plugins[plugin_name]

        try:
            await plugin.unregister()
            del self.plugins[plugin_name]

            # 从系统模块中移除
            if plugin_name in sys.modules:
                del sys.modules[plugin_name]

            logger.info(f"插件 {plugin_name} 已卸载")
            return True
        except Exception as e:
            logger.error(f"卸载插件失败 {plugin_name}: {e}")
            return False

    async def reload_plugin(self, plugin_name: str) -> bool:
        """重载插件"""
        if plugin_name not in self.plugins:
            logger.warning(f"插件 {plugin_name} 未加载")
            return False

        plugin = self.plugins[plugin_name]

        try:
            await plugin.reload()
            logger.info(f"插件 {plugin_name} 已重载")
            return True
        except Exception as e:
            logger.error(f"重载插件失败 {plugin_name}: {e}")
            return False

    async def enable_plugin(self, plugin_name: str) -> bool:
        """启用插件"""
        if plugin_name not in self.plugins:
            return False

        return await self.plugins[plugin_name].enable()

    async def disable_plugin(self, plugin_name: str) -> bool:
        """禁用插件"""
        if plugin_name not in self.plugins:
            return False

        return await self.plugins[plugin_name].disable()

    async def install_plugin_from_zip(
        self, zip_path: Path, delete_data: bool = False
    ) -> bool:
        """从 ZIP 安装插件"""
        try:
            # 解压到临时目录
            extract_path = self.temp_dir / zip_path.stem
            if extract_path.exists():
                shutil.rmtree(extract_path)

            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_path)

            # 查找插件根目录
            plugin_root = self._find_plugin_root(extract_path)
            if not plugin_root:
                logger.error("ZIP 中未找到有效的插件")
                return False

            # 读取元数据
            metadata_file = plugin_root / "metadata.yaml"
            with open(metadata_file, "r", encoding="utf-8") as f:
                metadata = yaml.safe_load(f)

            plugin_name = metadata.get("name")
            if not plugin_name:
                logger.error("插件元数据缺少 name 字段")
                return False

            # 移动到插件目录
            target_path = self.plugin_dir / plugin_name
            if target_path.exists():
                if delete_data:
                    shutil.rmtree(target_path)
                else:
                    logger.warning(f"插件 {plugin_name} 已存在")
                    return False

            shutil.move(str(plugin_root), str(target_path))

            # 安装依赖
            requirements_file = target_path / "requirements.txt"
            if requirements_file.exists():
                await self._install_requirements(requirements_file)

            # 加载插件
            await self.load_plugin(target_path, is_official=False)

            logger.info(f"插件 {plugin_name} 安装成功")
            return True

        except Exception as e:
            logger.error(f"安装插件失败: {e}")
            return False
        finally:
            # 清理临时文件
            if extract_path.exists():
                shutil.rmtree(extract_path)

    def _find_plugin_root(self, path: Path) -> Optional[Path]:
        """查找插件根目录"""
        # 检查当前目录
        if (path / "metadata.yaml").exists() and (path / "main.py").exists():
            return path

        # 检查子目录
        for subdir in path.iterdir():
            if subdir.is_dir():
                if (subdir / "metadata.yaml").exists() and (subdir / "main.py").exists():
                    return subdir

        return None

    async def _install_requirements(self, requirements_file: Path):
        """安装插件依赖"""
        try:
            logger.info(f"安装插件依赖: {requirements_file}")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                logger.info("依赖安装成功")
            else:
                logger.error(f"依赖安装失败: {result.stderr}")
        except Exception as e:
            logger.error(f"安装依赖时出错: {e}")

    async def _save_plugin_to_db(
        self, plugin: PluginBase, install_path: str, is_official: bool
    ):
        """保存插件信息到数据库"""
        try:
            async with self.db_manager.async_session_maker() as session:
                # 检查是否已存在
                result = await session.execute(
                    select(Plugin).where(Plugin.name == plugin.name)
                )
                existing = result.scalar_one_or_none()

                if existing:
                    existing.version = plugin.version
                    existing.description = plugin.description
                    existing.author = plugin.author
                    existing.repository = plugin.repository
                    existing.is_active = True
                    session.add(existing)
                else:
                    new_plugin = Plugin(
                        name=plugin.name,
                        version=plugin.version,
                        description=plugin.description,
                        author=plugin.author,
                        repository=plugin.repository,
                        is_official=is_official,
                        is_active=True,
                        install_path=install_path,
                    )
                    session.add(new_plugin)

                await session.commit()
        except Exception as e:
            logger.error(f"保存插件信息到数据库失败: {e}")

    def get_plugin(self, plugin_name: str) -> Optional[PluginBase]:
        """获取插件实例"""
        return self.plugins.get(plugin_name)

    def get_all_plugins(self) -> Dict[str, PluginBase]:
        """获取所有插件"""
        return self.plugins.copy()

    def get_plugin_list(self) -> List[Dict]:
        """获取插件列表（用于 API）"""
        result = []
        for name, plugin in self.plugins.items():
            result.append(
                {
                    "name": name,
                    "version": plugin.version,
                    "description": plugin.description,
                    "author": plugin.author,
                    "repository": plugin.repository,
                    "is_enabled": plugin.is_enabled,
                }
            )
        return result


# 全局插件管理器实例
_plugin_manager: Optional[PluginManager] = None


def get_plugin_manager() -> PluginManager:
    """获取插件管理器实例"""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager

