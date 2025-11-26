from __future__ import annotations

from typing import Protocol


class LLMClient(Protocol):
    """
    Minimal protocol for an LLM client.

    A real implementation would wrap StegVerse-AI / OpenAI / etc.
    This interface lets CosDenOS depend on a narrow abstraction:
    given a prompt, return a short text completion.

    For now, CosmeticPlannerAgent can work without any LLM – we
    still support a rule-based planner.
    """

    def complete(self, prompt: str, max_tokens: int = 256) -> str:
        ...
