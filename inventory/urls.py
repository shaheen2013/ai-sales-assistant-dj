from django.urls import path
from . import views

urlpatterns = [
    path(
        "v1/car-sale-chat/",
        views.CarSalesAssistantAPIView.as_view(),
        name="car_sale_chat",
    ),
]
