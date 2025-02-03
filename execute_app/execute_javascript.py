import subprocess
import json
import re
import os

def execute_javascript_code(code, input_data):
    try:
        # Extract function name dynamically
        function_name_match = re.search(r'function\s+(\w+)\s*\(', code)
        if not function_name_match:
            return {"status": "error", "message": "No valid function definition found in the provided code."}

        function_name = function_name_match.group(1)

        # Format input data as a JavaScript variable
        input_data_js = json.dumps(input_data)  # Serialize input data to JSON
        result_statement = f"const inputData = {input_data_js};\nconst result = {function_name}(inputData);\nconsole.log(result);"

        # Construct the JavaScript code
        full_code = f"""
{code}
{result_statement}
"""

        # Write the JavaScript code to a temporary file
        temp_file = "sandbox_code.js"
        with open(temp_file, 'w') as f:
            f.write(full_code)

        # Execute the JavaScript code using Node.js
        process = subprocess.run(
            ["node", temp_file],
            capture_output=True,
            text=True,
            timeout=30
        )

        # Cleanup: Delete the temporary file
        os.remove(temp_file)

        if process.returncode != 0:
            error = process.stderr.strip()
            return {"status": "error", "message": f"JavaScript code execution failed: {error}"}

        output = process.stdout.strip()

        # Attempt to format the output as JSON if applicable
        try:
            output_dict = json.loads(output)
            formatted_output = json.dumps(output_dict, indent=4)
        except json.JSONDecodeError:
            formatted_output = output

        return {
            "status": "success",
            "output": formatted_output
        }

    except subprocess.TimeoutExpired:
        return {"status": "error", "message": "JavaScript code took too long to execute."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
