import subprocess
import json
import re
from rest_framework.response import Response
from rest_framework import status

def execute_python_code(code, input_data):
    try:
        function_name_match = re.search(r'def\s+(\w+)\s*\(', code)
        if function_name_match:
            function_name = function_name_match.group(1)
        else:
            return Response({"status": "error", "message": "No valid function definition found in the provided code."}, status=status.HTTP_400_BAD_REQUEST)

        # Constructing the code dynamically
        if input_data:
            result_statement = f"input_data = {input_data}\nresult = {function_name}(**input_data)"
        else:
            result_statement = f"result = {function_name}()"  # Ensure a result is returned if no input_data

        test_code = f"""
input_data = {input_data}
{code}
{result_statement}
print(result)
"""

        with open('sandbox_code.py', 'w') as f:
            f.write(test_code)

        process = subprocess.run(
            ["python3", "sandbox_code.py"],
            capture_output=True,
            text=True,
            timeout=30
        )

        if process.returncode != 0:
            error = process.stderr.strip()
            return Response({"status": "error", "message": f"Python code execution failed: {error}"}, status=status.HTTP_400_BAD_REQUEST)

        output = process.stdout.strip()
        if not output:
            return Response({"status": "error", "message": "No output was returned from the Python code."}, status=status.HTTP_400_BAD_REQUEST)

        # Handle output
        try:
            output_dict = json.loads(output)
            formatted_output = json.dumps(output_dict)  # Ensure double quotes
        except json.JSONDecodeError:
            formatted_output = output  # If output is not JSON, just return it as a string

        return Response({
            "status": "success",
            "output": formatted_output
        }, status=status.HTTP_200_OK)

    except subprocess.TimeoutExpired:
        return Response({"status": "error", "message": "Python code took too long to execute."}, status=status.HTTP_408_REQUEST_TIMEOUT)
    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
