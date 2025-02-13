from django.urls import path
from .views import ExecuteCodeView,SupportedLanguagesView
# from myview import ExecuteCodeView

urlpatterns = [
    path('', ExecuteCodeView.as_view(), name='execute'),
    path("languages/", SupportedLanguagesView.as_view(), name="languages"),
]
