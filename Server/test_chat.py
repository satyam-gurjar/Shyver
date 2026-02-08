#!/usr/bin/env python3
"""
Simple CLI test client for the FastAPI /chat endpoint.
Run the server first:
  uvicorn app.main:app --reload
Then run this script:
  python3 test_chat.py
"""

import json
import os
import sys
from urllib import request as urlrequest
from urllib.error import HTTPError, URLError

API_URL = os.getenv("CHAT_API_URL", "http://localhost:8000/chat")


def post_message(session_id: str, message: str) -> str:
    payload = json.dumps({"session_id": session_id, "message": message}).encode("utf-8")
    req = urlrequest.Request(
        API_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlrequest.urlopen(req, timeout=120) as resp:
            body = resp.read().decode("utf-8")
            data = json.loads(body)
            return data.get("response", "")
    except HTTPError as exc:
        err_body = exc.read().decode("utf-8") if exc.fp else ""
        raise RuntimeError(f"HTTP {exc.code}: {err_body}") from exc
    except URLError as exc:
        raise RuntimeError(f"Connection error: {exc}") from exc


def main() -> int:
    print(f"Using API: {API_URL}")
    session_id = input("Session ID (default: test-session): ").strip() or "test-session"
    print("Type your message. Press Enter on empty line to quit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not user_input:
            print("Exiting.")
            break

        try:
            reply = post_message(session_id, user_input)
            print(f"Bot: {reply}\n")
        except RuntimeError as exc:
            print(f"Error: {exc}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
