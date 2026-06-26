import pyotp
import qrcode
import io
import base64
from typing import Tuple


def generate_totp_secret() -> str:
    return pyotp.random_base32()


def get_totp_uri(secret: str, email: str, issuer: str = "Stoxly.ai") -> str:
    return pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name=issuer)


def generate_qr_code_base64(secret: str, email: str) -> str:
    uri = get_totp_uri(secret, email)
    qr = qrcode.make(uri)
    buf = io.BytesIO()
    qr.save(buf, format="PNG")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()


def verify_totp(secret: str, code: str) -> bool:
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)
