from django.db import models


class BaseModel(models.Model):
    """Base Model for all model, All model will be inherited from this base class"""

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True


class AddressModelMixin(models.Model):
    """Address mixin class for addresses"""

    street_address = models.TextField(
        default="",
        blank=True,
    )
    zip_code = models.CharField(
        max_length=255,
        default="",
        blank=True,
    )
    city = models.CharField(
        max_length=255,
        default="",
        blank=True,
    )
    state = models.CharField(
        max_length=255,
        default="",
        blank=True,
    )
    country = models.CharField(
        max_length=255,
        default="",
        blank=True,
    )
    lat = models.CharField(
        max_length=32,
        blank=True,
        default="",
    )
    lng = models.CharField(
        max_length=32,
        blank=True,
        default="",
    )
    county = models.CharField(
        max_length=255,
        default="",
        blank=True,
    )

    class Meta:
        abstract = True


class VehicleModelMixin(models.Model):
    """Base mixins model for vehicle, all type of vehicle model will be inherited from this."""

    brand = models.CharField(max_length=255, null=True, blank=True)
    model = models.CharField(max_length=255)
    year = models.PositiveIntegerField(null=True, blank=True)
    mileage = models.DecimalField(
        max_digits=12, decimal_places=4, null=True, blank=True
    )

    class Meta:
        abstract = True


class ItemModelMixin(models.Model):
    """Base mixins model for items, all type of item model will be inherited from this."""

    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    quantity = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        abstract = True
