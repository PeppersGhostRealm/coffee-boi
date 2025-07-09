#!/usr/bin/env python3
import sys
import os
import json
import random
from PyQt5 import QtWidgets

# -- Configuration --
# Resources directory (where images.json and image files live)
RESOURCES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources')
# Path to JSON file listing image paths (one array of strings)
CONFIG_FILE = os.path.join(RESOURCES_DIR, 'images.json')

# Ensure the show_transparent script is in the same directory
# and named show_transparent.py
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

try:
    from show_transparent import TransparentPopup
except ImportError:
    print("Error: Could not import TransparentPopup. Make sure 'show_transparent.py' exists in the same directory.")
    sys.exit(1)


def load_image_list(config_path):
    if not os.path.exists(config_path):
        print(f"Error: Config file not found: {config_path}")
        sys.exit(1)
    try:
        with open(config_path, 'r') as f:
            data = json.load(f)
    except (ValueError, json.JSONDecodeError) as e:
        print(f"Error: Failed to parse JSON: {e}")
        sys.exit(1)

    if not isinstance(data, list) or not all(isinstance(p, str) for p in data):
        print("Error: JSON must be an array of image-path strings.")
        sys.exit(1)
    return data


def resolve_path(image_path):
    # If path is absolute, use it; otherwise, look inside resources directory
    if os.path.isabs(image_path):
        return image_path
    return os.path.join(RESOURCES_DIR, image_path)


def choose_image(images):
    if not images:
        print("Error: No images in list.")
        sys.exit(1)
    choice = random.choice(images)
    full_path = resolve_path(choice)
    if not os.path.exists(full_path):
        print(f"Error: Selected image does not exist: {full_path}")
        sys.exit(1)
    return full_path


def main():
    config_path = CONFIG_FILE
    if len(sys.argv) > 1:
        # allow overriding config path via arg, still relative to resources if not absolute
        arg_path = sys.argv[1]
        config_path = arg_path if os.path.isabs(arg_path) else os.path.join(RESOURCES_DIR, arg_path)

    image_list = load_image_list(config_path)
    img_path = choose_image(image_list)

    app = QtWidgets.QApplication(sys.argv)
    popup = TransparentPopup(img_path)
    popup.show()
    popup.fade_in()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
