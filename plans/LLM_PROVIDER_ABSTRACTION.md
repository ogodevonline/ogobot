# LLM Provider Abstraction Layer

## Концепция

Система должна поддерживать **любого OpenAI-compatible провайдера** без изменения кода:
- Groq (бесплатно, быстро)
- OpenAI (дорого, мощно)
- Anthropic Claude
- Ollama (локально)
- Together AI
- Replicate
- И другие...

## Реализация

### 1. Конфигурация (`.env`)

```env
# Выбираемый провайдер
LLM_PROVIDER=groq              # или openai, anthropic, ollama, etc.
LLM_API_KEY=your_key_here
LLM_MODEL=mixtral-8x7b-32768   # или gpt-4, claude-3, etc.
LLM_BASE_URL=https://api.groq.com/openai/v1  # опционально
```

### 2. Абстракция провайдера

```python
# src/infrastructure/llm/provider.py
from abc import ABC, abstractmethod
from typing import Any

class LLMProvider(ABC):
    """Abstract LLM provider"""
    
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Generate text"""
        pass
    
    @abstractmethod
    async def generate_code(self, spec: str) -> str:
        """Generate code from specification"""
        pass
```

### 3. Конкретные реализации

```python
# src/infrastructure/llm/groq_provider.py
from openai import AsyncOpenAI

class GroqProvider(LLMProvider):
    def __init__(self, api_key: str, model: str):
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        self.model = model
    
    async def generate(self, prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
```

### 4. Factory для создания провайдера

```python
# src/infrastructure/llm/factory.py
def create_llm_provider(provider_name: str) -> LLMProvider:
    """Create LLM provider by name"""
    providers = {
        "groq": GroqProvider,
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "ollama": OllamaProvider,
    }
    
    provider_class = providers.get(provider_name)
    if not provider_class:
        raise ValueError(f"Unknown provider: {provider_name}")
    
    return provider_class(
        api_key=os.getenv("LLM_API_KEY"),
        model=os.getenv("LLM_MODEL")
    )
```

### 5. Использование в графе

```python
# src/entrypoints/graph.py
from src.infrastructure.llm.factory import create_llm_provider

class CoderNode:
    def __init__(self):
        self.llm = create_llm_provider(os.getenv("LLM_PROVIDER"))
    
    async def execute(self, state: ExecutionState) -> ExecutionState:
        state.generated_code = await self.llm.generate_code(
            spec="\n".join(state.plan)
        )
        return state
```

## Преимущества

✅ **Гибкость** — Легко переключаться между провайдерами  
✅ **Экономия** — Использовать дешевые провайдеры (Groq)  
✅ **Локальность** — Поддержка Ollama для локального запуска  
✅ **Масштабируемость** — Добавлять новых провайдеров без изменения кода  
✅ **Тестируемость** — Mock провайдер для тестов  

## Фазы реализации

- **Phase 2** — Реализовать LLMProvider интерфейс
- **Phase 2** — Добавить GroqProvider (основной)
- **Phase 2** — Добавить OpenAIProvider (альтернатива)
- **Phase 3** — Добавить AnthropicProvider
- **Phase 4** — Добавить OllamaProvider (локально)

---

**Это позволит использовать S.E.A.C. с любым LLM провайдером!**
