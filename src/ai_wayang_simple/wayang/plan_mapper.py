from ai_wayang_simple.llm.models import WayangOperation, WayangPlan
from ai_wayang_simple.wayang.operator_mapper import OperatorMapper
from typing import List

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
        
    def map(self, plan_draft: WayangPlan):
        """
        Converts WayangPlan til JSON Wayang plan (correct formatting)
        """
        if not isinstance(plan_draft, WayangPlan):
            raise ValueError("Plan draft must be a wayang plan")
        
        operations = plan_draft.operations

        self._add_operators(operations)

        return self.plan

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
                name = op.operationName

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
    
    

