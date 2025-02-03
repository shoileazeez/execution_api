from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CodeExecutionSerializer
from .execute_python import execute_python_code
from .execute_javascript import execute_javascript_code
from .execute_java import execute_java_code

class ExecuteCodeView(APIView):
    def post(self, request):
        # Validate and parse the request data using the serializer
        serializer = CodeExecutionSerializer(data=request.data)
        
        if serializer.is_valid():
            code = serializer.validated_data['code']
            input_data = serializer.validated_data['input_data']
            expected_output = serializer.validated_data.get('expected_output', None)
            language = serializer.validated_data['language']
            
            # Execute the code based on the specified language
            if language == 'python':
                result = execute_python_code(code, input_data)
            elif language == 'javascript':
                result = execute_javascript_code(code, input_data)
            elif language == 'java':
                result = execute_java_code(code, input_data)
            else:
                return Response({"status": "error", "message": "Unsupported language."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Compare the output with the expected output
            if result.data["status"] == "success":
                print("Execution result:", result.data)

                if str(result.data["output"]) == str(expected_output):
                    return Response({
                        "status": "success",
                        "output": result.data["output"],
                        "message": "Your code passed all test cases!"
                    })
                else:
                    return Response({
                        "status": "failure",
                        "output": result.data["output"],
                        "expected_output": expected_output,
                        "message": "Output does not match the expected output."
                    })
            else:
                return Response({
                    "status": "error",
                    "message": result.data["message"]
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "status": "error",
                "message": "Invalid input data",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
