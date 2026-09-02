import os
import json
from pathlib import Path
import logging

# 설정 파일이 저장될 경로 (서버 루트 디렉토리 기준)
CONFIG_DIR = Path("config")
CONFIG_DIR.mkdir(exist_ok=True)
CONFIG_FILE = CONFIG_DIR / "user_settings.json"

class ConfigManager:
    @staticmethod
    def _load_data() -> dict:
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    @staticmethod
    def _save_data(data: dict):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    @staticmethod
    def get_api_key() -> str:
        # 환경 변수 우선 확인, 없으면 설정 파일에서 조회
        env_key = os.getenv("GEMINI_API_KEY")
        if env_key:
            return env_key
            
        data = ConfigManager._load_data()
        return data.get("api_config", {}).get("key", "")

    @staticmethod
    def set_api_key(new_key: str):
        data = ConfigManager._load_data()
        if "api_config" not in data:
            data["api_config"] = {}
        data["api_config"]["key"] = new_key.strip()
        ConfigManager._save_data(data)

    @staticmethod
    def get_target_lang() -> str:
        data = ConfigManager._load_data()
        return data.get("app_prefs", {}).get("target_lang", "ko")

    @staticmethod
    def set_target_lang(lang: str):
        data = ConfigManager._load_data()
        if "app_prefs" not in data:
            data["app_prefs"] = {}
        data["app_prefs"]["target_lang"] = lang.strip()
        ConfigManager._save_data(data)

# OCR 및 시스템 기본 설정 상수
OCR_LANG = "chi_sim+eng"
OCR_PSM = 3
TARGET_LANG = ConfigManager.get_target_lang()

# 서버 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OCRTranslateServer")
