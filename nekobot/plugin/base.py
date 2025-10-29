"""
插件基类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class PluginBase(ABC):
    """插件基类 - 所有插件必须继承此类"""

    def __init__(self):
        self.name: str = ""
        self.version: str = "1.0.0"
        self.description: str = ""
        self.author: str = ""
        self.repository: str = ""
        self.is_enabled: bool = False

    @abstractmethod
    async def register(self) -> bool:
        """注册插件 - 必须实现"""
        pass

    async def unregister(self) -> bool:
        """卸载插件"""
        return True

    async def reload(self) -> bool:
        """重载插件"""
        await self.unregister()
        return await self.register()

    async def enable(self) -> bool:
        """启用插件"""
        self.is_enabled = True
        return True

    async def disable(self) -> bool:
        """禁用插件"""
        self.is_enabled = False
        return True

    async def update(self) -> bool:
        """更新插件"""
        return True

    def export_commands(self) -> Dict[str, Any]:
        """导出插件命令 API"""
        return {}

    def get_metadata(self) -> Dict[str, str]:
        """获取插件元数据"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "repository": self.repository,
        }

