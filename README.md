# Gemini OCR-Translate (Android)

Gemini 3 Flash API를 활용한 안드로이드 전용 OCR 및 번역 도구입니다. 로컬 데이터베이스나 외부 OCR 엔진 없이, Gemini의 긴 컨텍스트 창을 활용하여 데이터 관리와 번역을 통합 처리합니다.

---

## 설계

- Stateless Architecture: SQLite 등 로컬 캐시를 제거하고, 이전 번역 맥락을 프롬프트에 포함하여 실시간으로 참조합니다.
- Unified Pipeline: 이미지 인식(OCR)과 문맥 번역을 단일 API 호출로 수행합니다.
- Android Native: Kivy 프레임워크를 사용하여 모바일 환경 및 구글 플레이 스토어 배포에 최적화되었습니다.
- Dynamic Configuration: 사용자가 직접 자신의 API Key를 입력하고 관리할 수 있는 설정 기능을 제공합니다.

---

## 프로젝트 구조

```plaintext
OCR-Translate/
├── main.py              # 앱 엔트리 포인트 및 화면 전환 로직
├── buildozer.spec       # 안드로이드 빌드 및 권한 설정
├── config/
│   └── config.py        # JsonStore 기반 API 키 및 사용자 설정 관리
├── utils/
│   └── gemini_engine.py  # 컨텍스트 기반 번역 엔진 (데이터 관리 통합)
└── requirements.txt     # 최소 의존성 리스트

## GNU General Public License v3.0 (GPL-3.0)