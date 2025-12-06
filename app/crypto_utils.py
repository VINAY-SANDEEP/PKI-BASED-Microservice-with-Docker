import base64
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from cryptography.hazmat.primitives import hashes, serialization


def load_private_key(path: str = "student_private.pem") -> RSAPrivateKey:
    """
    Load the student's RSA private key from a PEM file.
    """
    with open(path, "rb") as f:
        pem_data = f.read()

    private_key = serialization.load_pem_private_key(
        pem_data,
        password=None,  # no password as per assignment
    )
    return private_key


def is_valid_hex_seed(seed: str) -> bool:
    """
    Validate that the seed is a 64-character lowercase hex string.
    """
    if len(seed) != 64:
        return False
    valid_chars = "0123456789abcdef"
    return all(c in valid_chars for c in seed)


def decrypt_seed(encrypted_seed_b64: str, private_key: RSAPrivateKey) -> str:
    """
    Decrypt base64-encoded encrypted seed using RSA/OAEP with SHA-256.

    Returns:
        hex seed (64-character string)

    Raises:
        ValueError if decryption fails or seed is invalid.
    """
    try:
        # 1. Base64 decode
        ciphertext = base64.b64decode(encrypted_seed_b64)
    except Exception as e:
        raise ValueError(f"Base64 decode failed: {e}")

    try:
        # 2. RSA/OAEP decrypt with SHA-256 + MGF1(SHA-256)
        plaintext_bytes = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
    except Exception as e:
        raise ValueError(f"RSA decryption failed: {e}")

    try:
        # 3. Decode UTF-8 string
        seed_str = plaintext_bytes.decode("utf-8").strip()
    except Exception as e:
        raise ValueError(f"UTF-8 decode failed: {e}")

    # 4. Validate hex seed
    if not is_valid_hex_seed(seed_str):
        raise ValueError("Decrypted value is not a valid 64-character hex seed.")

    return seed_str


def save_seed_to_file(seed: str, path: Path):
    """
    Save the hex seed string to a file (creating parent directory if needed).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(seed, encoding="utf-8")
