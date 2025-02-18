from django.db import models
from config.mixins.models import BaseModel
from orders.models import VehicleItemOrder


class VehicleItemOrderPayment(BaseModel):
    """Payment details for the Vehicle Item Order, One Order can have one payment."""

    order = models.OneToOneField(
        VehicleItemOrder,
        related_name="vehicle_item_order_payments",
        on_delete=models.CASCADE,
    )

    payment_id = models.CharField(max_length=512)

    # payment_status_choices =[
    #     ("pending", "Pending"),
    #     ("succeeded", "Succeeded"),
    #     ("failed", "Failed"),
    # ]
    # payment_status = models.CharField(
    #     max_length=255, choices=payment_status_choices, default="pending"
    # )
    total_paid_amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name_plural = "Vehicle Item Order Payments"
        verbose_name = "Vehicle Item Order Payment"
