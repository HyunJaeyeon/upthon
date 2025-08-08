from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import tempfile
from dotenv import load_dotenv
from document_analyzer import DocumentAnalyzer
from text_improver import TextImprover

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return render_template("html_viewer.html")

@app.route("/api/analyze-document", methods=["POST"])
def analyze_document():
    file = request.files.get("file")
    if not file:
        return jsonify(success=False, error="파일이 없습니다.")

    save_path = os.path.join("uploads", file.filename)
    file.save(save_path)

    analyzer = DocumentAnalyzer()
    result = analyzer.analyze_document(save_path)
    file_info = analyzer.get_file_info(save_path)

    if result["success"]:
        return jsonify(
            success=True,
            original_filename=file.filename,
            file_info=file_info,
            html_content=result["data"].get("html", ""),
            full_api_response=result["data"]
        )
    else:
        return jsonify(success=False, error=result["error"], message=result["message"])

@app.route('/api/improve-text', methods=['POST'])
def improve_text():
    """문장 개선 API"""
    try:
        data = request.get_json()
        text = data.get("text", "")
        if not text:
            return jsonify({'success': False, 'error': '문장이 비어 있습니다.'}), 400

        improver = TextImprover()
        result = improver.improve_text(text)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500