@echo off
echo 중국어 학습 OCR 프로그램을 시작합니다...
set PYTHONPATH=%PYTHONPATH%;%cd%\app
call venv\Scripts\activate
streamlit run app/ui.py
pause