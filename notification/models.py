from django.db import models
from config.mixins.models import BaseModel
from authentication.models import User


class AutomatedNotficationConfiguration(BaseModel):
    """
    This class is responsible for holds the notification automation settings. Which user want automatic notification.
    Also store the notfication methods.
    """

    user = models.OneToOneField(User, db_index=True, on_delete=models.CASCADE)

    # Field to check if automated notification is enabled or not for a user.
    is_automated_notification_enabled = models.BooleanField(default=False)

    # Choices for notification methods.
    notification_method_choices = [
        ("EMAIL", "Email"),
        ("SMS", "SMS"),
        ("BOTH", "Both"),
    ]

    # Field to store the notification methods for a user.
    notification_methods = models.CharField(
        max_length=6,
        choices=notification_method_choices,
    )

    class Meta:
        verbose_name = "Automated Notification Configuration"
        verbose_name_plural = "Automated Notification Configurations"

    def __str__(self):
        return f"{self.user} - {self.is_automated_notification_enabled}"
