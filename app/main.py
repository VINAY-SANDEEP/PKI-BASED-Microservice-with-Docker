from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pathlib import Path
import os

from .crypto_utils import (
    load_private_key,
    decrypt_seed,
    save_seed_to_file,
    is_valid_hex_seed,
)
from .totp_utils import (
    generate_totp_code,
    verify_totp_code,
    get_seconds_remaining,
)

app = FastAPI()

# Seed file path:
# - In Docker, we'll set SEED_FILE_PATH=/data/seed.txt via env
# - Locally, default is ./data/seed.txt
SEED_FILE_PATH = Path(os.getenv("SEED_FILE_PATH", "data/seed.txt"))


@app.get("/health")
def health():
    return {"status": "ok"}


class DecryptSeedRequest(BaseModel):
    encrypted_seed: str


@app.post("/decrypt-seed")
def decrypt_seed_endpoint(body: DecryptSeedRequest):
    """
    POST /decrypt-seed
    Body: {"encrypted_seed": "BASE64_STRING"}
    On success:
        200 {"status": "ok"}
    On failure:
        500 {"error": "Decryption failed"}
    """
    # Load private key
    try:
        private_key = load_private_key("student_private.pem")
    except Exception:
        # For assignment spec, treat all failures as "Decryption failed"
        return JSONResponse(
            status_code=500,
            content={"error": "Decryption failed"},
        )

    # Decrypt seed
    try:
        hex_seed = decrypt_seed(body.encrypted_seed, private_key)
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"error": "Decryption failed"},
        )

    # Save seed to file
    try:
        save_seed_to_file(hex_seed, SEED_FILE_PATH)
    except Exception:
        # Saving failed – treat as server error
        return JSONResponse(
            status_code=500,
            content={"error": "Decryption failed"},
        )

    return {"status": "ok"}


def load_hex_seed_from_file() -> str | None:
    """
    Helper to read the hex seed from SEED_FILE_PATH.
    Returns the seed string, or None if not available/invalid.
    """
    if not SEED_FILE_PATH.exists():
        return None

    try:
        seed = SEED_FILE_PATH.read_text(encoding="utf-8").strip()
    except Exception:
        return None

    if not is_valid_hex_seed(seed):
        return None

    return seed


@app.get("/generate-2fa")
def generate_2fa():
    """
    GET /generate-2fa
    Response on success:
        200 {"code": "123456", "valid_for": 30}
    On failure (no seed):
        500 {"error": "Seed not decrypted yet"}
    """
    hex_seed = load_hex_seed_from_file()
    if not hex_seed:
        return JSONResponse(
            status_code=500,
            content={"error": "Seed not decrypted yet"},
        )

    try:
        code = generate_totp_code(hex_seed)
        valid_for = get_seconds_remaining(period=30)
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to generate TOTP code"},
        )

    return {"code": code, "valid_for": valid_for}


class Verify2FARequest(BaseModel):
    code: str | None = None


@app.post("/verify-2fa")
def verify_2fa(body: Verify2FARequest):
    """
    POST /verify-2fa
    Body:
        {"code": "123456"}

    Responses:
        - 200 {"valid": true/false}
        - 400 {"error": "Missing code"}
        - 500 {"error": "Seed not decrypted yet"}
    """
    # 1. Validate code present
    if not body.code:
        return JSONResponse(
            status_code=400,
            content={"error": "Missing code"},
        )

    # 2. Load seed
    hex_seed = load_hex_seed_from_file()
    if not hex_seed:
        return JSONResponse(
            status_code=500,
            content={"error": "Seed not decrypted yet"},
        )

    # 3. Verify TOTP with ±1 window
    try:
        is_valid = verify_totp_code(hex_seed, body.code, valid_window=1)
    except Exception:
        # If something goes really wrong, treat as invalid
        is_valid = False

    return {"valid": is_valid}
