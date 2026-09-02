from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import shutil
from pathlib import Path
import os

# OCR-Translate 루트 기준 core 및 기타 모듈 임포트
try:
    from core.translation_cache_crosslink import CrossLingualCache
    from gemini_ocr_translate import GeminiOCRTranslate
except ImportError:
    CrossLingualCache = None
    GeminiOCRTranslate = None

app = FastAPI(title="OCR-Translate Server", version="1.0")

# 캐시 매니저 초기화 (OCR-Translate 내부 캐시 경로 활용)
cache_manager = CrossLingualCache() if CrossLingualCache else None

# OCI 서버 환경변수에서 제미나이 API 키 로드
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
        if cache_manager:
            cached_result = cache_manager.cache.get_entry(text)
            if cached_result:
                return {"translated_text": cached_result, "source": "cache"}

        if not translator:
            raise HTTPException(status_code=500, detail="Gemini translator is not initialized (Check GEMINI_API_KEY).")
            
        translated = translator.translate_text(text)
        
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
    
    with temp_file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        if not translator:
            raise HTTPException(status_code=500, detail="Gemini translator is not initialized.")
            
        result_text = translator.process_all(str(temp_file_path))
        
        return {
            "message": "OCR 및 번역 성공",
            "filename": file.filename,
            "result": result_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_file_path.exists():
            temp_file_path.unlink()
