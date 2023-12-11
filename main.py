# main.py

import tkinter as tk
from View.view import PDFConverterView
from Controller.controller import PDFConverterController

def main():
    root = tk.Tk()
    root.title("PDF Converter")

    controller = PDFConverterController(None)  # Initially pass None for the view
    view = PDFConverterView(master=root, controller=controller)
    controller.view = view  # Now set the view for the controller

    view.pack()
    root.mainloop()

if __name__ == "__main__":
    main()
