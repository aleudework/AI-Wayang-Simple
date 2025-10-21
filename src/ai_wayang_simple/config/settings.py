import os
from dotenv import load_dotenv

# Read env variables from .env file
load_dotenv()

# Server port for MCP server
MCP_CONFIG = {
    "port": int(os.getenv("MCP_PORT", 9400))
}

# LLM client model settings
MODEL_CONFIG = {
    "model": os.getenv("LLM_MODEL", "gpt-5-nano"),
    "reason_effort": os.getenv("REASON_EFFORT", None)
}

# JDBC settings
JDBC_CONFIG = {
    "jdbc_uri": os.getenv("JDBC_URI", "jdbc:postgresql://localhost:5432/master_thesis_db"),
    "jdbc_username": os.getenv("JDBC_USERNAME", "master_thesis"),
    "jdbc_password": os.getenv("JDBC_PASSWORD", "master"),
}

# Log settings
LOG_CONFIG = {
    "log_folder": os.getenv("LOG_FOLDER")
}