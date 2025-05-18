from PySide6.QtWidgets import (
    QMainWindow, QFileDialog, QPushButton, QTextEdit,
    QVBoxLayout, QWidget, QLabel, QProgressBar, QApplication
)
from PySide6.QtCore import QObject, Signal, QThreadPool


class SignalHandler(QObject):
    page_done = Signal(int, str)
    finished = Signal()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OCR Translate GUI")
        self.setGeometry(300, 200, 800, 600)

        self.text_output = QTextEdit(self)
        self.text_output.setReadOnly(True)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        self.status_label = QLabel("상태: 대기 중", self)

        self.translate_button = QPushButton("PDF 선택 및 번역", self)
        self.translate_button.clicked.connect(self.run_translate)

        self.cancel_button = QPushButton("중단", self)
        self.cancel_button.clicked.connect(self.cancel_translation)

        self.save_button = QPushButton("결과 저장", self)
        self.save_button.clicked.connect(self.save_result)

        self.epub_button = QPushButton("EPUB 번역 → PDF 저장", self)
        self.epub_button.clicked.connect(self.run_epub_translate)

        layout = QVBoxLayout()
        layout.addWidget(self.translate_button)
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.cancel_button)
        layout.addWidget(self.save_button)
        layout.addWidget(self.epub_button)
        layout.addWidget(self.text_output)

        self.cancel_requested = False

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.thread_pool = QThreadPool()

    def run_translate(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "PDF 파일 선택", "", "PDF Files (*.pdf)"
        )
        if not file_path:
            return

        self.signal_handler = SignalHandler()
        self.signal_handler.page_done.connect(self.handle_page_done)
        self.signal_handler.finished.connect(self.handle_finished)

        from core.translate import TranslateWorker
        self.worker = TranslateWorker(file_path, self.signal_handler)
        self.thread_pool.start(self.worker)

        self.page_results = {}
        self.total_pages = 0  # TODO: 실제 페이지 수로 초기화 필요
        self.completed_pages = 0
        self.status_label.setText("상태: 처리 중...")
        self.progress_bar.setValue(0)

    def handle_page_done(self, index, result):
        self.page_results[index] = result
        self.completed_pages += 1

        percent = int((self.completed_pages / max(1, self.total_pages)) * 100)
        self.progress_bar.setValue(percent)

    def handle_finished(self):
        output = "\n\n".join(self.page_results[k] for k in sorted(self.page_results))
        self.text_output.setPlainText(output)
        self.status_label.setText("상태: 완료됨")
        self.progress_bar.setValue(100)

    def cancel_translation(self):
        self.cancel_requested = True
        self.status_label.setText("상태: 중단 요청됨")
        # TODO: TranslateWorker에 취소 신호 전달 구현 필요

    def save_result(self):
        if not hasattr(self, "page_results") or not self.page_results:
            return
        path, _ = QFileDialog.getSaveFileName(self, "결과 저장", "", "Text Files (*.txt)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                for k in sorted(self.page_results):
                    f.write(self.page_results[k] + "\n\n")
            self.status_label.setText("상태: 결과 저장 완료")

    def run_epub_translate(self):
        from core.epub_translate import translate_epub_to_chapters
        from core.pdf_writer import write_chapters_to_pdf

        epub_path, _ = QFileDialog.getOpenFileName(self, "EPUB 파일 선택", "", "EPUB Files (*.epub)")
        if not epub_path:
            return

        self.status_label.setText("상태: EPUB 번역 중...")
        QApplication.processEvents()

        try:
            chapters = translate_epub_to_chapters(epub_path)
            save_path, _ = QFileDialog.getSaveFileName(self, "저장 위치 선택", "", "PDF Files (*.pdf)")
            if save_path:
                write_chapters_to_pdf(chapters, save_path)
                self.status_label.setText("상태: EPUB 변환 완료")
        except Exception as e:
            self.status_label.setText(f"상태: 오류 발생 - {e}")
