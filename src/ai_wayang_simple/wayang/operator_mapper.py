from ai_wayang_simple.llm.models import WayangOperation, WayangPlan
from typing import List

class OperatorMapper:
    def __init__(self, operation):
        self.op = operation
    
    def validate(self):
        if self.op.id is None:
            raise ValueError('ID must not be null')
        
        if self.op.cat == 'unary' and len(self.op.output) > 1:
            raise ValueError('Unary operators can only have a single output')
        
        if self.op.cat == 'unary' and len(self.op.input) is not 1:
            raise ValueError('Unary operators must have excatly one input')

    def map(self):
        self.validate()

        return {
            "id": self.op.id,
            "cat": "unary",
            "input": self.op.input,
            "output": self.op.output,
            "operatorName": "map",
            "data": {
                "udf": self.op.udf,
                "inputType": None,
                "outputType": None
            }
        }

    def flatmap(self):
        self.validate()

        return {
            "id": self.op.id,
            "cat": "unary",
            "input": self.op.input,
            "output": self.op.output,
            "operatorName": "flatMap",
            "data": {
                "udf": self.op.udf,
                "inputType": None,
                "outputType": None
            }
        }
    
    def filter(self):
        self.validate()

        return {
            "id": self.op.id,
            "cat": "unary",
            "input": self.op.input,
            "output": self.op.output,
            "operatorName": "filter",
            "data": {
                "udf": self.op.udf,
                "inputType": None,
                "outputType": None
            }
        }
    
    def reduce(self):
        self.validate()

        return {
            "id": self.op.id,
            "cat": "unary",
            "input": self.op.input,
            "output": self.op.output,
            "operatorName": "reduce",
            "data": {
                "udf": self.op.udf,
                "inputType": None,
                "outputType": None
            }
        }

    def reduceby(self):
        self.validate()

        return {
            "id": self.op.id,
            "cat": "unary",
            "input": self.op.input,
            "output": self.op.output,
            "operatorName": "reduceBy",
            "data": {
                "keyUdf": self.op.keyUdf,
                "udf": self.op.udf,
                "inputType": None,
                "outputType": None
            }
        }

    def groupby(self):
        self.validate()

        return {
            "id": self.op.id,
            "cat": "unary",
            "input": self.op.input,
            "output": self.op.output,
            "operatorName": "groupBy",
            "data": {
                "udf": self.op.udf,
                "inputType": None,
                "outputType": None
            }
        }

    def sort(self):
        self.validate()

        return {
            "id": self.op.id,
            "cat": "unary",
            "input": self.op.input,
            "output": self.op.output,
            "operatorName": "sort",
            "data": {
                "keyUdf": self.op.keyUdf,
                "inputType": None,
                "outputType": None
            }
        }
    
    def jdbc_input(self, config):
        self.validate()

        return {
            "id": self.op.id,
            "cat": "input",
            "input": self.op.input,
            "output": self.op.output,
            "operatorName": "jdbcRemoteInput",
            "data": {
                "uri": config["jdbc_uri"],
                "username": config["jdbc_username"],
                "password": config["jdbc_password"],
                "table": self.op.table,
                "columnNames": self.op.columnNames
            }
        }