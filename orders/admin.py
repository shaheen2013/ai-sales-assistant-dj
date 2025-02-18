from django.contrib import admin
from . import models

admin.site.register(models.VehicleItemOrder)
admin.site.register(models.VehicleItemOrderDetail)
