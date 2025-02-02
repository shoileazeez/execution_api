from rest_framework.views import APIView
from rest_framework.response import Response
import subprocess
import re
import json
class ExecuteCodeView(APIView):
    def post(self, request):
        code = request.data.get('code', '')
        input_data = request.data.get('input_data', {})
        expected_output = request.data.get('expected_output', None)
        
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
                f.write(test_code)
            
            install_process = subprocess.run(
                ["python3", "-m", "pip", "install", "numpy", "pandas"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if install_process.returncode != 0:
                error_message = install_process.stderr.strip()
                return Response({"status": "error", "message": f"Error installing dependencies: {error_message}"})

            # Execute the code in a sandboxed environment
            process = subprocess.run(
            ["python3", "sandbox_code.py"],
            capture_output=True,
            text=True,
            timeout=30
            )

            if process.returncode != 0:
                error = process.stderr.strip()
                return Response({"status": "error", "message": f"Code execution failed: {error}"})
            
            # Retrieve and process output
            # output = process.stdout.strip()
            output_lines = process.stdout.strip().split('\n')
            output = output_lines[-1] if output_lines else ''
            # Compare output with the expected result
            try:
                output_dict = json.loads(output)
                formatted_output = json.dumps(output_dict)  # Ensure double quotes
            except json.JSONDecodeError:
                formatted_output = output
            if str(formatted_output) == str(expected_output):
                return Response({
                    "status": "success",
                    "output": output,
                    "message": "Your code passed all test cases!"
                })
            else:
                return Response({
                    "status": "failure",
                    "output": formatted_output,
                    "expected_output": expected_output,
                    "message": "Output does not match the expected output."
                })
        
        except subprocess.TimeoutExpired:
            return Response({
                "status": "error",
                "message": "Your code took too long to execute."
            })
        except Exception as e:
            return Response({
                "status": "error",
                "message": f"An error occurred: {str(e)}"
            })
