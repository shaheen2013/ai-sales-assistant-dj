from django.urls import path
from . import views

urlpatterns = [
    path(
        "v1/get-contact",
        views.AutomatedNotificationConfigurationContactDetailsAPI.as_view(),
        name="get_contact",
    ),
    path(
        "v1/automated-notification-configuration",
        views.AutomatedNotificationConfigurationAPI.as_view(),
        name="automated_notification_configuration",
    ),
]
