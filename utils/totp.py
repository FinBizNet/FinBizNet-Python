import pyotp

def get_totp_token(qr_key):
    return pyotp.TOTP(qr_key).now()
