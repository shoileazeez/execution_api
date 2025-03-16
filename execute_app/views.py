from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utilis import execute_code, LANGUAGE_CONFIG

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

        result = execute_code(language, code, input_data, expected_output)
        if "error" in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        return Response(result, status=status.HTTP_200_OK)

class SupportedLanguagesView(APIView):
    def get(self, request):
        languages = list(LANGUAGE_CONFIG.keys())
        return Response({"languages": languages})
