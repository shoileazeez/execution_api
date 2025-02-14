from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utilis import execute_code, LANGUAGE_CONFIG
import re
import json

def is_malicious_code(code):
    """
    Check for malicious code patterns (e.g., system calls, file operations).
    """
    dangerous_patterns = [
        r"import os",         # Prevent OS module import
        r"import sys",        # Prevent system access
        r"subprocess",        # Prevent command execution
        r"open\(",            # Prevent file manipulation
        r"eval\(",            # Prevent arbitrary code execution
        r"exec\(",            # Prevent arbitrary code execution
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, code):
            return True
    return False

class ExecuteCodeView(APIView):
    def post(self, request):
        language = request.data.get("language")
        code = request.data.get("code")
        input_data = request.data.get("input", "")
        expected_output = request.data.get("expected", "")

        if not language or not code or expected_output is None:
            return Response(
                {"error": "language, code, and expected output are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if is_malicious_code(code):
            return Response({"error": "Potentially malicious code detected!"}, status=400)

        if isinstance(input_data, (dict, list)):
            try:
                input_data = json.dumps(input_data)
            except (TypeError, ValueError):
                return Response({"error": "Invalid JSON structure in input"}, status=400)
        elif not isinstance(input_data, str):
            try:
                input_data = str(input_data)
            except:
                return Response({"error": "Input must be convertible to a string"}, status=400)

        # Handle expected output in different formats
        if isinstance(expected_output, (dict, list)):
            try:
                expected_output = json.dumps(expected_output)
            except (TypeError, ValueError):
                return Response({"error": "Invalid JSON structure in expected output"}, status=400)
        elif not isinstance(expected_output, str):
            try:
                expected_output = str(expected_output)
            except:
                return Response({"error": "Expected output must be convertible to a string"}, status=400)

        # Execute the code
        result = execute_code(language, code, input_data, expected_output)
        if "error" in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        return Response(result, status=status.HTTP_200_OK)

class SupportedLanguagesView(APIView):
    def get(self, request):
        languages = list(LANGUAGE_CONFIG.keys())
        return Response({"languages": languages})
