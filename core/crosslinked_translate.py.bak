from core.gpt_refiner import rewrite_with_gpt
from translate.google_translate_api import translate_with_google
from config import TARGET_LANG
from cache.translation_cache_crosslink import CrossLingualCache

def crosslinked_translate(texts_by_lang: dict, target_lang=TARGET_LANG):
    # texts_by_lang 예시: {"en": "I love you", "zh": "我爱你"}
    results = {}
    common_translation = None

    for lang, text in texts_by_lang.items():
        translated = translate_with_google(text, source_lang=lang, target_lang=target_lang)
        refined = rewrite_with_gpt(translated)
        results[lang] = refined

        if not common_translation:
            common_translation = refined

    # 의미가 충분히 동일하다고 간주 → 교차 캐싱
    cross_cache = CrossLingualCache()
    cross_cache.add_crosslinked(texts_by_lang, common_translation)

    return results, common_translation