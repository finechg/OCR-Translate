
# core/engines/google_translate.py - Google Cloud Translation v3 API 호출용

import requests
import json
from pathlib import Path

# API 키 불러오기
def load_api_key():
    key_path = Path(__file__).resolve().parent.parent / "keys.txt"
    if not key_path.exists():
        raise FileNotFoundError("keys.txt 파일이 누락되었습니다.")
    with open(key_path, "r", encoding="utf-8") as f:
        return f.read().strip()


def google_translate_api(text, src_lang, tgt_lang):
    api_key = load_api_key()
    url = "https://translation.googleapis.com/v3/projects/translate-project:translateText"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [text],
        "sourceLanguageCode": src_lang,
        "targetLanguageCode": tgt_lang,
        "mimeType": "text/plain"
    }
    params = {"key": api_key}

    response = requests.post(url, headers=headers, params=params, json=data)
    if response.status_code == 200:
        return response.json()["translations"][0]["translatedText"]
    else:
        raise Exception(f"Cloud Translation API 오류: {response.status_code}, {response.text}")
