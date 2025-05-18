from config import KEYS
import logging

class BaseTranslator:
    def __init__(self, source='auto', target='ko'):
        self.source = source
        self.target = target

    def translate(self, text):
        raise NotImplementedError

    def close(self):
        pass


class GoogleTranslator(BaseTranslator):
    def __init__(self, source='auto', target='ko'):
        super().__init__(source, target)
        from googletrans import Translator
        self.translator = Translator()

    def translate(self, text):
        try:
            result = self.translator.translate(text, src=self.source, dest=self.target)
            return result.text
        except Exception as e:
            logging.warning(f"Google 번역 실패: {e}")
            return f"[번역 실패] {text}"


class DummyTranslator(BaseTranslator):
    def translate(self, text):
        return f"{text} (번역됨)"


def get_translator(engine="google", source="auto", target="ko"):
    if engine == "google":
        return GoogleTranslator(source, target)
    else:
        return DummyTranslator(source, target)