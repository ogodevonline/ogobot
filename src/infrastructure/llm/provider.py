"""Abstract LLM provider interface"""

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Abstract LLM provider for OpenAI-compatible APIs"""

    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Generate text from prompt"""
        pass

    @abstractmethod
    async def generate_code(self, spec: str) -> str:
        """Generate code from specification"""
        pass
