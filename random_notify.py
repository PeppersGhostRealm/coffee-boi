#!/usr/bin/env python3
import json
import random
import subprocess
import sys
import os

def main():
    # Only run on Windows
    if sys.platform != "win32":
        print("This script only works on Windows.", file=sys.stderr)
        sys.exit(1)

    # Locate JSON file alongside this script
    base = os.path.dirname(os.path.realpath(__file__))
    json_path = os.path.join(base, "resources/notifications.json")

    # Load titles and messages
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            titles = data.get("titles", [])
            messages = data.get("messages", [])
    except Exception as e:
        print(f"Error loading {json_path}: {e}", file=sys.stderr)
        sys.exit(1)

    if not titles or not messages:
        print("JSON must contain non-empty 'titles' and 'messages' lists.", file=sys.stderr)
        sys.exit(1)

    # Pick one of each
    title = random.choice(titles)
    message = random.choice(messages)

    # Call notify.py (make sure it's named/located correctly)
    notify_script = os.path.join(base, "notify.py")
    try:
        subprocess.run(
            [sys.executable, notify_script, title, message],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Failed to send notification: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
