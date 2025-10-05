"""数据库模型定义"""
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """用户模型"""

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True, max_length=50)
    password_hash: str = Field(max_length=128)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Plugin(SQLModel, table=True):
    """插件模型"""

    __tablename__ = "plugins"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True, max_length=100)
    version: str = Field(max_length=20)
    description: Optional[str] = None
    author: Optional[str] = Field(max_length=100)
    repository: Optional[str] = Field(max_length=255)
    enabled: bool = Field(default=True)
    is_official: bool = Field(default=False)
    path: str = Field(max_length=255)
    installed_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class LLMProvider(SQLModel, table=True):
    """LLM提供商模型"""

    __tablename__ = "llm_providers"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    provider_type: str = Field(max_length=50)
    api_keys: str = Field()
    model: str = Field(max_length=100)
    base_url: Optional[str] = Field(max_length=255)
    timeout: int = Field(default=60)
    enabled: bool = Field(default=True)
    config: Optional[str] = Field(default="{}")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Prompt(SQLModel, table=True):
    """提示词模型"""

    __tablename__ = "prompts"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    content: str = Field()
    category: Optional[str] = Field(max_length=50)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SystemLog(SQLModel, table=True):
    """系统日志模型"""

    __tablename__ = "system_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    level: str = Field(max_length=20, index=True)
    message: str = Field()
    module: str = Field(max_length=100)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    extra: Optional[str] = Field(default="{}")