"""Pydantic AI agents for planning and code generation"""

import asyncio
from typing import Any

from loguru import logger

from src.application.dto import CodeResult, PlanResult
from src.infrastructure.llm.provider import LLMProvider

# System prompts
PLANNER_SYSTEM_PROMPT = """You are an expert task planner. Your job is to:
1. Analyze the user's intent
2. Break it down into clear, actionable steps
3. Assess the complexity of the task
4. Provide reasoning for your plan

Return a JSON response with:
- steps: list of step descriptions
- reasoning: explanation of the plan
- estimated_complexity: "low", "medium", or "high"
"""

CODER_SYSTEM_PROMPT = """You are an expert Python developer. Your job is to:
1. Read the task plan
2. Generate clean, well-documented Python code
3. List all required dependencies
4. Provide clear explanation of the code

Return a JSON response with:
- code: the generated Python code
- explanation: description of what the code does
- dependencies: list of required packages
"""

# Retry configuration
MAX_RETRIES = 3
TIMEOUT_SECONDS = 60


class PlannerAgent:
    """Agent for task planning using LLM"""

    def __init__(self, provider: LLMProvider) -> None:
        """Initialize planner agent"""
        self.provider = provider
        logger.info("PlannerAgent initialized")

    async def run(self, intent: dict[str, Any]) -> PlanResult:
        """Run planner agent with retry logic"""
        intent_str = str(intent)
        logger.info(f"PlannerAgent.run: Processing intent: {intent_str[:100]}")

        for attempt in range(MAX_RETRIES):
            try:
                prompt = f"""{PLANNER_SYSTEM_PROMPT}

User intent: {intent_str}

Respond with valid JSON only."""
                response = await asyncio.wait_for(
                    self.provider.generate(prompt),
                    timeout=TIMEOUT_SECONDS,
                )
                result = self._parse_plan_response(response)
                logger.info(f"PlannerAgent.run: Success on attempt {attempt + 1}")
                return result
            except asyncio.TimeoutError:
                logger.warning(
                    f"PlannerAgent.run: Timeout on attempt {attempt + 1}/{MAX_RETRIES}"
                )
                if attempt == MAX_RETRIES - 1:
                    raise
            except Exception as e:
                logger.error(f"PlannerAgent.run: Error on attempt {attempt + 1}: {e}")
                if attempt == MAX_RETRIES - 1:
                    raise
        raise RuntimeError("PlannerAgent failed after all retries")

    def _parse_plan_response(self, response: str) -> PlanResult:
        """Parse LLM response into PlanResult"""
        import json

        try:
            data = json.loads(response)
            return PlanResult(
                steps=data.get("steps", []),
                reasoning=data.get("reasoning", ""),
                estimated_complexity=data.get("estimated_complexity", "medium"),
            )
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"PlannerAgent._parse_plan_response: Parse error: {e}")
            raise ValueError(f"Invalid plan response: {e}") from e


class CoderAgent:
    """Agent for code generation using LLM"""

    def __init__(self, provider: LLMProvider) -> None:
        """Initialize coder agent"""
        self.provider = provider
        logger.info("CoderAgent initialized")

    async def run(self, plan: list[str]) -> CodeResult:
        """Run coder agent with retry logic"""
        plan_str = "\n".join(plan)
        logger.info(f"CoderAgent.run: Processing plan with {len(plan)} steps")

        for attempt in range(MAX_RETRIES):
            try:
                prompt = f"""{CODER_SYSTEM_PROMPT}

Task plan:
{plan_str}

Respond with valid JSON only."""
                response = await asyncio.wait_for(
                    self.provider.generate(prompt),
                    timeout=TIMEOUT_SECONDS,
                )
                result = self._parse_code_response(response)
                logger.info(f"CoderAgent.run: Success on attempt {attempt + 1}")
                return result
            except asyncio.TimeoutError:
                logger.warning(
                    f"CoderAgent.run: Timeout on attempt {attempt + 1}/{MAX_RETRIES}"
                )
                if attempt == MAX_RETRIES - 1:
                    raise
            except Exception as e:
                logger.error(f"CoderAgent.run: Error on attempt {attempt + 1}: {e}")
                if attempt == MAX_RETRIES - 1:
                    raise
        raise RuntimeError("CoderAgent failed after all retries")

    def _parse_code_response(self, response: str) -> CodeResult:
        """Parse LLM response into CodeResult"""
        import json

        try:
            data = json.loads(response)
            return CodeResult(
                code=data.get("code", ""),
                explanation=data.get("explanation", ""),
                dependencies=data.get("dependencies", []),
            )
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"CoderAgent._parse_code_response: Parse error: {e}")
            raise ValueError(f"Invalid code response: {e}") from e
