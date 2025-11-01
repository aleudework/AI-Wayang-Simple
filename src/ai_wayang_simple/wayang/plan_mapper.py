from ai_wayang_simple.llm.models import WayangOperation, WayangPlan
from ai_wayang_simple.wayang.operator_mapper import OperatorMapper
from typing import List

class PlanMapper:
    def __init__(self, config):
        self.config = config
        self.plan = self._new_plan()

        self.operator_map = {
            "jdbcRemoteInput": lambda op: OperatorMapper(op).jdbc_input(self.config),
            "map": lambda op: OperatorMapper(op).map(),
            "flatMap": lambda op: OperatorMapper(op).flatmap(),
            "filter": lambda op: OperatorMapper(op).filter(),
            "reduce": lambda op: OperatorMapper(op).reduce(),
            "reduceBy": lambda op: OperatorMapper(op).reduceby(),
            "groupBy": lambda op: OperatorMapper(op).groupby(),
            "sort": lambda op: OperatorMapper(op).sort()
        }
    
    def _new_plan(self):
        return {
            "context": { "platforms": ["java"], "configuration": {} },
            "operators": []
        }
    
    def validate_plan(self, plan) -> bool:
        """
        Validates if a plan is correctly mapped
        """
        try:
            for i, operation in enumerate(plan["operators"]):
                # Check unary operations
                if operation.get("cat") == "unary":
                    input = operation.get("input", [])
                    output = operation.get("output", [])
                    id = int(operation.get("id", -1))

                    # Input must have at least one id
                    if len(input) < 1:
                        print("[VALIDATON ERROR] Missing input operator")
                        return False

                    # Output must have a least one id and not be the last operation
                    if len(output) < 1 and i != len(plan["operators"]) - 1:
                        # Temp, to test for last output
                        if i == len(plan["operators"]) - 2:
                            continue
                        
                        print("[VALIDATON ERROR] Missing output operator")
                        return False
                    
                    # Input id's must be lower than the operation id itself
                    for input_id in input:
                        if input_id >= id:
                            print("[VALIDATON ERROR] Input value higher than operation id")
                            return False

                    # Output id's must be higher than the operation id itself
                    for output_id in output:
                        if output_id <= id:
                            print("[VALIDATON ERROR] Output value lower than operation id")
                            return False
                    

            return True

        except Exception as e:
            print(e)
            return False
        

    def map(self, plan_draft: WayangPlan, output_path: str):
        """
        Converts WayangPlan til JSON Wayang plan (correct formatting)
        """
        if not isinstance(plan_draft, WayangPlan):
            raise ValueError("Plan draft must be a wayang plan")
        
        operations = plan_draft.operations

        self._add_operators(operations)

        self._add_text_output(output_path)

        return self.plan
        

    def _add_operators(self, operations: List[WayangOperation]):
        """
        Adds and format wayang operators correctly
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

    ######
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
        for operation in anonymized_plan["operators"]:
            if operation.get("operatorName") == "jdbcRemoteInput":
                data = operation.get("data", {})
                data["username"] = self.config["jdbc_username"]
                data["password"] = self.config["jdbc_password"]
                operation["data"] = data

        return anonymized_plan
    
    

