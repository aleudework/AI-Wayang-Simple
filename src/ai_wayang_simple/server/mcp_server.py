from mcp.server.fastmcp import FastMCP
from ai_wayang_simple.config.settings import MCP_CONFIG, INPUT_CONFIG, OUTPUT_CONFIG, DEBUGGER_MODEL_CONFIG
from ai_wayang_simple.llm.agent_builder import Builder
from ai_wayang_simple.llm.agent_debugger import Debugger
from ai_wayang_simple.wayang.plan_mapper import PlanMapper
from ai_wayang_simple.wayang.plan_validator import PlanValidator
from ai_wayang_simple.wayang.wayang_executor import WayangExecutor
from ai_wayang_simple.utils.logger import Logger
from datetime import datetime

# Initialize MCP-server
mcp = FastMCP(name="AI-Wayang-Simple", port=MCP_CONFIG.get("port"))

# Initialize configs
config = {
    "input_config": INPUT_CONFIG,
    "output_config": OUTPUT_CONFIG
}

# Initialize agents and objects
builder_agent = Builder() # Initialize builder agent
debugger_agent = Debugger() # Initialize debugger agent
plan_mapper = PlanMapper(config=config) # Initialize mapper
plan_validator = PlanValidator() # Initialize validator
wayang_executor = WayangExecutor() # Wayang executor

# Temp to test output
temp_out = "Nothing to output"

@mcp.tool()
def query_wayang(describe_wayang_plan: str) -> str:
    """
    Ask in English and describe the plan as detailed as possible.
    The function generates a wayang plan and executes it based on natural language in English
    """

    global temp_out # temp

    try:
        # Set up logger 
        logger = Logger()
        logger.add_message("Plan description from client LLM", describe_wayang_plan)
        
        # Initialize variables
        status_code = None
        result = None
        version = 1


        ### --- Generate Wayang Plan Draft --- ###

        # Generate plan
        print("[INFO] Generates raw plan")
        response = builder_agent.generate_plan(describe_wayang_plan)
        raw_plan = response.get("wayang_plan")

        # Logs
        print("[INFO] Draft generated")
        logger.add_message("Builder Agent information", {"model": str(response["raw"].model), "usage": response["raw"].usage.model_dump()})
        logger.add_message("Builder Agent's abstract/raw plan", raw_plan.model_dump())


        ### --- Map Raw Plan to Executable Plan --- ###

        # Map plan
        print("[INFO] Mapping plan")
        wayang_plan = plan_mapper.plan_to_json(raw_plan)

        # Logs
        print("[INFO] Plan mapped")
        logger.add_message("Mapped plan finalized for execution", {"version": 1, "plan": wayang_plan})


        ### --- Validate Plan --- ###

        # Validate plan before execution
        val_success, val_errors = plan_validator.validate_plan(wayang_plan)

        # Tell and log validation result
        if val_success:
            print("[INFO] Plan validated sucessfully")

        else:
            print(f"[INFO] Plan {version} failed validation: {val_errors}")
            logger.add_message(f"Failed validation", {"version": version, "errors": val_errors})
            status_code = 400


        ### --- Execute Plan If Validated Successfully --- ###

        if val_success:
            # Execute plan in Wayang
            print("[INFO] Plan sent to Wayang for execution")
            status_code, result = wayang_executor.execute_plan(wayang_plan)
            
            # Log if plan couldn't execute
            if status_code != 200:
                print(f"[INFO] Couldn't execute plan succesfully, status {status_code}")
                logger.add_message("Plan executed unsucessful", {"status_code": status_code, "output": result})
        

        ### --- Debug Plan --- ###
        
        # Check if debugger should be used
        use_debugger = DEBUGGER_MODEL_CONFIG.get("use_debugger")

        # Use debugger if true
        if use_debugger == "True" and status_code != 200:

            # Start logging
            print("[INFO] Using Debugger Agent to fix plan")

            # Set debugging parameters
            max_itr = int(DEBUGGER_MODEL_CONFIG.get("max_itr")) # Get max iterations for debugging
            debugger_agent.set_vesion(version) # Set version to number of plans already created this session
            debugger_agent.start_debugger() # Load debugger session 

            # Debug and execute plan up to max iterations
            for _ in range(max_itr):

                # Map and anonymize plan from JSON to raw
                failed_plan = plan_mapper.plan_from_json(wayang_plan)

                # Debug plan
                response = debugger_agent.debug_plan(failed_plan, wayang_errors=result, val_errors=val_errors) # Debug plan
                version = debugger_agent.get_version() # Current plan version
                raw_plan = response.get("wayang_plan") # Get only the debugged plan

                # Map the debugged plan to JSON-format
                wayang_plan = plan_mapper.plan_to_json(raw_plan)

                # Get current plan version
                version = debugger_agent.get_version()

                # Logs
                logger.add_message(f"Debug version {version}", {"model": str(response["raw"].model), "usage": response["raw"].usage.model_dump()})
                logger.add_message(f"Debugged plan: {version}", {"version": version, "plan": wayang_plan})

                # Validate debugged plan
                val_success, val_errors = plan_validator.validate_plan(wayang_plan)

                # If plan failed validation, continue debugging
                if not val_success:
                    print(f"[INFO] Plan {version} failed validation: {val_errors}")
                    logger.add_message(f"Failed validation", {"version": version, "errors": val_errors})
                    status_code = 400
                    result = None
                    continue

                print(f"[INFO] Succesfully validated and debugged plan, version {version}") # If plan validation succesfully
                
                # Execute Wayang plan
                print(f"[INFO] Plan {version} sent to Wayang for execution")
                status_code, result = wayang_executor.execute_plan(wayang_plan)

                # Break debugging loop if sucessfully executed
                if status_code == 200:
                    break

                # Continue debugging if execution failed
                if status_code != 200:
                    print(f"[ERROR] Couldn't execute plan version {version}, status {status_code}")
                    logger.add_message(f"Plan version {version} executed unsucessful", {"status_code": status_code, "output": result})
                    continue
            
        # Return output when success
        if status_code == 200:
            print("[INFO] Plan succesfully executed")
            logger.add_message("Plan executed", "Success")
            temp_out = result # temp

            # Return result to client
            return result

        # If failed to execute plan after debugging
        if status_code != 200:
            print(f"[ERROR] Couldn't execute plan succesfully, status {status_code}")
            logger.add_message("Plan executed unsucessful", {"status_code": status_code, "output": result})
            
            # Return failure to client
            return "Couldn't execute wayang plan succesfully"

    except Exception as e:

        print(f"[ERROR] {e}")

        # Return error to client LLM to explain to user
        msg = f"An error occured, explain for the user: {e}"
        temp_out = msg # temp
        # Return error message to client
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

# Maybe not necessary anymore with anonymization (will be remapped)
# Re-do the Debugger as it nows need to have operation part in its system prompt