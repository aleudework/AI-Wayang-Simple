from pathlib import Path
import json
from typing import List
from ai_wayang_simple.llm.models import WayangPlan


class PromptLoader:
    """
    Loads and prepares prompts for agents

    """
    def __init__(self, path: str | None = None):
        self.path = Path(__file__).resolve().parent / "prompts"
    
    def load_builder_system_prompt(self) -> str:
        """
        Load and prepare system prompt for Builder Agent

        Returns:
            (str): Builder's system prompt

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
        Load and prepare system prompt for Debugger Agent

        Returns:
            (str): Debuggers's system prompt

        """

        # Load prompts
        system_prompt = self._read_file("debugger_prompts/system_prompt.txt")
        operators_prompt = self._read_file("operators.txt")
        few_shot = None

        # Fill system prompt
        # REMEMBER TO LOAD
        system_prompt = system_prompt.replace("{operators}", operators_prompt)

        # Get and return system prompt
        return system_prompt
    

    def load_debugger_prompt_template(self, failed_plan: WayangPlan, wayang_errors: str, val_errors: List) -> str:
        """
        Load and prepare prompt to be sent to the Debugger.
        The prompt is about fixing a failed plan

        Args:
            failed_plan (WayangPlan): The failed Wayang plan
            wayang_errors (str): The error provided by the Wayang server
            val_errors (List): Errors from PlanValidator if any

        Returns:
            (str): Debuggers prompt to be sent to the Debugger Agent

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
        Load and prepare Debugger Agents answer. It is for it to keep track of its own answers when debugging in multiple iterations

        Args:
            wayang_plan (WayangPlan): The WayangPlan fixed by the Debugger Agent in current iteration

        Returns:
            (str): The answer to be linked to the Debugger Agent's chat in current session

        """

        # Load answer template
        answer_template = self._read_file("debugger_prompts/agent_answer.txt")

        # Load debuggers fixed plan and thoughts
        fixed_plan = json.dumps([op.model_dump() for op in wayang_plan.operations], indent=2, ensure_ascii=False)
        thoughts = wayang_plan.thoughts
        
        # Fill template
        answer_template = answer_template.replace("{fixed_plan}", fixed_plan)
        answer_template = answer_template.replace("{thoughts}", thoughts)

        return answer_template
        
    
    def _read_file(self, file: str) -> str:
        """
        Helper function to open prompt template files

        Args:
            file (str): Name of prompt file including extension (.txt)

        Returns:
            (str): The file

        """
        file_path = self.path / file
        if not file_path.exists():
            raise FileNotFoundError(f"Couldn't find prompt file {file_path}")
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()

        

