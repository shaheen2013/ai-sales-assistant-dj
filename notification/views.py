from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from . import serializers
from authentication.serializers import (
    AutomatedNotificationConfigurationUserDetailsSerializers,
)
from authentication.models import User
from . import models
from utils.notification.emails import send_automated_notifications_configuration_email
from rest_framework.permissions import IsAuthenticated


class AutomatedNotificationConfigurationContactDetailsAPI(APIView):
    """
    A view for to view and update user contact informations for automated notifications configurations.
    """

    permission_classes = (IsAuthenticated,)

    # /get_contact
    @swagger_auto_schema(
        tags=["Automated Notification Configured"],
        request_body=AutomatedNotificationConfigurationUserDetailsSerializers(),
    )
    def post(self, request, *args, **kwargs):
        user = User.objects.get(id=1)
        new_data = request.data

        if new_data:
            # Update data to the user profile
            serializer = AutomatedNotificationConfigurationUserDetailsSerializers(
                user, new_data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"message": "Contact details saved."}, status=status.HTTP_200_OK
                )
            return Response(
                {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {"message": "No data provided."}, status=status.HTTP_400_BAD_REQUEST
        )

    @swagger_auto_schema(
        tags=["Automated Notification Configured"],
    )
    def get(self, request, *args, **kwargs):
        user_contact_details = (
            User.objects.filter(id=1)
            .values(
                "first_name",
                "last_name",
                "email",
                "phone_number",
                "street_address",
                "zip_code",
                "city",
                "country",
            )
            .first()
        )
        if user_contact_details:
            return Response(
                {"message": "Contact details found.", "data": user_contact_details},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"message": "User not found."}, status=status.HTTP_404_NOT_FOUND
        )


class AutomatedNotificationConfigurationAPI(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        tags=["Automated Notification Configured"],
        request_body=serializers.AutomatedNotificationConfigurationSerializer(),
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        data = request.data

        notification_methods = data.get("notification_methods")

        existing_notification_configuration_obj = (
            models.AutomatedNotficationConfiguration.objects.filter(user=user).first()
        )
        if existing_notification_configuration_obj:
            serializer = serializers.AutomatedNotificationConfigurationSerializer(
                instance=existing_notification_configuration_obj, data=data
            )
        else:
            serializer = serializers.AutomatedNotificationConfigurationSerializer(
                data=data
            )

        if serializer.is_valid():
            serializer.save()

            # Send Email
            context = {
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
            if notification_methods:
                if notification_methods == "BOTH":
                    context["notification_methods"] = "Email and SMS"
                else:
                    context["notification_methods"] = notification_methods

            try:
                send_automated_notifications_configuration_email(user.email, context)
            except Exception as e:
                print(f"Error sending email: {e}")
                return Response({"Mail Send Error: ": str(e)})

            return Response(
                {"message": "Automated notification configuration saved."},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )
