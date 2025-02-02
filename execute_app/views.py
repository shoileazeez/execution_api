# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from .serializers import CodeExecutionSerializer
# from RestrictedPython import compile_restricted, safe_globals, utility_builtins
# class ExecuteCodeView(APIView):
#     def post(self, request):
#         serializer = CodeExecutionSerializer(data=request.data)
#         if serializer.is_valid():
#             code = serializer.validated_data.get('code')
#             test_cases = serializer.validated_data.get('test_cases', [])

#             results = []  # Store results for each test case

#             for test_case in test_cases:
#                 input_data = test_case.get('input_data', {})
#                 expected_output = test_case.get('expected_output', None)

#                 try:
#                     # Execute the user's code dynamically
#                     exec_globals = {
#                         "__builtins__": utility_builtins,  # Restrict built-in functions
#                         "input_data": input_data,          # Pass input data
#                     }
#                     exec_locals = {}

#                     # Compile the user's code securely
#                     compiled_code = compile_restricted(code, "<string>", "exec")

#                     # Execute the compiled code
#                     exec(compiled_code, exec_globals, exec_locals)
                    
#                     # Fetch the result from the user's code
#                     user_output = exec_locals.get("result")  # Assume user stores result in a variable named "result"

#                     # Compare user output to expected output
#                     if user_output == expected_output:
#                         results.append({
#                             "input_data": input_data,
#                             "expected_output": expected_output,
#                             "user_output": user_output,
#                             "status": "passed",
#                         })
#                     else:
#                         results.append({
#                             "input_data": input_data,
#                             "expected_output": expected_output,
#                             "user_output": user_output,
#                             "status": "failed",
#                         })

#                 except Exception as e:
#                     # Handle code execution errors
#                     results.append({
#                         "input_data": input_data,
#                         "expected_output": expected_output,
#                         "error": str(e),
#                         "status": "error",
#                     })

#             return Response({"results": results}, status=status.HTTP_200_OK)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.views import APIView
from rest_framework.response import Response
import subprocess
import re
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
            ["python3", "-m", "pip", "install", "pandas", "numpy"],
            capture_output=True,
            text=True,
            timeout=5
            )

# Check for errors during installation
            if install_process.returncode != 0:
                print(f"Error installing dependencies: {install_process.stderr}")
            else:
                print("Dependencies installed successfully.")

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
            if str(output) == str(expected_output):
                return Response({
                    "status": "success",
                    "output": output,
                    "message": "Your code passed all test cases!"
                })
            else:
                return Response({
                    "status": "failure",
                    "output": output,
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
