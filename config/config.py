import os
from pathlib import Path
from dotenv import load_dotenv

# .env 로드
load_dotenv()

# OCR 기본 설정
OCR_LANG = os.getenv("OCR_LANG", "eng+chi_sim")
OCR_PSM = int(os.getenv("OCR_PSM", 3))
TARGET_LANG = os.getenv("TARGET_LANG", "ko")

# 번역기 API 키 로딩: keys.txt 로부터
def load_keys(file_path="ocr_translate/keys.txt"):
    keys = {}
    path = Path(file_path)
    if not path.exists():
        return keys
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip() and "=" in line:
                k, v = line.strip().split("=", 1)
                keys[k.strip()] = v.strip()
    return keys

KEYS = load_keys()

# 예시:
# GOOGLE_API_KEY = KEYS.get("GOOGLE")
# DEEPL_API_KEY = KEYS.get("DEEPL")

import logging

LOG_FILE = "ocr_translate/logs/ocr_translate.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)