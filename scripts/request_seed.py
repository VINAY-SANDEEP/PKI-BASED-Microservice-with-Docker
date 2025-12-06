import json
import requests  # library to make HTTP POST request

# Instructor API URL (given in the assignment)
API_URL = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"


STUDENT_ID = "23MH1A4227" 
GITHUB_REPO_URL = "https://github.com/Saimanikantakoppireddy/pki-2fa-microservice.git"


def load_public_key_pem(path: str) -> str:
    """
    Read the student public key as text (PEM format).
    We keep the BEGIN/END lines as-is.
    """
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def request_seed(student_id: str, github_repo_url: str, api_url: str = API_URL):
    """
    Request encrypted seed from the instructor API and save it to encrypted_seed.txt
    """
    # 1. Read your public key content
    public_key_pem = load_public_key_pem("student_public.pem")

    # 2. Prepare request body
    payload = {
        "student_id": student_id,
        "github_repo_url": github_repo_url,
        "public_key": public_key_pem,
    }

    print("Sending request to instructor API...")
    try:
        response = requests.post(api_url, json=payload, timeout=20)
    except Exception as e:
        print("Error sending request:", e)
        return

    print("Status code:", response.status_code)

    if response.status_code != 200:
        print("Non-200 response:", response.text)
        return

    # 3. Parse JSON response
    try:
        data = response.json()
    except json.JSONDecodeError:
        print("Error: Response is not valid JSON")
        print("Raw response:", response.text)
        return

    # 4. Check status
    if data.get("status") != "success":
        print("API returned error:", data)
        return

    encrypted_seed = data.get("encrypted_seed")
    if not encrypted_seed:
        print("No 'encrypted_seed' in response:", data)
        return

    # 5. Save encrypted seed to file
    with open("encrypted_seed.txt", "w", encoding="utf-8") as f:
        f.write(encrypted_seed.strip())

    print("✅ Encrypted seed saved to encrypted_seed.txt")


if __name__ == "__main__":
    if STUDENT_ID == "YOUR_STUDENT_ID_HERE":
        print("❌ Please set STUDENT_ID in this script before running.")
    elif "your-username" in GITHUB_REPO_URL:
        print("❌ Please set GITHUB_REPO_URL in this script before running.")
    else:
        request_seed(STUDENT_ID, GITHUB_REPO_URL)
