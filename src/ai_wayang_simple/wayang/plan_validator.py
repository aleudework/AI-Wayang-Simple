class PlanValidator:

    def validate_plan(self, plan):
        """
        Validates if a plan is correctly mapped.
        """

        errors = []

        for i, operation in enumerate(plan.get("operators", [])):
            op_id = int(operation.get("id", -1))

            try:
                if operation.get("cat") == "unary":
                    inputs = operation.get("input", [])
                    outputs = operation.get("output", [])

                    # Input must have at least one id
                    if len(inputs) < 1:
                        errors.append(f"Operation id {op_id}: Missing input operator")

                    # Output must have at least one id and not be the last operation
                    if len(outputs) < 1 and i != len(plan["operators"]) - 1:
                        if i != len(plan["operators"]) - 2:
                            errors.append(f"Operation id {op_id}: Missing output operator")

                    # Input ids must be lower than operation id
                    for input_id in inputs:
                        if input_id >= op_id:
                            errors.append(f"Operation id {op_id}: Input id {input_id} ≥ operation id")

                    # Output ids must be higher than operation id
                    for output_id in outputs:
                        if output_id <= op_id:
                            errors.append(f"Operation id {op_id}: Output id {output_id} ≤ operation id")

            except Exception as e:
                errors.append(f"Operation id {op_id}: Unexpected error - {e}")

        if errors:
            return False, errors
        else:
            return True, []