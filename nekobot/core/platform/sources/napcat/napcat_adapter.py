"""
NapCat 平台适配器
基于 OneBot V11 协议对接 QQ 个人号
"""

import aiohttp
from typing import Dict, Any, Optional, List
from nekobot.utils.logger import get_logger

logger = get_logger("napcat")


class NapCatAdapter:
    """NapCat 适配器 - 用于对接 QQ 个人号"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化 NapCat 适配器

        Args:
            config: 配置字典，包含:
                - host: NapCat HTTP API 地址 (默认: localhost)
                - port: NapCat HTTP API 端口 (默认: 3000)
                - access_token: 访问令牌 (可选)
                - ws_host: WebSocket 服务器地址 (用于接收消息)
                - ws_port: WebSocket 服务器端口
        """
        self.host = config.get("host", "localhost")
        self.port = config.get("port", 3000)
        self.access_token = config.get("access_token")
        self.ws_host = config.get("ws_host", "0.0.0.0")
        self.ws_port = config.get("ws_port", 6299)

        self.base_url = f"http://{self.host}:{self.port}"
        self.headers = {}

        if self.access_token:
            self.headers["Authorization"] = f"Bearer {self.access_token}"

        self.session: Optional[aiohttp.ClientSession] = None
        self.bot_info: Optional[Dict] = None

        logger.info(f"NapCat 适配器初始化: {self.base_url}")

    async def connect(self):
        """连接到 NapCat"""
        self.session = aiohttp.ClientSession(headers=self.headers)

        try:
            self.bot_info = await self.get_login_info()
            logger.info(
                f"NapCat 连接成功 - 账号: {self.bot_info.get('nickname')} "
                f"({self.bot_info.get('user_id')})"
            )
            return True
        except Exception as e:
            logger.error(f"NapCat 连接失败: {e}")
            return False

    async def disconnect(self):
        """断开连接"""
        if self.session:
            await self.session.close()
            logger.info("NapCat 连接已关闭")

    async def _call_api(
        self, endpoint: str, data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        调用 NapCat API

        Args:
            endpoint: API 端点
            data: 请求数据

        Returns:
            API 响应数据
        """
        if not self.session:
            raise RuntimeError("NapCat 未连接")

        url = f"{self.base_url}/{endpoint}"

        try:
            async with self.session.post(url, json=data or {}) as resp:
                result = await resp.json()

                if result.get("status") != "ok":
                    logger.error(f"API 调用失败: {result}")
                    raise Exception(f"API 错误: {result.get('message', 'Unknown')}")

                return result.get("data", {})

        except Exception as e:
            logger.error(f"API 调用异常 [{endpoint}]: {e}")
            raise

    async def send_group_msg(
        self, group_id: int, message: List[Dict]
    ) -> Dict[str, Any]:
        """
        发送群消息

        Args:
            group_id: 群号
            message: 消息内容 (OneBot V11 消息段格式)

        Returns:
            包含 message_id 的字典
        """
        data = {"group_id": group_id, "message": message}

        logger.info(f"发送群消息 -> 群 {group_id}")
        return await self._call_api("send_group_msg", data)

    async def send_private_msg(
        self, user_id: int, message: List[Dict]
    ) -> Dict[str, Any]:
        """
        发送私聊消息

        Args:
            user_id: QQ 号
            message: 消息内容 (OneBot V11 消息段格式)

        Returns:
            包含 message_id 的字典
        """
        data = {"user_id": user_id, "message": message}

        logger.info(f"发送私聊消息 -> 用户 {user_id}")
        return await self._call_api("send_private_msg", data)

    async def send_msg(
        self, message_type: str, target_id: int, message: List[Dict]
    ) -> Dict[str, Any]:
        """
        发送消息（通用）

        Args:
            message_type: 消息类型 ("group" 或 "private")
            target_id: 目标 ID (群号或 QQ 号)
            message: 消息内容

        Returns:
            包含 message_id 的字典
        """
        if message_type == "group":
            data = {"message_type": "group", "group_id": target_id, "message": message}
        else:
            data = {"message_type": "private", "user_id": target_id, "message": message}

        logger.info(f"发送{message_type}消息 -> {target_id}")
        return await self._call_api("send_msg", data)

    async def delete_msg(self, message_id: int) -> Dict[str, Any]:
        """
        撤回消息

        Args:
            message_id: 消息 ID

        Returns:
            API 响应
        """
        data = {"message_id": message_id}
        logger.info(f"撤回消息: {message_id}")
        return await self._call_api("delete_msg", data)

    async def get_msg(self, message_id: int) -> Dict[str, Any]:
        """
        获取消息详情

        Args:
            message_id: 消息 ID

        Returns:
            消息详情
        """
        data = {"message_id": message_id}
        return await self._call_api("get_msg", data)

    async def get_login_info(self) -> Dict[str, Any]:
        """
        获取登录账号信息

        Returns:
            包含 user_id 和 nickname 的字典
        """
        return await self._call_api("get_login_info")

    async def get_group_list(self) -> List[Dict[str, Any]]:
        """
        获取群列表

        Returns:
            群列表
        """
        return await self._call_api("get_group_list")

    async def get_group_info(self, group_id: int) -> Dict[str, Any]:
        """
        获取群信息

        Args:
            group_id: 群号

        Returns:
            群信息
        """
        data = {"group_id": group_id}
        return await self._call_api("get_group_info", data)

    async def get_group_member_list(self, group_id: int) -> List[Dict[str, Any]]:
        """
        获取群成员列表

        Args:
            group_id: 群号

        Returns:
            群成员列表
        """
        data = {"group_id": group_id}
        return await self._call_api("get_group_member_list", data)

    async def get_group_member_info(
        self, group_id: int, user_id: int
    ) -> Dict[str, Any]:
        """
        获取群成员信息

        Args:
            group_id: 群号
            user_id: QQ 号

        Returns:
            群成员信息
        """
        data = {"group_id": group_id, "user_id": user_id}
        return await self._call_api("get_group_member_info", data)

    async def get_friend_list(self) -> List[Dict[str, Any]]:
        """
        获取好友列表

        Returns:
            好友列表
        """
        return await self._call_api("get_friend_list")

    async def set_group_ban(
        self, group_id: int, user_id: int, duration: int = 600
    ) -> Dict[str, Any]:
        """
        群禁言

        Args:
            group_id: 群号
            user_id: QQ 号
            duration: 禁言时长（秒），0 为解除禁言

        Returns:
            API 响应
        """
        data = {"group_id": group_id, "user_id": user_id, "duration": duration}
        logger.info(f"群禁言: 群 {group_id}, 用户 {user_id}, 时长 {duration}秒")
        return await self._call_api("set_group_ban", data)

    async def set_group_kick(
        self, group_id: int, user_id: int, reject_add_request: bool = False
    ) -> Dict[str, Any]:
        """
        踢出群成员

        Args:
            group_id: 群号
            user_id: QQ 号
            reject_add_request: 是否拒绝再次加群请求

        Returns:
            API 响应
        """
        data = {
            "group_id": group_id,
            "user_id": user_id,
            "reject_add_request": reject_add_request,
        }
        logger.info(f"踢出群成员: 群 {group_id}, 用户 {user_id}")
        return await self._call_api("set_group_kick", data)

    async def set_group_card(
        self, group_id: int, user_id: int, card: str
    ) -> Dict[str, Any]:
        """
        设置群名片

        Args:
            group_id: 群号
            user_id: QQ 号
            card: 群名片内容

        Returns:
            API 响应
        """
        data = {"group_id": group_id, "user_id": user_id, "card": card}
        logger.info(f"设置群名片: 群 {group_id}, 用户 {user_id}")
        return await self._call_api("set_group_card", data)

    def build_text_message(self, text: str) -> List[Dict]:
        """
        构建文本消息

        Args:
            text: 文本内容

        Returns:
            OneBot V11 消息段列表
        """
        return [{"type": "text", "data": {"text": text}}]

    def build_image_message(self, file: str) -> List[Dict]:
        """
        构建图片消息

        Args:
            file: 图片文件路径或 URL

        Returns:
            OneBot V11 消息段列表
        """
        return [{"type": "image", "data": {"file": file}}]

    def build_at_message(self, qq: int) -> List[Dict]:
        """
        构建 @ 消息

        Args:
            qq: 要 @ 的 QQ 号，"all" 表示 @全体成员

        Returns:
            OneBot V11 消息段列表
        """
        return [{"type": "at", "data": {"qq": str(qq)}}]

    def build_reply_message(self, message_id: int) -> List[Dict]:
        """
        构建回复消息

        Args:
            message_id: 要回复的消息 ID

        Returns:
            OneBot V11 消息段列表
        """
        return [{"type": "reply", "data": {"id": str(message_id)}}]

    def build_mixed_message(self, *segments: List[Dict]) -> List[Dict]:
        """
        构建混合消息

        Args:
            *segments: 多个消息段

        Returns:
            OneBot V11 消息段列表
        """
        result = []
        for seg_list in segments:
            result.extend(seg_list)
        return result

