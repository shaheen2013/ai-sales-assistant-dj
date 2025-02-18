from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from utils.inventory.car_sales_assistant import CarSalesAssistant
from . import serializers
from . import models
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from chat_history.models import ChatHistory
from utils.inventory.agent.vehicle_item_agent import run_agent_executor


class CarSalesAssistantAPIView(APIView):
    """Car Sales Assistant API view"""

    @swagger_auto_schema(
        tags=["Car AI Assistant"], request_body=serializers.UserInputSerializer
    )
    def post(self, request, *args, **kwargs):
        """
        Sample Input Data:
        {
            "message": "Content",
        }
        """

        data = request.data
        user_input = data.get("message")
        if not user_input:
            return Response(
                {"error": "No message provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            car_details = models.CarDetails.objects.values(
                "brand",
                "model",
                "year",
                "body_style",
                "engine_type",
                "fuel_type",
                "mileage",
            )
            # Create a instance of car sale assistance class with car data, that has all the functionality for end to end ai chat
            car_sales_bot = CarSalesAssistant(car_objects=car_details)

            # Run the conversation using the user input and get the response from the car sale assistant
            response = car_sales_bot.run_conversation(user_input)

            # If user is authenticated, save the message and response to the chat history model
            if request.user.is_authenticated:
                # Save Chat histry
                chat_history = ChatHistory(
                    user=request.user, message=user_input, response=response
                )
                chat_history.save()

            return Response({"response": response})
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VehicleItemChatAPI(APIView):
    """Vehicle Item Chat API, for inventory details, item purchase and others chat."""

    # permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        tags=["Inventory Item AI Assistant"],
        request_body=serializers.UserInputSerializer,
    )
    def post(self, request, *args, **kwargs):
        data = request.data
        user = request.user

        user_input = data.get("message")

        # session_id = data.get("session_id", "default")

        # tts - text to speech
        enable_tts = data.get("enable_tts", False)

        if not user_input:
            return Response(
                {"error": "No message provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not user.is_authenticated:
            return Response(
                {"error": "Please Login First."},
                status=status.HTTP_403_FORBIDDEN,
            )

        response = run_agent_executor(user_input, user.id)

        # if enable_tts:
        # return text_to_speech_response(response)

        return Response({"response": response})

