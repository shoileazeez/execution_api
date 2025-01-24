from celery.result import AsyncResult
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse

from .serializers import CodeExecutionSerializer
from .tasks import execute_code_task


@api_view(["POST"])
def execute_code(request):
    serializer = CodeExecutionSerializer(data=request.data)
    if serializer.is_valid():
        language = serializer.validated_data["language"]
        code = serializer.validated_data["code"]
        input_data = serializer.validated_data.get("input_data", "")

        task = execute_code_task.delay(language, code, input_data)
        return Response({"task_id": str(task.id)}, status=status.HTTP_202_ACCEPTED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_task_result(request, task_id):
    task = AsyncResult(task_id)
    if task.ready():
        result = task.get()
        return Response(result, status=status.HTTP_200_OK)
    elif task.failed():
        return Response(
            {"status": "FAILURE"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    else:
        return Response({"status": "PENDING"}, status=status.HTTP_202_ACCEPTED)


from django.http import HttpResponse


def health_check(request):
    """Performs a simple health check (no database)."""
    return HttpResponse("OK", status=200, content_type="text/plain")
