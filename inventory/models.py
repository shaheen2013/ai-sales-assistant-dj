from django.db import models
from config.mixins.models import BaseModel, VehicleModelMixin, ItemModelMixin


class CarDetails(BaseModel, VehicleModelMixin):
    """Car Details model"""

    body_style = models.CharField(max_length=512, null=True, blank=True)
    engine_type = models.CharField(max_length=512, null=True, blank=True)
    fuel_type = models.CharField(max_length=512, null=True, blank=True)

    def __str__(self):
        return f"{self.brand} - {self.model}"

    class Meta:
        verbose_name = "Car Details"
        verbose_name_plural = "Car Details"


class VehicleItemInventory(ItemModelMixin, BaseModel):
    """Vehicle Item Inventory Stock Details"""

    class Meta:
        verbose_name = "Vehicle Item Inventory"
        verbose_name_plural = "Vehicle Item Inventories"

    def __str__(self):
        return f"{self.name} - {self.price} - {self.stock_quantity}"

    def increase_stock(self, quantity):
        """Increase stock"""
        self.stock_quantity += quantity
        self.save()

    def reduce_stock(self, quantity):
        """Reduce stock when an order is placed."""
        if self.stock_quantity >= quantity:
            self.stock_quantity -= quantity
            self.save()
        else:
            raise ValueError("Insufficient stock quantity!")
