from ai_wayang_simple.llm.models import WayangOperation, WayangPlan
from ai_wayang_simple.wayang.operator_mapper import OperatorMapper
from typing import List

class PlanBuilder:
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

    def build(self, plan_draft: WayangPlan, output_path: str):
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


