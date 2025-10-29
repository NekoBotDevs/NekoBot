"""
平台适配器管理器
"""

from typing import Dict, Optional
from pathlib import Path

from nekobot.database.engine import get_db_manager
from nekobot.database.models import PlatformAdapter
from nekobot.utils.logger import get_logger
from sqlmodel import select

logger = get_logger("adapter_manager")


class AdapterManager:
    """平台适配器管理器"""

    def __init__(self):
        self.adapters: Dict[str, any] = {}
        self.db_manager = get_db_manager()
        logger.info("平台适配器管理器初始化完成")

    async def load_adapters_from_db(self):
        """从数据库加载所有平台适配器"""
        try:
            async with self.db_manager.async_session_maker() as session:
                result = await session.execute(
                    select(PlatformAdapter).where(PlatformAdapter.is_active)
                )
                adapters = result.scalars().all()

                for adapter in adapters:
                    try:
                        await self._load_adapter(adapter)
                        logger.info(f"平台适配器已加载: {adapter.name}")
                    except Exception as e:
                        logger.error(f"加载平台适配器失败 {adapter.name}: {e}")

                logger.info(f"从数据库加载了 {len(self.adapters)} 个平台适配器")
        except Exception as e:
            logger.error(f"从数据库加载平台适配器失败: {e}")

    async def _load_adapter(self, adapter_config):
        """加载单个适配器"""
        platform_type = adapter_config.platform_type.lower()
        adapter_path = (
            Path("nekobot/core/platform/sources") / platform_type
        )

        if not adapter_path.exists():
            logger.warning(f"平台适配器目录不存在: {platform_type}")
            return False

        logger.info(f"平台适配器 {adapter_config.name} 配置已加载")
        self.adapters[adapter_config.name] = {
            "type": platform_type,
            "config": adapter_config.config,
            "is_active": adapter_config.is_active,
        }
        return True

    async def add_adapter(
        self, name: str, platform_type: str, config: Dict, is_active: bool = True
    ) -> bool:
        """添加新的平台适配器"""
        try:
            async with self.db_manager.async_session_maker() as session:
                adapter = PlatformAdapter(
                    name=name,
                    platform_type=platform_type,
                    config=config,
                    is_active=is_active,
                )
                session.add(adapter)
                await session.commit()

            await self._load_adapter(adapter)
            logger.info(f"平台适配器已添加: {name}")
            return True

        except Exception as e:
            logger.error(f"添加平台适配器失败: {e}")
            return False

    async def remove_adapter(self, name: str) -> bool:
        """移除平台适配器"""
        try:
            if name in self.adapters:
                del self.adapters[name]

            async with self.db_manager.async_session_maker() as session:
                result = await session.execute(
                    select(PlatformAdapter).where(PlatformAdapter.name == name)
                )
                adapter = result.scalar_one_or_none()
                if adapter:
                    await session.delete(adapter)
                    await session.commit()

            logger.info(f"平台适配器已移除: {name}")
            return True

        except Exception as e:
            logger.error(f"移除平台适配器失败: {e}")
            return False

    def get_adapter(self, name: str) -> Optional[Dict]:
        """获取平台适配器"""
        return self.adapters.get(name)

    def get_all_adapters(self) -> Dict:
        """获取所有平台适配器"""
        return self.adapters.copy()


# 全局适配器管理器实例
_adapter_manager: Optional[AdapterManager] = None


def get_adapter_manager() -> AdapterManager:
    """获取适配器管理器实例"""
    global _adapter_manager
    if _adapter_manager is None:
        _adapter_manager = AdapterManager()
    return _adapter_manager

