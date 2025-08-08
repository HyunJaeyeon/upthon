import requests
import os
from typing import Dict, Any
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class DocumentAnalyzer:
    def __init__(self, api_key: str = None):
        """
        Upstage Document Digitization API를 사용한 문서 분석기
        """
        self.api_key = api_key or os.getenv("UPSTAGE_API_KEY")
        if not self.api_key:
            raise ValueError("UPSTAGE_API_KEY가 설정되지 않았습니다.")
            
        self.url = "https://api.upstage.ai/v1/document-digitization"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
    
    def analyze_document(self, file_path: str) -> Dict[str, Any]:
        """
        문서를 분석하고 결과를 반환합니다.
        """
        try:
            with open(file_path, "rb") as file:
                files = {"document": file}
                data = {
                    "model": "document-parse-250618",
                    "ocr": "auto",
                    "chart_recognition": True,
                    "coordinates": True,
                    "output_formats": '["html"]',
                    "base64_encoding": '["figure"]',
                }

                response = requests.post(self.url, headers=self.headers, files=files, data=data)
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "data": response.json(),
                        "status_code": response.status_code
                    }
                else:
                    return {
                        "success": False,
                        "error": f"API 오류: {response.status_code}",
                        "message": response.text,
                        "status_code": response.status_code
                    }
                    
        except FileNotFoundError:
            return {
                "success": False,
                "error": "파일을 찾을 수 없습니다.",
                "message": f"파일 경로: {file_path}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": "문서 분석 중 오류가 발생했습니다.",
                "message": str(e)
            }
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """파일 정보를 반환합니다."""
        if not os.path.exists(file_path):
            return {"error": "파일이 존재하지 않습니다."}
        
        stat = os.stat(file_path)
        return {
            "filename": os.path.basename(file_path),
            "size": stat.st_size,
            "modified": stat.st_mtime
        }