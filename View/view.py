import tkinter as tk
from tkinter import ttk  # Import the ttk module for themed widgets

class PDFConverterView(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        self.style = ttk.Style()
        self.style.configure('TLabel', font=('Arial', 11))
        self.style.configure('TButton', font=('Arial', 11), padding=5)
        self.style.configure('TEntry', padding=5)

        ttk.Label(self, text="Input Directory:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.input_entry = ttk.Entry(self, width=50)
        self.input_entry.grid(row=0, column=1, padx=5, pady=5)

        button_width = 15  # Set a consistent width for both buttons
        browse_input_button = ttk.Button(self, text="Browse Input", command=self.controller.browse_input, width=button_width)
        browse_input_button.grid(row=0, column=2, padx=5, pady=5, sticky='ew')

        ttk.Label(self, text="Output Directory:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.output_entry = ttk.Entry(self, width=50)
        self.output_entry.grid(row=1, column=1, padx=5, pady=5)

        browse_output_button = ttk.Button(self, text="Browse Output", command=self.controller.browse_output, width=button_width)
        browse_output_button.grid(row=1, column=2, padx=5, pady=5, sticky='ew')

        convert_button = ttk.Button(self, text="Convert", command=self.controller.start_conversion)
        convert_button.grid(row=2, column=1, padx=5, pady=5)

        self.status_label = ttk.Label(self, text="", font=('Arial', 11))
        self.status_label.grid(row=3, column=0, columnspan=3, padx=5, pady=5)

    def display_error(self, message):
        """Displays an error message in the status label."""
        self.status_label.config(text=message, foreground='red')

    def display_info(self, message):
        """Displays a normal (non-error) message in the status label."""
        self.status_label.config(text=message, foreground='black')