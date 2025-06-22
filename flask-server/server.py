from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os

# Import OCR and Q&A logic from your services
from services.ocr_utils import extract_text_from_pdf, extract_text_from_image
from services.langchain_pipeline import build_qa_chain

app = Flask(__name__)
os.makedirs("data", exist_ok=True)

# Define a route to handle POST requests
@app.route("/ask", methods=["POST"])
def ask():
    try:
        # Get list of uploaded files and the question
        uploaded_files = request.files.getlist("files")
        question = request.form["question"]

        if not uploaded_files:
            return jsonify({"error": "No files uploaded"}), 400

        combined_text = ""

        # Process each uploaded file
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

        if not combined_text.strip():
            return jsonify({"error": "No text could be extracted"}), 400

        # Pass the combined text into the QA chain
        qa_chain = build_qa_chain(combined_text)
        answer = qa_chain.invoke(question)

        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Clean up all saved files
        for file in request.files.getlist("files"):
            filepath = os.path.join("data", secure_filename(file.filename))
            if os.path.exists(filepath):
                os.remove(filepath)


if __name__ == "__main__":
    app.run(host='localhost', port=8888, debug=True)
