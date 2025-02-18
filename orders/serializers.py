from rest_framework import serializers
from . import models


class VehicleItemOrderSerializer(serializers.ModelSerializer):
    """Serializer for Vehicle Item Order model"""

    class Meta:
        model = models.VehicleItemOrder
        fields = "__all__"


class VehicleItemOrderDetailSerializer(serializers.ModelSerializer):
    "Serializer for Vehicle Item Order details model"

    class Meta:
        model = models.VehicleItemOrderDetail
        fields = "__all__"
