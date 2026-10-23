# 🌐 Advanced Translator (Streamlit) — Themed Edition

Modern translator with **Voice / Text / Image (OCR)**, **multi-theme UI**, gradient header, hover animations, and a clean Settings page with live preview.

## 🧰 Windows Setup
```bat
cd advanced_translator_streamlit_themes
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```
### Install Tesseract OCR
- Download for Windows: https://github.com/UB-Mannheim/tesseract/wiki
- Add `C:\Program Files\Tesseract-OCR` to PATH
- Verify: `tesseract --version`

### (Optional) Enable Microphone on Windows
`pyaudio` can be installed via pipwin:
```bat
pip install pipwin
pipwin install pyaudio
```

## 🚀 Run
```bat
streamlit run app.py
```

Open the browser (usually http://localhost:8501).

## 🎛️ Features
- 🎤 Voice: speech → text → translation → speech
- ⌨️ Text: manual input → translation → speech
- 🖼️ Image: OCR (pytesseract) → translation → speech
- 50+ common languages (googletrans)
- Sidebar navigation: Voice / Text / Image / Settings
- Settings page: theme selection, animation toggle, reset, **live preview**
- Gradient header bar matching theme
- Hover animations, copy/download buttons
- Graceful handling for empty inputs/unreadable images

## 📁 Structure
```
advanced_translator_streamlit_themes/
├─ app.py
├─ requirements.txt
├─ README.md
└─ utils/
   ├─ translation.py
   ├─ speech.py
   ├─ ocr.py
   ├─ widgets.py
   └─ theme_manager.py
```

## ℹ️ Notes
- If Google services rate-limit, consider offline STT/TTS/translation backends.
- For better OCR, use clear, high-contrast images.
