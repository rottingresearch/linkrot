import string
import re
import json
import os
from flask import Flask, flash, render_template, redirect, request, session, make_response, session, redirect, url_for, send_from_directory
import requests
from werkzeug.utils import secure_filename
import subprocess as sp
import linkrot

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp/'
app.secret_key = os.environ.get('APP_SECRET_KEY')

ALLOWED_EXTENSIONS = set(['pdf'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_form():
    return render_template('upload.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/', methods=['POST'])
def upload_pdf():
    website = request.form['text']
    if website:
        if website.endswith('.pdf'):
            metadata, refs = pdfdata(website)
            return render_template('analysis.html', meta_titles=list(metadata.keys()), meta_values=list(metadata.values()), pdfs=refs['pdf'], urls=refs['url'])
        else:
            return render_template('upload.html', flash='pdf')
    else:
        if 'file' not in request.files:
            return render_template('upload.html')
        file = request.files['file']
        if file.filename == '':
            return render_template('upload.html')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print(path)
            file.save(path)
            metadata, refs = pdfdata(path)
            os.remove(path)
            return render_template('analysis.html', meta_titles=list(metadata.keys()), meta_values=list(metadata.values()), pdfs=refs['pdf'], urls=refs['url'])
        else:
            return render_template('upload.html', flash='pdf')


def pdfdata(path):
    pdf = linkrot.linkrot(path)
    metadata = pdf.get_metadata()
    references_dict = pdf.get_references_as_dict()
    return metadata, references_dict


if __name__ == '__main__':
    app.run(debug=True, port=5000)
