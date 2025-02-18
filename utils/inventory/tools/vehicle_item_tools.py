from typing import Type, Optional
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
import pandas as pd
import json
import os
import uuid
import numpy as np
from inventory.models import VehicleItemInventory
from utils.authentication.tools.contact_tools import load_contact_details
from django.conf import settings
from authentication.models import User
from orders.models import VehicleItemOrder, VehicleItemOrderDetail
from inventory.models import VehicleItemInventory
from django.db import transaction
import stripe


INVOICE_FOLDER = os.path.join(settings.BASE_DIR, "invoices")

# Load vehicle item inventory
# INVENTORY_FILE = "../data/dummy_vehicle_item_inventory.csv"
item_inventory_objects = VehicleItemInventory.objects.values(
    "name", "code", "price", "stock_quantity"
)
df_item_inventory = pd.DataFrame(item_inventory_objects)

CARD_DETAILS_FILE = "card_details.json"


stripe.api_key = settings.STRIPE_SECRET_KEY


def save_inventory():
    """Saves the updated inventory back to the CSV file."""
    # df_item_inventory.to_csv(INVENTORY_FILE, index=False)
    pass


# 🔎 **Item Selection Tool**
class ItemSelectionInput(BaseModel):
    item_name: str = Field(description="Name of the vehicle item")


class GetItemAvailabilityTool(BaseTool):
    name: str = "get_item_availability"
    description: str = "Fetches availability details for a specific vehicle item."
    args_schema: Type[BaseModel] = ItemSelectionInput

    def _run(self, item_name: str):
        item_data = df_item_inventory[
            df_item_inventory["name"].str.lower() == item_name.lower()
        ]
        if item_data.empty:
            return f"❌ No item found for '{item_name}'."
        return f"✅ {item_data.iloc[0]['name']} is available. Price: ${item_data.iloc[0]['price']}. Stock: {item_data.iloc[0]['stock_quantity']}."


# 💰 **Price Inquiry Tool**
class PriceInquiryInput(BaseModel):
    item_name: str = Field(description="Name of the vehicle item")


class GetItemPriceTool(BaseTool):
    name: str = "get_item_price"
    description: str = "Fetches the price of a specific vehicle item."
    args_schema: Type[BaseModel] = PriceInquiryInput

    def _run(self, item_name: str):
        item_name = item_name.lower()
        item_data = df_item_inventory[
            df_item_inventory["name"].str.lower() == item_name
        ]
        if item_data.empty:
            return f"❌ No item found for '{item_name}'."
        return f"💰 The price of {item_data.iloc[0]['name']} is ${item_data.iloc[0]['price']}."


# 📦 **Stock Availability Tool**
class StockAvailabilityInput(BaseModel):
    item_name: str = Field(description="Name of the vehicle item")


class GetStockAvailabilityTool(BaseTool):
    name: str = "get_stock_availability"  # ✅ Explicit type annotation
    description: str = "Checks the stock availability of a specific vehicle item."
    args_schema: Type[BaseModel] = StockAvailabilityInput

    def _run(self, item_name: str):
        item_name = item_name.lower()
        item_data = df_item_inventory[
            df_item_inventory["name"].str.lower() == item_name
        ]
        if item_data.empty:
            return f"❌ No item found for '{item_name}'."
        return f"📦 Stock for {item_data.iloc[0]['name']}: {item_data.iloc[0]['stock_quantity']} units."


# 🛒 **Order Confirmation Tool**
class OrderItemInput(BaseModel):
    item_name: str = Field(description="Name of the vehicle item")
    quantity: int = Field(description="Quantity of the item to order")


class OrderItemTool(BaseTool):
    name: str = "order_vehicle_item"
    description: str = "Processes an order for a vehicle item."
    args_schema: Type[BaseModel] = OrderItemInput

    def _run(self, item_name: str, quantity: int):
        item_data = df_item_inventory[
            df_item_inventory["name"].str.lower() == item_name.lower()
        ]
        if item_data.empty or item_data.iloc[0]["stock_quantity"] < quantity:
            return f"❌ Order cannot be placed. Not enough stock for '{item_name}'."

        total_price = item_data.iloc[0]["price"] * quantity
        return f"✅ Order placed for {quantity} {item_name}(s). Total cost: ${total_price}. Proceed to payment."


# 💳 **Card Details Collection Tool** (🆕 New tool)
# class CardDetailsInput(BaseModel):
#     card_number: str = Field(description="User's credit card number")
#     card_expiry: str = Field(description="Card expiration date (MM/YY)")
#     card_cvv: str = Field(description="Card security code (CVV)")


# class CardDetailsCollectionTool(BaseTool):
#     name: str = "collect_card_details"
#     description: str = (
#         "Collects and saves user credit card details for payment processing."
#     )
#     args_schema: Type[BaseModel] = CardDetailsInput

#     def _run(self, card_number: str, card_expiry: str, card_cvv: str):
#         card_details = {
#             "card_number": card_number,
#             "card_expiry": card_expiry,
#             "card_cvv": card_cvv,
#         }
#         with open(CARD_DETAILS_FILE, "w") as f:
#             json.dump(card_details, f, indent=4)
#         return "✅ Card details saved successfully! Now proceeding to payment."


class ProcessPaymentInput(BaseModel):
    items: list = Field(description="List of purchased items with name and quantity.")


class ProcessPaymentTool(BaseTool):
    name: str = "process_payment"
    description: str = "Processes payment for ordered vehicle items."
    args_schema: Type[BaseModel] = ProcessPaymentInput
    user_id: int = None

    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id

    def _run(self, items: list):
        """Handles multiple item purchases, deducts stock, and generates an invoice."""

        total_price = 0
        purchased_items = []

        # Validate `items`
        if not isinstance(items, list) or not all(
            isinstance(item, dict) and "name" in item and "quantity" in item
            for item in items
        ):
            return {
                "error": "Invalid items format. Each item must have 'name' and 'quantity'."
            }

        # 🔍 Load & Debug Contact Details
        contact_details = load_contact_details(self.user_id)
        if not contact_details or not isinstance(contact_details, dict):
            return {
                "error": "No valid contact details found. Invoice cannot be generated."
            }

        # ✅ Ensure contact_details contains all required fields
        required_fields = {
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "street_address",
            "zip_code",
            "city",
            "state",
        }

        if not all(field in contact_details for field in required_fields):
            return {
                "error": "Missing contact details fields. Please update your profile."
            }

        # ✅ Convert all values in contact_details to strings
        contact_details = {str(k): str(v) for k, v in contact_details.items()}

        print("contact_details", contact_details)

        for item in items:
            item_name = item["name"].strip().lower()
            quantity = int(item["quantity"])

            item_data = df_item_inventory[
                df_item_inventory["name"].str.lower() == item_name
            ]

            if item_data.empty:
                return {"error": f"No item found for '{item_name}'. Payment failed."}

            # Calculate item price
            item_price = (
                float(item_data.iloc[0]["price"]) * quantity
            )  # ✅ Convert to `float`
            total_price += item_price

            # Add item to purchased items list
            purchased_items.append(
                {
                    "name": item_name,
                    "quantity": quantity,
                    "price": float(item_data.iloc[0]["price"]),  # ✅ Convert to `float`
                }
            )

        # Create Vehicle Item Order and Order Details
        try:
            user = User.objects.get(id=self.user_id)

            # �� Atomic Transaction for Database Operations
            with transaction.atomic():
                order = VehicleItemOrder.objects.create(user=user)
                for item in items:
                    item_obj = VehicleItemInventory.objects.filter(
                        name__iexact=item["name"]
                    ).first()
                    if item:
                        order_details = VehicleItemOrderDetail.objects.create(
                            order=order, item=item_obj, quantity=item["quantity"]
                        )
                        # Reduce the stock quantity from inventory
                        item_obj.reduce_stock(item["quantity"])

                metadata = {
                    "order_id": str(order.id),
                }

        except User.DoesNotExist:
            return {"error": "User not found. Invoice cannot be generated."}
        except Exception as e:
            return {"error": str(e.message)}

        # Generate unique invoice ID
        # invoice_id = str(uuid.uuid4())

        # TODO Stripe Payment Gateway Integration
        line_items = [
            {
                "price_data": {
                    "currency": "usd",
                    "unit_amount": int(float(item["price"]) * 100),
                    "product_data": {
                        "name": item["name"].strip(),
                    },
                },
                "quantity": int(item["quantity"]),
            }
            for item in purchased_items
        ]

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            payment_intent_data={"metadata": metadata},
            mode="payment",
            success_url="http://localhost:8000/docs/",
            cancel_url="http://localhost:8000/docs/",
        )

        redirect_url = checkout_session.url

        # ✅ Call GenerateInvoiceTool with correct parameters
        # invoice_tool = GenerateInvoiceTool()
        # invoice_result = invoice_tool._run(
        #     # invoice_id=invoice_id,
        #     items=purchased_items,
        #     total_price=float(total_price),
        #     contact_details=contact_details,
        # )

        return {
            "status": "success",
            "message": f"Payment processed for {len(items)} items.",
            "total_price": total_price,
            # "invoice_id": invoice_id,
            # "invoice_result": invoice_result,
            "stripe_payment_url": redirect_url,
        }


# 🧾 **Invoice Generation Tool**
class GenerateInvoiceInput(BaseModel):
    invoice_id: str = Field(description="Unique ID for the invoice")
    items: list = Field(description="List of items purchased")
    total_price: float = Field(description="Total price of the purchase")
    user_id: int = Field(description="User's contact details")
    contact_details: dict = Field(description="User's contact details")


class GenerateInvoiceTool(BaseTool):
    name: str = "generate_invoice"
    description: str = "Generates and saves an invoice for the purchased items."
    args_schema: Type[BaseModel] = GenerateInvoiceInput

    def _run(
        self,
        invoice_id: str,
        items: list,
        total_price: float,
        contact_details: dict,
    ):
        """Ensures invoice directory exists and saves invoice to a unique file."""

        # Debugging Logs
        if not contact_details:
            return {
                "error": "Missing or invalid contact details. Invoice cannot be generated."
            }

        # ✅ Ensure all numeric values are converted to Python `int` or `float`
        def convert_numpy_types(obj):
            if isinstance(obj, (np.int64, np.int32)):
                return int(obj)
            elif isinstance(obj, (np.float64, np.float32)):
                return float(obj)
            elif isinstance(obj, dict):
                return {k: convert_numpy_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(v) for v in obj]
            else:
                return obj

        # ✅ Convert all numpy types in the input data
        items = convert_numpy_types(items)
        total_price = convert_numpy_types(total_price)

        invoice_data = {
            "invoice_id": invoice_id,
            "contact_details": contact_details,
            "items": items,
            "total_price": total_price,
        }

        # ✅ Ensure `invoices/` directory exists
        if not os.path.exists(INVOICE_FOLDER):
            os.makedirs(INVOICE_FOLDER)

        # ✅ Save each invoice in a unique file
        invoice_file_path = os.path.join(INVOICE_FOLDER, f"invoice_{invoice_id}.json")

        with open(invoice_file_path, "w") as f:
            json.dump(invoice_data, f, indent=4)

        return {
            "status": "success",
            "invoice_id": invoice_id,
            "total_price": total_price,
        }
