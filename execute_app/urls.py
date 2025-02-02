from django.urls import path
from .views import ExecuteCodeView
# from myview import ExecuteCodeView

urlpatterns = [
    path('', ExecuteCodeView.as_view(), name='execute'),
]
