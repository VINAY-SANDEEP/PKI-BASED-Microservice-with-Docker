import base64
import time

import pyotp


def hex_to_base32(hex_seed: str) -> str:
    """
    Convert 64-character hex seed string to base32-encoded string.
    """
    seed_bytes = bytes.fromhex(hex_seed)
    base32_bytes = base64.b32encode(seed_bytes)
    return base32_bytes.decode("utf-8")


def get_totp_from_hex_seed(hex_seed: str) -> pyotp.TOTP:
    """
    Create a TOTP object from a hex seed, using SHA-1, 30s, 6 digits (pyotp defaults).
    """
    base32_seed = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(base32_seed)
    return totp


def generate_totp_code(hex_seed: str) -> str:
    """
    Generate the current 6-digit TOTP code as a string.
    """
    totp = get_totp_from_hex_seed(hex_seed)
    return totp.now()


def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    """
    Verify the TOTP code with ±valid_window periods tolerance.
    """
    totp = get_totp_from_hex_seed(hex_seed)
    code = code.strip()
    return totp.verify(code, valid_window=valid_window)


def get_seconds_remaining(period: int = 30) -> int:
    """
    Return how many seconds the current TOTP code is still valid for.
    """
    now = int(time.time())
    elapsed = now % period
    remaining = period - elapsed
    return remaining
