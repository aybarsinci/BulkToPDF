import tkinter as tk
from View.view import PDFConverterView
from Controller.controller import PDFConverterController

def main():
    root = tk.Tk()
    root.title("PDF Converter")

    # Set a fixed window size
    root.geometry("600x180")  # Width x Height in pixels

    # Prevent resizing the window
    root.resizable(False, False)

    controller = PDFConverterController(None)  # Initially pass None for the view
    view = PDFConverterView(master=root, controller=controller)
    controller.view = view  # Now set the view for the controller

    view.pack(fill=tk.BOTH, expand=True)
    root.mainloop()

if __name__ == "__main__":
    main()
