import random

from django.conf import settings
from django.utils import timezone

from users.models import OTP, User


# =========================
# GENERATE OTP
# =========================
def generate_otp_code():
    return str(random.randint(100000, 999999))


# =========================
# SEND OTP SMS via Twilio
# =========================
def send_otp_sms(phone, otp_code, purpose):
    try:
        from twilio.rest import Client

        if not phone.startswith("+"):
            phone = "+91" + phone.lstrip("0")

        print(f"SENDING SMS TO: {phone}")

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        if purpose == "register":
            message_body = (
                f"Welcome to VoltStream!\n"
                f"Your verification OTP is: {otp_code}\n"
                f"Valid for 10 minutes. Do not share."
            )
        elif purpose == "login":
            message_body = (
                f"VoltStream Login OTP: {otp_code}\n"
                f"Valid for 10 minutes. Do not share."
            )
        elif purpose == "forgot_password":
            message_body = (
                f"VoltStream Password Reset\n"
                f"Your OTP is: {otp_code}\n"
                f"Valid for 10 minutes."
            )
        else:
            message_body = f"VoltStream OTP: {otp_code}\n" f"Valid for 10 minutes."

        message = client.messages.create(
            body=message_body, from_=settings.TWILIO_PHONE_NUMBER, to=phone
        )

        print(f"SMS SENT — SID: {message.sid}")
        return True

    except Exception as e:
        print(f"SMS ERROR: {str(e)}")
        return False


# =========================
# SEND OTP EMAIL (fallback)
# =========================
def send_otp_email(email, otp_code, purpose):
    from django.core.mail import send_mail

    if purpose == "forgot_password":
        subject = "VoltStream - Reset Password OTP"
    else:
        subject = "VoltStream - Verification OTP"

    message = (
        f"Hello,\n\n"
        f"Your OTP is: {otp_code}\n\n"
        f"Valid for 10 minutes.\n\n"
        f"Team VoltStream"
    )

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        print(f"EMAIL SENT TO: {email}")
        return True
    except Exception as e:
        print(f"EMAIL ERROR: {str(e)}")
        return False


# =========================
# CREATE OTP
# =========================
def create_otp(user, purpose):

    # Invalidate old OTPs
    OTP.objects.filter(user=user, purpose=purpose, is_used=False).update(is_used=True)

    otp_code = generate_otp_code()

    otp = OTP.objects.create(
        user=user, purpose=purpose, otp_code=otp_code, resend_count=0
    )

    print(f"USER PHONE: {user.phone}")
    print(f"OTP CODE: {otp_code}")

    # Send via SMS if phone exists
    if user.phone:
        print("SENDING VIA SMS")
        sms_sent = send_otp_sms(user.phone, otp_code, purpose)
        if not sms_sent and user.email:
            print("SMS FAILED — FALLING BACK TO EMAIL")
            send_otp_email(user.email, otp_code, purpose)
    elif user.email:
        print("NO PHONE — SENDING VIA EMAIL")
        send_otp_email(user.email, otp_code, purpose)

    return otp


# =========================
# VERIFY OTP (by email - kept for Google login)
# =========================
def verify_otp(email, otp_code, purpose):

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return False, "User not found"

    otp = OTP.objects.filter(user=user, purpose=purpose, is_used=False).first()

    if not otp:
        return False, "No OTP found. Please request a new one"

    if otp.is_expired():
        return False, "OTP has expired. Please request a new one"

    if otp.otp_code != otp_code:
        return False, "Invalid OTP. Please try again"

    otp.is_used = True
    otp.save()

    return True, user


# =========================
# RESEND OTP (by email - kept for compatibility)
# =========================
def resend_otp(email, purpose="register"):

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return False, "User not found"

    old_otp = OTP.objects.filter(user=user, purpose=purpose, is_used=False).first()

    if old_otp and old_otp.resend_count >= 5:
        return False, "Maximum resend limit reached"

    if old_otp and old_otp.last_resend_at:
        cooldown = timezone.now() - old_otp.last_resend_at
        if cooldown.total_seconds() < 30:
            seconds_left = int(30 - cooldown.total_seconds())
            return False, f"Please wait {seconds_left} seconds"

    OTP.objects.filter(user=user, purpose=purpose, is_used=False).update(is_used=True)

    otp_code = generate_otp_code()

    OTP.objects.create(
        user=user,
        purpose=purpose,
        otp_code=otp_code,
        resend_count=(old_otp.resend_count + 1) if old_otp else 1,
        last_resend_at=timezone.now(),
    )

    if user.phone:
        send_otp_sms(user.phone, otp_code, purpose)
    elif user.email:
        send_otp_email(user.email, otp_code, purpose)

    return True, "OTP resent successfully"


# =========================
# VERIFY OTP BY PHONE
# =========================
def verify_otp_by_phone(phone, otp_code, purpose):
    """
    Verifies OTP using phone number.
    Used for register and login flows.
    """
    try:
        user = User.objects.get(phone=phone)
    except User.DoesNotExist:
        return False, "User not found"

    otp = OTP.objects.filter(user=user, purpose=purpose, is_used=False).first()

    if not otp:
        return False, "No OTP found. Please request a new one"

    if otp.is_expired():
        return False, "OTP has expired. Please request a new one"

    if otp.otp_code != otp_code:
        return False, "Invalid OTP. Please try again"

    otp.is_used = True
    otp.save()

    return True, user


# =========================
# RESEND OTP BY PHONE
# =========================
def resend_otp_by_phone(phone, purpose="register"):
    """
    Resends OTP using phone number.
    Used for register and login flows.
    """
    try:
        user = User.objects.get(phone=phone)
    except User.DoesNotExist:
        return False, "User not found"

    old_otp = OTP.objects.filter(user=user, purpose=purpose, is_used=False).first()

    if old_otp and old_otp.resend_count >= 5:
        return False, "Maximum resend limit reached"

    if old_otp and old_otp.last_resend_at:
        cooldown = timezone.now() - old_otp.last_resend_at
        if cooldown.total_seconds() < 30:
            seconds_left = int(30 - cooldown.total_seconds())
            return False, f"Please wait {seconds_left} seconds"

    OTP.objects.filter(user=user, purpose=purpose, is_used=False).update(is_used=True)

    otp_code = generate_otp_code()

    OTP.objects.create(
        user=user,
        purpose=purpose,
        otp_code=otp_code,
        resend_count=(old_otp.resend_count + 1) if old_otp else 1,
        last_resend_at=timezone.now(),
    )

    send_otp_sms(user.phone, otp_code, purpose)

    return True, "OTP resent successfully"
