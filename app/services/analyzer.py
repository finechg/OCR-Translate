import jieba.posseg as pseg
import re
from pypinyin import pinyin, Style

class ChineseAnalyzer:
    def __init__(self, translate_service):
        self.ts = translate_service

    def is_chinese(self, text: str) -> bool:
        """텍스트에 중국어 한자가 포함되어 있는지 확인"""
        return bool(re.search(r'[\u4e00-\u9fa5]', text))

    def get_pinyin_sentence(self, text: str) -> str:
        if not self.is_chinese(text): return ""
        pinyin_list = pinyin(text, style=Style.TONE)
        return " ".join([item[0] for item in pinyin_list])

    async def extract_vocab(self, text: str) -> list:
        """중국어일 때만 단어를 추출하고 병음/뜻 생성"""
        if not self.is_chinese(text):
            return []  # 영어일 경우 빈 단어장 반환

        words_with_tag = pseg.cut(text)
        target_words = []
        seen = set()

        for word, tag in words_with_tag:
            # 한자이고 2글자 이상인 단어만 추출
            if len(word) >= 2 and word not in seen and self.is_chinese(word):
                target_words.append(word)
                seen.add(word)
            if len(target_words) >= 15: break

        if not target_words: return []

        # DeepL로 단어 뜻 일괄 번역
        meanings = await self.ts.translate_words_batch(target_words)

        vocab_list = []
        for i, word in enumerate(target_words):
            py = "".join([item[0] for item in pinyin(word, style=Style.TONE)])
            vocab_list.append({
                "word": word,
                "pinyin": py,
                "meaning": meanings[i] if i < len(meanings) else "뜻 없음"
            })
        return vocab_list