from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


def generate_rsa_keypair(key_size: int = 4096):
    """
    Generate RSA key pair with 4096 bits and public exponent 65537.
    Returns (private_key, public_key).
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )
    public_key = private_key.public_key()
    return private_key, public_key


def save_keys(private_key, public_key,
              private_file="student_private.pem",
              public_file="student_public.pem"):
    """
    Save private and public keys to PEM files.
    Private key unencrypted as required by assignment.
    """
    # Save private key
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    with open(private_file, "wb") as f:
        f.write(private_bytes)

    # Save public key
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    with open(public_file, "wb") as f:
        f.write(public_bytes)

    print("Keys generated successfully:")
    print(f"- Private key: {private_file}")
    print(f"- Public key: {public_file}")


if __name__ == "__main__":
    priv, pub = generate_rsa_keypair()
    save_keys(priv, pub)
