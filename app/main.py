import os
# [필수] Protobuf 호환성 에러 해결 (사용자님 환경용)
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from typing import List
import pymupdf as fitz
from ebooklib import epub
from bs4 import BeautifulSoup
import io
import asyncio
import re
from urllib.parse import quote

# 서비스 모듈 임포트
from .schemas import TranslationResponse, WordDetail
from .services.ocr import OCRService
from .services.translate import TranslationService
from .services.analyzer import ChineseAnalyzer
from .services.exporter import ExporterService

app = FastAPI(title="DeepL Powered Chinese/English OCR Tutor")

# 전역 서비스 인스턴스 초기화
ocr_service = OCRService()
ts_service = TranslationService()
analyzer = ChineseAnalyzer(ts_service)
exporter = ExporterService()

def clean_text(text: str) -> str:
    """텍스트의 불필요한 줄바꿈과 공백 정리"""
    return re.sub(r'\s+', ' ', text).strip()

def clean_html(html_content):
    """EPUB 내부의 HTML 태그 제거 및 텍스트 추출"""
    if isinstance(html_content, bytes):
        html_content = html_content.decode('utf-8', errors='ignore')
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text()

async def process_single_page(page_num: int, image_or_text, is_epub=False) -> TranslationResponse:
    """한 페이지의 텍스트를 분석하여 학습용 데이터를 생성"""
    # 1. OCR 또는 텍스트 추출 (ocr.py의 Semaphore가 한 장씩 안전하게 처리)
    raw_text = image_or_text if is_epub else await ocr_service.extract_text(image_or_text)
    cleaned = clean_text(raw_text)
    
    if not cleaned:
        return TranslationResponse(
            page_number=page_num, header_pinyin="", 
            original_text="", translated_text="", footer_vocab=[]
        )

    # 2. DeepL 번역 실행 (중국어/영어 자동 감지)
    translated_text = await ts_service.translate_text(cleaned)
    
    # 3. 중국어 포함 여부 확인 후 조건부 단어장 생성
    # [차이점] 원문에 한자가 있을 때만 단어 분석을 돌려 속도를 높이고 영어 단어장을 방지합니다.
    vocab_raw = []
    if analyzer.is_chinese(cleaned):
        vocab_raw = await analyzer.extract_vocab(cleaned)
    
    return TranslationResponse(
        page_number=page_num,
        header_pinyin="", # 사용자님 요청으로 상단 병음 제거
        original_text=cleaned,
        translated_text=translated_text,
        footer_vocab=[WordDetail(**v) for v in vocab_raw]
    )

@app.post("/translate-study")
async def translate_study(
    file: UploadFile = File(...),
    start_page: int = Query(1, ge=1),
    end_page: int = Query(1, ge=1),
    output_format: str = Query("html", regex="^(json|html|word)$")
):
    """메인 엔드포인트: 파일 업로드 및 분석 결과 반환"""
    file_bytes = await file.read()
    page_tasks = []

    # 1. 파일 형식별 페이지 태스크 생성
    if file.filename.lower().endswith(".pdf"):
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        s_idx, e_idx = max(0, start_page - 1), min(doc.page_count, end_page)
        for i in range(s_idx, e_idx):
            page = doc.load_page(i)
            # 고해상도(2배) 이미지 생성
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            page_tasks.append(process_single_page(i + 1, pix.tobytes("png")))
        doc.close()

    elif file.filename.lower().endswith(".epub"):
        book = epub.read_epub(io.BytesIO(file_bytes))
        items = [item for item in book.get_items() if item.get_type() == 9]
        s_idx, e_idx = max(0, start_page - 1), min(len(items), end_page)
        for i in range(s_idx, e_idx):
            raw_text = clean_html(items[i].get_content())
            page_tasks.append(process_single_page(i + 1, raw_text, is_epub=True))

    elif file.content_type.startswith("image/"):
        page_tasks.append(process_single_page(1, file_bytes))

    else:
        raise HTTPException(status_code=400, detail="지원하지 않는 파일 형식입니다.")

    if not page_tasks:
        raise HTTPException(status_code=422, detail="분석할 페이지가 없습니다.")

    # 2. 모든 페이지 병렬 분석 실행
    results = await asyncio.gather(*page_tasks)
    
    # 3. 출력 포맷별 응답 처리 (파일명 인코딩 포함)
    encoded_filename = quote(file.filename)

    if output_format == "json":
        return results

    elif output_format == "html":
        html_content = exporter.to_html(results)
        return Response(
            content=html_content,
            media_type="text/html",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''study_note_{encoded_filename}.html"}
        )

    elif output_format == "word":
        word_stream = exporter.to_word_stream(results)
        return StreamingResponse(
            word_stream,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''study_report_{encoded_filename}.docx"}
        )