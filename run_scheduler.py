#!/usr/bin/env python3
"""
Tray-based runner script to periodically execute random_notify.py and random_popup.py.
Run this headless (no console) and you’ll get a tray icon to exit the scheduler.
"""
import time
import random
import subprocess
import sys
import os
import threading

import pystray
from PIL import Image

# Configuration: minimum and maximum interval between runs (in seconds)
MIN_INTERVAL = 6  # 5 minutes
MAX_INTERVAL = 6  # 10 minutes

# Event to signal shutdown
STOP_EVENT = threading.Event()


def run_both_scripts():
    """Launch both scripts in parallel and wait for them to finish."""
    base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    scripts = ["random_notify", "random_popup"]
    procs = []

    for name in scripts:
        exe = os.path.join(base_dir, name + (".exe" if os.name == "nt" else ""))
        script = os.path.join(base_dir, name + ".py")
        if os.path.exists(exe):
            cmd = [exe]
        elif os.path.exists(script):
            cmd = [sys.executable, script]
        else:
            print(f"[Error] Script not found: {name}", file=sys.stderr)
            continue
        try:
            proc = subprocess.Popen(cmd)
            procs.append(proc)
        except Exception as e:
            print(f"[Error] Failed to start {name}: {e}", file=sys.stderr)

    for proc in procs:
        proc.wait()


def scheduler_loop():
    """Main loop: run scripts, then sleep until next run or shutdown."""
    while not STOP_EVENT.is_set():
        run_both_scripts()
        interval = random.uniform(MIN_INTERVAL, MAX_INTERVAL)
        # Wait with possibility to exit early
        STOP_EVENT.wait(interval)


def on_exit(icon, item):
    """Callback to stop scheduler and remove tray icon."""
    STOP_EVENT.set()
    icon.stop()


def create_tray_icon():
    """Set up system tray icon with an Exit menu."""
    base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    icon_path = os.path.join(base_dir, "icon.ico")
    if not os.path.exists(icon_path):
        # Fallback: generate a simple blank image
        img = Image.new("RGB", (64, 64), color=(0, 0, 0))
    else:
        img = Image.open(icon_path)

    menu = pystray.Menu(pystray.MenuItem("Exit", on_exit))
    tray = pystray.Icon("Scheduler", img, "Runner", menu)
    return tray


def main():
    # Start scheduler thread
    t = threading.Thread(target=scheduler_loop, daemon=True)
    t.start()

    # Launch tray icon (blocks until icon.stop())
    tray_icon = create_tray_icon()
    tray_icon.run()


if __name__ == "__main__":
    main()
