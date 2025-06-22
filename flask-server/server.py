from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS
import os

# Import OCR and Q&A logic from your services
from services.ocr_utils import extract_text_from_pdf, extract_text_from_image
from services.langchain_pipeline import build_qa_chain

app = Flask(__name__)
CORS(app)
os.makedirs("data", exist_ok=True)

# Global variable to cache the chain
qa_chain = None

# Define a routes to handle POST requests
@app.route("/upload", methods=["POST"])
def upload():
    global qa_chain

    try:
        uploaded_files = request.files.getlist("files")
        if not uploaded_files:
            return jsonify({"error": "No files uploaded"}), 400

        combined_text = ""

        for file in uploaded_files:
            filename = secure_filename(file.filename)
            filepath = os.path.join("data", filename)
            file.save(filepath)

            ext = filename.split(".")[-1].lower()
            if ext == "pdf":
                text = extract_text_from_pdf(filepath)
            elif ext in ["png", "jpg", "jpeg"]:
                text = extract_text_from_image(filepath)
            else:
                continue  # Skip unsupported files

            combined_text += text + "\n\n"

            # Clean up temp file
            os.remove(filepath)

        if not combined_text.strip():
            return jsonify({"error": "No text extracted"}), 400

        # Build and store the QA chain in memory
        qa_chain = build_qa_chain(combined_text)

        return jsonify({"status": "ready"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/ask", methods=["POST"])
def ask():
    global qa_chain

    try:
        data = request.get_json()
        question = data.get("question")

        if not qa_chain:
            return jsonify({"error": "No document uploaded yet"}), 400

        if not question or not question.strip():
            return jsonify({"error": "Question is empty"}), 400

        answer = qa_chain.invoke(question)
        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host='localhost', port=8888, debug=True)
