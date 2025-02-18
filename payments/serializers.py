from rest_framework import serializers
from . import models


class VehicleItemOrderPaymentSerializer(serializers.ModelSerializer):
    """Serializer for Vehicle Item Order Payment model"""

    class Meta:
        model = models.VehicleItemOrderPayment
        fields = "__all__"
