# OCR-Translate

A modular, high-performance OCR-based multilingual document translation system.  
Combining Google Cloud Translation API, GPT-based post-processing, and multi-language system components (Python, Go, Rust, C++), this tool provides a streamlined pipeline for scanning, translating, and exporting documents—designed for single-user precision, powered by open-source flexibility.

---

## Overview

OCR_Translate_Modularized enables automatic extraction and translation of scanned documents (PDFs, images, EPUBs) with high-quality output and local caching for performance optimization.

This project is built with:

- Google Cloud Translation API for baseline translations  
- GPT-4 for post-translation naturalization  
- SQLite multi-tier caching for efficient reuse  
- ReportLab PDF rendering with full CJK font support  
- Modular codebase in Python, Go, Rust, and C++  
- PySide6 tab-based GUI for streamlined interaction  

---

## Features

- OCR processing and sentence-level translation  
- GPT-powered refinement with optional feedback integration  
- SQLite-based tiered caching (`translation_cache00.db`, `...01.db`, etc.)  
- Modular architecture with Go (API caller), Rust (text refiner), C++ (cache writer)  
- OTF-compatible PDF output with full Unicode/CJK font support  
- Intuitive tab-based GUI with live progress tracking  
- AIHub-style bilingual corpus compatibility (KR-CN, KR-EN)  

---

## Installation

### Prerequisites

- Python 3.11 or higher  
- Google Cloud Translation API key (saved as `keys.txt`, not tracked by Git)

### Setup

```bash
pip install -r requirements.txt
# Optional: build native modules and launch GUI
bash scripts/run_gui.sh
```

---

## Usage

```bash
python -m ocr_translate.ui.main_window
```

1. Load scanned PDFs, images, or EPUB files  
2. Perform OCR and translate sentence-by-sentence  
3. Review and manage translations via the cache view  
4. Export final translated documents as high-quality PDFs  

---

## Architecture

- Input: PDF/Image  
  ↓  
- OCR Engine  
  ↓  
- Sentence Splitter  
  ↓  
- Cache Lookup ↔ GPT ↔ Google API  
  ↓  
- Post-processing (Rust)  
  ↓  
- PDF Rendering (ReportLab)  
  ↓  
- GUI / Output File

---

## Modules

| Language | Module                | Purpose                              |
|----------|-----------------------|--------------------------------------|
| Python   | `core/`               | Main pipeline, GPT handler, GUI      |
| Rust     | `fast_text_refiner/`  | Fast text normalization, CJK handling |
| Go       | `translate_caller.go` | API caller for Google Translation    |
| C++      | `cache_writer.cpp`    | High-speed bulk cache writer         |
| Bash     | `run_gui.sh`          | Full pipeline launcher               |

---

## Directory Structure

```plaintext
core/                → Python core modules  
ui/                  → GUI built with PySide6  
cpp_modules/         → C++ fast cache handler  
go_modules/          → Go API caller  
rust_modules/        → Rust refiner module  
scripts/             → Shell scripts for execution  
cache/               → Tiered SQLite cache DBs  
config/, test_data/  → Supporting assets and test cases  
README.md            → You are here  
LICENSE              → GPL-3.0  
```

---

## Contribution

This is a single-user system developed for performance and self-sufficiency.  
However, bug reports and feature requests are welcome.

- Pull requests are accepted if well-contained and documented  
- Please respect the modular architecture  
- Core logic changes should be discussed in advance  

---

## License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0).  
You may freely use, modify, and redistribute the code, but all derivative works must also be open-sourced under the same license.

---

> Built for precision, optimized for speed, and open by design — but still, I made it for me.
