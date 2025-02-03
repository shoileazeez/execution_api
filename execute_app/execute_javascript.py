import subprocess
import json
from rest_framework.response import Response
from rest_framework import status
def execute_javascript_code(code, input_data):
    try:
        # Prepare the JavaScript code to be executed dynamically
        input_data_str = json.dumps(input_data)
        test_code = f"""
        const inputData = {input_data_str};
        {code}
        console.log(result);  // Make sure result is printed
        """

        # Write the code to a temporary file
        with open('sandbox_code.js', 'w') as f:
            f.write(test_code)

        # Execute the JavaScript code in a Node.js environment
        process = subprocess.run(
            ["node", "sandbox_code.js"],
            capture_output=True,
            text=True,
            timeout=30
        )

        if process.returncode != 0:
            error = process.stderr.strip()
            return Response({"status": "error", "message": f"JavaScript code execution failed: {error}"}, status=status.HTTP_400_BAD_REQUEST)

        output = process.stdout.strip()
        if not output:
            return Response({"status": "error", "message": "No output was returned from the JavaScript code."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "status": "success",
            "output": output
        }, status=status.HTTP_200_OK)

    except subprocess.TimeoutExpired:
        return Response({"status": "error", "message": "JavaScript code took too long to execute."}, status=status.HTTP_408_REQUEST_TIMEOUT)
    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
