"""平台适配器管理器"""
import asyncio
from typing import Dict, List, Optional, Any
from .base_adapter import BasePlatformAdapter, PlatformEvent


class AdapterManager:
    """适配器管理器,负责管理所有平台适配器"""
    
    def __init__(self):
        """初始化适配器管理器"""
        self._adapters: Dict[str, BasePlatformAdapter] = {}
        self._event_handlers: List[callable] = []
    
    def register_adapter(self, name: str, adapter: BasePlatformAdapter) -> None:
        """注册适配器
        
        Args:
            name: 适配器名称
            adapter: 适配器实例
        """
        self._adapters[name] = adapter
    
    def unregister_adapter(self, name: str) -> None:
        """注销适配器
        
        Args:
            name: 适配器名称
        """
        if name in self._adapters:
            del self._adapters[name]
    
    def get_adapter(self, name: str) -> Optional[BasePlatformAdapter]:
        """获取适配器
        
        Args:
            name: 适配器名称
            
        Returns:
            适配器实例
        """
        return self._adapters.get(name)
    
    def get_all_adapters(self) -> Dict[str, BasePlatformAdapter]:
        """获取所有适配器"""
        return self._adapters.copy()
    
    def add_event_handler(self, handler: callable) -> None:
        """添加事件处理器
        
        Args:
            handler: 事件处理函数
        """
        self._event_handlers.append(handler)
    
    def remove_event_handler(self, handler: callable) -> None:
        """移除事件处理器
        
        Args:
            handler: 事件处理函数
        """
        if handler in self._event_handlers:
            self._event_handlers.remove(handler)
    
    async def dispatch_event(self, event: PlatformEvent) -> None:
        """分发事件到所有处理器
        
        Args:
            event: 平台事件
        """
        for handler in self._event_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                print(f"[AdapterManager] 事件处理失败: {e}")
    
    async def start_all(self) -> None:
        """启动所有适配器"""
        for name, adapter in self._adapters.items():
            try:
                await adapter.start()
                print(f"[AdapterManager] 适配器 {name} 启动成功")
            except Exception as e:
                print(f"[AdapterManager] 适配器 {name} 启动失败: {e}")
    
    async def stop_all(self) -> None:
        """停止所有适配器"""
        for name, adapter in self._adapters.items():
            try:
                await adapter.stop()
                print(f"[AdapterManager] 适配器 {name} 已停止")
            except Exception as e:
                print(f"[AdapterManager] 适配器 {name} 停止失败: {e}")