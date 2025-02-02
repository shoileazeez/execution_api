import subprocess

def execute_javascript_code(code, input_data):
    try:
        if input_data:
            input_data_declaration = f"const inputData = {input_data};\n"
            code = input_data_declaration + code
        # Write the JavaScript code to a temporary file
        with open('sandbox_code.js', 'w') as f:
            f.write(code)

        # Execute the JavaScript code using Node.js
        process = subprocess.run(
            ["node", "sandbox_code.js"],
            capture_output=True,
            text=True,
            timeout=30
        )

        if process.returncode != 0:
            error = process.stderr.strip()
            return {"status": "error", "message": f"JavaScript execution failed: {error}"}

        formatted_output = process.stdout.strip()
        return {"status": "success", "output": formatted_output}
    
    except subprocess.TimeoutExpired:
        return {"status": "error", "message": "JavaScript code took too long to execute."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
