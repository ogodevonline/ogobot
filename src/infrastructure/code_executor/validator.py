"""AST-based code validation for safety"""

import ast

FORBIDDEN_IMPORTS = {"os", "subprocess", "sys", "importlib", "eval", "exec"}


def validate_code_safety(code: str) -> list[str]:
    """Validate code for dangerous operations"""
    errors: list[str] = []

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return [f"Syntax error: {e}"]

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in FORBIDDEN_IMPORTS:
                    errors.append(f"Forbidden import: {alias.name}")

        if isinstance(node, ast.ImportFrom):
            if node.module and node.module in FORBIDDEN_IMPORTS:
                errors.append(f"Forbidden import: {node.module}")

        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in {"eval", "exec", "__import__"}:
                    errors.append(f"Forbidden call: {node.func.id}")

    return errors
