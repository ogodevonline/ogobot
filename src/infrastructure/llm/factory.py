"""LLM provider factory"""

import os

from loguru import logger

from src.infrastructure.llm.openai_compatible import OpenAICompatibleProvider
from src.infrastructure.llm.provider import LLMProvider


def create_llm_provider() -> LLMProvider:
    """Create LLM provider from environment variables"""
    provider_name = os.getenv("LLM_PROVIDER", "groq").lower()
    api_key = os.getenv("LLM_API_KEY")
    model = os.getenv("LLM_MODEL")
    base_url = os.getenv("LLM_BASE_URL")

    if not api_key:
        raise ValueError("LLM_API_KEY not set")
    if not model:
        raise ValueError("LLM_MODEL not set")

    logger.info(f"Creating LLM provider: {provider_name}")

    # Map provider names to base URLs
    base_urls = {
        "groq": "https://api.groq.com/openai/v1",
        "openai": "https://api.openai.com/v1",
        "ollama": "http://localhost:11434/v1",
    }

    if not base_url and provider_name in base_urls:
        base_url = base_urls[provider_name]

    return OpenAICompatibleProvider(
        api_key=api_key,
        model=model,
        base_url=base_url,
    )
