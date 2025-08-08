# 문서 HTML 뷰어

Document Digitization API로 HWP/PDF 파일을 HTML로 변환하고, 변환된 HTML을 그대로 웹에 표시하는 뷰어입니다.

## 🎯 기능

- **HWP/PDF 파일 업로드**: 드래그 앤 드롭 또는 파일 선택  
- **Document Digitization API 호출**: HWP/PDF → HTML 변환
- **HTML 직접 표시**: API에서 받은 HTML을 웹에 그대로 렌더링
- **이미지 표시**: 문서 내 이미지도 함께 표시

## 🚀 실행 방법

### 1. 서버 시작
```bash
python3 app_simple.py
```

### 2. 브라우저 접속
```
http://localhost:5002
```

### 3. 파일 업로드
- `exam_sample.hwp` 파일 또는 PDF 파일 업로드
- Document Digitization API가 HTML로 변환
- 변환된 HTML이 웹에 표시됨 (이미지 포함)

## 📋 파일 구조

```
upthon/
├── app_simple.py           # 간단한 Flask 서버
├── document_analyzer.py    # Document Digitization API 클래스
├── templates/
│   └── html_viewer.html   # HTML 뷰어 인터페이스
├── .env                   # API 키 설정
└── exam_sample.hwp        # 테스트용 HWP 파일
```

## 🔧 API 키 설정

`.env` 파일에 이미 설정되어 있음:
```
UPSTAGE_API_KEY=up_KQO0Q8M6fqrMazQN49U6UbrFsP5WG
```

## 📄 결과 예시

업로드한 HWP 파일이 다음과 같이 HTML로 변환되어 표시됩니다:

```html
<header>6-1 국어과</header>
<h1>2회 수행평가 지도자료</h1>
<table>
  <tr>
    <td>단 원 명</td>
    <td>1. 비유하는 표현</td>
  </tr>
  <tr>
    <td>평가 과제</td>
    <td>비유하는 표현을 생각하며 시 읽기</td>
  </tr>
  ...
</table>
```

## 💡 특징

- **단순함**: 필드 편집 기능 없이 HTML만 표시
- **정확성**: Document Digitization API의 HTML을 그대로 렌더링
- **실시간**: 업로드 즉시 변환된 HTML 확인
- **디버깅**: 브라우저 콘솔에서 전체 API 응답 확인 가능

바로 테스트해보세요! 🎉