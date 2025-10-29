"""
LLM 服务商管理
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncIterator
from enum import Enum

from nekobot.utils.logger import get_logger

logger = get_logger("llm")


class ProviderType(str, Enum):
    """服务商类型"""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    CUSTOM = "custom"


class LLMProviderBase(ABC):
    """LLM 服务商基类"""

    def __init__(
        self,
        name: str,
        api_keys: List[str],
        model: str,
        base_url: Optional[str] = None,
        **kwargs,
    ):
        self.name = name
        self.api_keys = api_keys
        self.model = model
        self.base_url = base_url
        self.config = kwargs
        self.current_key_index = 0

    def _get_next_api_key(self) -> str:
        """轮询获取 API Key"""
        if not self.api_keys:
            raise ValueError("未配置 API Key")

        key = self.api_keys[self.current_key_index]
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        return key

    @abstractmethod
    async def chat(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> Dict[str, Any]:
        """聊天接口"""
        pass

    @abstractmethod
    async def chat_stream(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> AsyncIterator[str]:
        """流式聊天接口"""
        pass

    async def test_connection(self) -> bool:
        """测试连接"""
        try:
            test_messages = [{"role": "user", "content": "Hello"}]
            await self.chat(test_messages, max_tokens=10)
            return True
        except Exception as e:
            logger.error(f"连接测试失败: {e}")
            return False


class OpenAIProvider(LLMProviderBase):
    """OpenAI 服务商"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from openai import AsyncOpenAI

        self.client = AsyncOpenAI(
            api_key=self._get_next_api_key(),
            base_url=self.base_url,
        )

    async def chat(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> Dict[str, Any]:
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **kwargs,
            )

            return {
                "content": response.choices[0].message.content,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
            }
        except Exception as e:
            logger.error(f"OpenAI 调用失败: {e}")
            raise

    async def chat_stream(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> AsyncIterator[str]:
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                **kwargs,
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"OpenAI 流式调用失败: {e}")
            raise


class AnthropicProvider(LLMProviderBase):
    """Anthropic (Claude) 服务商"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from anthropic import AsyncAnthropic

        self.client = AsyncAnthropic(api_key=self._get_next_api_key())

    async def chat(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> Dict[str, Any]:
        try:
            # 提取系统消息
            system_message = None
            filtered_messages = []

            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    filtered_messages.append(msg)

            response = await self.client.messages.create(
                model=self.model,
                messages=filtered_messages,
                system=system_message,
                max_tokens=kwargs.get("max_tokens", 4096),
                **{k: v for k, v in kwargs.items() if k != "max_tokens"},
            )

            return {
                "content": response.content[0].text,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens
                    + response.usage.output_tokens,
                },
            }
        except Exception as e:
            logger.error(f"Anthropic 调用失败: {e}")
            raise

    async def chat_stream(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> AsyncIterator[str]:
        try:
            system_message = None
            filtered_messages = []

            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    filtered_messages.append(msg)

            async with self.client.messages.stream(
                model=self.model,
                messages=filtered_messages,
                system=system_message,
                max_tokens=kwargs.get("max_tokens", 4096),
                **{k: v for k, v in kwargs.items() if k != "max_tokens"},
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        except Exception as e:
            logger.error(f"Anthropic 流式调用失败: {e}")
            raise


class GoogleProvider(LLMProviderBase):
    """Google (Gemini) 服务商"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from google import genai
        from google.genai.types import GenerateContentConfig

        self.client = genai.Client(api_key=self._get_next_api_key())
        self.config_class = GenerateContentConfig

    async def chat(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> Dict[str, Any]:
        try:
            # 转换消息格式
            contents = self._convert_messages(messages)

            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=contents,
                config=self.config_class(**kwargs) if kwargs else None,
            )

            return {
                "content": response.text,
                "model": self.model,
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                },
            }
        except Exception as e:
            logger.error(f"Google 调用失败: {e}")
            raise

    async def chat_stream(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> AsyncIterator[str]:
        try:
            contents = self._convert_messages(messages)

            async for chunk in self.client.aio.models.generate_content_stream(
                model=self.model,
                contents=contents,
                config=self.config_class(**kwargs) if kwargs else None,
            ):
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.error(f"Google 流式调用失败: {e}")
            raise

    def _convert_messages(self, messages: List[Dict[str, str]]) -> str:
        """转换消息格式为 Google 格式"""
        result = []
        for msg in messages:
            role = msg["role"]
            if role == "assistant":
                role = "model"
            result.append(f"{role}: {msg['content']}")
        return "\n".join(result)


def create_provider(
    provider_type: str,
    name: str,
    api_keys: List[str],
    model: str,
    base_url: Optional[str] = None,
    **kwargs,
) -> LLMProviderBase:
    """工厂函数：创建 LLM 服务商实例"""
    provider_type = provider_type.lower()

    if provider_type == ProviderType.OPENAI or provider_type == "custom":
        return OpenAIProvider(name, api_keys, model, base_url, **kwargs)
    elif provider_type == ProviderType.ANTHROPIC:
        return AnthropicProvider(name, api_keys, model, base_url, **kwargs)
    elif provider_type == ProviderType.GOOGLE:
        return GoogleProvider(name, api_keys, model, base_url, **kwargs)
    else:
        raise ValueError(f"不支持的服务商类型: {provider_type}")

