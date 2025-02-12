from django.conf import settings
from twilio.rest import Client


def send_sms(phone_number: str, body: str):
    """
    Sends an SMS notification using Twilio API.

    Args:
        phone_number (str): Recipient phone number.
        body (str): Message body

    Returns:
        bool: True if SMS sent successfully, False otherwise.
    """
    try:
        if settings.TWILIO_PHONE_NUMBER == phone_number:
            print("🚨 Error: Cannot send SMS to the same Twilio number.")
            return False

        client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN,
        )
        client.messages.create(
            body=body,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number,
        )

        print(f"📩 SMS sent successfully to {phone_number}!")
        return True
    except Exception as e:
        print(f"🚨 SMS error: {e}")
        return False
