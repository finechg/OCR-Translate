from pydantic import BaseModel
from typing import List, Optional

class WordDetail(BaseModel):
    word: str
    pinyin: str
    meaning: str

class TranslationResponse(BaseModel):
    page_number: int
    header_pinyin: str
    original_text: str
    translated_text: str
    footer_vocab: List[WordDetail]