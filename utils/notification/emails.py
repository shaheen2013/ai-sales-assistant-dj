from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings


def send_automated_notifications_configuration_email(recipient_email, context):
    subject = "Automated Notification Enabled!"

    # Render the email template with context
    message = render_to_string(
        "email/automated_notification_configuration_email.html", context
    )
    # Send email with HTML content
    send_mail(
        subject,
        # Empty plain-text body (optional)
        "Hello",
        settings.EMAIL_HOST_USER,
        [recipient_email],
        fail_silently=False,
        # Pass HTML content
        html_message=message,
    )
