from ai_wayang_simple.wayang.plan_mapper import PlanMapper
from ai_wayang_simple.llm.models import WayangPlan, WayangOperation
from ai_wayang_simple.config.settings import MCP_CONFIG, DEBUGGER_MODEL_CONFIG, INPUT_CONFIG, OUTPUT_CONFIG
import json

config = {"input_config": INPUT_CONFIG, "output_config": OUTPUT_CONFIG}

plan_mapper = PlanMapper(config)

raw_plan = {
            "operations": [
                {
                    "cat": "input",
                    "id": 1,
                    "input": [],
                    "output": [
                        2
                    ],
                    "operatorName": "jdbcRemoteInput",
                    "keyUdf": None,
                    "udf": None,
                    "table": "person_test",
                    "columnNames": [
                        "id",
                        "navn",
                        "alder",
                        "email",
                        "created_at"
                    ]
                },
                {
                    "cat": "unary",
                    "id": 2,
                    "input": [
                        1
                    ],
                    "output": [
                        3
                    ],
                    "operatorName": "map",
                    "keyUdf": None,
                    "udf": "(r: org.apache.wayang.basic.data.Record) => r.getField(0).toString",
                    "table": None,
                    "columnNames": []
                },
                {
                    "cat": "unary",
                    "id": 3,
                    "input": [
                        2
                    ],
                    "output": [],
                    "operatorName": "filter",
                    "keyUdf": None,
                    "udf": "(r: org.apache.wayang.basic.data.Record) => ((Number) r.getField(2)).intValue() > 18",
                    "table": None,
                    "columnNames": []
                }
            ],
            "description_of_plan": "Plan reads data from person_test, applies a simple per-record transformation, then filters adults over 18. The plan intentionally avoids multiple input IDs for input stage in order to keep the flow valid and coherent."
        }

raw_wayangplan = WayangPlan(**raw_plan)

print(json.dumps(raw_wayangplan.model_dump(), indent=4, ensure_ascii=False))

print("-----")

plan1 = plan_mapper.plan_to_json(raw_wayangplan)
# Pænt print af dict (output fra plan_to_json)
print(json.dumps(plan1, indent=4, ensure_ascii=False))

print("-----")

plan2 = plan_mapper.plan_from_json(plan1)

print(json.dumps(plan2.model_dump(), indent=4, ensure_ascii=False))