"""
OpenAI Agent integration for natural language task management.

This module provides the OpenAI agent configuration and runner
for processing user messages and executing task operations.
"""

from app.agent.config import get_openai_client, SYSTEM_PROMPT, get_agent_tools
from app.agent.runner import run_agent

__all__ = [
    "get_openai_client",
    "SYSTEM_PROMPT",
    "get_agent_tools",
    "run_agent",
]
