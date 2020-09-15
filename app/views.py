import os
import json

from flask import abort, render_template, request, jsonify
from werkzeug.utils import secure_filename

from app import app
from app.benford_chart import Chart, BenfordData, InvalidDataFormat
from app.constants import ALLOWED_EXTENSIONS

app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ALLOWED_EXTENSIONS


@app.errorhandler(413)
def too_large(e):
    return "File is too large", 413


@app.errorhandler(InvalidDataFormat)
def invalid_data(e):
    return jsonify(idf=str(e)), 400


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def upload_files():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            return "Invalid file extension", 400
        bfd = BenfordData(uploaded_file, file_ext).benford_data  # TODO warnings
        chart = Chart(data=bfd)
        return jsonify(found_values=list(chart.found.values()), expected_values=list(chart.expected.values()),
                       labels=list(chart.labels.values()))
    return '', 204
