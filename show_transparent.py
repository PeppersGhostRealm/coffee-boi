# show_transparent.py
#!/usr/bin/env python3
import sys
import ctypes
import argparse
from PyQt5 import QtWidgets, QtGui, QtCore

# Default configuration constants
FADE_TIME_MS      = 500       # Fade-in/out duration in milliseconds
DISPLAY_TIME_MS   = 5000      # Time to display fully opaque before fading out
MAX_HEIGHT_RATIO  = 0.3       # Maximum image height as a fraction of screen height
ANCHOR            = 'bottom-right'  # Options: bottom-right, bottom-left, top-right, top-left, center
MARGIN_X          = 400
MARGIN_Y          = 0
POSITION_X        = None      # Override absolute X coordinate
POSITION_Y        = None      # Override absolute Y coordinate


class TransparentPopup(QtWidgets.QWidget):
    def __init__(
        self,
        image_path,
        fade: int         = None,
        display: int      = None,
        max_height: float = None,
        anchor: str       = None,
        margin_x: int     = None,
        margin_y: int     = None
    ):
        super().__init__()

        # override module-level defaults if provided
        global FADE_TIME_MS, DISPLAY_TIME_MS, MAX_HEIGHT_RATIO, ANCHOR, MARGIN_X, MARGIN_Y
        if fade        is not None: FADE_TIME_MS     = fade
        if display     is not None: DISPLAY_TIME_MS  = display
        if max_height  is not None: MAX_HEIGHT_RATIO = max_height
        if anchor      is not None: ANCHOR           = anchor
        if margin_x    is not None: MARGIN_X         = margin_x
        if margin_y    is not None: MARGIN_Y         = margin_y

        # Always-on-top, frameless, per-pixel transparent window
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint
            | QtCore.Qt.Tool
            | QtCore.Qt.WindowStaysOnTopHint
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # Screen geometry & scaled image
        screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
        max_h_px = int(screen.height() * MAX_HEIGHT_RATIO)

        pixmap = QtGui.QPixmap(image_path)
        if pixmap.isNull():
            raise FileNotFoundError(f"Could not load image: {image_path}")
        if pixmap.height() > max_h_px:
            pixmap = pixmap.scaledToHeight(max_h_px, QtCore.Qt.SmoothTransformation)

        label = QtWidgets.QLabel(self)
        label.setPixmap(pixmap)
        self.resize(pixmap.size())

        # position calculation
        if POSITION_X is not None or POSITION_Y is not None:
            x = POSITION_X if POSITION_X is not None else screen.x() + (screen.width() - self.width()) // 2
            y = POSITION_Y if POSITION_Y is not None else screen.y() + (screen.height() - self.height()) // 2
        else:
            # horizontal
            if ANCHOR in ('bottom-right', 'top-right'):
                anchor_x = screen.x() + screen.width() - MARGIN_X
            elif ANCHOR in ('bottom-left', 'top-left'):
                anchor_x = screen.x() + MARGIN_X
            else:
                anchor_x = screen.x() + screen.width() // 2
            x = int(anchor_x - self.width() / 2)

            # vertical
            if ANCHOR in ('bottom-right', 'bottom-left'):
                y = screen.y() + screen.height() - self.height() - MARGIN_Y
            elif ANCHOR in ('top-right', 'top-left'):
                y = screen.y() + MARGIN_Y
            else:
                y = screen.y() + (screen.height() - self.height()) // 2

        self.move(x, y)

        # opacity animation
        self.anim = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(FADE_TIME_MS)

    def showEvent(self, event):
        super().showEvent(event)
        self.raise_()
        self.activateWindow()
        if sys.platform.startswith('win'):
            self._place_under_taskbar()

    def _place_under_taskbar(self):
        user32 = ctypes.WinDLL('user32', use_last_error=True)
        SetWindowPos = user32.SetWindowPos
        SWP_NOMOVE     = 0x0002
        SWP_NOSIZE     = 0x0001
        SWP_NOACTIVATE = 0x0010
        SWP_SHOWWINDOW = 0x0040
        HWND_TOPMOST   = -1
        hwnd = int(self.winId())
        SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                     SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW)

        taskbar = user32.FindWindowW("Shell_TrayWnd", None)
        if taskbar:
            SetWindowPos(taskbar, HWND_TOPMOST, 0, 0, 0, 0,
                         SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW)

    def fade_in(self):
        self.anim.stop()
        self.setWindowOpacity(0.0)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.start()
        QtCore.QTimer.singleShot(FADE_TIME_MS + DISPLAY_TIME_MS, self.fade_out)

    def fade_out(self):
        self.anim.stop()
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.0)
        self.anim.start()
        QtCore.QTimer.singleShot(FADE_TIME_MS, QtWidgets.QApplication.instance().quit)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Show a transparent popup with CLI-controlled parameters."
    )
    parser.add_argument('image', help="PNG image path.")
    parser.add_argument('--fade', type=int, default=None,
                        help="Fade duration in ms (overrides default)")
    parser.add_argument('--display', type=int, default=None,
                        help="Full-opacity display time in ms")
    parser.add_argument('--max-height', type=float, default=None,
                        help="Max image height fraction")
    parser.add_argument('--anchor',
                        choices=['bottom-right','bottom-left','top-right','top-left','center'],
                        default=None, help="Anchor position")
    parser.add_argument('--margin-x', type=int, default=None,
                        help="Horizontal margin")
    parser.add_argument('--margin-y', type=int, default=None,
                        help="Vertical margin")
    parser.add_argument('--pos-x', type=int, default=None,
                        help="Absolute X coordinate override.")
    parser.add_argument('--pos-y', type=int, default=None,
                        help="Absolute Y coordinate override.")
    args = parser.parse_args()

    # apply CLI-only position overrides
    if args.pos_x is not None:  POSITION_X = args.pos_x
    if args.pos_y is not None:  POSITION_Y = args.pos_y

    app = QtWidgets.QApplication(sys.argv)
    popup = TransparentPopup(
        args.image,
        fade=args.fade,
        display=args.display,
        max_height=args.max_height,
        anchor=args.anchor,
        margin_x=args.margin_x,
        margin_y=args.margin_y
    )
    popup.show()
    popup.fade_in()
    sys.exit(app.exec_())
