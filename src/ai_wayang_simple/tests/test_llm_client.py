import pytest
from ai_wayang_simple.llm.client import LLMClient

def test_llm_output():
    llm = LLMClient()
    prompt = "Fill the plan simple and fast"
    output = llm.generate_plan(prompt)

    print(output)
    print(output["wayang_plan"])

    assert isinstance(output, dict)
    assert "wayang_plan" in output
    assert output["wayang_plan"] is not None