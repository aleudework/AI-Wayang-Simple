import pytest
from ai_wayang_simple.llm.prompt_loader import PromptLoader

pl = PromptLoader()

print(pl.load_few_shot_prompt())

print(pl.load_debugger_system_prompt())