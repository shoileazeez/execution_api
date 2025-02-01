from django.urls import path

from . import views

urlpatterns = [
    path("execute/", views.execute_code, name="execution_api"),
    path("execute_result/<str:task_id>", views.get_task_result, name="result"),
    path("health/", views.health_check, name="health_check"),
]
