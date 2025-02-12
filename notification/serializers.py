from rest_framework import serializers
from . import models
from authentication.models import User


class AutomatedNotificationConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AutomatedNotficationConfiguration
        fields = ["is_automated_notification_enabled", "notification_methods"]
        # fields = "__all__"

    def create(self, validated_data):
        request = self.context.get("request")

        # Ensure request exists
        user = request.user if request else None

        if user and user.is_authenticated:
            validated_data["user"] = user
            return super().create(validated_data)
        else:
            raise serializers.ValidationError(
                "User must be authenticated to create a configuration."
            )
