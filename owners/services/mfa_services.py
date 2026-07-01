import pyotp
import qrcode
import base64
from io import BytesIO


def generate_mfa_secret():
    """
    Generate a random secret key for MFA.
    This secret is saved in the database and used to verify TOTP codes.
    """
    return pyotp.random_base32()


def generate_qr_code(secret: str, email: str):
    """
    Generate a QR code image that the owner scans with
    Google Authenticator app.

    Returns a base64 encoded PNG image string.
    """
    # Create the OTP auth URL
    totp = pyotp.TOTP(secret)
    otp_uri = totp.provisioning_uri(
        name=email,
        issuer_name="VoltStream"
    )

    # Generate QR code image
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(otp_uri)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to base64 string to send via API
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return img_base64


def verify_totp(secret: str, code: str):
    """
    Verify the 6-digit code from Google Authenticator.
    Returns True if valid, False if invalid.
    window=1 allows 30 seconds grace period.
    """
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)