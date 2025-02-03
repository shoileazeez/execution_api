import subprocess
from rest_framework.response import Response
def execute_java_code(code, input_data):
    try:
        if input_data:
                input_data_declaration = f"""
public static String inputData = "{input_data}";
"""
                # Assume the user places `inputData` where needed in their code
                code = code.replace("/*input_data_placeholder*/", input_data_declaration)

        # Write the Java code to a temporary file
        with open('sandbox_code.java', 'w') as f:
            f.write(code)

        # Compile the Java code
        compile_process = subprocess.run(
            ["javac", "sandbox_code.java"],
            capture_output=True,
            text=True
        )

        if compile_process.returncode != 0:
            error = compile_process.stderr.strip()
            return {"status": "error", "message": f"Java code compilation failed: {error}"}

        # Execute the compiled Java code
        run_process = subprocess.run(
            ["java", "sandbox_code"],
            capture_output=True,
            text=True,
            timeout=30
        )

        if run_process.returncode != 0:
            error = run_process.stderr.strip()
            return {"status": "error", "message": f"Java code execution failed: {error}"}

        formatted_output = run_process.stdout.strip()
        return Response({
            "status": "success",
            "output": output
        }, status=status.HTTP_200_OK)

    except subprocess.TimeoutExpired:
        return Response({"status": "error", "message": "Java code took too long to execute."}, status=status.HTTP_408_REQUEST_TIMEOUT)
    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)