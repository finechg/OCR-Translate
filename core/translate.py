
import asyncio
import html
import io
import logging
import re
from collections import defaultdict
from contextlib import suppress
from multiprocessing import Pool, cpu_count
from typing import Dict, Tuple

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


def _translate_text_sync(text, target_lang, source_lang=None):
    """Translate *text* synchronously.

    The previous implementation accidentally called ``translate_text`` from
    within itself via the asynchronous wrapper which resulted in infinite
    recursion.  To keep the synchronous implementation reusable by both the
    public synchronous and asynchronous helpers we perform the actual work in
    this internal helper.
    """

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


class TranslateWorker(QRunnable):
    """Worker responsible for extracting text and performing translations.

    The previous implementation instantiated a new ``TranslatorManager`` for
    every page/language combination which is unnecessarily expensive.  A single
    PDF may contain hundreds of sentences in the same language which means the
    creation/teardown of the manager dominated the translation time.  We now
    keep the managers alive for the lifetime of the worker and reuse
    translations for identical sentences which significantly reduces repeated
    RPC calls.
    """

    def __init__(self, file_path, signal_handler, lang=TARGET_LANG):
        super().__init__()
        self.file_path = file_path
        self.signal_handler = signal_handler
        self.lang = lang
        self.cache_enabled = True
        self._managers: Dict[str, TranslatorManager] = {}
        self._sentence_cache: Dict[Tuple[str, str], str] = {}

    @Slot()
    def run(self):
        doc = None
        try:
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

                    lang_groups = defaultdict(list)
                    for sentence in sentences:
                        lang = detect_language_safe(sentence)
                        if lang in ALLOWED_SOURCE_LANGS:
                            lang_groups[lang].append(sentence)

                    translated_sentences = [
                        self._translate_sentence(lang, sentence)
                        for lang, group in lang_groups.items()
                        for sentence in group
                    ]

                    result = (
                        f"[Page {i+1}]\n"
                        + html.unescape(" ".join(translated_sentences).strip())
                    )
                except Exception as exc:
                    logging.error(f"Page {i+1} 처리 실패: {exc}")
                    result = f"[Page {i+1}]\n[번역 실패: {exc}]"

                self.signal_handler.page_done.emit(i, result)
        finally:
            self._close_managers()
            if doc is not None:
                with suppress(Exception):
                    doc.close()
            self.signal_handler.finished.emit()

    def _translate_sentence(self, lang: str, sentence: str) -> str:
        cache_key = (lang, sentence)
        cached = self._sentence_cache.get(cache_key)
        if cached is not None:
            return cached

        manager = self._managers.get(lang)
        if manager is None:
            manager = TranslatorManager(source=lang, target=self.lang)
            self._managers[lang] = manager

        translated = manager.translate(sentence, target=self.lang)
        self._sentence_cache[cache_key] = translated
        return translated

    def _close_managers(self) -> None:
        for manager in self._managers.values():
            try:
                manager.close()
            except Exception:
                logging.exception("TranslatorManager 종료 중 오류 발생")
        self._managers.clear()
        self._sentence_cache.clear()


async def translate_text_async(text, target_lang, source_lang=None):
    """Asynchronous wrapper around :func:`_translate_text_sync`."""

    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None, _translate_text_sync, text, target_lang, source_lang
    )
    return result
