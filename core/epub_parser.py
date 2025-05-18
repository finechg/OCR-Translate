from ebooklib import epub
from bs4 import BeautifulSoup

def extract_epub_text_by_chapter(epub_path):
    book = epub.read_epub(epub_path)
    chapters = []
    for item in book.get_items():
        if item.get_type() == epub.EpubHtml:
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            chapter_text = soup.get_text(separator='\n').strip()
            if chapter_text:
                chapters.append(chapter_text)
    return chapters

if __name__ == "__main__":
    chapters = extract_epub_text_by_chapter("example.epub")
    for i, ch in enumerate(chapters):
        print(f"--- Chapter {i+1} ---\n{ch[:200]}...\n")