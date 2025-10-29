import tkinter as tk

from bulktopdf.config import CONFIG
from bulktopdf.logging_utils import configure_logging
from bulktopdf.ui.controller import PDFConverterController
from bulktopdf.ui.view import PDFConverterView

try:
    from tkinterdnd2 import TkinterDnD  # type: ignore
except ImportError:
    TkinterDnD = None


def main():
    configure_logging()
    if TkinterDnD is not None:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    root.title(CONFIG.ui.title)

    # Set a fixed window size
    root.geometry(f"{CONFIG.ui.window_width}x{CONFIG.ui.window_height}")

    # Prevent resizing the window
    root.resizable(False, False)

    controller = PDFConverterController(None)  # Initially pass None for the view
    view = PDFConverterView(master=root, controller=controller)
    controller.view = view  # Now set the view for the controller

    view.pack(fill=tk.BOTH, expand=True)
    root.mainloop()

if __name__ == "__main__":
    main()
