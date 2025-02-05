import openai
from django.conf import settings
from rest_framework.exceptions import APIException
from requests.exceptions import RequestException


class OpenAIBaseClient:
    """Base client class for openai api call, This class will initiate the openai client with the key when instanciated."""

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY

        if not self.api_key:
            raise APIException("OPENAI_API_KEY is not available in the settings")
        openai.api_key = self.api_key

    # def _handle_api_error(self, error):
    #     """
    #     Handles API error and raises an appropriate Django API exception.
    #     """
    #     if isinstance(error, openai.error.OpenAIError):
    #         raise APIException(f"OpenAI API Error: {error}")
    #     elif isinstance(error, RequestException):
    #         raise APIException("Network error while communicating with OpenAI API.")
    #     else:
    #         raise APIException(f"An unexpected error occurred: {error}")
