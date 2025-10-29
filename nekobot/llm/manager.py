"""
LLM 管理器
"""

from typing import Dict, Optional, List, Any
from nekobot.llm.provider import LLMProviderBase, create_provider
from nekobot.database.engine import get_db_manager
from nekobot.database.models import LLMProvider
from nekobot.utils.logger import get_logger
from sqlmodel import select

logger = get_logger("llm_manager")


class LLMManager:
    """LLM 管理器 - 负责管理多个 LLM 服务商"""

    def __init__(self):
        self.providers: Dict[str, LLMProviderBase] = {}
        self.db_manager = get_db_manager()
        logger.info("LLM 管理器初始化完成")

    async def load_providers_from_db(self):
        """从数据库加载所有 LLM 服务商"""
        try:
            async with self.db_manager.async_session_maker() as session:
                result = await session.execute(
                    select(LLMProvider).where(LLMProvider.is_active)
                )
                providers = result.scalars().all()

                for provider in providers:
                    try:
                        provider_instance = create_provider(
                            provider_type=provider.provider_type,
                            name=provider.name,
                            api_keys=provider.api_keys,
                            model=provider.model,
                            base_url=provider.base_url,
                            **provider.config,
                        )
                        self.providers[provider.name] = provider_instance
                        logger.info(f"LLM 服务商已加载: {provider.name}")
                    except Exception as e:
                        logger.error(f"加载 LLM 服务商失败 {provider.name}: {e}")

                logger.info(f"从数据库加载了 {len(self.providers)} 个 LLM 服务商")
        except Exception as e:
            logger.error(f"从数据库加载 LLM 服务商失败: {e}")

    async def add_provider(
        self,
        name: str,
        provider_type: str,
        api_keys: List[str],
        model: str,
        base_url: Optional[str] = None,
        **config,
    ) -> bool:
        """添加新的 LLM 服务商"""
        try:
            # 创建服务商实例
            provider = create_provider(
                provider_type=provider_type,
                name=name,
                api_keys=api_keys,
                model=model,
                base_url=base_url,
                **config,
            )

            # 保存到数据库
            async with self.db_manager.async_session_maker() as session:
                db_provider = LLMProvider(
                    name=name,
                    provider_type=provider_type,
                    api_keys=api_keys,
                    model=model,
                    base_url=base_url,
                    config=config,
                    is_active=True,
                )
                session.add(db_provider)
                await session.commit()

            self.providers[name] = provider
            logger.info(f"LLM 服务商已添加: {name}")
            return True

        except Exception as e:
            logger.error(f"添加 LLM 服务商失败: {e}")
            return False

    async def remove_provider(self, name: str) -> bool:
        """移除 LLM 服务商"""
        try:
            if name in self.providers:
                del self.providers[name]

            # 从数据库删除
            async with self.db_manager.async_session_maker() as session:
                result = await session.execute(
                    select(LLMProvider).where(LLMProvider.name == name)
                )
                provider = result.scalar_one_or_none()
                if provider:
                    await session.delete(provider)
                    await session.commit()

            logger.info(f"LLM 服务商已移除: {name}")
            return True

        except Exception as e:
            logger.error(f"移除 LLM 服务商失败: {e}")
            return False

    async def test_provider(self, name: str) -> bool:
        """测试 LLM 服务商连接"""
        provider = self.providers.get(name)
        if not provider:
            logger.warning(f"LLM 服务商不存在: {name}")
            return False

        return await provider.test_connection()

    def get_provider(self, name: str) -> Optional[LLMProviderBase]:
        """获取 LLM 服务商实例"""
        return self.providers.get(name)

    def get_all_providers(self) -> Dict[str, LLMProviderBase]:
        """获取所有 LLM 服务商"""
        return self.providers.copy()

    def get_provider_list(self) -> List[Dict[str, Any]]:
        """获取 LLM 服务商列表（用于 API）"""
        result = []
        for name, provider in self.providers.items():
            result.append(
                {
                    "name": name,
                    "model": provider.model,
                    "base_url": provider.base_url,
                    "api_key_count": len(provider.api_keys),
                }
            )
        return result

    async def chat(
        self, provider_name: str, messages: List[Dict[str, str]], **kwargs
    ) -> Dict[str, Any]:
        """使用指定服务商进行对话"""
        provider = self.get_provider(provider_name)
        if not provider:
            raise ValueError(f"LLM 服务商不存在: {provider_name}")

        return await provider.chat(messages, **kwargs)


# 全局 LLM 管理器实例
_llm_manager: Optional[LLMManager] = None


def get_llm_manager() -> LLMManager:
    """获取 LLM 管理器实例"""
    global _llm_manager
    if _llm_manager is None:
        _llm_manager = LLMManager()
    return _llm_manager

