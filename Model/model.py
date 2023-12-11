# model.py

import os
import shutil
import comtypes.client
from urllib.parse import unquote


def convert_to_pdf(input_file, output_file):
    file_type = os.path.splitext(input_file)[1].lower()
    app = None

    try:
        if file_type in ['.doc', '.docx']:
            app = comtypes.client.CreateObject('Word.Application')
            app.DisplayAlerts = False
            doc = app.Documents.Open(input_file)
            doc.SaveAs(output_file, FileFormat=17)
            doc.Close()
        elif file_type in ['.xls', '.xlsx']:
            app = comtypes.client.CreateObject('Excel.Application')
            app.DisplayAlerts = False
            doc = app.Workbooks.Open(input_file)
            doc.ExportAsFixedFormat(0, output_file)
            doc.Close()
    except Exception as e:
        print(f"Error converting {input_file}: {str(e)}")
    finally:
        if app is not None:
            app.Quit()


def process_file(file_path, input_dir, output_dir):
    file_path = os.path.normpath(unquote(file_path))

    if os.path.basename(file_path) == '.DS_Store':
        print(f"Skipping system file: {file_path}")
        return

    relative_path = os.path.relpath(file_path, start=input_dir)
    output_file_path = os.path.normpath(os.path.join(output_dir, os.path.splitext(relative_path)[0] + '.pdf'))

    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    print(f"Starting processing of {file_path}")  # Log reading the file
    if os.path.splitext(file_path)[1].lower() in ['.doc', '.docx', '.xls', '.xlsx']:
        convert_to_pdf(file_path, output_file_path)
    elif os.path.splitext(file_path)[1].lower() == '.pdf':
        shutil.copy2(file_path, output_file_path)
    print(f"Saved converted file to {output_file_path}")  # Log saving the file
