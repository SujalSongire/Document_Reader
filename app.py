from flask import Flask, render_template, request, jsonify, send_file
import fitz  # PyMuPDF for PDF text extraction
import os
import gtts  # Google Text-to-Speech
import logging

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

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)
    logging.info(f"File uploaded: {file.filename}")

    try:
        extracted_text = extract_text(file_path)
        return jsonify({"text": extracted_text})
    except Exception as e:
        logging.error(f"Error extracting text: {e}")
        return jsonify({"error": "Failed to extract text"}), 500


def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = "\n".join([page.get_text("text") for page in doc])
    return text


@app.route("/speak", methods=["POST"])
def speak():
    data = request.json
    text = data.get("text", "")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    tts = gtts.gTTS(text)
    audio_path = "static/output.mp3"
    tts.save(audio_path)

    return jsonify({"audio_url": audio_path})


if __name__ == "__main__":
    app.run(debug=True)
