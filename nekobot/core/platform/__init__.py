"""平台适配器模块"""
from .base_adapter import BasePlatformAdapter, PlatformEvent, MessageType
from .adapter_manager import AdapterManager
from .sources.wecom.wecom_adapter import WeComAdapter
from .sources.aiocqhttp.aiocqhttp_platform_adapter import AiocqhttpAdapter
from .sources.qqofficial_webhook.qo_webhook_adapter import QQOfficialWebhookAdapter
from .sources.slack.slack_adapter import SlackAdapter

__all__ = [
    "BasePlatformAdapter",
    "PlatformEvent",
    "MessageType",
    "AdapterManager",
    "WeComAdapter",
    "AiocqhttpAdapter",
    "QQOfficialWebhookAdapter",
    "SlackAdapter",
]