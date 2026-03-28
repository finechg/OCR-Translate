import requests

class GeminiOCRTranslate:
    def __init__(self):
        self.api_url = 'https://api.gemini.com/translate'  # Example URL
        self.headers = {'Authorization': 'Bearer YOUR_API_KEY'}  # Add your API key here

    def translate_image(self, image_path):
        with open(image_path, 'rb') as image_file:
            response = requests.post(self.api_url, headers=self.headers, files={'file': image_file})
        return response.json()

    def translate_conversation(self, conversation):
        response = requests.post(self.api_url, headers=self.headers, json={'text': conversation})
        return response.json()

# Example usage:
# translator = GeminiOCRTranslate()
# translation_result = translator.translate_image('path_to_your_image.jpg')
# print(translation_result)
# conversation_result = translator.translate_conversation('Hello, how are you?')
# print(conversation_result)