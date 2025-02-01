import json
import subprocess
import os
from RestrictedPython import compile_restricted, safe_globals
from django.conf import settings 
from celery_app import app

@app.task
def execute_code_task(code, language, input_data=""):
    try:
        if language not in ("python", "javascript"):
            return {"error": "Unsupported language", "status": 400}

        if language == "python":
            try:
                byte_code = compile_restricted(code, '<string>', 'exec')
                restricted_globals = safe_globals.copy()
                restricted_globals['__builtins__'] = {
                    'print': print,
                    'range': range,
                    'len': len,
                    'int': int,
                    'float': float,
                    'str': str,
                    'list': list,
                    'dict': dict,
                    'tuple': tuple,
                    'set': set,
                    'abs': abs,
                    'sum': sum,
                    'min': min,
                    'max': max,
                    'bool': bool,
                    'enumerate': enumerate,
                    'zip': zip,
                    'map': map,
                    'filter': filter,
                    'sorted': sorted,
                    'any': any,
                    'all': all,
                    'input': lambda: input_data
                }
                
                exec(byte_code, restricted_globals)
                output = restricted_globals.get('__result__', None)
                if output is None:
                    output = "No output produced (did you use print or return a value?)"
                
                return {"output": str(output), "status": 200}
            except Exception as e:
                return {"error": str(e), "status": 500}

        elif language == "javascript":
            try:
                executor_path = os.path.join(settings.BASE_DIR, 'utils', 'executor.js')
                result = subprocess.run(
                    ['node', executor_path, code, input_data],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode == 0:
                    try:
                        return json.loads(result.stdout)
                    except json.JSONDecodeError as e:
                        return {"error": f"Invalid JSON from executor: {e}", "status": 500}
                else:
                    try:
                        return json.loads(result.stderr)
                    except json.JSONDecodeError as e:
                        return {"error": f"Invalid JSON error from executor: {e}", "status": 500}

            except subprocess.TimeoutError:
                return {"error": "JavaScript execution timed out", "status": 500}
            except FileNotFoundError:
                return {"error": f"Executor not found at {executor_path}", "status": 500}
            except Exception as e:
                return {"error": str(e), "status": 500}

    except Exception as e:
        return {"error": str(e), "status": 500}