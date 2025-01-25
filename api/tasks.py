import json
import subprocess
import os
from restrictedpython import compile_restricted, safe_globals
from vm2 import VM

from celery_app import app  # Assuming your Celery app is in celery_app.py

@app.task
def execute_code_task(code, language, input_data=""):
    try:
        if language not in ("python", "javascript"):
            return {"error": "Unsupported language"}, 400

        if language == "python":
            try:
                # Compile restricted code
                byte_code = compile_restricted(code, '<string>', 'exec')
                # Create a safe globals environment
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
                # Execute in the restricted environment
                exec(byte_code, restricted_globals)
                output = restricted_globals.get('__result__', None)
                if output is None:
                    output = "No output produced (did you use print or return a value?)"
                
                return {"output": str(output)}, 200
            except Exception as e:
                return {"error": str(e)}, 500

        elif language == "javascript":
            try:
                vm = VM(timeout=5, eval_timeout=5)
                result = vm.run(code, input_data=input_data)
                return {"output": str(result)}, 200
            except Exception as e:
                return {"error": str(e)}, 500

    except Exception as e:
        return {"error": str(e)}, 500