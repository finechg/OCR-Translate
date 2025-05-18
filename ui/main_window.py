from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QTextEdit, QVBoxLayout, QLabel
import subprocess, json

# Rust 모듈 import
try:
    from fast_text_refiner import refine_text
except ImportError:
    def refine_text(text): return text  # Fallback

# C++ 모듈 import
try:
    import cache_writer
except ImportError:
    cache_writer = None

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OCR Translate GUI")
        self.setMinimumSize(600, 400)

        self.input_text = QTextEdit()
        self.output_text = QTextEdit()
        self.translate_btn = QPushButton("Translate")
        self.status_label = QLabel("")

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Input Text"))
        layout.addWidget(self.input_text)
        layout.addWidget(self.translate_btn)
        layout.addWidget(QLabel("Translated Output"))
        layout.addWidget(self.output_text)
        layout.addWidget(self.status_label)
        self.setLayout(layout)

        self.translate_btn.clicked.connect(self.on_translate)

    def on_translate(self):
        text = self.input_text.toPlainText().strip()
        if not text:
            self.status_label.setText("Please enter text.")
            return

        # 1. Rust로 정제
        refined = refine_text(text)

        # 2. 로컬 캐시 확인 (건너뜀 - 데모)
        translated = self.call_translate_go(refined)

        # 3. C++ 캐시에 저장
        if cache_writer:
            cache_writer.insert_translation("translation_cache.db", refined, translated, "ko_zh")

        # 4. 결과 출력
        self.output_text.setPlainText(translated)
        self.status_label.setText("Translated and cached.")

    def call_translate_go(self, text):
        req = {
            "text": text,
            "source_lang": "ko",
            "target_lang": "zh"
        }
        try:
            proc = subprocess.Popen(
                ["go", "run", "translate_caller.go"],
                cwd="../go_modules/translate_caller",
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            out, err = proc.communicate(input=json.dumps(req), timeout=10)
            return json.loads(out)["translated_text"]
        except Exception as e:
            return f"[Error] {str(e)}"

if __name__ == "__main__":
    app = QApplication([])
    win = MainWindow()
    win.show()
    app.exec()