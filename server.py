from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import shutil
from pathlib import Path

# core 폴더 내에 있는 실제 모듈 및 클래스 임포트
# (프로젝트 구조에 맞추어 경로를 점검해주세요)
try:
    from core.translation_cache_crosslink import CrossLingualCache
    from gemini_ocr_translate import GeminiOCRTranslate
except ImportError:
    # 경로가 다를 경우를 대비한 방어 코드
    CrossLingualCache = None
    GeminiOCRTranslate = None

import os

app = FastAPI(title="OCR-Translate Server", version="1.0")

# 서버 시작 시 캐시 매니저 초기화 (cache 디렉토리에 자동 생성)
cache_manager = CrossLingualCache() if CrossLingualCache else None

# 제미나이 번역기 초기화 (환경 변수나 시스템 설정의 API 키 활용)
# OCI 서버 환경변수에서 API 키를 읽어오도록 설정
API_KEY = os.getenv("GEMINI_API_KEY", "")
translator = GeminiOCRTranslate(API_KEY) if (GeminiOCRTranslate and API_KEY) else None


@app.get("/")
def health_check():
    return {"status": "running", "message": "OCR-Translate OCI Server is up!"}


@app.post("/api/translate")
async def api_translate(
    text: str = Form(...), 
    target_lang: str = Form("ko"), 
    source_lang: str = Form("zh")
):
    """순수 텍스트 번역 엔드포인트 (교차 캐시 적용)"""
    try:
        # 1. 캐시 매니저를 통해 기존 번역 이력이 있는지 확인
        if cache_manager:
            cached_result = cache_manager.cache.get_entry(text)
            if cached_result:
                return {"translated_text": cached_result, "source": "cache"}

        # 2. 캐시에 없으면 제미나이 엔진을 통해 번역 수행
        if not translator:
            raise HTTPException(status_code=500, detail="Gemini translator is not initialized (Check API Key).")
            
        translated = translator.translate_text(text)
        
        # 3. 결과가 정상적이면 교차 캐시에 저장
        if translated and cache_manager:
            source_dict = {source_lang: text}
            cache_manager.add_crosslinked(source_dict, translated)

        return {"translated_text": translated, "source": "api"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ocr-translate")
async def api_ocr_translate(
    file: UploadFile = File(...), 
    target_lang: str = Form("ko")
):
    """이미지 업로드 기반 OCR 및 번역 엔드포인트"""
    temp_file_path = Path(f"temp_{file.filename}")
    
    # 업로드된 이미지를 임시 파일로 저장
    with temp_file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        if not translator:
            raise HTTPException(status_code=500, detail="Gemini translator is not initialized.")
            
        # 기존 GeminiOCRTranslate의 이미지 처리 함수 호출
        result_text = translator.process_all(str(temp_file_path))
        
        return {
            "message": "OCR 및 번역 성공",
            "filename": file.filename,
            "result": result_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # 사용 완료된 임시 파일 정리
        if temp_file_path.exists():
            temp_file_path.unlink()
