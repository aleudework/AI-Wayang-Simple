from pathlib import Path
import json

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
        system_prompt = self._read_file("builder_system_prompt.txt")
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

        # Get and return system prompt
        return self._read_file("debugger_system_prompt.txt")
    
    def load_debugger_prompt_template(self, failed_plan: str, error: str) -> str:
        """
        Output a new message for the debugger agent to handle on
        """

        # Get prompt template
        prompt_template = self._read_file("debugger_standard_prompt.txt")

        # Convert to JSON
        if not isinstance(failed_plan, str):
            failed_plan = json.dumps(failed_plan, indent=4)

        # Convert to JSON
        if not isinstance(error, str):
            error = json.dumps(error, indent=4)

        # Fill template
        prompt_template = prompt_template.replace("{failed_plan}", failed_plan)
        prompt_template = prompt_template.replace("{error}", error)

        return prompt_template
    
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

        

