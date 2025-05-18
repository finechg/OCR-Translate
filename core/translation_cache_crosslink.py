from cache.cache_handler import TranslationCacheManager
import logging

class CrossLingualCache:
    def __init__(self, base_dir="cache", base_name="translation_cache"):
        self.cache = TranslationCacheManager(base_dir=base_dir, base_name=base_name)

    def add_crosslinked(self, source_texts: dict, translated: str):
        # source_texts 예시:
        # {"en": "I love you", "zh": "我爱你"}
        try:
            for lang1, text1 in source_texts.items():
                self.cache.add_entry(text1, translated)
                for lang2, text2 in source_texts.items():
                    if lang1 != lang2:
                        # text1 -> translated -> text2 라고 간주하고 연결 저장
                        self.cache.add_entry(text1, text2)
                        self.cache.add_entry(text2, text1)
        except Exception as e:
            logging.warning(f"교차 캐시 저장 실패: {e}")