from mcp.server.fastmcp import FastMCP
from ai_wayang_simple.config.settings import MCP_CONFIG, JDBC_CONFIG, DEBUGGER_MODEL_CONFIG
from ai_wayang_simple.llm.agent_builder import Builder
from ai_wayang_simple.wayang.plan_mapper import PlanMapper
from ai_wayang_simple.wayang.wayang_executor import WayangExecutor
from ai_wayang_simple.utils.logger import Logger
from datetime import datetime
import json

# Initialize MCP-server
mcp = FastMCP(name="AI-Wayang-Simple", port=MCP_CONFIG.get("port"))

# Initialise OpenAI Client
builder_agent = Builder()

@mcp.tool()
def query_wayang(describe_wayang_plan: str) -> str:
    """
    Ask in English and describe the plan as detailed as possible.
    The function generates a wayang plan and executes it based on natural language in English
    """
    try:

        # Initialize logger
        logger = Logger()

        # Log query message
        logger.add_message("Plan description from client LLM", describe_wayang_plan)

        # Generate draft plan
        print("[INFO] Generates draft plan")
        response = builder_agent.generate_plan(describe_wayang_plan)
        draft_plan = response.get("wayang_plan")

        # Logs
        print("[INFO] Draft generated")
        logger.add_message("Builder Agent information", {"model": response["raw"].model, "usage": response["raw"].usage})
        logger.add_message("Builder Agent's abstract/draft plan", draft_plan)


        # Initialize and create timestamp for  (maybe remove for tem)
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        temp_outfile = f"file:///Users/alexander/Downloads/output_{timestamp}.txt"

        # Maps plan into Wayang JSON Plan
        print("[INFO] Mapping plan")
        plan_mapper = PlanMapper(JDBC_CONFIG)
        wayang_plan = plan_mapper.map(draft_plan, temp_outfile)

        # Log
        print("[INFO] Plan mapped")
        logger.add_message("Mapped plan finilized for execution", {"version": 1, "plan": wayang_plan})

        # Execute plan
        print("[INFO] Plan sent to Wayang for execution")
        wayang_executor = WayangExecutor()
        status_code, output = wayang_executor.execute_plan(wayang_plan)

        # Return output when success
        if status_code == 200:
            print("[INFO] Plan succesfully executed")
            logger.add_message("Plan executed", "Success")
            return output
        
        # Check if debugger should be used
        use_debugger = DEBUGGER_MODEL_CONFIG.get("use_debugger")

        # Use debugger if true
        if use_debugger == "True":
            max_itr = DEBUGGER_MODEL_CONFIG.get("max_itr")

            #for i in range(max_itr):





        # Return when unsuccesfully
        if status_code != 200:
            print(f"[INFO] Couldn't execute plan succesfully, status {status_code}")
            logger.add_message("Plan executed unsucessful", {"status_code": status_code, "output": output})
            return "Couldn't execute wayang plan succesfully"

        return
    
    except Exception as e:
        print(f"[ERROR] {e}")


# To test
@mcp.tool()
def greeto(name: str) -> str:
    return f"Hello:)), {name}!"
