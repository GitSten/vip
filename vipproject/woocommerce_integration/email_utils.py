# woocommerce_integration/email_utils.py
from django.core.mail import send_mail


def send_order_notification(order_id, total_amount):
    subject = f"New Order Notification - Order ID: {order_id}"
    message = f"An order with ID {order_id} has been placed with a total amount of {total_amount}."
    from_email = "stensagar@gmail.com"  # Replace with your email
    recipient_list = ["stensagar@gmail.com"]  # Replace with your email(s)

    send_mail(subject, message, from_email, recipient_list)
