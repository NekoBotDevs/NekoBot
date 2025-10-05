"""数据库管理器"""
from pathlib import Path
from typing import List, Optional, Type, TypeVar
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlmodel import SQLModel, select
from .models import User, Plugin, LLMProvider, Prompt, SystemLog

T = TypeVar("T", bound=SQLModel)


class DatabaseManager:
    """数据库管理器"""

    def __init__(self, db_path: str = "./data/nekobot.db"):
        """初始化数据库管理器
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        db_url = f"sqlite+aiosqlite:///{self.db_path}"
        self.engine: AsyncEngine = create_async_engine(
            db_url, echo=False, future=True
        )
        self.session_maker = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def init_db(self) -> None:
        """初始化数据库表"""
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    async def get_session(self) -> AsyncSession:
        """获取数据库会话"""
        async with self.session_maker() as session:
            return session

    async def create(self, model: T) -> T:
        """创建记录
        
        Args:
            model: 模型实例
            
        Returns:
            创建的模型实例
        """
        async with self.session_maker() as session:
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return model

    async def get_by_id(
        self, model_class: Type[T], record_id: int
    ) -> Optional[T]:
        """根据ID获取记录
        
        Args:
            model_class: 模型类
            record_id: 记录ID
            
        Returns:
            模型实例或None
        """
        async with self.session_maker() as session:
            return await session.get(model_class, record_id)

    async def get_all(
        self, model_class: Type[T], limit: int = 100, offset: int = 0
    ) -> List[T]:
        """获取所有记录
        
        Args:
            model_class: 模型类
            limit: 限制数量
            offset: 偏移量
            
        Returns:
            模型实例列表
        """
        async with self.session_maker() as session:
            stmt = select(model_class).limit(limit).offset(offset)
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def get_by_field(
        self, model_class: Type[T], field: str, value: any
    ) -> Optional[T]:
        """根据字段获取记录
        
        Args:
            model_class: 模型类
            field: 字段名
            value: 字段值
            
        Returns:
            模型实例或None
        """
        async with self.session_maker() as session:
            stmt = select(model_class).where(
                getattr(model_class, field) == value
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def update(self, model: T) -> T:
        """更新记录
        
        Args:
            model: 模型实例
            
        Returns:
            更新后的模型实例
        """
        async with self.session_maker() as session:
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return model

    async def delete(self, model: T) -> None:
        """删除记录
        
        Args:
            model: 模型实例
        """
        async with self.session_maker() as session:
            await session.delete(model)
            await session.commit()

    async def delete_by_id(
        self, model_class: Type[T], record_id: int
    ) -> bool:
        """根据ID删除记录
        
        Args:
            model_class: 模型类
            record_id: 记录ID
            
        Returns:
            是否删除成功
        """
        record = await self.get_by_id(model_class, record_id)
        if record:
            await self.delete(record)
            return True
        return False

    async def close(self) -> None:
        """关闭数据库连接"""
        await self.engine.dispose()