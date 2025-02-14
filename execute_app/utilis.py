import subprocess
import tempfile
import os
import json
import sys
import traceback

LANGUAGE_CONFIG = {
    "python": {"filename": "code.py", "run_command": ["python3", "code.py"]},
    "javascript": {"filename": "code.js", "run_command": ["node", "code.js"]},
    "java": {
        "filename": "Main.java",
        "compile_command": ["javac", "Main.java"],
        "run_command": ["java", "Main"],
    },
    "cpp": {
        "filename": "code.cpp",
        "compile_command": ["g++", "code.cpp", "-o", "code.out"],
        "run_command": ["./code.out"],
    },
    "c": {
        "filename": "code.c",
        "compile_command": ["gcc", "code.c", "-o", "code.out"],
        "run_command": ["./code.out"],
    },
    "ruby": {"filename": "code.rb", "run_command": ["ruby", "code.rb"]},
    "go": {"filename": "main.go", "run_command": ["go", "run", "main.go"]},
    "php": {"filename": "code.php", "run_command": ["php", "code.php"]},
    "rust": {
        "filename": "main.rs",
        "compile_command": ["rustc", "main.rs", "-o", "main.out"],
        "run_command": ["./main.out"],
    },
    "kotlin": {
        "filename": "main.kt",
        "compile_command": ["kotlinc", "main.kt", "-include-runtime", "-d", "main.jar"],
        "run_command": ["java", "-jar", "main.jar"],
    },
    "r": {"filename": "script.R", "run_command": ["Rscript", "script.R"]},
    "perl": {"filename": "script.pl", "run_command": ["perl", "script.pl"]},
    "lua": {"filename": "main.lua", "run_command": ["lua", "main.lua"]},
    "typescript": {"filename": "code.ts", "run_command": ["ts-node", "code.ts"]},
    "bash": {"filename": "script.sh", "run_command": ["bash", "script.sh"]},
    "erlang": {
        "filename": "script.erl",
        "compile_command": ["erlc", "script.erl"],
        "run_command": ["erl", "-noshell", "-s", "script", "start", "-s", "init", "stop"],
    },
    "elixir": {"filename": "script.exs", "run_command": ["elixir", "script.exs"]},
}

def prepare_input(language, input_data):
    """Prepare input data based on language-specific requirements."""
    if input_data is None:
        return None
    
    # Convert simple values to string
    if isinstance(input_data, (int, float, bool, str)):
        return str(input_data).encode("utf-8")
    # For complex data structures, use JSON for languages that can handle it easily
    return json.dumps(input_data).encode("utf-8")

def normalize_output(output_str, expected_output):
    """Normalize output for comparison."""
    if output_str is None:
        return "", ""
    if expected_output is None:
        expected_output = ""
    
    norm_output = str(output_str).strip()
    norm_expected = str(expected_output).strip()
    return norm_output, norm_expected

def execute_code(language, code, input_data, expected_output):
    if language not in LANGUAGE_CONFIG:
        return {"error": f"Unsupported language: {language}"}

    config = LANGUAGE_CONFIG[language]
    filename = config["filename"]

    with tempfile.TemporaryDirectory() as tmpdir:
        code_path = os.path.join(tmpdir, filename)

        # Write code to temporary file
        try:
            with open(code_path, "w") as code_file:
                code_file.write(code)
        except Exception as e:
            return {"error": f"Failed to write code file: {str(e)}"}

        # Add debug information
        print(f"Executing in directory: {tmpdir}")
        print(f"Language: {language}")
        print(f"Command: {config['run_command']}")
        print(f"Input data type: {type(input_data)}")
        print(f"Input data: {input_data}")
        print(f"Expected output: {expected_output}")
        
        try:
            # Compilation step if needed
            if "compile_command" in config:
                print(f"Compiling with: {config['compile_command']}")
                compile_result = subprocess.run(
                    config["compile_command"],
                    cwd=tmpdir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=10,
                )
                if compile_result.returncode != 0:
                    compile_stderr = compile_result.stderr.decode("utf-8", errors="ignore").strip()
                    print(f"Compilation failed with stderr: {compile_stderr}")
                    return {"error": "Compilation failed", "stderr": compile_stderr}

            # Prepare input based on language
            prepared_input = prepare_input(language, input_data)
            print(f"Prepared input ({len(prepared_input) if prepared_input else 0} bytes): {prepared_input!r}")
            
            # List files in directory before execution
            print(f"Files before execution: {os.listdir(tmpdir)}")
            
            # Run the code
            result = subprocess.run(
                config["run_command"],
                cwd=tmpdir,
                input=prepared_input,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10,
                check=False,  # Don't raise exception on non-zero return code
            )
            
            # Process results
            print(f"Command completed with return code: {result.returncode}")
            print(f"Raw stdout length: {len(result.stdout)}")
            print(f"Raw stderr length: {len(result.stderr)}")
            
            stdout = result.stdout.decode("utf-8", errors="ignore").strip()
            stderr = result.stderr.decode("utf-8", errors="ignore").strip()
            
            print(f"Decoded stdout: {stdout!r}")
            print(f"Decoded stderr: {stderr!r}")
            
            # List files after execution
            print(f"Files after execution: {os.listdir(tmpdir)}")
            
            # Normalize and compare output
            norm_stdout, norm_expected = normalize_output(stdout, expected_output)
            status = "Passed" if norm_stdout == norm_expected else "Failed"
            
            return {
                "stdout": stdout,
                "stderr": stderr,
                "output": stdout,
                "expected": expected_output,
                "status": status,
                "return_code": result.returncode
            }

        except subprocess.TimeoutExpired:
            print("Execution timed out")
            return {"error": "Execution timed out"}
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            print(traceback.format_exc())
            return {"error": str(e), "traceback": traceback.format_exc()}