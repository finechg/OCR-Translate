# ocr_translate/config/config.py
from kivy.storage.jsonstore import JsonStore
import os
from pathlib import Path

# 앱 데이터가 저장될 경로 (안드로이드 내부 저장소)
store = JsonStore('user_settings.json')

class ConfigManager:
    @staticmethod
    def get_api_key():
        # 저장소에서 키를 가져오고, 없으면 빈 문자열 반환
        if store.exists('api_config'):
            return store.get('api_config')['key']
        return ""

    @staticmethod
    def set_api_key(new_key):
        # 사용자가 입력한 키를 저장소에 기록
        store.put('api_config', key=new_key.strip())

    @staticmethod
    def get_target_lang():
        if store.exists('app_prefs'):
            return store.get('app_prefs')['target_lang']
        return "ko" # 기본값 한국어

# 로그 설정 (터미널 출력용)
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GeminiApp")
