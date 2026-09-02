# OCR & Translation FastAPI Server

A personal OCR and translation system built to read Chinese publications in Korean. It started as a small personal project and has gradually evolved from a mobile application into a FastAPI-based backend with parallel processing, caching, and native modules in Go and Rust.

The system is designed to make efficient use of limited server resources, using CPU affinity (core pinning) to separate high-performance (P-core) and efficiency (E-core) workloads.

---

## 🚀 Key Features

- **FastAPI Backend Migration**  
  Completely removed dependencies on legacy PySide6/Kivy GUI and local storage (`JsonStore`), restructuring into a standard REST API optimized for Linux server environments.
- **CPU Core Pinning Optimization**  
  Reserved the high-performance core (Core 0) exclusively for the main system and API response handling, while restricting heavy parallel OCR and translation workers to user-designated low-performance core (E-core) regions to ensure system stability.
- **High-Performance Native Module Integration**  
  - **Go (`translate_caller`)**: High-speed API communication and translation call bridge utilizing goroutines.
  - **Rust (`fast_text_refiner`)**: High-speed noise refinement for extracted texts and translations.
- **High-Speed Parallel Processing and Caching**  
  - Page-by-page parallel OCR processing based on `multiprocessing.Pool`.
  - Cross-language caching system (`OcrCache`, sentence-level cache) introduced to minimize redundant computations and repetitive API calls.

---

## 🛠️ Tech Stack

- **Backend Framework**: FastAPI, Uvicorn
- **Core Processing**: Python (Multiprocessing, PyMuPDF/fitz, Pytesseract)
- **Native Modules**: Go, Rust
- **AI / API**: Google Gemini API

---

## ⚙️ Configuration & Environment Variables (`config/config.py`)

Configurations are managed via standard JSON and environment variables tailored for the server environment.

- **API Key Setting**: Register the environment variable `GEMINI_API_KEY` or manage it through the configuration file.
- **Core Allocation Setting**:
  ```python
  # Specify dedicated cores for OCR workers, excluding main system core 0
  ALLOWED_OCR_CORES = [1, 2, 3, 4, 5, 6, 7]
  # To explain the high-performance core (Core 0) and low-performance core (E-core) mentioned in the middle, personally, I thought of cores 0 and 1 as important cores, and the remaining cores as general, low-performance, low-power cores.
