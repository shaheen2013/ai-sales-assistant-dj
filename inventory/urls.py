from django.urls import path
from . import views

urlpatterns = [
    path("car-sale-ai-assistant-chat/", views.CarSalesAssistantAPIView.as_view()),
]
