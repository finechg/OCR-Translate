from cache.cache_handler import TranslationCacheManager
import logging
import re

def is_valid_text(text: str, min_length: int = 2) -> bool:
    if not text or len(text.strip()) < min_length:
        return False
    # 의미 있는 문자(알파벳, 숫자, 한글, 한자)가 최소 min_length개 이상 포함되어 있는지 확인
    valid_chars = re.findall(r'[a-zA-Z0-9가-힣一-鿿]', text)
    return len(valid_chars) >= min_length

class CrossLingualCache:
    def __init__(self, base_dir="cache", base_name="translation_cache"):
        self.cache = TranslationCacheManager(base_dir=base_dir, base_name=base_name)

    def add_crosslinked(self, source_texts: dict, translated: str):
        # 번역 결과 자체가 유효한지 먼저 체크
        if not is_valid_text(translated):
            return

        try:
            for lang1, text1 in source_texts.items():
                if not is_valid_text(text1):
                    continue
                
                self.cache.add_entry(text1, translated)
                for lang2, text2 in source_texts.items():
                    if lang1 != lang2 and is_valid_text(text2):
                        self.cache.add_entry(text1, text2)
                        self.cache.add_entry(text2, text1)
        except Exception as e:
            logging.warning(f"교차 캐시 저장 실패: {e}")
