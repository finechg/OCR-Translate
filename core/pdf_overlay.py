import fitz  # PyMuPDF
from pathlib import Path

def write_text_on_pdf(input_pdf, texts_by_page, output_pdf):
    doc = fitz.open(input_pdf)
    for i, page in enumerate(doc):
        if i in texts_by_page:
            text = texts_by_page[i]
            rect = fitz.Rect(50, 50, 550, 750)  # 여백 포함 전체
            page.insert_textbox(rect, text, fontsize=9, color=(0, 0, 0), overlay=True)
    doc.save(output_pdf)

if __name__ == "__main__":
    # 예시 실행
    test_pdf = "example.pdf"
    out_pdf = "translated_output.pdf"
    dummy_texts = {0: "첫 페이지 번역문입니다.", 1: "두 번째 페이지입니다."}
    write_text_on_pdf(test_pdf, dummy_texts, out_pdf)