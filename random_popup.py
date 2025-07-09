#!/usr/bin/env python3
import sys
import os
import json
import secrets
from PyQt5 import QtWidgets
from show_transparent import TransparentPopup

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
RESOURCES    = os.path.join(BASE_DIR, 'resources')
CONFIG_FILE  = os.path.join(RESOURCES, 'config.json')
IMAGES_FILE  = os.path.join(RESOURCES, 'images.json')


# ── Helpers ────────────────────────────────────────────────────────────────────
def load_json(path, description):
    if not os.path.isfile(path):
        print(f"Error: {description} not found at {path}")
        sys.exit(1)
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error: Failed to parse {description}: {e}")
        sys.exit(1)

def resolve_path(fn):
    return fn if os.path.isabs(fn) else os.path.join(RESOURCES, fn)

def choose_image_entry(images):
    if not images:
        print("Error: no images defined")
        sys.exit(1)
    # use secrets.choice for cryptographically strong randomness
    entry = secrets.choice(images)
    if 'filename' not in entry:
        print("Error: each image entry must have a 'filename' field")
        sys.exit(1)
    full = resolve_path(entry['filename'])
    if not os.path.exists(full):
        print(f"Error: image not found: {full}")
        sys.exit(1)
    return entry, full


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    # 1) load global display settings
    cfg = load_json(CONFIG_FILE, 'config.json')
    fade       = cfg.get('fade', 100)
    display_ms = cfg.get('display', 1000)
    max_h      = cfg.get('max_height', 0.25)
    anchor     = cfg.get('anchor', 'bottom-right')
    
    # 2) load per-image list
    images = load_json(IMAGES_FILE, 'images.json')
    entry, img_path = choose_image_entry(images)
    
    # 3) pull per-image margins (defaults to 0)
    margin_x = entry.get('margin_x', 0)
    margin_y = entry.get('margin_y', 0)
    
    # 4) fire up Qt and show
    app   = QtWidgets.QApplication(sys.argv)
    popup = TransparentPopup(
        img_path,
        fade=fade,
        display=display_ms,
        max_height=max_h,
        anchor=anchor,
        margin_x=margin_x,
        margin_y=margin_y
    )
    popup.show()
    popup.fade_in()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
