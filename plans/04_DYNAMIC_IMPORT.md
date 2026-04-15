# 4. Механизм Динамического Импорта Инструментов

## Архитектура

```
CoderNode генерирует код
    ↓
ValidationNode проверяет безопасность
    ↓
ApprovalNode ждет подтверждения
    ↓
register_tool() сохраняет в БД + файловую систему
    ↓
ToolRegistry перезагружает модуль через importlib
    ↓
Инструмент доступен для использования БЕЗ рестарта
```

## Реестр Инструментов

```python
# src/tools/registry.py
import importlib
import sys
from pathlib import Path
from typing import Callable, Any

class ToolRegistry:
    """Управляет динамически загружаемыми инструментами"""
    
    def __init__(self, tools_dir: Path):
        self.tools_dir = tools_dir
        self.tools: dict[str, Callable] = {}
    
    def register(self, name: str, code: str) -> None:
        """Сохраняет код и загружает инструмент"""
        # 1. Сохранить в БД
        tool_model = Tool(
            name=name,
            code=code,
            version=1
        )
        db.add(tool_model)
        db.commit()
        
        # 2. Сохранить в файловую систему
        file_path = self.tools_dir / f"{name}.py"
        file_path.write_text(code)
        
        # 3. Загрузить через importlib
        self._reload_tool(name)
    
    def _reload_tool(self, name: str) -> None:
        """Перезагружает модуль инструмента"""
        module_name = f"src.tools.{name}"
        
        # Удалить старый модуль из sys.modules
        if module_name in sys.modules:
            del sys.modules[module_name]
        
        # Импортировать заново
        module = importlib.import_module(module_name)
        
        # Сохранить функцию в реестр
        if hasattr(module, "execute"):
            self.tools[name] = module.execute
    
    def get_tool(self, name: str) -> Callable | None:
        """Получить инструмент по имени"""
        return self.tools.get(name)
    
    def list_tools(self) -> list[str]:
        """Список всех доступных инструментов"""
        return list(self.tools.keys())
```

## Структура Сгенерированного Инструмента

```python
# src/tools/my_tool.py (автоматически создается)
from typing import Any
from loguru import logger

async def execute(input_data: dict[str, Any]) -> dict[str, Any]:
    """
    Сгенерированный инструмент
    
    Args:
        input_data: Входные параметры
    
    Returns:
        Результат выполнения
    """
    logger.info(f"Executing my_tool with {input_data}")
    
    # Сгенерированная логика
    result = process_data(input_data)
    
    logger.info(f"my_tool completed: {result}")
    return result
```

## Безопасность (AST Validation)

```python
# src/infrastructure/code_executor/validator.py
import ast
from typing import set

FORBIDDEN_IMPORTS = {
    "os", "subprocess", "sys", "importlib",
    "eval", "exec", "__import__"
}

def validate_code_safety(code: str) -> list[str]:
    """Проверяет код на опасные операции"""
    errors = []
    
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return [f"Syntax error: {e}"]
    
    for node in ast.walk(tree):
        # Проверка импортов
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in FORBIDDEN_IMPORTS:
                    errors.append(f"Forbidden import: {alias.name}")
        
        # Проверка вызовов опасных функций
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in {"eval", "exec", "__import__"}:
                    errors.append(f"Forbidden call: {node.func.id}")
    
    return errors
```

## Sandbox Execution

```python
# src/infrastructure/code_executor/sandbox.py
import asyncio
import subprocess
from typing import Any

async def execute_in_sandbox(
    code: str,
    timeout: int = 30
) -> Any:
    """Выполняет код в изолированном процессе"""
    
    try:
        # Запустить в subprocess с таймаутом
        result = await asyncio.wait_for(
            asyncio.create_subprocess_exec(
                "python", "-c", code,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            ),
            timeout=timeout
        )
        
        stdout, stderr = await result.communicate()
        
        if result.returncode != 0:
            raise RuntimeError(stderr.decode())
        
        return stdout.decode()
    
    except asyncio.TimeoutError:
        raise TimeoutError(f"Code execution exceeded {timeout}s")
```

---

**Далее:** [`05_GRAPH_FLOW.md`](05_GRAPH_FLOW.md)
