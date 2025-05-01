# tests/conftest.py
# -*- coding: utf-8 -*-
"""Stubs external libs required by findora during import time."""

from types import ModuleType
from unittest.mock import MagicMock
import sys

# ----- stub llmatch ---------------------------------------------------------
llmatch_stub = ModuleType("llmatch")
llmatch_stub.llmatch = MagicMock(name="llmatch")
sys.modules["llmatch"] = llmatch_stub

# ----- stub langchain_llm7.ChatLLM7 ----------------------------------------
langchain_stub = ModuleType("langchain_llm7")

class _ChatLLM7:
    def __init__(self, *_, **__): ...

langchain_stub.ChatLLM7 = _ChatLLM7
sys.modules["langchain_llm7"] = langchain_stub
