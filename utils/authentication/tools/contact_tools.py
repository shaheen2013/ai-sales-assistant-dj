from typing import Type, Optional
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from authentication.models import User


def load_contact_details(user_id):
    """Loads contact details from the database if available."""
    try:
        contact = User.objects.get(
            id=user_id
        )  # Ensure this matches your model's primary key field
        return {
            "first_name": contact.first_name,
            "last_name": contact.last_name,
            "email": contact.email,
            "phone_number": contact.phone_number,
            "street_address": contact.street_address,
            "zip_code": contact.zip_code,
            "city": contact.city,
            "state": contact.state,
            # "country": contact.country,
        }
    except User.DoesNotExist:
        return None


class CheckContactDetailsInput(BaseModel):
    pass  # No input required


class ContactDetailsInput(BaseModel):
    # first_name: str = Field(description="First name of the user")
    # last_name: str = Field(description="Last name of the user")
    # email: str = Field(description="User's email address")
    phone_number: str = Field(description="User's phone number")
    street_address: str = Field(description="User's street address")
    zip_code: str = Field(description="User's zip code")
    city: str = Field(description="User's city")
    state: str = Field(description="User's state")


class CheckContactDetailsTool(BaseTool):
    name: str = "check_contact_details"
    description: str = (
        "Checks if user contact details exist and returns them if available."
    )
    args_schema: Type[BaseModel] = CheckContactDetailsInput
    user_id: Optional[int] = None

    def __init__(self, user_id: int, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id

    def _run(self):
        contact_details = load_contact_details(self.user_id)
        if contact_details:
            return (
                f"✅ **Existing Contact Details Found:**\n"
                f"👤 **Name:** {contact_details['first_name']} {contact_details['last_name']}\n"
                f"📧 **Email:** {contact_details['email']}\n"
                f"📞 **Phone:** {contact_details['phone_number']}\n"
                f"🏠 **Street address:** {contact_details['street_address']}\n"
                f"📪 **Zip code:** {contact_details['zip_code']}\n"
                f"🌆 **City:** {contact_details['city']}\n"
                f"🌐 **State:** {contact_details['state']}\n"
                # f"{contact_details['user_city']}, {contact_details['user_state']} - {contact_details['user_zip_code']}\n"
                "Would you like to update any information? If so, specify the field(s) to update."
            )
        return "❌ No contact details found. I will collect them when necessary."


class CollectContactDetailsTool(BaseTool):
    name: str = "collect_contact_details"  # ✅ FIXED: Added explicit type annotation
    description: str = "Collects and saves user contact details for vehicle inquiries."
    args_schema: Type[BaseModel] = ContactDetailsInput
    user_id: Optional[int] = None

    def __init__(self, user_id: int, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id

    def _run(
        self,
        # first_name: str,
        # last_name: str,
        # email: str,
        phone_number: str,
        street_address: str,
        zip_code: str,
        city: str,
        state: str,
    ) -> str:
        contact_details = {
            # "first_name": first_name,
            # "last_name": last_name,
            # "email": email,
            "phone_number": phone_number,
            "street_address": street_address,
            "zip_code": zip_code,
            "city": city,
            "state": state,
        }
        try:
            # Fetch the user by user_id
            user = User.objects.get(id=self.user_id)

            if phone_number:
                user.phone_number = phone_number
            if street_address:
                user.street_address = street_address
            if zip_code:
                user.zip_code = zip_code
            if city:
                user.city = city
            if state:
                user.state = state

            user.save()

            return "Contact details saved successfully!"
        except User.DoesNotExist:
            return "User not found. Please Login First"
