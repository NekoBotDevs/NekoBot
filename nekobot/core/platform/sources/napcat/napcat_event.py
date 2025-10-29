"""
NapCat 事件处理
"""

from typing import Dict, Any, Optional, Callable, List
from enum import Enum


class MessageType(str, Enum):
    """消息类型"""

    PRIVATE = "private"
    GROUP = "group"


class PostType(str, Enum):
    """上报类型"""

    MESSAGE = "message"
    NOTICE = "notice"
    REQUEST = "request"
    META_EVENT = "meta_event"


class NapCatEvent:
    """NapCat 事件基类"""

    def __init__(self, raw_event: Dict[str, Any]):
        self.raw_event = raw_event
        self.post_type = raw_event.get("post_type")
        self.time = raw_event.get("time")
        self.self_id = raw_event.get("self_id")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.raw_event


class MessageEvent(NapCatEvent):
    """消息事件"""

    def __init__(self, raw_event: Dict[str, Any]):
        super().__init__(raw_event)
        self.message_type = raw_event.get("message_type")
        self.sub_type = raw_event.get("sub_type")
        self.message_id = raw_event.get("message_id")
        self.user_id = raw_event.get("user_id")
        self.message = raw_event.get("message")
        self.raw_message = raw_event.get("raw_message")
        self.font = raw_event.get("font")
        self.sender = raw_event.get("sender", {})

        # 群消息特有字段
        if self.message_type == MessageType.GROUP:
            self.group_id = raw_event.get("group_id")
            self.anonymous = raw_event.get("anonymous")

    def is_group_message(self) -> bool:
        """是否为群消息"""
        return self.message_type == MessageType.GROUP

    def is_private_message(self) -> bool:
        """是否为私聊消息"""
        return self.message_type == MessageType.PRIVATE

    def get_plain_text(self) -> str:
        """获取纯文本内容"""
        if isinstance(self.message, str):
            return self.message

        text_parts = []
        if isinstance(self.message, list):
            for seg in self.message:
                if seg.get("type") == "text":
                    text_parts.append(seg.get("data", {}).get("text", ""))

        return "".join(text_parts).strip()

    def get_images(self) -> List[str]:
        """获取图片列表"""
        images = []
        if isinstance(self.message, list):
            for seg in self.message:
                if seg.get("type") == "image":
                    file = seg.get("data", {}).get("file")
                    if file:
                        images.append(file)
        return images

    def has_at(self, qq: Optional[int] = None) -> bool:
        """
        检查是否包含 @ 消息

        Args:
            qq: 指定 QQ 号，None 表示检查是否 @ 了任何人

        Returns:
            是否包含 @
        """
        if not isinstance(self.message, list):
            return False

        for seg in self.message:
            if seg.get("type") == "at":
                if qq is None:
                    return True
                at_qq = seg.get("data", {}).get("qq")
                if at_qq and int(at_qq) == qq:
                    return True

        return False


class NoticeEvent(NapCatEvent):
    """通知事件"""

    def __init__(self, raw_event: Dict[str, Any]):
        super().__init__(raw_event)
        self.notice_type = raw_event.get("notice_type")
        self.sub_type = raw_event.get("sub_type")


class GroupNoticeEvent(NoticeEvent):
    """群通知事件"""

    def __init__(self, raw_event: Dict[str, Any]):
        super().__init__(raw_event)
        self.group_id = raw_event.get("group_id")
        self.operator_id = raw_event.get("operator_id")
        self.user_id = raw_event.get("user_id")


class RequestEvent(NapCatEvent):
    """请求事件"""

    def __init__(self, raw_event: Dict[str, Any]):
        super().__init__(raw_event)
        self.request_type = raw_event.get("request_type")
        self.sub_type = raw_event.get("sub_type")
        self.comment = raw_event.get("comment")
        self.flag = raw_event.get("flag")


class FriendRequestEvent(RequestEvent):
    """好友请求事件"""

    def __init__(self, raw_event: Dict[str, Any]):
        super().__init__(raw_event)
        self.user_id = raw_event.get("user_id")


class GroupRequestEvent(RequestEvent):
    """加群请求事件"""

    def __init__(self, raw_event: Dict[str, Any]):
        super().__init__(raw_event)
        self.group_id = raw_event.get("group_id")
        self.user_id = raw_event.get("user_id")


class MetaEvent(NapCatEvent):
    """元事件"""

    def __init__(self, raw_event: Dict[str, Any]):
        super().__init__(raw_event)
        self.meta_event_type = raw_event.get("meta_event_type")


def parse_event(raw_event: Dict[str, Any]) -> NapCatEvent:
    """
    解析事件

    Args:
        raw_event: 原始事件数据

    Returns:
        对应的事件对象
    """
    post_type = raw_event.get("post_type")

    if post_type == PostType.MESSAGE:
        return MessageEvent(raw_event)
    elif post_type == PostType.NOTICE:
        notice_type = raw_event.get("notice_type")
        if "group" in notice_type:
            return GroupNoticeEvent(raw_event)
        return NoticeEvent(raw_event)
    elif post_type == PostType.REQUEST:
        request_type = raw_event.get("request_type")
        if request_type == "friend":
            return FriendRequestEvent(raw_event)
        elif request_type == "group":
            return GroupRequestEvent(raw_event)
        return RequestEvent(raw_event)
    elif post_type == PostType.META_EVENT:
        return MetaEvent(raw_event)
    else:
        return NapCatEvent(raw_event)


class EventHandler:
    """事件处理器"""

    def __init__(self):
        self.message_handlers: List[Callable] = []
        self.notice_handlers: List[Callable] = []
        self.request_handlers: List[Callable] = []

    def on_message(self, func: Callable):
        """注册消息处理器"""
        self.message_handlers.append(func)
        return func

    def on_notice(self, func: Callable):
        """注册通知处理器"""
        self.notice_handlers.append(func)
        return func

    def on_request(self, func: Callable):
        """注册请求处理器"""
        self.request_handlers.append(func)
        return func

    async def handle_event(self, event: NapCatEvent):
        """处理事件"""
        if isinstance(event, MessageEvent):
            for handler in self.message_handlers:
                try:
                    await handler(event)
                except Exception as e:
                    print(f"消息处理器错误: {e}")

        elif isinstance(event, NoticeEvent):
            for handler in self.notice_handlers:
                try:
                    await handler(event)
                except Exception as e:
                    print(f"通知处理器错误: {e}")

        elif isinstance(event, RequestEvent):
            for handler in self.request_handlers:
                try:
                    await handler(event)
                except Exception as e:
                    print(f"请求处理器错误: {e}")

