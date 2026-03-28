import google.generativeai as genai
import PIL.Image

class GeminiOCRTranslate:
    def __init__(self, api_key):
        # 1. API 설정
        genai.configure(api_key=api_key)
        # 2. Gemini 3 Flash 모델 선택
        self.model = genai.GenerativeModel('gemini-3-flash')

    def process_all(self, image_path):
        """이미지를 읽어서 텍스트 추출과 번역을 한 번에 수행"""
        img = PIL.Image.open(image_path)
        
        # 프롬프트: 자연스러운 번역지침
        prompt = (
            "이미지 속의 모든 중국어를 찾아서 한국어로 번역해줘. "
            "의역은 오역과 같으니 최대한 원문 그대로 번역하고, "
            "결과는 번역문만 깔끔하게 텍스트로 출력해."
        )
        
        # 3. 클라우드 엔진 가동 (OCR + 번역 통합)
        response = self.model.generate_content([prompt, img])
        return response.text

    def translate_text(self, text):
        """단순 텍스트(대화) 번역"""
        prompt = f"다음 중국어 문장을 한국어로 번역해: '{text}'"
        response = self.model.generate_content(prompt)
        return response.text

# --- 사용법 (탭 S9 터미널용) ---
# 1. API 키를 넣으세요
# translator = GeminiOCRTranslate("여기에_API_KEY_입력")

# 2. 이미지 번역 테스트
# print(translator.process_all('test_image.jpg'))

# 3. 일반 대화 번역 테스트
# print(translator.translate_text("你好，今天天气怎么样？"))
