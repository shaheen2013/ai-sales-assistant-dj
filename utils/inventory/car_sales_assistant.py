import pandas as pd
import json
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory


class CarSalesAssistant:
    def __init__(self, car_objects: list, temperature=0.7):
        """ "
        Initialize the CarSalesAssistant with a temperature and a car data dataframe.

        params:
        car_objects: List of CarDetails Model objects
        """

        # Convert querysets to a dataframe
        self.df_inventory = pd.DataFrame(list(car_objects))

        # Convert inventory to a string for the prompt
        inventory_str = self.df_inventory.to_string(index=False)

        self.system_prompt = f"""
        You are an AI car dealership assistant. Your goal is to help users find the perfect vehicle while encouraging them to book a test drive or schedule a demo.

        - When a user asks about a brand, list all available models from the inventory and suggest a test drive.
        - When a user selects a model, store it as the active vehicle and offer next steps (test drive, demo, financing, etc.).
        - Recognize car selections in any order, e.g., "Volvo XC90 2021" or "2021 Volvo XC90".
        - Show the model as Brand: brand, Model: model, Year: year,  Body Style: body_style, Engine Type: engine_type, Fuel Type: fuel_type, Mileage: mileage,
        - Answer follow-up questions (engine type, fuel type, mileage, body style) about the selected vehicle.
        - Actively guide users toward test drives, financing, and bookings by making engaging suggestions.
        - If a car is not in inventory, provide general information but **always redirect the user to available options**.

        Here is the current inventory:
        {inventory_str}

        🎯 **Remember:** Your job is not just to provide information but to encourage users to take action!
        Example engagement phrases you can use:
        - "That’s a fantastic choice! Would you like to book a test drive?"
        - "This model is in high demand! Shall I schedule a demo for you?"
        - "Want to experience it in person? Let’s book a test drive!"
        """

        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=temperature)
        self.memory = ConversationBufferMemory(return_messages=True)
        self.conversation_state = {
            "last_vehicle": None,
            "available_models": None,
            "booking": False,
            "scheduling_demo": False,
            "collecting_details": False,
            "contact_details": {},
            "current_detail_request": None,  # Tracks which detail is being collected
        }

    def get_available_models(self, brand):
        """Filter the inventory for available models of the given brand."""
        return self.df_inventory[
            self.df_inventory["brand"].str.lower() == brand.lower()
        ]

    def select_vehicle(self, user_input):
        if not self.conversation_state["available_models"]:
            return "Please specify a brand first so I can show you available options."

        words = user_input.lower().split()
        selected_vehicle = None

        for vehicle in self.conversation_state["available_models"]:
            model_match = vehicle["model"].lower() in words
            brand_match = vehicle["brand"].lower() in words
            year_match = str(vehicle["year"]) in words

            if model_match and (brand_match or year_match):
                selected_vehicle = vehicle
                break

        if selected_vehicle:
            self.conversation_state["last_vehicle"] = selected_vehicle
            self.conversation_state["available_models"] = None

            return (
                f"Great choice! You're looking at the {selected_vehicle['year']} {selected_vehicle['brand']} {selected_vehicle['model']}.\n"
                f"This model has {selected_vehicle['mileage']} miles and features a {selected_vehicle['engine_type']} engine.\n"
                f"It runs on {selected_vehicle['fuel_type']} and has a {selected_vehicle['body_style']} body type.\n"
                "Would you like to:\n"
                "1. **Book a test drive**\n"
                "2. **Schedule a demo**\n"
                "Please type the number to proceed."
            )

        return (
            "I didn't catch that. Could you specify the model and year from the list?"
        )

    def start_collecting_contact_details(self, user_input):
        if "book" in user_input.lower() or "test drive" in user_input.lower():
            self.conversation_state["booking"] = True
            self.conversation_state["scheduling_demo"] = False
        elif "schedule" in user_input.lower() or "demo" in user_input.lower():
            self.conversation_state["scheduling_demo"] = True
            self.conversation_state["booking"] = False
        else:
            return "Please choose either 'Book a test drive' or 'Schedule a demo' to proceed."

        self.conversation_state["collecting_details"] = True
        self.conversation_state["contact_details"] = {}
        self.conversation_state["current_detail_request"] = "first_name"
        return "Sure! Let's get started. What's your **first name**?"

    def collect_contact_details(self, user_input):
        detail_order = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "street",
            "zip_code",
            "city",
            "country",
        ]
        next_question = {
            "first_name": "Got it, {first_name}! What's your **last name**?",
            "last_name": "Thanks, {first_name} {last_name}. What's your **email address**?",
            "email": "Great! Now, what's your **phone number**?",
            "phone_number": "What's your **street address**?",
            "street": "Almost done! What's your **zip code**?",
            "zip_code": "Which **city** do you live in?",
            "city": "And finally, which **country** are you from?",
            "country": "Thank you! Your details have been saved. Would you like to proceed with booking?",
        }

        current_detail = self.conversation_state["current_detail_request"]
        self.conversation_state["contact_details"][current_detail] = user_input.strip()

        if current_detail == "country":  # Last field, save details
            with open("contact_details.json", "w") as f:
                json.dump(self.conversation_state["contact_details"], f, indent=4)

            self.conversation_state["collecting_details"] = False
            return "Thank you! Your details have been saved. Would you like to proceed with booking?"

        # Move to the next required detail
        next_detail_index = detail_order.index(current_detail) + 1
        next_detail = detail_order[next_detail_index]
        self.conversation_state["current_detail_request"] = next_detail

        return next_question[current_detail].format(
            **self.conversation_state["contact_details"]
        )

    def run_conversation(self, user_input):
        if self.conversation_state["collecting_details"]:
            return self.collect_contact_details(user_input)

        if "book" in user_input.lower() or "schedule" in user_input.lower():
            return self.start_collecting_contact_details(user_input)

        # Check if the user is asking about a specific car
        if any(
            word in user_input.lower()
            for word in ["model", "brand", "year", "car", "vehicle"]
        ):
            # Extract brand from user input
            brand = None
            for word in user_input.lower().split():
                if word in self.df_inventory["brand"].str.lower().values:
                    brand = word
                    break

            if brand:
                available_models = self.get_available_models(brand)
                if not available_models.empty:
                    self.conversation_state["available_models"] = (
                        available_models.to_dict("records")
                    )
                    return self.select_vehicle(user_input)
                else:
                    return f"I'm sorry, we don't have any {brand.capitalize()} models in our inventory. Would you like information about other available brands?"
            else:
                return "I'm sorry, I couldn't identify the brand you're asking about. Could you please specify the brand?"

        # If the user is asking a general question, let the LLM handle it
        response = self.llm.invoke(
            f"{self.system_prompt}\nUser input: '{user_input}'.\nYour response:"
        ).content.strip()
        return response
