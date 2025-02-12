from rest_framework import serializers
from . import models


class AutomatedNotificationConfigurationUserDetailsSerializers(
    serializers.ModelSerializer
):
    class Meta:
        model = models.User
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "street_address",
            "zip_code",
            "city",
            "country",
        ]
