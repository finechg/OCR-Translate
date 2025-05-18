# OCR_Translate_Modularized

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
