import subprocess
import json
import re
from rest_framework import status
from rest_framework.response import Response
def execute_python_code(code, input_data):
    try:
        function_name_match = re.search(r'def\s+(\w+)\s*\(', code)
        if function_name_match:
            function_name = function_name_match.group(1)
        else:
            return Response({"status": "error", "message": "No valid function definition found in the provided code."})

            # Constructing the code dynamically
        if input_data:
                # If input_data is provided, use it
            result_statement = f"input_data = {input_data}\nresult = {function_name}(**input_data)"
        else:
                # Otherwise, assume the user's code contains the function call
            result_statement = ""
            
            # Construct the dynamic code to be executed
        test_code = f"""
input_data = {input_data}
{code}

{result_statement}
print(result)
"""
        # Write the code to a temporary file
        with open('sandbox_code.py', 'w') as f:
            f.write(code)

        # Execute the Python code in a sandboxed environment
        process = subprocess.run(
            ["python3", "sandbox_code.py"],
            capture_output=True,
            text=True,
            timeout=30
        )

        if process.returncode != 0:
            error = process.stderr.strip()
            return {"status": "error", "message": f"Python code execution failed: {error}"}
        
        output = process.stdout.strip()
        print(f"output is {output}")
            # Compare output with the expected result
        try:
            output_dict = json.loads(output)
            formatted_output = json.dumps(output_dict)
            print(f"formatted_output is {formatted_output}")
        except json.JSONDecodeError:
            formatted_output = output
        return Response({
            "status": "success",
            "output": formatted_output
        }, status=status.HTTP_200_OK)
    
    except subprocess.TimeoutExpired:
        return {"status": "error", "message": "Python code took too long to execute."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
