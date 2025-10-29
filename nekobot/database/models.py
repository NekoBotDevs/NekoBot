"""
数据库模型定义
"""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, JSON
from sqlalchemy import Text


class User(SQLModel, table=True):
    """用户表"""

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True, max_length=50)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = Field(default=True)
    must_change_password: bool = Field(default=False)


class BotConfig(SQLModel, table=True):
    """机器人配置表"""

    __tablename__ = "bot_configs"

    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(unique=True, index=True, max_length=100)
    value: str = Field(sa_column=Column(Text))
    description: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class LLMProvider(SQLModel, table=True):
    """LLM 服务商配置表"""

    __tablename__ = "llm_providers"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True, max_length=100)
    provider_type: str = Field(max_length=50)
    api_keys: list = Field(default=[], sa_column=Column(JSON))
    base_url: Optional[str] = Field(default=None, max_length=255)
    model: str = Field(max_length=100)
    config: dict = Field(default={}, sa_column=Column(JSON))
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class PlatformAdapter(SQLModel, table=True):
    """平台适配器配置表"""

    __tablename__ = "platform_adapters"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True, max_length=100)
    platform_type: str = Field(max_length=50)
    config: dict = Field(default={}, sa_column=Column(JSON))
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Plugin(SQLModel, table=True):
    """插件信息表"""

    __tablename__ = "plugins"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True, max_length=100)
    version: str = Field(max_length=20)
    description: Optional[str] = Field(default=None, max_length=500)
    author: Optional[str] = Field(default=None, max_length=100)
    repository: Optional[str] = Field(default=None, max_length=255)
    is_official: bool = Field(default=False)
    is_active: bool = Field(default=True)
    config: dict = Field(default={}, sa_column=Column(JSON))
    install_path: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Conversation(SQLModel, table=True):
    """对话历史表"""

    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, max_length=100)
    platform: str = Field(index=True, max_length=50)
    messages: list = Field(default=[], sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

