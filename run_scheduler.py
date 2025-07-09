#!/usr/bin/env python3
"""
Tray-based runner script to periodically execute random_notify.py and random_popup.py,
with a Snooze menu (15 min, 30 min, 1 hr) plus Exit.
"""
import time
import random
import subprocess
import sys
import os
import threading
import json

import pystray
from PIL import Image

# Default configuration: fallback intervals in seconds
DEFAULT_MIN_INTERVAL = 300   # 5 minutes
DEFAULT_MAX_INTERVAL = 600   # 10 minutes

# Global snooze timestamp (epoch seconds). If now < SNOOZE_UNTIL, scheduler will sleep instead of running.
SNOOZE_UNTIL = 0

# Load interval settings from resources/config.json
script_dir = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(script_dir, "resources", "config.json")
try:
    with open(config_path, 'r', encoding='utf-8') as cfg_file:
        cfg = json.load(cfg_file)
        MIN_INTERVAL = float(cfg.get('min_interval', DEFAULT_MIN_INTERVAL))
        MAX_INTERVAL = float(cfg.get('max_interval', DEFAULT_MAX_INTERVAL))
except Exception as e:
    print(f"[Warning] Could not load config.json ({e}); using default intervals.", file=sys.stderr)
    MIN_INTERVAL = DEFAULT_MIN_INTERVAL
    MAX_INTERVAL = DEFAULT_MAX_INTERVAL

# Event to signal shutdown
STOP_EVENT = threading.Event()


def run_both_scripts():
    """Launch random_notify.py and random_popup.py in parallel."""
    scripts = ["random_notify.py", "random_popup.py"]
    procs = []
    for script in scripts:
        path = os.path.join(script_dir, script)
        if not os.path.exists(path):
            print(f"[Error] Script not found: {path}", file=sys.stderr)
            continue
        try:
            proc = subprocess.Popen([sys.executable, path])
            procs.append(proc)
        except Exception as e:
            print(f"[Error] Failed to start {script}: {e}", file=sys.stderr)
    for proc in procs:
        proc.wait()


def scheduler_loop():
    """Main loop: respect snooze, then run scripts, then wait a random interval."""
    global SNOOZE_UNTIL
    while not STOP_EVENT.is_set():
        now = time.time()
        # If we're snoozed, sleep until snooze expires
        if now < SNOOZE_UNTIL:
            wait_time = SNOOZE_UNTIL - now
            STOP_EVENT.wait(wait_time)
            SNOOZE_UNTIL = 0
            continue

        # Otherwise run the scripts
        run_both_scripts()

        # Then sleep a random interval before next run
        interval = random.uniform(MIN_INTERVAL, MAX_INTERVAL)
        STOP_EVENT.wait(interval)


def snooze(minutes):
    """Pause all notifications for `minutes`."""
    global SNOOZE_UNTIL
    SNOOZE_UNTIL = time.time() + minutes * 60
    print(f"[Info] Snoozed for {minutes} minutes.")


def on_exit(icon, item):
    """Stop scheduler and remove tray icon."""
    STOP_EVENT.set()
    icon.stop()


def create_tray_icon():
    """Set up system tray icon with Snooze options and Exit."""
    icon_path = os.path.join(script_dir, "resources", "icon.ico")
    if os.path.exists(icon_path):
        img = Image.open(icon_path)
    else:
        img = Image.new("RGB", (64, 64), color=(0, 0, 0))

    menu = pystray.Menu(
        pystray.MenuItem("Snooze 15 min", lambda icon, item: snooze(15)),
        pystray.MenuItem("Snooze 30 min", lambda icon, item: snooze(30)),
        pystray.MenuItem("Snooze 1 hr",   lambda icon, item: snooze(60)),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Exit", on_exit)
    )
    tray = pystray.Icon("CoffeeBoi", img, "CoffeeBoi", menu)
    return tray


def main():
    # Start the scheduler in a background thread
    t = threading.Thread(target=scheduler_loop, daemon=True)
    t.start()

    # Run the tray icon (blocks until icon.stop())
    tray_icon = create_tray_icon()
    tray_icon.run()


if __name__ == "__main__":
    main()
