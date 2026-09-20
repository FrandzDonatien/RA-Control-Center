from tkinter import Tk
import sys
import ctypes
from ui.dashboard import Dashboard
from config import APP_TITLE


def enable_high_dpi():

    if sys.platform != "win32":
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)

    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

def main(self=None):
    enable_high_dpi()
    root = Tk()
    Dashboard(root)
    root.mainloop()


if __name__ == "__main__":
    main()
