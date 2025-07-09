#!/usr/bin/env python3
import argparse
from win10toast import ToastNotifier
import sys

def main():
    parser = argparse.ArgumentParser(
        description="Send a Windows toast notification."
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
    parser.add_argument(
        "--duration",
        type=int,
        default=5,
        help="How many seconds to display the notification (default: 5)"
    )
    args = parser.parse_args()

    # Join the list of message words into a single string
    message = " ".join(args.message)

    toaster = ToastNotifier()
    toaster.show_toast(
        args.title,
        message,
        duration=args.duration,
        threaded=False
    )

if __name__ == "__main__":
    # guard for Windows-only
    if sys.platform != "win32":
        print("This script only works on Windows.", file=sys.stderr)
        sys.exit(1)
    main()
