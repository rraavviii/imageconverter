from flask import Flask, render_template, request, flash, send_file, redirect, url_for
from PIL import Image, ImageOps
from fpdf import FPDF
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/edit', methods=['POST'])
def edit():
    if 'files' not in request.files:
        flash('No file part')
        return redirect(request.url)

    files = request.files.getlist('files')
    operation = request.form.get('operation')

    if not files or not operation:
        flash('No file selected or operation not chosen')
        return redirect(request.url)

    uploaded_files = []
    for file in files:
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        uploaded_files.append(filepath)

    if operation == 'cpng':
        return convert_to_format(uploaded_files, 'PNG')
    elif operation == 'cgray':
        return convert_to_grayscale(uploaded_files)
    elif operation == 'cwebp':
        return convert_to_format(uploaded_files, 'WEBP')
    elif operation == 'cjpg':
        return convert_to_format(uploaded_files, 'JPEG')
    elif operation == 'multiple_to_pdf':
        return convert_multiple_to_pdf(uploaded_files)
    else:
        flash('Invalid operation selected')
        return redirect(request.url)

def convert_to_format(filepaths, format):
    converted_files = []
    for filepath in filepaths:
        image = Image.open(filepath)
        output_path = os.path.join(RESULT_FOLDER, os.path.splitext(os.path.basename(filepath))[0] + f".{format.lower()}")
        image.save(output_path, format=format)
        converted_files.append(output_path)
    flash('Files converted successfully!')
    return serve_files_as_zip(converted_files)

def convert_to_grayscale(filepaths):
    converted_files = []
    for filepath in filepaths:
        image = Image.open(filepath)
        gray_image = ImageOps.grayscale(image)
        output_path = os.path.join(RESULT_FOLDER, os.path.splitext(os.path.basename(filepath))[0] + "_gray.jpg")
        gray_image.save(output_path)
        converted_files.append(output_path)
    flash('Files converted to grayscale successfully!')
    return serve_files_as_zip(converted_files)

def convert_multiple_to_pdf(filepaths):
    pdf = FPDF()
    for filepath in filepaths:
        image = Image.open(filepath)
        image = image.convert('RGB')
        output_path = os.path.join(RESULT_FOLDER, "merged.pdf")
        pdf.add_page()
        pdf.image(filepath, x=10, y=10, w=190)
    pdf.output(output_path)
    flash('Images combined into PDF successfully!')
    return send_file(output_path, as_attachment=True)

def serve_files_as_zip(filepaths):
    import zipfile
    zip_path = os.path.join(RESULT_FOLDER, "converted_files.zip")
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for filepath in filepaths:
            zipf.write(filepath, os.path.basename(filepath))
    return send_file(zip_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
