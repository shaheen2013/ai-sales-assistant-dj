from rest_framework import serializers
from . import models


class CarDetailsSerializer(serializers.ModelSerializer):
    """Serializer for CarDetails model"""

    class Meta:
        model = models.CarDetails
        fields = "__all__"


class UserInputSerializer(serializers.Serializer):
    """Serializer for user input"""

    message = serializers.CharField()


class VehicleItemInventorySerializer(serializers.ModelSerializer):
    """Serializer for VehicleItemInventory model"""

    class Meta:
        model = models.VehicleItemInventory
        fields = "__all__"
