from mcp.server.fastmcp import FastMCP
from ai_wayang_simple.config.settings import MCP_CONFIG, JDBC_CONFIG, DEBUGGER_MODEL_CONFIG
from ai_wayang_simple.llm.agent_builder import Builder
from ai_wayang_simple.llm.agent_debugger import Debugger
from ai_wayang_simple.wayang.plan_mapper import PlanMapper
from ai_wayang_simple.wayang.wayang_executor import WayangExecutor
from ai_wayang_simple.utils.logger import Logger
from datetime import datetime

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
        logger.add_message("Builder Agent information", {"model": str(response["raw"].model), "usage": response["raw"].usage.model_dump()})
        logger.add_message("Builder Agent's abstract/draft plan", draft_plan.model_dump())


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
            
            # Logs from first fail
            print(f"[INFO] Couldn't execute plan succesfully, status {status_code}")
            logger.add_message("Plan executed unsucessful", {"status_code": status_code, "output": output})
            
            # Start logging
            print("[INFO] Initialize and use debugger to fix plan")

            # Initialize debugger and max iterations to fix
            max_itr = int(DEBUGGER_MODEL_CONFIG.get("max_itr"))
            debugger_agent = Debugger(version=1)

            # Try to debug up to max iteration
            for i in range(max_itr):

                # Anonymize plan (remove password and username)
                anonymized_plan = plan_mapper.anonymize_plan(wayang_plan)

                # Debug and extract plan
                response = debugger_agent.debug_plan(anonymized_plan, output)
                wayang_plan = response.get("wayang_plan")

                # Get plan version
                version = debugger_agent.get_version()

                # Logs
                logger.add_message(f"Debug version {version}", {"model": str(response["raw"].model), "usage": response["raw"].usage.model_dump()})
                logger.add_message(f"Debugged plan: {version}", {"version": version, "plan": wayang_plan})

               # If plan is not a valid json, continue debugging 
                if wayang_plan is None:
                    print(f"[INFO] Unsuccesfully debugged, version {version}")
                    continue

                # Redo anonymization before execution
                wayang_plan = plan_mapper.unanonymize_plan(wayang_plan)
                
                print(f"[INFO] Succesfully debugged plan, version {version}")

                # Execute plan
                print(f"[INFO] Plan {version} sent to Wayang for execution")
                wayang_executor = WayangExecutor()
                status_code, output = wayang_executor.execute_plan(wayang_plan)

                # Validate execution
                if status_code == 200:
                    print(f"[INFO] Plan version {version} succesfully executed")
                    logger.add_message(f"Plan version {version} executed", "Success")
                    return output
                else:
                    print(f"[ERROR] Couldn't execute plan version {version}, status {status_code}")
                    logger.add_message(f"Plan version {version} executed unsucessful", {"status_code": status_code, "output": output})
                    continue
            
            # Logs
            print(f"[INFO] Debugger reached max iteration at {max_itr}")
            logger.add_message("Debugger reached limit", f"The debug loop reached max iterations at {max_itr}")


        # If execution went unsuccesfully and no debugging, or debugging got to max itr
        if status_code != 200:
            print(f"[ERROR] Couldn't execute plan succesfully, status {status_code}")
            logger.add_message("Plan executed unsucessful", {"status_code": status_code, "output": output})
            return "Couldn't execute wayang plan succesfully"

        return

    except Exception as e:
        print(f"[ERROR] {e}")


# To test
@mcp.tool()
def greeto(name: str) -> str:
    return f"Hello:)), {name}!"
