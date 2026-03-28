# main.py
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from config.config import ConfigManager
# 여기에 아까 만든 GeminiOCRTranslate 클래스를 임포트합니다.

class SettingScreen(Screen):
    # API 키를 입력받는 설정 화면 (스토어 출시용 필수 화면)
    pass

class TranslationScreen(Screen):
    # 실제 번역 결과가 나오는 메인 화면
    pass

class GeminiApp(App):
    def build(self):
        sm = ScreenManager()
        
        # 앱 시작 시 키 체크
        api_key = ConfigManager.get_api_key()
        
        if not api_key:
            # 키가 없으면 설정 화면부터
            sm.add_widget(SettingScreen(name='settings'))
            sm.current = 'settings'
        else:
            # 키가 있으면 바로 번역 화면으로
            sm.add_widget(TranslationScreen(name='main'))
            sm.current = 'main'
            
        return sm

if __name__ == '__main__':
    GeminiApp().run()
