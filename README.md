
# OCR Translate 프로젝트

## 개요
이 프로젝트는 OCR 기반 다국어 번역 시스템으로, Google Cloud Translation API와 GPT 리라이팅을 통합하여 고품질 번역을 제공합니다.

## 주요 기능
- PDF 및 EPUB 문서 OCR 처리 및 문장 단위 번역
- SQLite 기반 캐시 시스템과 교차 번역 자동화
- GPT 리라이팅 및 사용자 평가 시스템 포함
- 탭 기반 GUI로 직관적인 작업 흐름 지원

## 설치 및 실행
1. Python 3.11 이상 설치
2. 필요한 패키지 설치:
   ```
   pip install -r requirements.txt
   ```
3. Google Cloud API 키를 `keys.txt` 파일에 저장 (비공개)
4. GUI 실행:
   ```
   python -m ocr_translate.ui.main_window
   ```

## 기여 안내
- 내부 키(`keys.txt`)와 캐시(`cache/`)는 공개 저장소에서 제외됩니다.
- 버그 제보 및 기능 개선 PR은 언제든 환영합니다.
- 코드 스타일과 커밋 메시지 규칙을 준수해 주세요.

## 라이선스
MIT License
