"""
Cerebras LLM client for text generation.
This is the ONLY interface for LLM generation in the application.
"""
from typing import Optional, AsyncGenerator
from openai import AsyncOpenAI

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class CerebrasClient:
    """
    Async Cerebras LLM client using OpenAI-compatible API.

    Responsibilities:
    - Text generation
    - Streaming responses
    - Token management
    """

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.CEREBRAS_API_KEY,
            base_url="https://api.cerebras.ai/v1"
        )
        self.model = settings.CEREBRAS_MODEL
        self.max_tokens = settings.CEREBRAS_MAX_TOKENS
        self.temperature = settings.CEREBRAS_TEMPERATURE

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Generate text completion.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            max_tokens: Override default max tokens
            temperature: Override default temperature

        Returns:
            Generated text
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature,
            )

            content = response.choices[0].message.content
            logger.info(
                "LLM generation completed",
                model=self.model,
                tokens_used=response.usage.total_tokens,
            )
            return content

        except Exception as e:
            logger.error("LLM generation failed", error=str(e))
            raise

    async def stream_generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Stream text completion.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            max_tokens: Override default max tokens
            temperature: Override default temperature

        Yields:
            Text chunks as they are generated
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

            logger.info("LLM streaming completed", model=self.model)

        except Exception as e:
            logger.error("LLM streaming failed", error=str(e))
            raise


# Global client instance
cerebras_client = CerebrasClient()
