"""
Entrypoint
"""
import sys
from pathlib import Path

# Tilføj src-mappen til Pythons søgesti
sys.path.append(str(Path(__file__).resolve().parent / "src"))

from src.ai_wayang_simple.server.mcp_server import mcp

def main():

    mcp.run(transport="streamable-http")
    print(f"Starts MCP-server")

if __name__ == "__main__":
    main()