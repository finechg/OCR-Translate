# OCR & Translation FastAPI Server

A personal OCR and translation system built to read Chinese publications in Korean. 
The project started as a small personal application and gradually evolved into a 
FastAPI-based backend with parallel processing, caching, and native modules written 
in Go and Rust.

I used AI tools including ChatGPT, Gemini, Claude, and Replit extensively as 
development and debugging assistants throughout the project. The overall architecture, 
feature requirements, and decisions about what to build were driven by my own 
requirements and problem-solving process.

The system is designed to make efficient use of limited server resources through 
CPU affinity (core pinning), separating API workloads from CPU-intensive OCR 
processing.

---

## 🚀 Key Features

- **FastAPI Backend Migration**
  - Removed dependencies on the legacy PySide6/Kivy GUI and local `JsonStore` storage.
  - Restructured the application into a REST API designed for Linux server environments.

- **CPU Core Pinning**
  - Reserved dedicated CPU cores for system and API workloads.
  - Assigned CPU-intensive OCR workers to separate cores to prevent heavy processing 
    from affecting API responsiveness.

- **Native Module Integration**
  - **Go (`translate_caller`)**: Translation API communication and concurrent request handling using goroutines.
  - **Rust (`fast_text_refiner`)**: Text cleanup and noise refinement for OCR output and translations.

- **Parallel Processing & Caching**
  - Page-by-page parallel OCR processing using Python `multiprocessing.Pool`.
  - Cross-language caching using `OcrCache` and sentence-level caching to reduce 
    redundant processing and repeated API calls.

---

## 🛠️ Tech Stack

- **Backend**: FastAPI, Uvicorn
- **Core Processing**: Python, Multiprocessing, PyMuPDF, Pytesseract
- **Native Modules**: Go, Rust
- **AI / API**: Google Gemini API

---

## ⚙️ Configuration

Configuration is managed through JSON and environment variables.

- **API Key**
  - Set the `GEMINI_API_KEY` environment variable.

- **CPU Allocation**
  ```python
  # CPU cores dedicated to OCR workers
  ALLOWED_OCR_CORES = [2, 3, 4, 5, 6, 7]
