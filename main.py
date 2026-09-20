import sys
import ctypes
import tkinter as tk

from control_center.main_window import ControlCenter


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


if __name__ == "__main__":
    enable_high_dpi()
    root = ControlCenter()
    root.tk.call(
        "tk",
        "scaling",
        1.20
    )
    root.mainloop()