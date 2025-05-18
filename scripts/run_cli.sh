#!/bin/bash
# CLI 기반 OCR Translate 자동 처리기

export PYTHONPATH=$(pwd)
export GOOGLE_PROJECT_ID="your_project_id"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your_service_account.json"

python3 core/refined_translate_pipeline.py --input test_data/input.txt --output result.txt