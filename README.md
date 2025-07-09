# Coffee Boi

Small Windows utility that periodically shows a notification and an image popup.

## Running from source

Install dependencies (requires Python 3):

```bash
pip install -r requirements.txt
```

Run the scheduler:

```bash
python run_scheduler.py
```

## Building standalone executables

Use [PyInstaller](https://www.pyinstaller.org/) on Windows to create portable
executables. Each script is built separately and the scheduler will look for
`*.exe` files first.

Example commands:

```bat
pyinstaller --onefile --noconsole notify.py
pyinstaller --onefile --noconsole --add-data "resources;resources" random_notify.py
pyinstaller --onefile --noconsole --add-data "resources;resources" random_popup.py
pyinstaller --onefile --noconsole run_scheduler.py
```

After building, distribute the generated `.exe` files found in the `dist`
directory. Your friend only needs these executables to run the program.
