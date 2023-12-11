# view.py

import tkinter as tk
from tkinter import filedialog

class PDFConverterView(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        self.input_entry = tk.Entry(self, width=50)
        self.input_entry.grid(row=0, column=1)

        tk.Button(self, text="Browse Input", command=self.controller.browse_input).grid(row=0, column=2)

        self.output_entry = tk.Entry(self, width=50)
        self.output_entry.grid(row=1, column=1)

        tk.Button(self, text="Browse Output", command=self.controller.browse_output).grid(row=1, column=2)

        tk.Button(self, text="Convert", command=self.controller.start_conversion).grid(row=2, column=1, columnspan=2)

        self.status_label = tk.Label(self, text="")
        self.status_label.grid(row=3, column=0, columnspan=3)
