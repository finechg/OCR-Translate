\# 📚 Study-OCR-ZH

> \*\*"단순한 번역을 넘어 학습으로"\*\* - 중국어 OCR 이미지 번역 및 단어 학습 도우미



이 프로젝트는 이미지 속 중국어를 OCR로 인식하여 번역하고, 학습자를 위해 \*\*병음(Pinyin)\*\*과 \*\*주요 단어 리스트\*\*를 자동으로 생성해주는 FastAPI 기반 서비스입니다.



\## 🎯 주요 기능

1\. \*\*High-Accuracy OCR\*\*: PaddleOCR을 활용하여 복잡한 한자 인식 최적화.

2\. \*\*Smart Translation\*\*: 무료 API를 활용한 한국어 번역.

3\. \*\*Learning Support\*\*: 

&#x20;  - 문장별 \*\*병음(Pinyin)\*\* 표기 생성.

&#x20;  - \*\*Jieba\*\* 형태소 분석기를 통한 핵심 단어 자동 추출.

&#x20;  - HSK 등급 기반 또는 빈출 단어 위주의 단어장 생성.

4\. \*\*Header/Footer Style Output\*\*:

&#x20;  - \[Header] 문장 전체 병음 가이드.

&#x20;  - \[Body] 원문 및 한국어 번역.

&#x20;  - \[Footer] 단어별 병음 및 뜻풀이 리스트.



\## 🛠 Tech Stack

\- \*\*Backend\*\*: FastAPI (Python 3.10+)

\- \*\*OCR Engine\*\*: PaddleOCR (Open Source)

\- \*\*NLP/Analysis\*\*: Jieba (Segmentation), Pypinyin (Pinyin)

\- \*\*Translation\*\*: Googletrans / Deep-translator (Free Library)

\- \*\*Image Processing\*\*: OpenCV, Pillow



\## 📂 Project Structure

```text

study-ocr-zh/

├── app/

│   ├── main.py          # FastAPI 실행 및 엔드포인트

│   ├── schemas.py       # 데이터 모델 (Pydantic)

│   ├── services/        # 핵심 로직 분리

│   │   ├── ocr.py       # 이미지 인식 (PaddleOCR)

│   │   ├── translate.py # 텍스트 번역

│   │   └── analyzer.py  # 중국어 분석 (병음, 단어 추출)

│   └── utils/           # 이미지 전처리 등 유틸리티

├── requirements.txt     # 의존성 패키지

└── README.md            # 프로젝트 문서화

🚀 Roadmap

Phase 1: 기본 OCR + 번역 파이프라인 구축

Phase 2: 병음 및 형태소 분석 기능 추가

Phase 3: 단어장 추출 로직 고도화 (HSK 데이터 연동)

Phase 4: 간단한 웹 UI (Streamlit or HTML) 연결


