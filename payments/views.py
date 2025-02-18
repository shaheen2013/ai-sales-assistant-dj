from django.shortcuts import render
import stripe
import os
import json
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from orders.models import VehicleItemOrder
from payments.models import VehicleItemOrderPayment
from utils.authentication.tools.contact_tools import load_contact_details

# Set the Stripe secret key
stripe.api_key = settings.STRIPE_SECRET_KEY

INVOICE_FOLDER = os.path.join(settings.BASE_DIR, "invoices")


@csrf_exempt
def inventory_item_stripe_webhook(request):
    if request.method == "POST":
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

        # Verify the webhook signature
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )

        except ValueError as e:
            # Invalid payload
            return JsonResponse({"error": str(e)}, status=400)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return JsonResponse({"error": str(e)}, status=400)

        # Handle the event
        if event["type"] == "payment_intent.succeeded":
            try:
                stripe_intent = event["data"]["object"]
                metadata = stripe_intent["metadata"]

                # Get the paid amount (in cents)
                amount_received = stripe_intent["amount_received"]
                amount_received_usd = amount_received / 100

                order_id = metadata["order_id"]
                vehicle_item_order = VehicleItemOrder.objects.get(id=order_id)

                # Create a VehicleItemOrderPayment
                payment_obj = VehicleItemOrderPayment.objects.create(
                    order=vehicle_item_order,
                    payment_id=stripe_intent.id,
                    total_paid_amount=amount_received_usd,
                )

                # Create Invoice
                contact_details = load_contact_details(vehicle_item_order.user.id)
                items_obj = vehicle_item_order.vehicle_order_details.all()

                items_list = [
                    {
                        "name": item.item.name,
                        "quantity": item.quantity,
                        "price": float(item.item.price),
                    }
                    for item in items_obj
                ]

                invoice_data = {
                    "payment_id": stripe_intent.id,
                    "contact_details": contact_details,
                    "items": items_list,
                    "total_price": amount_received_usd,
                }

                # ✅ Ensure `invoices/` directory exists
                if not os.path.exists(INVOICE_FOLDER):
                    os.makedirs(INVOICE_FOLDER)

                # ✅ Save each invoice in a unique file
                invoice_file_path = os.path.join(
                    INVOICE_FOLDER, f"invoice_{stripe_intent.id}.json"
                )

                with open(invoice_file_path, "w") as f:
                    json.dump(invoice_data, f, indent=4)

            except VehicleItemOrder.DoesNotExist:
                return JsonResponse({"error": "Order not found"}, status=404)
            except Exception as e:
                return JsonResponse(
                    {"error": f"Error processing payment intent: str{e}"}, status=500
                )

        return JsonResponse({"status": "success"}, status=200)

    return JsonResponse({"error": "Method not allowed"}, status=405)
