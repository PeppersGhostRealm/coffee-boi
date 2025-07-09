#!/usr/bin/env python3
import argparse
import os
import sys
from winotify import Notification

def main():
    parser = argparse.ArgumentParser(
        description="Send a Windows toast notification as CoffeeBoi (short only)."
    )
    parser.add_argument(
        "title",
        help="Title of the notification"
    )
    parser.add_argument(
        "message",
        nargs="+",
        help="Message body of the notification"
    )
    args = parser.parse_args()

    # Combine the message words into one string
    message = " ".join(args.message)

    # Locate your custom icon
    icon_path = os.path.join(
        os.path.dirname(__file__),
        "resources",
        "icon.ico"
    )
    if not os.path.isfile(icon_path):
        print(f"🚨 Icon not found: {icon_path}", file=sys.stderr)
        sys.exit(1)

    # Fire off the toast with a short duration (~7s)
    toast = Notification(
        app_id="CoffeeBoi",   # shows up as the app name
        title=args.title,
        msg=message,
        icon=icon_path,
        duration="short"      # fixed to short
    )
    toast.show()

if __name__ == "__main__":
    if sys.platform != "win32":
        print("This script only works on Windows.", file=sys.stderr)
        sys.exit(1)
    main()
