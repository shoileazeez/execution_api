import subprocess
import tempfile
import os
import json
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


def execute_code(language, code, input_data, expected_output):
    if language not in LANGUAGE_CONFIG:
        return {"error": f"Unsupported language: {language}"}

    config = LANGUAGE_CONFIG[language]
    filename = config["filename"]
    print(f"input_data{input_data}")
    input_str = json.dumps(input_data)  # Convert input to JSON string
    print(f"input_data{input_str}")
    input_bytes = input_str.encode() 
    print(f"input_data{input_bytes}")


    with tempfile.TemporaryDirectory() as tmpdir:
        code_path = os.path.join(tmpdir, filename)

        # Write code to temporary file
        with open(code_path, "w") as code_file:
            code_file.write(code)

        try:
            if "compile_command" in config:
                compile_result = subprocess.run(
                    config["compile_command"],
                    cwd=tmpdir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=5,
                )
                if compile_result.returncode != 0:
                    return {"error": "Compilation failed", "stderr": compile_result.stderr.decode().strip()}

            # Run step
            result = subprocess.run(
                config["run_command"],
                cwd=tmpdir,
                input=input_bytes,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5,
            )

            stdout = result.stdout.decode().strip()
            print(f"stdout{stdout}")
            stderr = result.stderr.decode().strip()
            print(f"stderr{stderr}")
            try:
                stdout_data = json.loads(stdout)
                print(f"stdout_data{stdout_data}")
            except json.JSONDecodeError:
                stdout_data = stdout  # Fallback to raw output
            
            status = "Passed" if stdout_data == expected_output else "Failed"

            return {
                "stdout": stdout_data,
                "stderr": stderr,
                "output": stdout_data,
                "expected": expected_output,
                "status": status
            }

        except subprocess.TimeoutExpired:
            return {"error": "Execution timed out"}
        except Exception as e:
            return {"error": str(e)}
