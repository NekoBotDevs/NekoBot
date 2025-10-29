"""
数据库引擎管理
"""

from pathlib import Path
from typing import Optional
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from nekobot.utils.logger import get_logger

logger = get_logger("database")


class DatabaseManager:
    """数据库管理器"""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            data_dir = Path("./data")
            data_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(data_dir / "nekobot.db")

        self.db_url = f"sqlite:///{db_path}"
        self.async_db_url = f"sqlite+aiosqlite:///{db_path}"

        # 同步引擎
        self.engine = create_engine(self.db_url, echo=False)

        # 异步引擎
        self.async_engine = create_async_engine(
            self.async_db_url, echo=False, future=True
        )

        # 异步会话工厂
        self.async_session_maker = sessionmaker(
            self.async_engine, class_=AsyncSession, expire_on_commit=False
        )

        logger.info(f"数据库初始化完成: {db_path}")

    def create_db_and_tables(self):
        """创建数据库表"""
        SQLModel.metadata.create_all(self.engine)
        logger.info("数据库表创建完成")

    async def create_db_and_tables_async(self):
        """异步创建数据库表"""
        async with self.async_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        logger.info("数据库表创建完成（异步）")

    def get_session(self) -> Session:
        """获取同步会话"""
        return Session(self.engine)

    async def get_async_session(self) -> AsyncSession:
        """获取异步会话"""
        async with self.async_session_maker() as session:
            yield session

    async def close(self):
        """关闭数据库连接"""
        await self.async_engine.dispose()
        logger.info("数据库连接已关闭")


# 全局数据库实例
db_manager: Optional[DatabaseManager] = None


def get_db_manager() -> DatabaseManager:
    """获取数据库管理器实例"""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager

