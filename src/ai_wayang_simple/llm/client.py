from openai import OpenAI
from ai_wayang_simple.config.settings import MODEL_CONFIG
from ai_wayang_simple.llm.models import WayangPlan
from ai_wayang_simple.llm.prompt_loader import PromptLoader

class LLMClient:
    """
    OpenAI LLM client (a wrapper)
    """
    def __init__(self, model: str | None = None, system_prompt: str | None = None):
        self.client = OpenAI()
        self.model = model or MODEL_CONFIG.get("model")
        self.system_prompt = system_prompt or PromptLoader().system_prompt

    def generate_plan(self, prompt: str):
        """
        Generates a Wayang JSON-plan
        """

        params = {
            "model": self.model,
            "input": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ],
            "text_format": WayangPlan
        }

        effort = MODEL_CONFIG.get("reason_effort")

        if effort:
            params["reasoning"] = {"effort": effort}

        response = self.client.responses.parse(**params)

        return {
            "raw": response,
            "wayang_plan": response.output_parsed
        }

        

