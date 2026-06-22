import requests
import os

BASE_URL = "http://localhost:8000/api"

# 1. Register or Login
mobile = "9999999999"

# Send OTP
print("Sending OTP...")
res = requests.post(f"{BASE_URL}/register/mobile/", json={"mobile_number": mobile})
if res.status_code == 409: # Already registered
    print("Already registered. Logging in...")
    requests.post(f"{BASE_URL}/login/mobile/", json={"mobile_number": mobile})
    res = requests.post(f"{BASE_URL}/login/verify-otp/", json={"mobile_number": mobile, "otp": "123456"})
else:
    print("Registering...")
    res = requests.post(f"{BASE_URL}/register/verify-otp/", json={"mobile_number": mobile, "otp": "123456"})
    if res.status_code == 200:
        res = requests.post(f"{BASE_URL}/register/complete/", json={
            "mobile_number": mobile, "full_name": "Test User", "device_type": "web"
        })

if res.status_code not in [200, 201]:
    print("Auth failed:", res.text)
    exit(1)

data = res.json()
token = data.get("data", {}).get("access") or data.get("data", {}).get("tokens", {}).get("access")

if not token:
    print("No token found in response:", data)
    exit(1)

print("Got token.")

# 2. Upload Profile Image
print("Uploading image...")
headers = {"Authorization": f"Bearer {token}"}
files = {"avatar": ("test.jpg", b"fake_image_data", "image/jpeg")}

res = requests.put(f"{BASE_URL}/profile/update/", headers=headers, files=files)
print("Upload status:", res.status_code)
print("Upload response:", res.text)

# 3. Check profile
res = requests.get(f"{BASE_URL}/profile/", headers=headers)
print("Profile status:", res.status_code)
print("Profile response:", res.text)
