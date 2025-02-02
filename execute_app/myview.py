from rest_framework.views import APIView
from rest_framework.response import Response
import subprocess

class ExecuteCodeView(APIView):
    def post(self, request):
        code = request.data.get('code', '')
        input_data = request.data.get('input_data', {})
        expected_output = request.data.get('expected_output', None)
        
        try:
            # Construct the dynamic code to be executed
            test_code = f"""
input_data = {input_data}
{code}

result = add(**input_data)
print(result)
"""
            # Write the code to a temporary file
            with open('sandbox_code.py', 'w') as f:
                f.write(test_code)

            # Execute the code in a sandboxed environment
            process = subprocess.run(
                ["python3", "sandbox_code.py"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Retrieve and process output
            output = process.stdout.strip()
            
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
