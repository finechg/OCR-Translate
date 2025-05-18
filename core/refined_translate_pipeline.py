from core.gpt_refiner import rewrite_with_gpt
from core.translate import TranslateWorker
from config import TARGET_LANG
from translate.google_translate_api import translate_with_google

def translate_and_refine(text, source_lang='auto', target_lang=TARGET_LANG):
    # 1차 번역 (Google Cloud Translate)
    raw_translated = translate_with_google(text, source_lang, target_lang)

    # 2차 리라이팅 (GPT-4.1 mini or 3.5)
    refined = rewrite_with_gpt(raw_translated)

    return refined