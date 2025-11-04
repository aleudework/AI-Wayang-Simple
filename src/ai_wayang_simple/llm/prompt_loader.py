from pathlib import Path
import json
from typing import List
from ai_wayang_simple.llm.models import WayangPlan

class PromptLoader:
    """
    Prepares and loads prompts from the prompt folder
    """
    def __init__(self, path: str | None = None):
        self.path = Path(__file__).resolve().parent / "prompts"
    
    def load_builder_system_prompt(self) -> str:
        """
        Load and build system prompt for builder agent
        """

        # Get prompt templates
        system_prompt = self._read_file("builder_prompts/system_prompt.txt")
        operators_prompt = self._read_file("operators.txt")
        data_prompt = self._read_file("data.txt")
        few_shot = None

        # Fill system prompt template
        system_prompt = system_prompt.replace("{data}", data_prompt)
        system_prompt = system_prompt.replace("{operators}", operators_prompt)

        return system_prompt
    
    def load_debugger_system_prompt(self) -> str:
        """
        Load and build system prompt for debugger agent
        """

        # Load prompts
        system_prompt = self._read_file("debugger_prompts/system_prompt.txt")
        operators_prompt = self._read_file("operators.txt")

        # Fill system prompt
        # REMEMBER TO LOAD
        system_prompt = system_prompt.replace("{operators}", operators_prompt)

        # Get and return system prompt
        return system_prompt
    
    def load_debugger_prompt_template(self, failed_plan: WayangPlan, wayang_errors: str, val_errors: List) -> str:
        """
        Output a new message for the debugger agent to handle on
        """

        # Get prompt template
        prompt_template = self._read_file("debugger_prompts/standard_prompt.txt")

        # Convert to correct JSON from WayangPlan model
        if hasattr(failed_plan, "model_dump"):
            failed_plan = json.dumps(failed_plan.model_dump(), indent=4)
        elif hasattr(failed_plan, "to_json"):
            failed_plan = failed_plan.to_json(indent=4)
        else:
            failed_plan = json.dumps(failed_plan.__dict__, indent=4)

        # Convert to JSON
        if not isinstance(wayang_errors, str):
            wayang_errors = json.dumps(wayang_errors, indent=4)

        # Converts val error to string
        val_errors = "\n".join([f"- {str(e)}" for e in val_errors])

        # Fill template
        prompt_template = prompt_template.replace("{failed_plan}", failed_plan)
        prompt_template = prompt_template.replace("{wayang_errors}", wayang_errors)
        prompt_template = prompt_template.replace("{val_errors}", val_errors)

        return prompt_template
    
    def load_debugger_answer_template(self, wayang_plan: WayangPlan) -> str:
        """
        Template for the debugger agent answer to the chat-correspondance
        """

        answer_template = self._read_file("debugger/agent_answer_template.txt")

        fixed_plan = json.dumps([op.model_dump() for op in wayang_plan.operations], indent=2, ensure_ascii=False)
        thoughts = wayang_plan.thoughts

        answer_template = answer_template.replace("{fixed_plan}", fixed_plan)
        answer_template = answer_template.replace("{thoughts}", thoughts)

        return answer_template
        
    
    def _read_file(self, file) -> str:
        """
        Helper func to read a file
        """
        file_path = self.path / file
        if not file_path.exists():
            raise FileNotFoundError(f"Couldn't find prompt file {file_path}")
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()

        

