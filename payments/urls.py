from django.urls import path
from . import views

urlpatterns = [
    path(
        "inventory-item-stripe-webhook/",
        views.inventory_item_stripe_webhook,
        name="car_sale_chat",
    ),
]
