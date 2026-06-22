"""Local OpenAI API key tester.

Usage:
1. Create a file named `openai_keys.txt` in the project root (one key per line).
2. Install `requests` in your virtualenv if missing: `pip install requests`.
3. Run: `python backend/test_openai_keys.py`

This script checks each key by calling the OpenAI Models endpoint.
It runs locally only and does NOT send keys anywhere else.
Remove `openai_keys.txt` after testing to keep keys safe.
"""

import os
import sys
import time
from typing import List

try:
    import requests
except Exception:
    print("Please install 'requests' in your virtualenv: pip install requests")
    sys.exit(1)


KEYS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "openai_keys.txt")
API_URL = "https://api.openai.com/v1/models"


def mask_key(key: str) -> str:
    key = key.strip()
    if len(key) < 10:
        return key
    return f"{key[:6]}...{key[-4:]}"


def load_keys(path: str) -> List[str]:
    if not os.path.exists(path):
        print(f"Keys file not found: {path}")
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def test_key(key: str) -> tuple[bool, str]:
    try:
        headers = {"Authorization": f"Bearer {key}", "User-Agent": "cravehub-key-tester/1.0"}
        resp = requests.get(API_URL, headers=headers, timeout=10)
        if resp.status_code == 200:
            return True, "OK"
        try:
            body = resp.json()
            msg = body.get("error", {}).get("message") or str(body)
        except Exception:
            msg = resp.text or f"status {resp.status_code}"
        return False, f"{resp.status_code} {msg}"
    except Exception as exc:
        return False, str(exc)


def main():
    keys = load_keys(KEYS_FILE)
    if not keys:
        print("No keys to test. Create openai_keys.txt with one key per line at the repo root.")
        return

    print(f"Testing {len(keys)} key(s) from {KEYS_FILE}")
    for i, key in enumerate(keys, 1):
        masked = mask_key(key)
        print(f"[{i}/{len(keys)}] Testing {masked} ...", end=" ")
        ok, info = test_key(key)
        print("OK" if ok else "FAIL", "-", info)
        # short delay to avoid rate limits
        time.sleep(0.5)

    print("Done. Remove openai_keys.txt when finished to keep keys secure.")


if __name__ == "__main__":
    main()
