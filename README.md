# OCR Translate Project

## Overview
An OCR-based multilingual document translation system leveraging Google Cloud Translation API and GPT refinement. Supports PDF, EPUB, and other document formats with high-quality automatic translation.

## Features
- OCR processing and sentence-level translation  
- SQLite-based caching system with cross-linked translation support  
- GPT-powered refinement and user feedback integration  
- Tab-based GUI for intuitive workflow management

## Installation
1. Install Python 3.11 or higher  
2. Install required packages:  
   ```bash
   pip install -r requirements.txt
   ```
3. Place your Google Cloud API key in `keys.txt` (this file is excluded from version control)  
4. Run the GUI:  
   ```bash
   python -m ocr_translate.ui.main_window
   ```

## Usage
- Load documents (PDF, EPUB) and start OCR and translation  
- Monitor translation progress in the GUI tabs  
- Manage translation cache and provide feedback for GPT refinement

## Contribution
- Internal keys (`keys.txt`) and cache directories (`cache/`) are excluded from version control  
- Bug reports, feature requests, and pull requests are welcome  
- Please follow code style and commit message guidelines

## License
This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**. See the [LICENSE](LICENSE) file for details.
