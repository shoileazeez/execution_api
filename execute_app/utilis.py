import subprocess
import tempfile
import os

# Map of languages to Docker images and filenames
LANGUAGE_CONFIG = {
    "python": {"image": "sandbox-python", "filename": "code.py", "command": ["python", "code.py"]},
    "javascript": {"image": "sandbox-node", "filename": "code.js", "command": ["node", "code.js"]},
    "cpp": {"image": "sandbox-cpp", "filename": "code.cpp", "command": ["g++", "code.cpp", "-o", "code.out", "&&", "./code.out"]},
    "java": {"image": "sandbox-java", "filename": "Main.java", "command": ["javac", "Main.java", "&&", "java", "Main"]},
    "go": {"image": "sandbox-go", "filename": "main.go", "command": ["go", "run", "main.go"]},
    "ruby": {"image": "sandbox-ruby", "filename": "code.rb", "command": ["ruby", "code.rb"]},
    "php": {"image": "sandbox-php", "filename": "code.php", "command": ["php", "code.php"]},
    "csharp": {"image": "sandbox-csharp", "filename": "Program.cs", "command": ["mcs", "Program.cs", "&&", "mono", "Program.exe"]},
    "swift": {"image": "sandbox-swift", "filename": "main.swift", "command": ["swift", "main.swift"]},
    "kotlin": {"image": "sandbox-kotlin", "filename": "main.kt", "command": ["kotlinc", "main.kt", "-include-runtime", "-d", "main.jar", "&&", "java", "-jar", "main.jar"]},
}

def execute_code(language, code, input_data, expected_output):
    if language not in LANGUAGE_CONFIG:
        return {"error": f"Unsupported language: {language}"}

    config = LANGUAGE_CONFIG[language]
    filename = config["filename"]
    command = config["command"]
    image = config["image"]

    # Create a temporary directory for the code file
    with tempfile.TemporaryDirectory() as tmpdir:
        code_path = os.path.join(tmpdir, filename)
        input_path = os.path.join(tmpdir, "input.txt")

        # Write the code and input to files
        with open(code_path, "w") as code_file:
            code_file.write(code)
        with open(input_path, "w") as input_file:
            input_file.write(input_data)

        try:
            # Run the Docker container
            with open(input_path, "rb") as input_file:
                result = subprocess.run(
                    command,
                    cwd=tmpdir,
                    stdin=input_file,  # Pass input to subprocess
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=5
                )
            stdout = result.stdout.decode().strip()
            stderr = result.stderr.decode().strip()

            # Compare actual and expected output
            status = "Passed" if stdout == expected_output else "Failed"
            return {
                "stdout": stdout,
                "stderr": stderr,
                "output": stdout,
                "expected": expected_output,
                "status": status
            }

        except subprocess.TimeoutExpired:
            return {"error": "Execution timed out"}
        except Exception as e:
            return {"error": str(e)}
