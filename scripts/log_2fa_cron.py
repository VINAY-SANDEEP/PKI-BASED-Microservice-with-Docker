#!/usr/bin/env python3

import datetime
from pathlib import Path
import sys
import os

# --- Make sure /app is on sys.path so we can import app.totp_utils, app.crypto_utils ---
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # /app
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.totp_utils import generate_totp_code   # import from app package
from app.crypto_utils import is_valid_hex_seed  # import from app package

SEED_FILE = Path("/data/seed.txt")   # volume mount in Docker


def read_seed():
    if not SEED_FILE.exists():
        print("ERROR: Seed file not found at /data/seed.txt", file=sys.stderr)
        return None

    try:
        seed = SEED_FILE.read_text(encoding="utf-8").strip()
    except Exception as e:
        print(f"ERROR: Could not read seed file: {e}", file=sys.stderr)
        return None

    if not is_valid_hex_seed(seed):
        print("ERROR: Seed file contains invalid hex seed", file=sys.stderr)
        return None

    return seed


def log_code():
    seed = read_seed()
    if seed is None:
        return  # error already printed

    try:
        code = generate_totp_code(seed)
    except Exception as e:
        print(f"ERROR: Failed to generate TOTP code: {e}", file=sys.stderr)
        return

    # UTC timestamp
    now_utc = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # Format EXACTLY as required
    print(f"{now_utc} - 2FA Code: {code}")


if __name__ == "__main__":
    log_code()
