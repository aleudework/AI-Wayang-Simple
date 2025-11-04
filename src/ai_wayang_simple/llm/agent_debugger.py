from openai import OpenAI
import re
import json

from ai_wayang_simple.config.settings import DEBUGGER_MODEL_CONFIG
from ai_wayang_simple.llm.prompt_loader import PromptLoader
from ai_wayang_simple.llm.models import WayangPlan

class Debugger:
    """
    OpenAI LLM client as debugger
    """

    def __init__(self, model: str | None = None, system_prompt: str | None = None, version: int | None = None):
        self.client = OpenAI()
        self.model = model or DEBUGGER_MODEL_CONFIG.get("model")
        self.system_prompt = system_prompt or PromptLoader().load_builder_system_prompt()
        self.version = version or 0
        self.chat = []

    
    def get_version(self) -> int:
        """
        Getter to get plan version / iteration
        """

        return self.version
    
    def set_vesion(self, version: int) -> int:
        """
        Set the plan version / iteration
        """ 
        
        self.version = version
        return self.get_version()

    def debug_plan(self, plan: WayangPlan, wayang_errors, val_errors):
        """
        Debug a failed plan from an error message
        """

        # increment version
        self.version += 1

        # Create new user prompt
        prompt = PromptLoader().load_debugger_prompt_template(plan, wayang_errors, val_errors)

        # Add user prompt to chat
        self.chat.append({"role": "user", "content": prompt})

        # Add model and current chat
        params = {
            "model": self.model,
            "input": self.chat,
            "text_format": WayangPlan
        }

        # Initialize effort
        effort = DEBUGGER_MODEL_CONFIG.get("reason_effort")
        if effort:
            params["reasoning"] = {"effort": effort}

        # Generate response
        response = self.client.responses.parse(**params)

        # Format text answer from agent
        wayang_plan = response.output_parsed
        answer = PromptLoader().load_debugger_answer_template(wayang_plan)

        # Add agent answer to chat - necessary if another debug iteration is needed
        self.chat.append({"role": "assistant", "content": answer})

        # Return output
        return {
            "raw": response,
            "wayang_plan": wayang_plan,
            "version": self.version
        }
    
    def start_debugger(self) -> None:
        """
        Initialize a new debugger session.
        Removes previous chats from previous debugger sessions
        """

        self.chat = [{"role": "system", "content": self.system_prompt}]

    
    ### Temp, to be deleted after refactoring
    ########
    def _extract_json(self, text):
        """
        Helper to extract text-output from model and ensure it is json
        """

        # Check if output is text
        if not text:
            self.chat.append({"role": "assistant", "content": text})
            self.chat.append({"role": "user", "content": "You should only output in JSON"})
            print(f"[INFO] Debugger's output at itr {self.version} is not text")
            return None
        
        # Look for json in output
        match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL) # DOTALL goes through all lines (and not just a single line)

        # Check output has a match
        if not match:
            self.chat.append({"role": "assistant", "content": text})
            self.chat.append({"role": "user", "content": "You haven't outputted JSON correctly"})
            print(f"[INFO] Debugger's output at itr {self.version} is not JSON")
            return None
        
        # Get first JSON match
        json_str = match.group(1)

        # Parse JSON
        try:
            json_plan = json.loads(json_str)
            self.chat.append({"role": "assistant", "content": json.dumps(json_plan, indent=2)})
            return json_plan
        except Exception as e:
            print(f"[ERROR] Couldn't load in JSON, error: {e}")
            return None
