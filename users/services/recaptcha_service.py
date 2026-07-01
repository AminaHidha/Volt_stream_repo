import requests
from django.conf import settings


def verify_recaptcha(token):
    # Skip reCAPTCHA in development mode
    if settings.DEBUG:
        return True

    if not token:
        return False

    response = requests.post(
        "https://www.google.com/recaptcha/api/siteverify",
        data={
            "secret": settings.RECAPTCHA_SECRET_KEY,
            "response": token,
        },
    )
    result = response.json()
    return result.get("success", False)
