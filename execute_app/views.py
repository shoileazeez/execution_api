from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CodeExecutionSerializer

class ExecuteCodeView(APIView):
    def post(self, request):
        serializer = CodeExecutionSerializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data.get('code')
            test_cases = serializer.validated_data.get('test_cases', [])

            results = []  # Store results for each test case

            for test_case in test_cases:
                input_data = test_case.get('input_data', {})
                expected_output = test_case.get('expected_output', None)

                try:
                    # Execute the user's code dynamically
                    exec_locals = {}
                    exec(code, {}, {"input_data": input_data, **exec_locals})
                    
                    # Fetch the result from the user's code
                    user_output = exec_locals.get("result")  # Assume user stores result in a variable named "result"

                    # Compare user output to expected output
                    if user_output == expected_output:
                        results.append({
                            "input_data": input_data,
                            "expected_output": expected_output,
                            "user_output": user_output,
                            "status": "passed",
                        })
                    else:
                        results.append({
                            "input_data": input_data,
                            "expected_output": expected_output,
                            "user_output": user_output,
                            "status": "failed",
                        })

                except Exception as e:
                    # Handle code execution errors
                    results.append({
                        "input_data": input_data,
                        "expected_output": expected_output,
                        "error": str(e),
                        "status": "error",
                    })

            return Response({"results": results}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
