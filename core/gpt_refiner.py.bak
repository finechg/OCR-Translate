import os
import openai
import logging
from cache.rewrite_cache_manager import RewriteCacheManager
from config import KEYS

REWRITE_ENGINE = os.getenv("GPT_REWRITE_ENGINE", "gpt-4.1-mini")
OPENAI_API_KEY = KEYS.get("OPENAI")

openai.api_key = OPENAI_API_KEY

cache = RewriteCacheManager()

def rewrite_with_gpt(text, temperature=0.4):
    cached = cache.get(text)
    if cached:
        logging.info("리라이팅 캐시 적중")
        return cached

    prompt = f"다음 문장을 더 자연스럽고 부드럽게 다듬어줘. 의미는 유지하고 문장 표현만 개선해줘:\n\n{text}"

    try:
        response = openai.ChatCompletion.create(
            model=REWRITE_ENGINE,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        rewritten = response.choices[0].message.content.strip()
        cache.add(text, rewritten)
        return rewritten
    except Exception as e:
        logging.warning(f"GPT 리라이팅 실패: {e}")
        return text