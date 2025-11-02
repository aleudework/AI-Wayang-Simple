from datetime import datetime
import os
import urllib.parse

class OperatorMapper:
    def __init__(self, operation):
        self.op = operation

    def map(self):

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
    
    def textfile_output(self, config):

        folder = config["output_folder"]

        # Validate if folder path exists
        if not os.path.isdir(folder):
            print("[Warning] Folder path don't exists. Skipping output operation")
            return None
        
        # Ensure correct folder format
        folder = self._ensure_path_format(folder)

        # Create .txt filename with current timestamp        
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        filename = f"output_{timestamp}.txt"

        # Create path
        path = folder + filename

        return {
            "id": self.op.id,
            "cat": "output",
            "input": self.op.input,
            "output": [], # Note: If last always remember that output list should be empty but check up with Zoi
            "operatorName": "textFileOutput",
            "data": {"filename": path}
        }

    def _ensure_path_format(self, path):
        """
        Wayang needs to havde specifically formatted paths
        This method ensures that
        """
        # Remove spaces and use the absolute path
        abs_path = os.path.abspath(path.strip())

        # URl encode spaces and special characters
        abs_path = urllib.parse.quote(abs_path)

        # Add "file:///" if not exists
        if not abs_path.startswith("file:///"):
            abs_path = abs_path.lstrip("/") # Remove the first /
            abs_path = "file:///" + abs_path

        # Adds / in the end
        if not abs_path.endswith("/"):
            abs_path = abs_path + "/"

        return abs_path
        





