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
