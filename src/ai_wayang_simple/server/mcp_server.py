from mcp.server.fastmcp import FastMCP
from ai_wayang_simple.config.settings import MCP_CONFIG, INPUT_CONFIG, OUTPUT_CONFIG, DEBUGGER_MODEL_CONFIG
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

# Temp to test output
temp_out = "Nothing to output"

@mcp.tool()
def query_wayang(describe_wayang_plan: str) -> str:
    global temp_out # temp
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

        # Maps plan into Wayang JSON Plan
        print("[INFO] Mapping plan")

        # Adds configs
        config = {
            "input_config": INPUT_CONFIG,
            "output_config": OUTPUT_CONFIG
        }

        plan_mapper = PlanMapper(config)
        wayang_plan = plan_mapper.map(draft_plan)

        # Log
        print("[INFO] Plan mapped")
        logger.add_message("Mapped plan finalized for execution", {"version": 1, "plan": wayang_plan})

        # Validate plan before execution
        val_bool, val_errors = plan_mapper.validate_plan(wayang_plan)

        if val_bool:

            # Execute plan
            print("[INFO] Plan sent to Wayang for execution")
            wayang_executor = WayangExecutor()
            status_code, output = wayang_executor.execute_plan(wayang_plan)

            # Return output when success
            if status_code == 200:
                print("[INFO] Plan succesfully executed")
                logger.add_message("Plan executed", "Success")
                temp_out = output # temp
                return output
            else:
                print(f"[INFO] Couldn't execute plan succesfully, status {status_code}")
                logger.add_message("Plan executed unsucessful", {"status_code": status_code, "output": output})
        
        # For failed validation, goes straight to debugging if debugging
        else:
            print(f"[INFO] Plan {version} failed validation: {val_errors}")
            logger.add_message(f"Failed validation", {"version": version, "errors": val_errors})
            status_code = 400
            output = None
        
        # Check if debugger should be used
        use_debugger = DEBUGGER_MODEL_CONFIG.get("use_debugger")

        # Use debugger if true
        if use_debugger == "True":
            
            # Logs from first fail

            # Start logging
            print("[INFO] Initialize and use Debugger Agent to fix plan")

            # Initialize debugger and max iterations to fix
            max_itr = int(DEBUGGER_MODEL_CONFIG.get("max_itr"))
            debugger_agent = Debugger(version=1)

            # Try to debug up to max iteration
            for i in range(max_itr):

                # Anonymize plan (remove password and username)
                anonymized_plan = plan_mapper.anonymize_plan(wayang_plan)

                # Debug and extract plan
                response = debugger_agent.debug_plan(anonymized_plan, wayang_errors=output, val_errors=val_errors)
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

                # Validate plan
                val_bool, val_errors = plan_mapper.validate_plan(wayang_plan)

                # If validation fails
                if not val_bool:
                    print(f"[INFO] Plan {version} failed validation: {val_errors}")
                    logger.add_message(f"Failed validation", {"version": version, "errors": val_errors})
                    status_code = 400
                    output = None
                    continue
                
                # Sucessful validation
                print(f"[INFO] Succesfully validated and debugged plan, version {version}")

                # Execute plan
                print(f"[INFO] Plan {version} sent to Wayang for execution")
                wayang_executor = WayangExecutor()
                status_code, output = wayang_executor.execute_plan(wayang_plan)

                # Validate execution
                if status_code == 200:
                    print(f"[INFO] Plan version {version} succesfully executed")
                    logger.add_message(f"Plan version {version} executed", "Success")
                    temp_out = output # temp
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
        # Return error to client LLM to explain to user
        msg = f"An error occured, explain for the user: {e}"
        temp_out = msg # temp
        return msg

@mcp.tool()
def get_output() -> str:
    """
    Return output of executed wayang plan
    """
    return temp_out

# To test
@mcp.tool()
def greeto(name: str) -> str:
    return f"Hello:)), {name}!"


# Implement few-shot prompting
# Implement joins oepraiton
# Implement multiple output operations (not sure)
# Add More data 

# DEBUGGER fixes:
# 1) In Plan_Mapper. Make a function that re-do plans to WayangOperation model (obs on JDBC)
# 2) For debugger. Add the original not-working plan as well as the one it should fix
# 3) Make the debugger only do structured output as before
# 4) Make the new plan go through the mapper again and
# Validation class PlanValidator ?? 