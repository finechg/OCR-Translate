
"""OCR and translation helpers for the desktop client."""

from __future__ import annotations

import asyncio
import html
import io
import logging
import re
from collections import defaultdict
from multiprocessing import Pool, cpu_count
from typing import Dict, List, Optional, Tuple

import fitz
import pytesseract
from PIL import Image
from PySide6.QtCore import QRunnable, Slot

from config import OCR_LANG, OCR_PSM, TARGET_LANG
from core.lang_utils import detect_language_safe
from core.ocr_cache import OcrCache
from core.utils_text import split_into_sentences
from translate.manager import TranslatorManager

ALLOWED_SOURCE_LANGS = {"en", "zh", "zh-cn", "zh-tw", "ja", "fr", "de", "es"}

# ``multiprocessing`` spins up new Python interpreters for the worker pool.
# Instantiating :class:`OcrCache` is relatively heavy, so we lazily create a
# single instance per process and reuse it across invocations.
_OCR_CACHE: Optional[OcrCache] = None


def _get_ocr_cache(cache_enabled: bool) -> Optional[OcrCache]:
    if not cache_enabled:
        return None

    global _OCR_CACHE
    if _OCR_CACHE is None:
        _OCR_CACHE = OcrCache()
    return _OCR_CACHE


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
        # ``TranslatorManager`` exposes ``close`` to release any network or
        # process resources.  Always close it even if translation fails so the
        # caller does not leak resources.
        manager.close()


def translate_text(text, target_lang, source_lang=None):
    """Blocking translation helper used by the rest of the code base."""

    return _translate_text_sync(text, target_lang, source_lang)


def ocr_single_page(args: Tuple[int, bytes, bool]):
    i, page_bytes, cache_enabled = args
    ocr_cache = _get_ocr_cache(cache_enabled)

    try:
        img_bytes = page_bytes
        if ocr_cache is not None:
            cached = ocr_cache.get_text(img_bytes)
            if cached:
                return (i, cached)

        img = Image.open(io.BytesIO(img_bytes))
        text = pytesseract.image_to_string(img, lang=OCR_LANG, config=f"--psm {OCR_PSM}")

        if ocr_cache is not None:
            ocr_cache.save_text(img_bytes, text)

        return (i, text)
    except Exception as e:  # pragma: no cover - defensive coding for OCR
        return (i, f"[Page {i+1}] OCR 실패: {e}")


class TranslateWorker(QRunnable):
    def __init__(self, file_path, signal_handler, lang=TARGET_LANG):
        super().__init__()
        self.file_path = file_path
        self.signal_handler = signal_handler
        self.lang = lang
        self.cache_enabled = True

    @Slot()
    def run(self):
        doc = fitz.open(self.file_path)
        total_pages = len(doc)
        page_images = []

        for i in range(total_pages):
            page = doc.load_page(i)
            pix = page.get_pixmap(dpi=200)
            page_images.append((i, pix.tobytes("jpeg"), self.cache_enabled))

        with Pool(min(cpu_count(), 6)) as pool:
            ocr_results = pool.map(ocr_single_page, page_images)

        for i, text in sorted(ocr_results):
            try:
                cleaned = re.sub(r"(?<=[一-鿿])\s+(?=[一-鿿])", "", text)
                sentences = split_into_sentences(cleaned)
                if not sentences:
                    self.signal_handler.page_done.emit(
                        i, f"[Page {i+1}]\n[빈 페이지 또는 인식 실패]"
                    )
                    continue

                lang_groups: Dict[str, List[Tuple[int, str]]] = defaultdict(list)
                for idx, sentence in enumerate(sentences):
                    lang = detect_language_safe(sentence)
                    if lang in ALLOWED_SOURCE_LANGS:
                        lang_groups[lang].append((idx, sentence))

                translated_by_index: List[Optional[str]] = [None] * len(sentences)
                for lang, group in lang_groups.items():
                    manager = TranslatorManager(source=lang, target=self.lang)
                    try:
                        for idx, sentence in group:
                            translated_by_index[idx] = manager.translate(
                                sentence, target=self.lang
                            )
                    finally:
                        manager.close()

                translated_sentences = [
                    translation
                    for translation in translated_by_index
                    if translation is not None
                ]

                result = (
                    f"[Page {i+1}]\n"
                    + html.unescape(" ".join(translated_sentences).strip())
                )
            except Exception as e:  # pragma: no cover - runtime safety net
                logging.error(f"Page {i+1} 처리 실패: {e}")
                result = f"[Page {i+1}]\n[번역 실패: {e}]"

            self.signal_handler.page_done.emit(i, result)

        self.signal_handler.finished.emit()


async def translate_text_async(text, target_lang, source_lang=None):
    """Asynchronous wrapper around :func:`_translate_text_sync`."""

    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None, _translate_text_sync, text, target_lang, source_lang
    )
    return result
