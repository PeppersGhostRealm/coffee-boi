#!/usr/bin/env python3
"""
Tray-based runner script to periodically execute random_notify.py and random_popup.py.
Run this headless (no console) and you'll get a tray icon to exit the scheduler.
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

# Default configuration: minimum and maximum interval between runs (in seconds)
DEFAULT_MIN_INTERVAL = 300  # fallback if config load fails
DEFAULT_MAX_INTERVAL = 600  # fallback if config load fails

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
    """Launch both scripts in parallel and wait for them to finish."""
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
    """Main loop: run scripts, then sleep until next run or shutdown."""
    while not STOP_EVENT.is_set():
        run_both_scripts()
        interval = random.uniform(MIN_INTERVAL, MAX_INTERVAL)
        STOP_EVENT.wait(interval)


def on_exit(icon, item):
    """Callback to stop scheduler and remove tray icon."""
    STOP_EVENT.set()
    icon.stop()


def create_tray_icon():
    """Set up system tray icon with an Exit menu."""
    icon_path = os.path.join(script_dir, "resources", "icon.ico")
    if not os.path.exists(icon_path):
        img = Image.new("RGB", (64, 64), color=(0, 0, 0))
    else:
        img = Image.open(icon_path)

    menu = pystray.Menu(pystray.MenuItem("Exit", on_exit))
    tray = pystray.Icon("Scheduler", img, "CoffeeBoi", menu)
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
