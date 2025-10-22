from mcp.server.fastmcp import FastMCP
from ai_wayang_simple.config.settings import MCP_CONFIG, JDBC_CONFIG
from ai_wayang_simple.llm.client import LLMClient
from ai_wayang_simple.wayang.plan_builder import PlanBuilder
from ai_wayang_simple.wayang.wayang_executor import WayangExecutor
from datetime import datetime
import json

# Initialize MCP-server
mcp = FastMCP(name="AI-Wayang-Simple", port=MCP_CONFIG.get("port"))

# Initialise OpenAI Client
llm = LLMClient()

@mcp.tool()
def query_wayang(describe_wayang_plan: str) -> str:
    """
    Ask in English and describe the plan as detailed as possible.
    The function generates a wayang plan and executes it based on natural language in English
    """
    try:

        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
    
        print("[INFO] Generates draft plan")
        response = llm.generate_plan(describe_wayang_plan)

        draft_plan = response.get("wayang_plan")
        print("[INFO] Draft generated")
        print("[INFO] Compiles plan")
        plan_builder = PlanBuilder(JDBC_CONFIG)

        temp_outfile = f"file:///Users/alexander/Downloads/output_{timestamp}.txt"
        compiled_plan = plan_builder.build(draft_plan, temp_outfile)

        ### temp logging

        print("[INFO] Plan compiled")

        log = {
            "model": response['raw'].model,
            "usage": response['raw'].usage,
            "prompt": describe_wayang_plan,
            "llm_plan": draft_plan,
            "compiled_plan": compiled_plan
        }

        with open(f"./logs/wayang_{timestamp}.json", "w", encoding="utf-8") as f:
            def safe(obj):
                """Convert complex objects to something JSON-safe"""
                if hasattr(obj, "model_dump"):  # pydantic models
                    return obj.model_dump()
                elif hasattr(obj, "__dict__"):  # normal classes
                    return obj.__dict__
                else:
                    return str(obj)  # fallback for things like ResponseUsage
            
            json.dump(log, f, indent=4, ensure_ascii=False, default=safe)

        print("[INFO] Log printed")
 
        wayang_executor = WayangExecutor()
        output = wayang_executor.execute_plan(compiled_plan)

        print("[INFO] Wayang executed")

        return output
    
    except Exception as e:
        print(f"[ERROR] {e}")


# To test
@mcp.tool()
def greeto(name: str) -> str:
    return f"Hello:)), {name}!"
