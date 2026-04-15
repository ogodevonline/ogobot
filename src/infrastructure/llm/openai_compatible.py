"""OpenAI-compatible LLM provider implementation"""

from openai import AsyncOpenAI

from src.infrastructure.llm.provider import LLMProvider


class OpenAICompatibleProvider(LLMProvider):
    """OpenAI-compatible provider (Groq, OpenAI, etc.)"""

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str | None = None,
    ) -> None:
        """Initialize provider"""
        self.model = model
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
        )

    async def generate(self, prompt: str) -> str:
        """Generate text from prompt"""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response.choices[0].message.content or ""

    async def generate_code(self, spec: str) -> str:
        """Generate code from specification"""
        prompt = f"""Generate Python code based on this specification:

{spec}

Return only the code, no explanations."""
        return await self.generate(prompt)
