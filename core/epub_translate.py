from core.epub_parser import extract_epub_text_by_chapter
from translate.google_translate_api import translate_with_google
from core.gpt_refiner import rewrite_with_gpt
from config import TARGET_LANG
from pathlib import Path
import logging

def translate_epub_to_chapters(epub_path, target_lang=TARGET_LANG):
    chapters = extract_epub_text_by_chapter(epub_path)
    translated_chapters = []

    for i, chapter in enumerate(chapters):
        try:
            logging.info(f"번역 중: Chapter {i+1}")
            raw_translation = translate_with_google(chapter, source_lang="auto", target_lang=target_lang)
            refined = rewrite_with_gpt(raw_translation)
            translated_chapters.append(refined)
        except Exception as e:
            logging.warning(f"Chapter {i+1} 번역 실패: {e}")
            translated_chapters.append("[번역 실패]")

    return translated_chapters

if __name__ == "__main__":
    result = translate_epub_to_chapters("example.epub")
    for i, ch in enumerate(result):
        print(f"--- Translated {i+1} ---\n{ch[:200]}...\n")