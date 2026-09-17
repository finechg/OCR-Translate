import streamlit as st
import time
import asyncio
import io
from main import process_single_page, exporter, ocr_service
import pymupdf as fitz
from urllib.parse import quote

st.set_page_config(page_title="중국어 학습 OCR 번역기", layout="wide")

st.title("🇨🇳 중국어 학습 OCR & DeepL 번역기")
st.markdown("---")

# 사이드바 설정
with st.sidebar:
    st.header("⚙️ 설정")
    uploaded_file = st.file_uploader("파일 업로드 (PDF, 이미지)", type=["pdf", "png", "jpg", "jpeg"])
    
    col1, col2 = st.columns(2)
    with col1:
        start_pg = st.number_input("시작 페이지", min_value=1, value=1)
    with col2:
        end_pg = st.number_input("끝 페이지", min_value=1, value=1)
    
    output_format = st.selectbox("내보내기 형식", ["html", "word"])
    run_button = st.button("🚀 번역 시작", use_container_key=True)

# 메인 화면 로직
if run_button and uploaded_file:
    start_time = time.time() # 시간 측정 시작
    
    try:
        page_tasks = []
        file_bytes = uploaded_file.read()
        
        # 1. 파일 처리 및 태스크 생성
        if uploaded_file.name.lower().endswith(".pdf"):
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            s_idx, e_idx = max(0, start_pg - 1), min(doc.page_count, end_pg)
            
            st.info(f"총 {e_idx - s_idx}페이지를 분석합니다...")
            
            for i in range(s_idx, e_idx):
                page = doc.load_page(i)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                page_tasks.append(process_single_page(i + 1, pix.tobytes("png")))
            doc.close()
        else:
            page_tasks.append(process_single_page(1, file_bytes))

        # 2. 프로그레스 바 및 시간 표시
        progress_bar = st.progress(0)
        status_text = st.empty()
        timer_text = st.empty()

        # 비동기 작업 실행
        async def run_tasks():
            return await asyncio.gather(*page_tasks)

        # 작업을 수행하는 동안 타이머 업데이트 (간이 구현)
        with st.spinner("AI가 분석 중입니다..."):
            results = asyncio.run(run_tasks())
        
        end_time = time.time()
        duration = end_time - start_time
        
        st.success(f"✅ 분석 완료! (총 소요 시간: {duration:.2f}초)")

        # 3. 결과 대시보드
        st.markdown("### 📊 분석 결과 미리보기")
        for res in results:
            with st.expander(f"📄 Page {res.page_number} 결과 보기"):
                st.write("**[원문]**")
                st.info(res.original_text)
                st.write("**[번역]**")
                st.success(res.translated_text)
                
                if res.footer_vocab:
                    st.write("**[단어장]**")
                    st.table([{"단어": v.word, "병음": v.pinyin, "의미": v.meaning} for v in res.footer_vocab])

        # 4. 다운로드 버튼
        st.markdown("---")
        if output_format == "html":
            html_data = exporter.to_html(results)
            st.download_button(
                label="파일 다운로드 (HTML)",
                data=html_data,
                file_name=f"study_{uploaded_file.name}.html",
                mime="text/html"
            )
        else:
            word_stream = exporter.to_word_stream(results)
            st.download_button(
                label="파일 다운로드 (Word)",
                data=word_stream,
                file_name=f"study_{uploaded_file.name}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")

elif run_button:
    st.warning("파일을 먼저 업로드해주세요.")