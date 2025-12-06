import base64

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding



COMMIT_HASH = "f6cd3f783770fecd6a2e24d5799ca6f87f14ebd4"  


def load_private_key(path: str = "student_private.pem"):
    with open(path, "rb") as f:
        data = f.read()
    key = serialization.load_pem_private_key(data, password=None)
    return key


def load_public_key(path: str = "instructor_public.pem"):
    with open(path, "rb") as f:
        data = f.read()
    key = serialization.load_pem_public_key(data)
    return key


def sign_commit_hash(commit_hash: str, private_key) -> bytes:
    """
    Sign commit hash using RSA-PSS with SHA-256.
    IMPORTANT: sign the ASCII string, not binary!
    """
    message_bytes = commit_hash.encode("utf-8")
    signature = private_key.sign(
        message_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )
    return signature


def encrypt_with_instructor_key(data: bytes, public_key) -> bytes:
    """
    Encrypt data (signature) using RSA/OAEP with SHA-256.
    """
    ciphertext = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return ciphertext


def main():
    if COMMIT_HASH == "PASTE_YOUR_COMMIT_HASH_HERE":
        print("❌ Please set COMMIT_HASH at the top of this file.")
        return

    print(f"Using commit hash: {COMMIT_HASH}")

    # 1. Load keys
    student_private = load_private_key("student_private.pem")
    instructor_public = load_public_key("instructor_public.pem")

    # 2. Sign commit hash with student private key (RSA-PSS-SHA256)
    signature = sign_commit_hash(COMMIT_HASH, student_private)

    # 3. Encrypt signature with instructor public key (RSA-OAEP-SHA256)
    encrypted_signature = encrypt_with_instructor_key(signature, instructor_public)

    # 4. Base64 encode the encrypted signature (single line!)
    proof_b64 = base64.b64encode(encrypted_signature).decode("utf-8")

    print("\n==== COMMIT PROOF ====")
    print(f"Commit Hash: {COMMIT_HASH}")
    print("Encrypted Signature (Base64, single line):")
    print(proof_b64)
    print("======================\n")



if __name__ == "__main__":
    main()
