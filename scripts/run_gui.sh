#!/bin/bash
# Rust, Go, C++ 연동된 PySide6 GUI 실행

export PYTHONPATH=$(pwd)
export GOOGLE_PROJECT_ID="your_project_id"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your_service_account.json"

cd ui
python3 main_window.py