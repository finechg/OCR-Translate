import google.generativeai as genai
import PIL.Image
from cache.cross_lingual_cache import CrossLingualCache

class GeminiOCRTranslate:
    def __init__(self, api_key, model_name='gemini-1.5-flash'):
        # 1. API 설정
        genai.configure(api_key=api_key)
        # 2. 실제 지원되는 Gemini 모델 선택
        self.model = genai.GenerativeModel(model_name)
        # 3. 서버/로컬 공용 캐시 매니저 장착
        self.cache = CrossLingualCache()

    def process_all(self, image_path):
        """이미지를 읽어서 텍스트 추출과 번역을 한 번에 수행"""
        img = PIL.Image.open(image_path)
        
        prompt = (
            "이미지 속의 모든 중국어를 찾아서 한국어로 번역해줘. "
            "의역은 오역과 같으니 최대한 원문 그대로 번역하고, "
            "결과는 번역문만 깔끔하게 텍스트로 출력해."
        )
        
        response = self.model.generate_content([prompt, img])
        result_text = response.text.strip()
        
        return result_text

    def translate_text(self, text):
        """단순 텍스트 번역 (캐시 연동 적용)"""
        # 1. API 호출 전 캐시 검사로 비용 절감 및 속도 극대화
        cached = self.cache.cache.get_entry(text)
        if cached:
            return cached

        prompt = f"다음 중국어 문장을 의역 없이 원문 그대로 한국어로 번역해줘. 결과만 출력해: '{text}'"
        response = self.model.generate_content(prompt)
        translated = response.text.strip()
        
        # 2. 새로운 번역 결과는 교차 캐시에 자동 누적
        if translated:
            self.cache.add_crosslinked({"zh": text}, translated)
            
        return translated
