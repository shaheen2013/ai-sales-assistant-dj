from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from utils.inventory.car_sales_assistant import CarSalesAssistant
from . import serializers
from . import models


class CarSalesAssistantAPIView(APIView):
    """Car Sales Assistant API view"""

    # Car sale assistant chat api
    def post(self, request, *args, **kwargs):
        """
        api need to call with a dict with key: message and value.
        Sample User Input Data:
        {
            "message": "User Message",
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

            return Response({"response": response})

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
