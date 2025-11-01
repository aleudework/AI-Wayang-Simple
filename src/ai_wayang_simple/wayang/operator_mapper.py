
class OperatorMapper:
    def __init__(self, operation):
        self.op = operation
    
    def validate(self):
        if self.op.id is None:
            raise ValueError('ID must not be null')
        
        if self.op.cat == 'unary' and len(self.op.output) > 1:
            raise ValueError('Unary operators can only have a single output')
        
        if self.op.cat == 'unary' and len(self.op.input) != 1:
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
                "udf": self.op.udf
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
                "udf": self.op.udf
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
                "udf": self.op.udf
            }
        }
    
    def reduce(self):
        self.validate()
        # Reduce may always need a keyUDF

        return {
            "id": self.op.id,
            "cat": "unary",
            "input": self.op.input,
            "output": self.op.output,
            "operatorName": "reduce",
            "data": {
                "keyUdf": "(_ : Any) => 1",
                "udf": self.op.udf
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
                "udf": self.op.udf
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
                "keyUdf": self.op.keyUdf
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
                "keyUdf": self.op.keyUdf
            }
        }
    
    def jdbc_input(self, config):
        self.validate()

        # Creates SQL-select query
        # Important for keeping the correct placement / index
        columns = ", ".join(self.op.columnNames)
        table_query = f"(SELECT {columns} FROM {self.op.table}) as X"

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
                "table": table_query,
                "columnNames": self.op.columnNames
            }
        }