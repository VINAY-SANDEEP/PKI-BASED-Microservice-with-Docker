import requests

API_URL = "http://localhost:8080/decrypt-seed"


def main():
    # 1. Read encrypted_seed.txt
    with open("encrypted_seed.txt", "r", encoding="utf-8") as f:
        encrypted_seed = f.read().strip()

    payload = {
        "encrypted_seed": encrypted_seed
    }

    print("Sending request to /decrypt-seed ...")
    try:
        resp = requests.post(API_URL, json=payload, timeout=10)
    except Exception as e:
        print("Request error:", e)
        return

    print("Status code:", resp.status_code)
    print("Response JSON:", resp.json())


if __name__ == "__main__":
    main()
