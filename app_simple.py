from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import tempfile
from dotenv import load_dotenv
from document_analyzer import DocumentAnalyzer
from text_improver import TextImprover

# .env 파일 로드
load_dotenv()

app = Flask(__name__)
CORS(app)

# 업로드 폴더 설정
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB 제한

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/api/analyze-document', methods=['POST'])
def analyze_document():
    """문서 분석 API - HTML만 반환"""
    try:
        # 파일이 업로드되었는지 확인
        if 'file' not in request.files:
            return jsonify({'error': '파일이 업로드되지 않았습니다.'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '파일이 선택되지 않았습니다.'}), 400
        
        # HWP 또는 PDF 파일인지 확인
        allowed_extensions = ['.hwp', '.pdf']
        file_extension = os.path.splitext(file.filename.lower())[1]
        if file_extension not in allowed_extensions:
            return jsonify({'error': 'HWP 또는 PDF 파일만 업로드 가능합니다.'}), 400
        
        # 임시 파일로 저장 (확장자에 맞게)
        suffix = file_extension
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name
        
        try:
            # Document Digitization API 분석
            analyzer = DocumentAnalyzer()
            api_result = analyzer.analyze_document(temp_path)
            
            # API 응답을 콘솔에 출력
            print("=" * 50)
            print(f"📄 파일: {file.filename}")
            print("🔍 Document Digitization API 응답:")
            print("=" * 50)
            
            if api_result.get('success'):
                import json
                print(json.dumps(api_result, indent=2, ensure_ascii=False))
            else:
                print(f"❌ API 오류: {api_result.get('error')}")
                print(f"메시지: {api_result.get('message')}")
            
            print("=" * 50)
            
            if not api_result.get('success'):
                return jsonify({
                    'success': False,
                    'error': api_result.get('error', 'API 분석에 실패했습니다.'),
                    'message': api_result.get('message', '')
                })
            
            # HTML 콘텐츠 추출
            html_content = ""
            if api_result.get('data') and api_result['data'].get('content'):
                html_content = api_result['data']['content'].get('html', '')
            
            # 파일 정보
            file_info = analyzer.get_file_info(temp_path)
            
            return jsonify({
                'success': True,
                'html_content': html_content,
                'file_info': file_info,
                'original_filename': file.filename,
                'full_api_response': api_result  # 전체 API 응답도 함께 전달
            })
        
        finally:
            # 임시 파일 삭제
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    except Exception as e:
        return jsonify({'error': f'처리 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/api/generate-text-options', methods=['POST'])
def generate_text_options():
    """문장 옵션 생성 API"""
    try:
        data = request.get_json()
        text = data.get("text", "")
        context = data.get("context", None)
        num_options = data.get("num_options", 3)
        
        if not text:
            return jsonify({'success': False, 'error': '문장이 비어 있습니다.'}), 400

        improver = TextImprover()
        result = improver.generate_text_options(text, context, num_options)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/improve-text', methods=['POST'])
def improve_text():
    """문장 개선 API (기존 호환성 유지)"""
    try:
        data = request.get_json()
        text = data.get("text", "")
        context = data.get("context", None)
        
        if not text:
            return jsonify({'success': False, 'error': '문장이 비어 있습니다.'}), 400

        improver = TextImprover()
        result = improver.improve_text(text, context)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate-evaluation-criteria', methods=['POST'])
def generate_evaluation_criteria():
    """평가기준 4단계 생성 API"""
    try:
        data = request.get_json()
        evaluation_element = data.get("evaluationElement", "")
        original_criteria = data.get("originalCriteria", {})
        context = data.get("context", None)
        
        if not evaluation_element:
            return jsonify({'success': False, 'error': '평가요소가 비어 있습니다.'}), 400

        improver = TextImprover()
        result = improver.generate_evaluation_criteria(evaluation_element, original_criteria, context)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate-single-criteria', methods=['POST'])
def generate_single_criteria():
    """단일 평가기준 생성 API"""
    try:
        data = request.get_json()
        level = data.get("level", "")
        evaluation_element = data.get("evaluationElement", "")
        original_text = data.get("originalText", "")
        context = data.get("context", None)
        
        if not level or not evaluation_element:
            return jsonify({'success': False, 'error': '필수 정보가 누락되었습니다.'}), 400

        improver = TextImprover()
        result = improver.generate_single_criteria(level, evaluation_element, original_text, context)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """서버 상태 확인"""
    return jsonify({'status': 'healthy', 'message': 'HTML 뷰어 서버가 정상 작동 중입니다.'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)