from celery import shared_task
from django.conf import settings
from twilio.rest import Client


@shared_task
def send_booking_confirmation_sms(phone, booking_id, slot_time):
    """
    Runs in background after booking is created.
    Sends confirmation SMS to the user via Twilio.
    """
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=f"VoltStream: Your booking #{booking_id} is confirmed for {slot_time}. Thank you!",
        from_=settings.TWILIO_PHONE_NUMBER,
        to=phone,
    )
    return f"SMS sent to {phone}, SID: {message.sid}"


@shared_task
def send_cancellation_sms(phone, booking_id):
    """
    Runs in background after booking is cancelled.
    Sends cancellation SMS to the user via Twilio.
    """
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=f"VoltStream: Your booking #{booking_id} has been cancelled. We hope to see you again!",
        from_=settings.TWILIO_PHONE_NUMBER,
        to=phone,
    )
    return f"Cancellation SMS sent to {phone}, SID: {message.sid}"


@shared_task
def cancel_expired_bookings():
    """
    Celery Beat runs this every hour automatically.
    Finds all unpaid bookings older than 30 minutes and cancels them.
    """
    from datetime import timedelta

    from django.utils import timezone

    from bookings.models import Booking

    expiry_time = timezone.now() - timedelta(minutes=30)

    expired = Booking.objects.filter(
        payment_status="pending", created_at__lt=expiry_time, status="confirmed"
    )

    count = expired.count()
    expired.update(status="cancelled")

    return f"{count} expired bookings cancelled"
