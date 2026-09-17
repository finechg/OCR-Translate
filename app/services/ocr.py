import numpy as np
import cv2
from paddleocr import PaddleOCR
import logging
import asyncio
import psutil

logging.getLogger("ppocr").setLevel(logging.ERROR)

class OCRService:
    def __init__(self):
        # 코어 설정 (0번 제외)
        p = psutil.Process()
        all_cores = list(range(psutil.cpu_count()))
        if len(all_cores) > 1:
            p.cpu_affinity(all_cores[1:])
        
        self.ocr_engine = PaddleOCR(
            lang='ch',
            use_angle_cls=True,
            show_log=False,
            enable_mkldnn=True,
            cpu_threads=max(1, len(all_cores)-1),
            rec_batch_num=10,
            version='PP-OCRv4'
        )
        # 중요: PaddleOCR 엔진 보호를 위한 세마포어 (한 번에 1개만 처리)
        self.lock = asyncio.Semaphore(1)

    async def extract_text(self, image_bytes: bytes) -> str:
        # 엔진 보호: 이전 페이지 OCR이 끝나야 다음 페이지가 들어감
        async with self.lock:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._run_ocr_sync, image_bytes)
            
            if not result or not result[0]:
                return ""
            return " ".join([line[1][0] for line in result[0] if line])

    def _run_ocr_sync(self, image_bytes: bytes):
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None: return None
        # 메모리 에러 방지를 위해 명시적으로 실행
        return self.ocr_engine.ocr(img, cls=True)