import subprocess
import os
import uuid
import re

def execute_java_code(code, input_data):
    try:
        # Generate a unique filename for the Java file to avoid conflicts
        unique_filename = f"sandbox_code_{uuid.uuid4().hex}"
        java_file = f"{unique_filename}.java"
        class_name = unique_filename

        # Ensure the code has a valid class and main method
        if not re.search(r"public\s+class\s+\w+", code):
            code = f"""
public class {class_name} {{
    {code}
    public static void main(String[] args) {{
        // Pass input data and call the function
        System.out.println({class_name}.execute("{input_data}"));
    }}
}}
"""

        # Write the Java code to a temporary file
        with open(java_file, 'w') as f:
            f.write(code)

        # Compile the Java code
        compile_process = subprocess.run(
            ["javac", java_file],
            capture_output=True,
            text=True
        )

        if compile_process.returncode != 0:
            error = compile_process.stderr.strip()
            return {"status": "error", "message": f"Java code compilation failed: {error}"}

        # Execute the compiled Java code
        run_process = subprocess.run(
            ["java", unique_filename],
            capture_output=True,
            text=True,
            timeout=30
        )

        if run_process.returncode != 0:
            error = run_process.stderr.strip()
            return {"status": "error", "message": f"Java code execution failed: {error}"}

        # Capture the output
        output = run_process.stdout.strip()

        # Clean up generated files
        os.remove(java_file)
        os.remove(f"{unique_filename}.class")

        return {"status": "success", "output": output}

    except subprocess.TimeoutExpired:
        return {"status": "error", "message": "Java code took too long to execute."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

