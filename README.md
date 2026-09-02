OCR & Translation FastAPI Server
기존 모바일(Kivy/안드로이드) 기반의 OCR 및 번역 애플리케이션을 고성능 서버 환경에 맞춰 마이그레이션 및 리팩토링한 FastAPI 백엔드 시스템입니다.

저사양 서버 환경에서의 효율적인 자원 운용과 시스템 부하 최적화를 위해 고성능 코어(P-코어)와 저성능 코어(E-코어)를 분리하는 CPU 어피니티(Core Pinning) 기술을 적용했습니다.

🚀 주요 특징 (Key Features)
FastAPI 백엔드 전환

기존 PySide6/Kivy GUI 및 로컬 저장소(JsonStore) 의존성을 완전히 제거하고, Linux 서버 환경에 최적화된 표준 REST API 구조로 개편.

코어 어피니티 (CPU Core Pinning) 최적화

메인 시스템과 API 응답 처리는 고성능 코어(0, 1, 2번 등)에 양보하고, 무거운 병렬 OCR 및 번역 연산 워커는 사용자가 지정한 저성능 코어(E-코어) 영역에서만 동작하도록 제한하여 시스템 안정성 확보.

고성능 네이티브 모듈 통합

Go (translate_caller): 고루틴을 활용한 고속 API 통신 및 번역 호출 브릿지.

Rust (fast_text_refiner): 추출된 텍스트 및 번역문의 노이즈 고속 정제.

고속 병렬 처리 및 캐싱

multiprocessing.Pool 기반의 PDF 페이지별 병렬 OCR 처리.

교차 언어 캐시 시스템(OcrCache, 문장 단위 캐시)을 도입하여 중복 연산 및 반복 API 호출 최소화.

🛠️ 기술 스택 (Tech Stack)
Backend Framework: FastAPI, Uvicorn

Core Processing: Python (Multiprocessing, PyMuPDF/fitz, Pytesseract)

Native Modules: Go, Rust

AI / API: Google Gemini API

⚙️ 설정 및 환경 변수 (config/config.py)
서버 환경에 맞춰 표준 JSON 및 환경 변수를 통해 설정을 관리합니다.

API 키 설정: 환경 변수 GEMINI_API_KEY를 등록하거나 설정 파일을 통해 관리할 수 있습니다.

코어 할당 설정:

Python
# 메인 시스템 코어를 제외한 OCR 워커 전용 코어 지정
ALLOWED_OCR_CORES = [3, 4, 5, 6, 7] 
📦 실행 방법 (Getting Started)
의존성 패키지 설치

Bash
pip install -r requirements.txt
네이티브 모듈 빌드 (Go / Rust)

Rust 정제기 빌드:

Bash
cd rust_modules/fast_text_refiner && cargo build --release
Go 브릿지 빌드:

Bash
cd go_modules/translate_caller && go build -o translate_caller
FastAPI 서버 실행

Bash
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
