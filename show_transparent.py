#!/usr/bin/env python3
import sys
import os
import ctypes
from PyQt5 import QtWidgets, QtGui, QtCore

# Configuration constants
FADE_TIME_MS = 500       # Fade-in/out duration in milliseconds
DISPLAY_TIME_MS = 5000   # Time to display fully opaque before fading out

# Position configuration
ANCHOR = 'bottom-right'
MARGIN_X = 400
MARGIN_Y = 0
POSITION_X = None
POSITION_Y = None

class TransparentPopup(QtWidgets.QWidget):
    def __init__(self, image_path):
        super().__init__()
        # Add WindowStaysOnTopHint to ensure always-on-top behavior
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint
            | QtCore.Qt.Tool
            | QtCore.Qt.WindowStaysOnTopHint
        )
        # Enable per-pixel transparency
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # Load the image
        pixmap = QtGui.QPixmap(image_path)
        if pixmap.isNull():
            raise FileNotFoundError(f"Could not load image: {image_path}")

        # Display it in a label
        label = QtWidgets.QLabel(self)
        label.setPixmap(pixmap)
        self.resize(pixmap.size())

        # Determine window position
        screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
        if ANCHOR == 'bottom-right':
            x = screen.x() + screen.width() - self.width() - MARGIN_X
            y = screen.y() + screen.height() - self.height() - MARGIN_Y
        elif ANCHOR == 'bottom-left':
            x = screen.x() + MARGIN_X
            y = screen.y() + screen.height() - self.height() - MARGIN_Y
        elif ANCHOR == 'top-right':
            x = screen.x() + screen.width() - self.width() - MARGIN_X
            y = screen.y() + MARGIN_Y
        elif ANCHOR == 'top-left':
            x = screen.x() + MARGIN_X
            y = screen.y() + MARGIN_Y
        else:
            x = POSITION_X if POSITION_X is not None else screen.x() + (screen.width() - self.width()) // 2
            y = POSITION_Y if POSITION_Y is not None else screen.y() + (screen.height() - self.height()) // 2
        self.move(x, y)

        # Prepare opacity animation
        self.anim = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(FADE_TIME_MS)

    def showEvent(self, event):
        super().showEvent(event)
        # Raise and activate window, then ensure it's above all others
        self.raise_()
        self.activateWindow()
        if sys.platform.startswith('win'):
            self._place_under_taskbar()

    def _place_under_taskbar(self):
        user32 = ctypes.WinDLL('user32', use_last_error=True)
        SetWindowPos = user32.SetWindowPos
        SWP_NOMOVE = 0x0002
        SWP_NOSIZE = 0x0001
        SWP_NOACTIVATE = 0x0010
        SWP_SHOWWINDOW = 0x0040
        HWND_TOPMOST = -1

        hwnd = int(self.winId())
        # Make our window topmost and show it
        SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                     SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW)
        # Then re-assert taskbar above our window
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
        total_delay = FADE_TIME_MS + DISPLAY_TIME_MS
        QtCore.QTimer.singleShot(total_delay, self.fade_out)

    def fade_out(self):
        self.anim.stop()
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.0)
        self.anim.start()
        QtCore.QTimer.singleShot(FADE_TIME_MS, QtWidgets.QApplication.instance().quit)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} path/to/image.png")
        sys.exit(1)

    app = QtWidgets.QApplication(sys.argv)
    popup = TransparentPopup(sys.argv[1])
    popup.show()
    popup.fade_in()
    sys.exit(app.exec_())
