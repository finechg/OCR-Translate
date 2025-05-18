from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# 폰트 등록
font_path = "assets/SourceHanSansSC-Regular.otf"
if os.path.exists(font_path):
    pdfmetrics.registerFont(TTFont("SourceHan", font_path))
    DEFAULT_FONT = "SourceHan"
else:
    DEFAULT_FONT = "Helvetica"  # fallback
from reportlab.lib.units import mm

def write_chapters_to_pdf(chapters, output_path="output.pdf", title="EPUB 번역본"):
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    margin = 20 * mm
    max_width = width - 2 * margin
    y = height - margin

    c.setFont(DEFAULT_FONT, 16)
    c.drawString(margin, y, title)
    y -= 30

    for i, text in enumerate(chapters):
        c.setFont(DEFAULT_FONT, 14)
        c.drawString(margin, y, f"Chapter {i+1}")
        y -= 20

        c.setFont(DEFAULT_FONT, 11)
        for line in text.splitlines():
            if y < margin + 20:
                c.showPage()
                y = height - margin
            c.drawString(margin, y, line.strip())
            y -= 15

        y -= 30

    c.save()

if __name__ == "__main__":
    write_chapters_to_pdf(["첫 번째 장 텍스트입니다.", "두 번째 장 텍스트입니다."])