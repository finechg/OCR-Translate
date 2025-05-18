
# 더미 번역 함수 삽입 (translate_text 대체)
def translate_text(text, source_lang="ko", target_lang="en", method="google"):
    return text + "_translated"


def translate_text(text, target_lang):
    import asyncio
    return asyncio.run(translate_text_async(text, target_lang))
import io
import html
import logging
import time
import re
from PIL import Image
import pytesseract
import fitz
from collections import defaultdict
from multiprocessing import Pool, Manager, cpu_count

from core.ocr_cache import OcrCache
from core.lang_utils import detect_language_safe
from core.utils_text import split_into_sentences
from translate.manager import TranslatorManager
from PySide6.QtCore import QRunnable, Slot, QTimer

from config import OCR_LANG, OCR_PSM, TARGET_LANG

ALLOWED_SOURCE_LANGS = {"en", "zh", "zh-cn", "zh-tw", "ja", "fr", "de", "es"}


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
    def __init__(self, file_path, signal_handler, lang=TARGET_LANG):
        super().__init__()
        self.file_path = file_path
        self.signal_handler = signal_handler
        self.lang = lang
        self.cache_enabled = True
        self.queue = Manager().Queue()

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
                cleaned = re.sub(r'(?<=[一-鿿])\s+(?=[一-鿿])', '', text)
                sentences = split_into_sentences(cleaned)
                if not sentences:
                    self.signal_handler.page_done.emit(i, f"[Page {i+1}]\n[빈 페이지 또는 인식 실패]")
                    continue

                lang_groups = defaultdict(list)
                for s in sentences:
                    lang = detect_language_safe(s)
                    if lang in ALLOWED_SOURCE_LANGS:
                        lang_groups[lang].append(s)

                translated_sentences = []
                for lang, group in lang_groups.items():
                    manager = TranslatorManager(source=lang, target=self.lang)
                    for sentence in group:
                        translated = manager.translate(sentence, target=self.lang)
                        translated_sentences.append(translated)
                    manager.close()

                result = f"[Page {i+1}]\n" + html.unescape(" ".join(translated_sentences).strip())
            except Exception as e:
                logging.error(f"Page {i+1} 처리 실패: {e}")
                result = f"[Page {i+1}]\n[번역 실패: {e}]"

            self.signal_handler.page_done.emit(i, result)

        self.signal_handler.finished.emit()

import asyncio

async def translate_text_async(text, target_lang):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, translate_text, text, target_lang)
    return result
