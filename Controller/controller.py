# controller.py

import threading
from Model.model import process_file, convert_to_pdf
from tkinter import filedialog
from View.view import PDFConverterView
import tkinter as tk
import os

class PDFConverterController:
    def __init__(self, view):
        self.view = view
        self.input_dir = ''
        self.output_dir = ''

    def browse_input(self):
        self.input_dir = filedialog.askdirectory()
        if self.input_dir:
            self.view.input_entry.delete(0, tk.END)
            self.view.input_entry.insert(0, self.input_dir)

    def browse_output(self):
        self.output_dir = filedialog.askdirectory()
        if self.output_dir:
            self.view.output_entry.delete(0, tk.END)
            self.view.output_entry.insert(0, self.output_dir)

    def start_conversion(self):
        if not self.input_dir or not self.output_dir:
            self.view.status_label.config(text="Please select both input and output directories.")
            return
        self.view.status_label.config(text="Converting...")
        threading.Thread(target=self.convert, daemon=True).start()

    def convert(self):
        os.makedirs(self.output_dir, exist_ok=True)

        for root, dirs, files in os.walk(self.input_dir):
            for file in files:
                file_path = os.path.join(root, file)
                process_file(file_path, self.input_dir, self.output_dir)

        self.view.status_label.config(text="Conversion Completed")
