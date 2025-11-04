from sqlalchemy import create_engine
import pandas as pd
from pandas import DataFrame
import json
import os

class SchemaLoader():
    """
    Loads schemas and examples for system prompts to agents

    """

    def __init__(self, config, output_folder):
        self.config = config["input_config"]
        self.output_folder = output_folder

    
    def get_and_save_schemas(self) -> str:
        """
        Get all tables in the database, get two example records of each tables. Adds them to data_schema_examples folder.
        If a table already exists, it is not added again.

        Returns:
            str: Information on number of added schemas.

        """

        try:
            # Check that output folder exists
            if not os.path.exists(self.output_folder):
                raise Exception("Output folder doesn't exists")
            
            # Get schemas from db
            schemas = self._get_schemas()
            # Add example records to schemas
            schemas = self._add_record_examples(schemas)

            schema_exists_counter = 0
            schema_added_counter = 0

            # Go over each unique table in the schema:
            for table_name, table_data in schemas.groupby("table_name"):
                
                # Get filepath to output schema
                filepath = f"{self.output_folder}/{table_name}.json"

                # Continueto next if file already exists
                if os.path.isfile(filepath):
                    schema_exists_counter += 1
                    continue

                # Format schema to json structure
                schema = self._format_to_json(table_name, table_data)

                # Convert everything to strings (errors with other datatypes)
                schema = json.loads(json.dumps(schema, default=str))

                # Write schema to json file
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(schema, f, indent=2, ensure_ascii=False)
                
                print(f"[INFO] {table_name} schema added to {self.output_folder}")
                schema_added_counter += 1

            msg = f"[INFO] Added schemas. Added {schema_added_counter} schemas and {schema_exists_counter} schemas already exists"
            print(msg)

            return msg
        
        except Exception as e:
            print(f"[Error] {e}")

    
    def _get_schemas(self) -> DataFrame:
        """
        Helper function to get schema from database, postgress

        Returns:
            DataFrame: DF of schemas
        
        """

        # Create engine to get schemas
        engine = create_engine(f"postgresql+psycopg2://{self.config['jdbc_username']}:{self.config['jdbc_password']}@{self.config['jdbc_uri'].split('://')[1]}")

        # Query to get schemas
        query = """
        SELECT 
        table_name,
        column_name,
        data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position;
        """

        # Load schemas into dataframe
        schemas = pd.read_sql(query, engine)

        # Return dataframe
        return schemas
    
    
    def _add_record_examples(self, schemas: DataFrame) -> DataFrame:
        """
        Helper function. Take the schemas in DF and returns two examples of each column from each available table

        Args:
            schemas (DataFrame): schemas in DF

        Returns: 
            DataFrame: Updated DF ved schema and examples
        """

        # Engine to get data
        engine = create_engine(f"postgresql+psycopg2://{self.config['jdbc_username']}:{self.config['jdbc_password']}@{self.config['jdbc_uri'].split('://')[1]}")

        # Initialize example columns
        schemas_examples = schemas.copy()
        schemas_examples['example_1'] = None
        schemas_examples['example_2'] = None

        # Go over each table in the schema
        for table_name, _ in schemas.groupby("table_name"):
            
            # Take two random examples from table name
            query = f'SELECT * FROM "{table_name}" ORDER BY RANDOM() LIMIT 2;'

            # Load data into DF
            examples = pd.read_sql(query, engine)

            # Go over each column in the table
            for col in examples.columns:
                try: 
                    # Get the table and column in the schema
                    row =  (schemas_examples["table_name"] == table_name) & (schemas_examples["column_name"] == col)

                    # Add examples as example 1 and 2
                    schemas_examples.loc[row, "example_1"] = examples[col].iloc[0]
                    schemas_examples.loc[row, "example_2"] = examples[col].iloc[1]
                
                except Exception as e:
                    print(f"[Error] {e}")

        return schemas_examples
    

    def _format_to_json(self, table_name: str, table_data: DataFrame) -> str:
        """
        Helper function. Take a schema and examples for a table and returns it as JSON

        Args:
            table_name (str): Name of table
            table_data (DataFrame): Column and data from table
        
        Returns:
            str: JSON of formatted schema with example

        """

        # Add table name and initialize new dict
        schema_json = {
            table_name: {
                "table_description": None,
                "columns": {}
            }
        }

        # Go over each row of table data
        for _, row in table_data.iterrows():
            # Get fields
            column_name = row["column_name"]
            data_type = row["data_type"]
            example_1 = row["example_1"]
            example_2 = row["example_2"]

            # Add field to json
            schema_json[table_name]["columns"][column_name] = {
                "type": data_type,
                "examples": [example_1, example_2]
            }

        return schema_json
