from django.db import models
from config.mixins.models import BaseModel
from authentication.models import User
from inventory.models import VehicleItemInventory


class VehicleItemOrder(BaseModel):
    """Order Details model, It will store the details of the order for car inventory items."""

    user = models.ForeignKey(User, related_name="orders", on_delete=models.CASCADE)

    order_status_choices = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    order_status = models.CharField(
        max_length=255, choices=order_status_choices, default="pending"
    )

    class Meta:
        verbose_name_plural = "Vehicle Item Orders"
        verbose_name = "Vehicle Item Order"

    def __str__(self):
        return f"Order {self.id} - User: {self.user}"


class VehicleItemOrderDetail(BaseModel):
    """Order Items model, It will store the details of the items for the VehicleItemOrder order."""

    order = models.ForeignKey(
        VehicleItemOrder, related_name="vehicle_order_details", on_delete=models.CASCADE
    )
    item = models.ForeignKey(
        VehicleItemInventory,
        related_name="vehicle_order_items",
        on_delete=models.CASCADE,
    )

    quantity = models.PositiveIntegerField()

    class Meta:
        verbose_name_plural = "Vehicle Item Order Details"
        verbose_name = "Vehicle Item Order Detail"

    def total_price(self):
        return self.quantity * self.item.price

    def __str__(self):
        return f"Order: {self.order}"
