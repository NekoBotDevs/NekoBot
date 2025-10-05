"""平台适配器基础类"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from enum import Enum


class MessageType(Enum):
    """消息类型枚举"""
    TEXT = "text"
    IMAGE = "image"
    VOICE = "voice"
    VIDEO = "video"
    FILE = "file"
    AT = "at"
    REPLY = "reply"


class PlatformEvent:
    """平台事件基础类"""
    
    def __init__(
        self,
        event_type: str,
        platform: str,
        user_id: str,
        username: str,
        group_id: Optional[str] = None,
        message: Optional[str] = None,
        message_type: Optional[MessageType] = None,
        raw_data: Optional[Dict[str, Any]] = None,
    ):
        self.event_type = event_type
        self.platform = platform
        self.user_id = user_id
        self.username = username
        self.group_id = group_id
        self.message = message
        self.message_type = message_type or MessageType.TEXT
        self.raw_data = raw_data or {}
    
    def is_group_message(self) -> bool:
        """是否为群组消息"""
        return self.group_id is not None
    
    def is_private_message(self) -> bool:
        """是否为私聊消息"""
        return self.group_id is None


class BasePlatformAdapter(ABC):
    """平台适配器基础类"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化适配器
        
        Args:
            config: 适配器配置
        """
        self.config = config
        self.platform_name = self.__class__.__name__.replace("Adapter", "").lower()
        self._running = False
    
    @abstractmethod
    async def start(self) -> None:
        """启动适配器"""
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """停止适配器"""
        pass
    
    @abstractmethod
    async def send_message(
        self,
        user_id: str,
        message: str,
        group_id: Optional[str] = None,
        **kwargs
    ) -> bool:
        """发送消息
        
        Args:
            user_id: 用户ID
            message: 消息内容
            group_id: 群组ID(可选)
            **kwargs: 其他参数
            
        Returns:
            是否发送成功
        """
        pass
    
    @abstractmethod
    async def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户信息字典
        """
        pass
    
    def is_running(self) -> bool:
        """适配器是否运行中"""
        return self._running
    
    async def on_event(self, event: PlatformEvent) -> None:
        """事件回调(由子类重写)
        
        Args:
            event: 平台事件
        """
        pass