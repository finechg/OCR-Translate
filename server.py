# server.py
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import shutil
from pathlib import Path

# 예시 모듈들 임포트 (경로에 맞게 조정 필요)
from core.translate import _translate_text_sync
from cache.cross_lingual_cache import CrossLingualCache # 혹은 관련 캐시 모듈

app = FastAPI(title="OCR Translate Server", version="1.0")

# 캐시 매니저 초기화
cache_manager = CrossLingualCache()

@app.post("/api/translate")
async def api_translate(text: str = Form(...), target_lang: str = Form("ko"), source_lang: str = Form(None)):
    try:
        # 1. 캐시 먼저 확인
        cached_result = cache_manager.cache.get_entry(text)
        if cached_result:
            return {"translated_text": cached_result, "source": "cache"}

        # 2. 캐시에 없으면 기존 번역 로직 수행
        translated = _translate_text_sync(text, target_lang, source_lang)
        
        # 3. 결과 캐시 저장
        if translated:
            cache_manager.add_crosslinked({source_lang or "auto": text}, translated)

        return {"translated_text": translated, "source": "api"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ocr-translate")
async def api_ocr_translate(file: UploadFile = File(...), target_lang: str = Form("ko")):
    # 여기에 업로드된 이미지/PDF를 받아 기존 PyTesseract 또는 PDF 처리 로직을 태우는 코드를 연결
    temp_file_path = Path(f"temp_{file.filename}")
    with temp_file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # TODO: 기존 TranslateWorker나 ocr_single_page 로직을 호출하여 처리
        return {"message": "OCR 및 번역 처리 완료", "filename": file.filename}
    finally:
        if temp_file_path.exists():
            temp_file_path.unlink() # 임시 파일 삭제
