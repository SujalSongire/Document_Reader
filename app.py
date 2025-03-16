from flask import Flask, render_template, request, jsonify, send_file
import fitz  # PyMuPDF for PDF text extraction
import os
import logging
import pyttsx3
from werkzeug.utils import secure_filename
from docx import Document

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
logging.basicConfig(level=logging.INFO)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(file.filename))
    file.save(file_path)
    logging.info(f"File uploaded: {file.filename}")

    try:
        extracted_text = extract_text(file_path)
        if not extracted_text.strip():
            return jsonify({"error": "No text found in document"}), 400

        audio_file = generate_audio(extracted_text, file.filename)
        return jsonify({"text": extracted_text, "audio": f"/get_audio/{audio_file}"})

    except Exception as e:
        logging.error(f"Error extracting text: {e}")
        return jsonify({"error": "Failed to extract text"}), 500


def extract_text(file_path):
    text = ""
    if file_path.endswith(".pdf"):
        doc = fitz.open(file_path)
        text = "\n".join([page.get_text("text") for page in doc])
    elif file_path.endswith(".docx"):
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
    elif file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    return text


def generate_audio(text, filename):
    audio_path = os.path.join(app.config["UPLOAD_FOLDER"], filename.rsplit(".", 1)[0] + ".mp3")
    engine = pyttsx3.init()
    engine.save_to_file(text, audio_path)
    engine.runAndWait()
    return os.path.basename(audio_path)


@app.route("/get_audio/<filename>")
def get_audio(filename):
    return send_file(os.path.join(app.config["UPLOAD_FOLDER"], filename), as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
