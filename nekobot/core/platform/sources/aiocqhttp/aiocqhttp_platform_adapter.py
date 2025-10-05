"""QQ平台适配器(基于aiocqhttp/OneBot V11)"""
import asyncio
from typing import Dict, Any, Optional
from aiocqhttp import CQHttp
from ...base_adapter import BasePlatformAdapter, PlatformEvent, MessageType


class AiocqhttpAdapter(BasePlatformAdapter):
    """QQ平台适配器(OneBot V11协议)"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化QQ适配器
        
        Args:
            config: 配置字典,包含:
                - host: 监听地址(默认0.0.0.0)
                - port: 反向WebSocket端口(默认6299)
                - access_token: 访问令牌(可选)
        """
        super().__init__(config)
        self.host = config.get("host", "0.0.0.0")
        self.port = config.get("port", 6299)
        self.access_token = config.get("access_token")
        self.bot: Optional[CQHttp] = None
    
    async def start(self) -> None:
        """启动适配器"""
        self._running = True
        self.bot = CQHttp(
            access_token=self.access_token,
            enable_http_post=False
        )
        
        @self.bot.on_message
        async def handle_message(event: Dict[str, Any]):
            """处理消息事件"""
            try:
                platform_event = self._parse_event(event)
                if platform_event:
                    await self.on_event(platform_event)
            except Exception as e:
                print(f"[AiocqhttpAdapter] 处理消息失败: {e}")
        
        await self.bot.run_task(host=self.host, port=self.port)
    
    async def stop(self) -> None:
        """停止适配器"""
        self._running = False
        if self.bot:
            # aiocqhttp没有显式停止方法,通过标志控制
            pass
    
    def _parse_event(self, data: Dict[str, Any]) -> Optional[PlatformEvent]:
        """解析QQ事件
        
        Args:
            data: 原始事件数据
            
        Returns:
            平台事件对象
        """
        try:
            msg_type = data.get("message_type", "private")
            user_id = str(data.get("user_id", ""))
            group_id = str(data.get("group_id")) if msg_type == "group" else None
            message = data.get("raw_message", "")
            sender = data.get("sender", {})
            username = sender.get("nickname", user_id)
            
            # 判断消息类型
            message_type = MessageType.TEXT
            if "[CQ:image" in message:
                message_type = MessageType.IMAGE
            elif "[CQ:record" in message:
                message_type = MessageType.VOICE
            
            return PlatformEvent(
                event_type="message",
                platform="qq",
                user_id=user_id,
                username=username,
                group_id=group_id,
                message=message,
                message_type=message_type,
                raw_data=data
            )
        except Exception as e:
            print(f"[AiocqhttpAdapter] 解析事件失败: {e}")
            return None
    
    async def send_message(
        self,
        user_id: str,
        message: str,
        group_id: Optional[str] = None,
        **kwargs
    ) -> bool:
        """发送消息到QQ
        
        Args:
            user_id: 用户QQ号
            message: 消息内容
            group_id: 群号(可选)
            
        Returns:
            是否发送成功
        """
        if not self.bot:
            return False
        
        try:
            if group_id:
                await self.bot.send_group_msg(
                    group_id=int(group_id),
                    message=message
                )
            else:
                await self.bot.send_private_msg(
                    user_id=int(user_id),
                    message=message
                )
            return True
        except Exception as e:
            print(f"[AiocqhttpAdapter] 发送消息失败: {e}")
            return False
    
    async def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户信息
        
        Args:
            user_id: 用户QQ号
            
        Returns:
            用户信息字典
        """
        if not self.bot:
            return None
        
        try:
            info = await self.bot.get_stranger_info(user_id=int(user_id))
            return {
                "user_id": user_id,
                "nickname": info.get("nickname"),
                "age": info.get("age"),
                "sex": info.get("sex"),
                "platform": "qq"
            }
        except Exception as e:
            print(f"[AiocqhttpAdapter] 获取用户信息失败: {e}")
            return {
                "user_id": user_id,
                "platform": "qq"
            }