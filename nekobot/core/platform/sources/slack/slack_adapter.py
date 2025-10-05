"""Slack平台适配器"""
from typing import Dict, Any, Optional
from quart import Quart, request, jsonify
from ...base_adapter import BasePlatformAdapter, PlatformEvent, MessageType


class SlackAdapter(BasePlatformAdapter):
    """Slack平台适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化Slack适配器
        
        Args:
            config: 配置字典,包含:
                - bot_token: Bot令牌
                - signing_secret: 签名密钥
                - webhook_port: Webhook监听端口(默认6297)
        """
        super().__init__(config)
        self.bot_token = config.get("bot_token")
        self.signing_secret = config.get("signing_secret")
        self.webhook_port = config.get("webhook_port", 6297)
        self.app: Optional[Quart] = None
    
    async def start(self) -> None:
        """启动适配器"""
        self._running = True
        self.app = Quart(__name__)
        
        @self.app.route("/slack/events", methods=["POST"])
        async def events():
            """处理Slack事件回调"""
            try:
                data = await request.get_json()
                
                # URL验证
                if data.get("type") == "url_verification":
                    return jsonify({"challenge": data.get("challenge")})
                
                # 事件处理
                event = self._parse_event(data)
                if event:
                    await self.on_event(event)
                
                return jsonify({"ok": True})
            except Exception as e:
                print(f"[SlackAdapter] 处理消息失败: {e}")
                return jsonify({"ok": False, "error": str(e)}), 500
        
        await self.app.run_task(host="0.0.0.0", port=self.webhook_port)
    
    async def stop(self) -> None:
        """停止适配器"""
        self._running = False
        if self.app:
            await self.app.shutdown()
    
    def _parse_event(self, data: Dict[str, Any]) -> Optional[PlatformEvent]:
        """解析Slack事件
        
        Args:
            data: 原始事件数据
            
        Returns:
            平台事件对象
        """
        try:
            event_data = data.get("event", {})
            event_type = event_data.get("type")
            
            if event_type != "message":
                return None
            
            # 忽略机器人消息
            if event_data.get("bot_id"):
                return None
            
            user_id = event_data.get("user", "")
            channel_id = event_data.get("channel")
            text = event_data.get("text", "")
            channel_type = event_data.get("channel_type", "channel")
            
            # 判断是否为群组消息
            is_group = channel_type in ["channel", "group"]
            
            return PlatformEvent(
                event_type="message",
                platform="slack",
                user_id=user_id,
                username=user_id,
                group_id=channel_id if is_group else None,
                message=text,
                message_type=MessageType.TEXT,
                raw_data=data
            )
        except Exception as e:
            print(f"[SlackAdapter] 解析事件失败: {e}")
            return None
    
    async def send_message(
        self,
        user_id: str,
        message: str,
        group_id: Optional[str] = None,
        **kwargs
    ) -> bool:
        """发送消息到Slack
        
        Args:
            user_id: 用户ID
            message: 消息内容
            group_id: 频道ID(可选)
            
        Returns:
            是否发送成功
        """
        try:
            # 需要调用Slack API发送消息
            # 实际实现需要使用slack_sdk
            channel = group_id if group_id else user_id
            print(f"[SlackAdapter] 发送消息到 {channel}: {message}")
            return True
        except Exception as e:
            print(f"[SlackAdapter] 发送消息失败: {e}")
            return False
    
    async def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户信息字典
        """
        return {
            "user_id": user_id,
            "platform": "slack"
        }