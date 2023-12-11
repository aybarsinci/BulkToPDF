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
            self.view.display_error("Please select both input and output directories.")  #display_error method for errors
            return
        self.view.display_info("Converting...")  # display_info method for normal messages
        threading.Thread(target=self.convert, daemon=True).start()

    def convert(self):
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            errors_occurred = False  # Flag to indicate if any errors occurred

            for root, dirs, files in os.walk(self.input_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        # This assumes process_file raises exceptions on failure
                        process_file(file_path, self.input_dir, self.output_dir)
                    except Exception as e:
                        errors_occurred = True
                        # Schedule the error display to run on the main thread
                        self.view.after(0, self.view.display_error, f"Error converting {file}: {e}")
                        break  # Remove this if you want to continue processing after an error

            if not errors_occurred:
                #the info display to run on the main thread
                self.view.after(0, self.view.display_info, "Conversion Completed")
            else:
                self.view.after(0, self.view.display_error, "Errors occurred during conversion. Check logs for details.")
        except Exception as e:
            #the error display to run on the main thread for any unexpected errors
            self.view.after(0, self.view.display_error, f"Unexpected error: {e}")


