from pathlib import Path

class PromptLoader:
    """
    Prepares and loads prompts from the prompt folder
    """
    def __init__(self, path: str | None = None):
        self.path = Path(__file__).resolve().parent / "prompts"
        self.system_prompt = self.load_system_prompt()
    
    def load_system_prompt(self) -> str:
        """
        Load and build system prompt
        """

        system_prompt = self._read_file("system_prompt.txt")
        operators_prompt = self._read_file("operators.txt")
        data_prompt = self._read_file("data.txt")

        # Build prompt
        system_prompt = system_prompt.format(
            data=data_prompt,
            operators=operators_prompt
        )

        self.system_prompt = system_prompt
        return self.system_prompt
    
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

        

