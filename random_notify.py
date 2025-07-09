#!/usr/bin/env python3
import json
import random
import subprocess
import sys
import os


def resource_path(relative: str) -> str:
    """Return absolute path to resource, compatible with PyInstaller."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)

def main():
    # Only run on Windows
    if sys.platform != "win32":
        print("This script only works on Windows.", file=sys.stderr)
        sys.exit(1)

    # Locate JSON file alongside this script (handles PyInstaller)
    json_path = resource_path("resources/notifications.json")

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

    # Call notify.py/notify.exe from the same directory
    base_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    exe_path = os.path.join(base_dir, "notify.exe") if os.name == "nt" else None
    script_path = os.path.join(base_dir, "notify.py")

    if exe_path and os.path.exists(exe_path):
        cmd = [exe_path, title, message]
    else:
        cmd = [sys.executable, script_path, title, message]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to send notification: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
