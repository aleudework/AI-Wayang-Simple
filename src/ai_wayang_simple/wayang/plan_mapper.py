from ai_wayang_simple.llm.models import WayangOperation, WayangPlan
from ai_wayang_simple.wayang.operator_mapper import OperatorMapper
from typing import List
import json

class PlanMapper:
    def __init__(self, config):
        self.config = config
        self.plan = self._new_plan()

        self.operator_map = {
            # Input operators
            "jdbcRemoteInput": lambda op: OperatorMapper(op).jdbc_input(self.config["input_config"]),

            # Unary operators
            "map": lambda op: OperatorMapper(op).map(),
            "flatMap": lambda op: OperatorMapper(op).flatmap(),
            "filter": lambda op: OperatorMapper(op).filter(),
            "reduce": lambda op: OperatorMapper(op).reduce(),
            "reduceBy": lambda op: OperatorMapper(op).reduceby(),
            "groupBy": lambda op: OperatorMapper(op).groupby(),
            "sort": lambda op: OperatorMapper(op).sort(),

            # Output operators
            "textFileOutput": lambda op: OperatorMapper(op).textfile_output(self.config["output_config"])
        }
    
    def _new_plan(self):
        return {
            "context": { "platforms": ["java"], "configuration": {} },
            "operators": []
        }
        
    def map(self, plan: WayangPlan):
        """
        Converts WayangPlan til JSON Wayang plan (correct formatting)
        """
        if not isinstance(plan, WayangPlan):
            raise ValueError("Plan draft must be a wayang plan")
        
        operations = plan.operations

        self._add_operators(operations)

        return self.plan
    
    def plan_to_json(self, plan: WayangPlan):
        """
        Converts WayangPlan til JSON Wayang plan (correct formatting)
        """
        if not isinstance(plan, WayangPlan):
            raise ValueError("Plan draft must be a wayang plan")
        
        operations = plan.operations

        self._add_operators(operations)

        return self.plan
    
    def _flat_json(data: dict) -> WayangOperation:
        # Flats
        flat = {**data, **data.get("data", {})}
        filtered = {k: v for k, v in flat.items() if k in WayangOperation.model_fields}
        return WayangOperation(**filtered)
    

    def plan_from_json(self, plan) -> WayangPlan:
        """
        Converts a JSON Wayang plan to WayangPlan.
        Used for LLM Debugger to fix a failed plan
        """
        try:
            # Make sure plan is a dict (from json)
            if isinstance(plan, str):
                plan = json.loads(plan)

            # List to store operations
            operations = []

            # Maps each operation to WayangOperation model
            for op in plan["operators"]:
                # Flat nested structure (if called data)
                flat_op_data = {**op, **op.get("data", {})}
                # Filter to only relevant keys in WayangOperations
                op_data = {k: v for k, v in flat_op_data.items() if k in WayangOperation.model_fields}
                # Append to the operation list
                operations.append(WayangOperation(**op_data))
            
            # Add to Wayang plan and return
            return WayangPlan(operations=operations, description_of_plan="Plan from JSON")

        except Exception as e:
            raise ValueError("[Error] Not a correctly formatted JSON-plan")


    def anonymize_plan(self, wayang_plan):
        """
        Anonymize username and password in JDBC input. Mainly for debugger
        """
        for operation in wayang_plan["operators"]:
            if operation.get("operatorName") == "jdbcRemoteInput":
                data = operation.get("data", {})
                data["username"] = "anonymized"
                data["password"] = "anonymized"
                operation["data"] = data

        return wayang_plan
    
    def unanonymize_plan(self, anonymized_plan):
        """
        Redo anonymization of username and password in JDBC input. Mainly for debugger
        """
        input_config = self.config["input_config"]

        for operation in anonymized_plan["operators"]:
            if operation.get("operatorName") == "jdbcRemoteInput":
                data = operation.get("data", {})
                data["username"] = input_config["jdbc_username"]
                data["password"] = input_config["jdbc_password"]
                operation["data"] = data

        return anonymized_plan
        

    def _add_operators(self, operations: List[WayangOperation]):
        """
        Adds and format wayang operators correctl

        """
        for op in operations:
            try:
                name = op.operatorName

                # If an operator is mentioned in the map then skip
                if name not in self.operator_map:
                    print(f"[WARNING] Couldn't find or map operator")
                    continue

                operation = self.operator_map[name](op)

                if operation:
                    self.plan["operators"].append(operation)
            
            except Exception as e:
                print(f"[ERROR] Couldn't add operator {op}: {e}")

    ###### Temp
    # This is temp
    "Just for testing untill built in operators"
    def _add_text_output(self, output_path: str) -> None:
        operator_count = len(self.plan["operators"])
        self.plan["operators"].append({
            "id": operator_count + 1,
            "cat": "output",
            "input": [operator_count],
            "output": [],
            "operatorName": "textFileOutput",
            "data": {"filename": output_path}
        })
    #####
    
    

