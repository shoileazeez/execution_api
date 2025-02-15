import subprocess
import tempfile
import os
import resource
import json
LANGUAGE_CONFIG = {
    "python": {"filename": "code.py", "run_command": ["python3", "code.py"],
               "input_syntax": "import sys\ninput_data = sys.stdin.read().strip()\n"},
    "javascript": {"filename": "code.js", "run_command": ["node", "code.js"],
                   "input_syntax": "const fs = require('fs'); let input_data = fs.readFileSync(0, 'utf-8').trim();\n"},
    "java": {
        "filename": "Main.java",
        "compile_command": ["javac", "Main.java"],
        "run_command": ["java", "Main"],
        "input_syntax": "import java.util.*;\nclass Main {\npublic static void main(String[] args) {\nScanner sc = new Scanner(System.in);\nString input_data = sc.nextLine();\n"
    },
    "cpp": {
        "filename": "code.cpp",
        "compile_command": ["g++", "code.cpp", "-o", "code.out"],
        "run_command": ["./code.out"],
        "input_syntax": "#include<iostream>\nusing namespace std;\nint main() {\nstring input_data; getline(cin, input_data);\n"

    },
    "c": {
        "filename": "code.c",
        "compile_command": ["gcc", "code.c", "-o", "code.out"],
        "run_command": ["./code.out"],
        "input_syntax": "#include <stdio.h>\nint main() {\nchar input_data[1000]; fgets(input_data, 1000, stdin);\n"

    },
    "ruby": {"filename": "code.rb", "run_command": ["ruby", "code.rb"],"input_syntax": "input_data = STDIN.read.strip\n"},
    "go": {
        "filename": "main.go", "run_command": ["go", "run", "main.go"],
        "input_syntax": "package main\nimport (\n\"fmt\"\n\"bufio\"\n\"os\"\n)\nfunc main() {\nreader := bufio.NewReader(os.Stdin)\ninput_data, _ := reader.ReadString('\\n')\n"
        },

    "php": {"filename": "code.php", "run_command": ["php", "code.php"],
            "input_syntax": "$input_data = trim(fgets(STDIN));\n"},
    "rust": {
        "filename": "main.rs",
        "compile_command": ["rustc", "main.rs", "-o", "main.out"],
        "run_command": ["./main.out"],
        "input_syntax": "use std::io::{self, Read};\nfn main() {\nlet mut input_data = String::new(); io::stdin().read_to_string(&mut input_data).unwrap();\n"
    },
    "kotlin": {
        "filename": "main.kt",
        "compile_command": ["kotlinc", "main.kt", "-include-runtime", "-d", "main.jar"],
        "run_command": ["java", "-jar", "main.jar"],
        "input_syntax": "fun main() {\nval input_data = readLine() ?: \"\"\n"

    },
    "r": {"filename": "script.R", "run_command": ["Rscript", "script.R"],
          "input_syntax": "input_data <- readLines(file('stdin'))\n"},
    "perl": {"filename": "script.pl", "run_command": ["perl", "script.pl"],
            "input_syntax": "my $input_data = <STDIN>;\nchomp($input_data);\n"
            },
    "lua": {"filename": "main.lua", "run_command": ["lua", "main.lua"],"input_syntax": "input_data = io.read()\n"},
    "typescript": {"filename": "code.ts", "run_command": ["ts-node", "code.ts"],
                "input_syntax": "import * as fs from 'fs';\nconst input_data = fs.readFileSync(0, 'utf-8').trim();\n"
                },
    "bash": {"filename": "script.sh", "run_command": ["bash", "script.sh"],"input_syntax": "read input_data\n"},
    "erlang": {
        "filename": "script.erl",
        "compile_command": ["erlc", "script.erl"],
        "run_command": ["erl", "-noshell", "-s", "script", "start", "-s", "init", "stop"],
        "input_syntax": "input_data = io:get_line('').\n"
    },
    "elixir": {
        "filename": "script.exs", "run_command": ["elixir", "script.exs"],
        "input_syntax": "input_data = IO.gets(\"\") |> String.trim()\n"
    },
}

def set_limits():
    """Set CPU and memory limits for sandboxing."""
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))  # Max 5 seconds of CPU time
    resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024, 256 * 1024 * 1024))  # Max 256MB RAM

def execute_code(language, code, input_data, expected_output):
    if language not in LANGUAGE_CONFIG:
        return {"error": f"Unsupported language: {language}"}

    config = LANGUAGE_CONFIG[language]
    filename = config["filename"]
    
    

    with tempfile.TemporaryDirectory() as tmpdir:
        code_path = os.path.join(tmpdir, filename)
        
        
        input_path = os.path.join(tmpdir, "input.json")

        # Save input data as a JSON file
        with open(input_path, "w") as input_file:
            json.dump(input_data, input_file)

        # Language-specific input syntax to read the JSON file
        if language == "python":
            input_syntax = (
                "import json\n"
                f"with open('{input_path}', 'r') as f:\n"
                "    input_data = json.load(f)\n"
            )
        elif language == "javascript":
            input_syntax = (
                "const fs = require('fs');\n"
                f"const input_data = JSON.parse(fs.readFileSync('{input_path}', 'utf8'));\n"
            )
        elif language == "java":
            input_syntax = (
                "import java.nio.file.*;\n"
                "import org.json.*;\n"
                "class Main {\n"
                "    public static void main(String[] args) throws Exception {\n"
                f"        String content = new String(Files.readAllBytes(Paths.get(\"{input_path}\")));\n"
                "        JSONObject input_data = new JSONObject(content);\n"
            )
        elif language == "c":
            input_syntax = (
                "#include <stdio.h>\n"
                "#include <stdlib.h>\n"
                "#include <string.h>\n"
                "int main() {\n"
                f"    FILE *file = fopen(\"{input_path}\", \"r\");\n"
                "    if (!file) { printf(\"Error: Cannot open file\"); return 1; }\n"
                "    char buffer[1024]; fread(buffer, 1, 1024, file); fclose(file);\n"
                "    // Parse JSON manually in C\n"
            )
        elif language == "cpp":
            input_syntax = (
                "#include <iostream>\n"
                "#include <fstream>\n"
                "#include <nlohmann/json.hpp>\n"
                "using json = nlohmann::json;\n"
                "int main() {\n"
                f"    std::ifstream file(\"{input_path}\");\n"
                "    json input_data; file >> input_data;\n"
            )
        elif language == "ruby":
            input_syntax = (
                "require 'json'\n"
                f"input_data = JSON.parse(File.read('{input_path}'))\n"
                )
        elif language == "go":
            input_syntax = (
                "package main\n"
                "import (\n"
                "    \"encoding/json\"\n"
                "    \"fmt\"\n"
                "    \"io/ioutil\"\n"
                "    \"os\"\n"
                ")\n"
                "func main() {\n"
                f"    data, _ := ioutil.ReadFile(\"{input_path}\")\n"
                "    var input_data map[string]interface{}\n"
                "    json.Unmarshal(data, &input_data)\n"
                )
        elif language == "php":
            input_syntax = (
                "<?php\n"
                f"$input_data = json_decode(file_get_contents('{input_path}'), true);\n"
            )
        elif language == "rust":
            input_syntax = (
                "use std::fs;\n"
                "use serde_json::Value;\n"
                "fn main() {\n"
                f"    let data = fs::read_to_string(\"{input_path}\").unwrap();\n"
                "    let input_data: Value = serde_json::from_str(&data).unwrap();\n"
                )
        elif language == "kotlin":
            input_syntax = (
                "import java.io.File\n"
                "import org.json.JSONObject\n"
                "fun main() {\n"
                f"    val content = File(\"{input_path}\").readText()\n"
                "    val input_data = JSONObject(content)\n"
                )
        elif language == "r":
            input_syntax = (
                f"input_data <- jsonlite::fromJSON('{input_path}')\n"
                )
        elif language == "perl":
            input_syntax = (
                "use JSON;\n"
                f"my $input_data = decode_json(scalar read_file('{input_path}'));\n"
                )
        elif language == "lua":
            input_syntax = (
                "local json = require('dkjson')\n"
                f"local file = io.open('{input_path}', 'r')\n"
                "local input_data = json.decode(file:read('*a'))\n"
                )
        elif language == "typescript":
            input_syntax = (
                "import * as fs from 'fs';\n"
                f"const input_data = JSON.parse(fs.readFileSync('{input_path}', 'utf8'));\n"
                )
        elif language == "bash":
            input_syntax = (
                f"input_data=$(cat {input_path})\n"
                )
        elif language == "erlang":
            input_syntax = (
                "file:read_file(\"{input_path}\").\n"
                "json:decode(Data).\n"
                )
        elif language == "elixir":
            input_syntax = (
                "content = File.read!(\"{input_path}\")\n"
                "input_data = Jason.decode!(content)\n"
    )
        else:
            input_syntax = "Unsupported language"

        final_code = input_syntax + code

        # Write the code to a file
        with open(code_path, "w") as code_file:
            code_file.write(final_code)


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
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=set_limits,
                timeout=5,
            )

            stdout = result.stdout.decode().strip()
            stderr = result.stderr.decode().strip()
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
