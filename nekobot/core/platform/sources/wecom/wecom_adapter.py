"""企业微信(WeCom)平台适配器"""
from typing import Dict, Any, Optional
from quart import Quart, request, jsonify
from ...base_adapter import BasePlatformAdapter, PlatformEvent, MessageType


class WeComAdapter(BasePlatformAdapter):
    """企业微信适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化企业微信适配器
        
        Args:
            config: 配置字典,包含:
                - corp_id: 企业ID
                - agent_id: 应用ID
                - secret: 应用密钥
                - token: 用于验证URL的Token
                - encoding_aes_key: 用于消息加解密的密钥
                - webhook_port: Webhook监听端口(默认6294)
        """
        super().__init__(config)
        self.corp_id = config.get("corp_id")
        self.agent_id = config.get("agent_id")
        self.secret = config.get("secret")
        self.token = config.get("token")
        self.encoding_aes_key = config.get("encoding_aes_key")
        self.webhook_port = config.get("webhook_port", 6294)
        self.app: Optional[Quart] = None
        self._access_token: Optional[str] = None
    
    async def start(self) -> None:
        """启动适配器"""
        self._running = True
        self.app = Quart(__name__)
        
        @self.app.route("/wecom/webhook", methods=["POST"])
        async def webhook():
            """处理企业微信Webhook回调"""
            try:
                data = await request.get_json()
                event = self._parse_event(data)
                if event:
                    await self.on_event(event)
                return jsonify({"code": 0})
            except Exception as e:
                print(f"[WeComAdapter] 处理消息失败: {e}")
                return jsonify({"code": -1, "message": str(e)}), 500
        
        await self.app.run_task(host="0.0.0.0", port=self.webhook_port)
    
    async def stop(self) -> None:
        """停止适配器"""
        self._running = False
        if self.app:
            await self.app.shutdown()
    
    def _parse_event(self, data: Dict[str, Any]) -> Optional[PlatformEvent]:
        """解析企业微信事件
        
        Args:
            data: 原始事件数据
            
        Returns:
            平台事件对象
        """
        try:
            msg_type = data.get("MsgType", "text")
            from_user = data.get("FromUserName", "")
            content = data.get("Content", "")
            
            return PlatformEvent(
                event_type="message",
                platform="wecom",
                user_id=from_user,
                username=from_user,
                message=content,
                message_type=MessageType.TEXT if msg_type == "text" else MessageType.TEXT,
                raw_data=data
            )
        except Exception as e:
            print(f"[WeComAdapter] 解析事件失败: {e}")
            return None
    
    async def send_message(
        self,
        user_id: str,
        message: str,
        group_id: Optional[str] = None,
        **kwargs
    ) -> bool:
        """发送消息到企业微信
        
        Args:
            user_id: 用户ID
            message: 消息内容
            group_id: 群组ID(暂不支持)
            
        Returns:
            是否发送成功
        """
        try:
            # 这里需要调用企业微信API发送消息
            # 实际实现需要使用企业微信SDK
            print(f"[WeComAdapter] 发送消息到 {user_id}: {message}")
            return True
        except Exception as e:
            print(f"[WeComAdapter] 发送消息失败: {e}")
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
            "platform": "wecom"
        }