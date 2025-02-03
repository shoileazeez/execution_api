import subprocess
import json
import re
import os


def execute_python_code(code, input_data):
    try:
        # Extract function name
        function_name_match = re.search(r'def\s+(\w+)\s*\(', code)
        if not function_name_match:
            return {"status": "error", "message": "No valid function definition found in the provided code."}

        function_name = function_name_match.group(1)

        # Construct input and result statements
        input_data_str = json.dumps(input_data) if input_data else "{}"
        result_statement = f"""
input_data = {input_data_str}
result = {function_name}(**input_data)
print(result)
"""

        # Write the code and result statements to a temporary file
        temp_file = "sandbox_code.py"
        with open(temp_file, "w") as f:
            f.write(code + "\n" + result_statement)

        # Execute the Python script
        process = subprocess.run(
            ["python3", temp_file],
            capture_output=True,
            text=True,
            timeout=30
        )

        # Cleanup: Delete the temporary file
        os.remove(temp_file)

        if process.returncode != 0:
            error = process.stderr.strip()
            return {"status": "error", "message": f"Python code execution failed: {error}"}

        output = process.stdout.strip()

        # Handle empty output
        if not output:
            return {"status": "error", "message": "No output was returned from the Python code."}

        # Attempt to parse output as JSON
        try:
            output_dict = json.loads(output)
            formatted_output = json.dumps(output_dict, indent=4)  # Pretty print JSON output
        except json.JSONDecodeError:
            formatted_output = output  # Return plain text if not JSON

        return {"status": "success", "output": formatted_output}

    except subprocess.TimeoutExpired:
        return {"status": "error", "message": "Python code took too long to execute."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
