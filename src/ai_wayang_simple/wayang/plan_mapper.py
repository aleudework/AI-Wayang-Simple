from ai_wayang_simple.llm.models import WayangOperation, WayangPlan
from ai_wayang_simple.wayang.operator_mapper import OperatorMapper
from typing import List
import json

class PlanMapper:
    def __init__(self, config):
        self.config = config

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
        

    def plan_to_json(self, plan: WayangPlan):
        """
        Converts WayangPlan til JSON Wayang plan (correct formatting)
        """
        if not isinstance(plan, WayangPlan):
            raise ValueError("Plan draft must be a wayang plan")
        
        mapped_plan = self._new_plan()

        operations = plan.operations

        mapped_operators = self._map_operators(operations)

        mapped_plan["operators"] = mapped_operators

        return mapped_plan
    

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


    def _new_plan(self):
        return {
            "context": { "platforms": ["java"], "configuration": {} },
            "operators": []
        }


    def _map_operators(self, operations: List[WayangOperation]):
        """
        Adds and format wayang operators correctl

        """

        mapped_operations = []
        
        for op in operations:
            try:
                name = op.operatorName

                # If an operator is mentioned in the map then skip
                if name not in self.operator_map:
                    print(f"[WARNING] Couldn't find or map operator")
                    continue

                operation = self.operator_map[name](op)

                if operation:
                    mapped_operations.append(operation)
            
            except Exception as e:
                print(f"[ERROR] Couldn't add operator {op}: {e}")
        
        return mapped_operations

    

