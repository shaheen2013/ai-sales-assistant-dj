from django.db import models
from config.mixins.models import BaseModel, VehicleModelMixin


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
