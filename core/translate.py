import asyncio
import html
import io
import logging
import re
from multiprocessing import Pool, cpu_count
from typing import Dict, Optional, Tuple

import fitz
import pytesseract
from PIL import Image

from config import OCR_LANG, OCR_PSM, TARGET_LANG
from core.lang_utils import detect_language_safe
from core.ocr_cache import OcrCache
from core.utils_text import split_into_sentences
from translate.manager import TranslatorManager

ALLOWED_SOURCE_LANGS = {"en", "zh", "zh-cn", "zh-tw", "ja", "fr", "de", "es"}


def _translate_text_sync(text, target_lang, source_lang=None):
    """Translate *text* synchronously."""
    detected_lang = source_lang or detect_language_safe(text)

    manager_kwargs = {"target": target_lang}
    if detected_lang:
        manager_kwargs["source"] = detected_lang

    manager = TranslatorManager(**manager_kwargs)
    try:
        return manager.translate(text, target=target_lang)
    finally:
        manager.close()


def translate_text(text, target_lang, source_lang=None):
    """Blocking translation helper used by the rest of the code base."""
    return _translate_text_sync(text, target_lang, source_lang)


def ocr_single_page(args):
    i, page_bytes, cache_enabled = args
    ocr_cache = OcrCache() if cache_enabled else None

    try:
        img_bytes = page_bytes
        if cache_enabled:
            cached = ocr_cache.get_text(img_bytes)
            if cached:
                return (i, cached)

        img = Image.open(io.BytesIO(img_bytes))
        text = pytesseract.image_to_string(img, lang=OCR_LANG, config=f"--psm {OCR_PSM}")

        if cache_enabled:
            ocr_cache.save_text(img_bytes, text)

        return (i, text)
    except Exception as e:
        return (i, f"[Page {i+1}] OCR 실패: {e}")


def process_pdf_backend(file_path: str, target_lang: str = TARGET_LANG) -> dict:
    """
    FastAPI 서버 환경에서 UI 시그널 없이 PDF 전체를 병렬 OCR 및 번역하고
    결과를 딕셔너리 형태로 반환하는 순수 함수 백엔드 로직
    """
    results = {}
    managers: Dict[str, TranslatorManager] = {}
    sentence_cache: Dict[Tuple[str, str], str] = {}
    language_detection_cache: Dict[str, Optional[str]] = {}
    cache_enabled = True

    def _translate_sentence(lang: str, sentence: str) -> str:
        cache_key = (lang, sentence)
        cached = sentence_cache.get(cache_key)
        if cached is not None:
            return cached

        manager = managers.get(lang)
        if manager is None:
            manager = TranslatorManager(source=lang, target=target_lang)
            managers[lang] = manager

        translated = manager.translate(sentence, target=target_lang)
        sentence_cache[cache_key] = translated
        return translated

    try:
        with fitz.open(file_path) as doc:
            total_pages = len(doc)

            def _page_image_iter():
                for page_index in range(total_pages):
                    page = doc.load_page(page_index)
                    pix = page.get_pixmap(dpi=200)
                    yield (
                        page_index,
                        pix.tobytes("jpeg"),
                        cache_enabled,
                    )

            with Pool(min(cpu_count(), 6)) as pool:
                page_iter = pool.imap(
                    ocr_single_page, _page_image_iter(), chunksize=1
                )
                for i, text in page_iter:
                    try:
                        cleaned = re.sub(r"(?<=[一-鿿])\s+(?=[一-鿿])", "", text)
                        sentences = split_into_sentences(cleaned)
                        if not sentences:
                            results[f"page_{i+1}"] = "[빈 페이지 또는 인식 실패]"
                            continue

                        translated_sentences = []
                        for sentence in sentences:
                            normalized = sentence.strip()
                            if not normalized:
                                continue

                            try:
                                lang = language_detection_cache[normalized]
                            except KeyError:
                                lang = detect_language_safe(normalized)
                                language_detection_cache[normalized] = lang

                            if lang in ALLOWED_SOURCE_LANGS:
                                translated = _translate_sentence(lang, normalized)
                            else:
                                translated = normalized

                            translated_sentences.append(translated)

                        page_result = html.unescape(" ".join(translated_sentences).strip())
                        results[f"page_{i+1}"] = page_result
                    except Exception as exc:
                        logging.error(f"Page {i+1} 처리 실패: {exc}")
                        results[f"page_{i+1}"] = f"[번역 실패: {exc}]"
    finally:
        for manager in managers.values():
            try:
                manager.close()
            except Exception:
                logging.exception("TranslatorManager 종료 중 오류 발생")
        managers.clear()
        sentence_cache.clear()
        language_detection_cache.clear()

    return results


async def translate_text_async(text, target_lang, source_lang=None):
    """Asynchronous wrapper around :func:`_translate_text_sync`."""
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None, _translate_text_sync, text, target_lang, source_lang
    )
    return result
