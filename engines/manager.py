from translate.engine import get_translator

class TranslatorManager:
    def __init__(self, source="auto", target="ko", engine="google"):
        self.translator = get_translator(engine, source, target)

    def translate(self, text, target=None):
        return self.translator.translate(text)

    def close(self):
        self.translator.close()