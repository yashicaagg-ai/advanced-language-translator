import pytesseract
# Set the path to tesseract.exe
pytesseract.pytesseract.tesseract_cmd = "C:\\Users\\Piyus\\Downloads\\tesseract-ocr-w64-setup-5.5.0.20241111(2).exe"
import streamlit as st
import speech_recognition as sr
from googletrans import Translator, LANGUAGES
from gtts import gTTS
import pytesseract
from PIL import Image
import os
import io

# ---------- Configure Tesseract Path (Windows only) ----------
# If installed in a custom directory, update this path
# Example: r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ---------- Initialize ----------
translator = Translator()

# Build language dictionary with Auto Detect
LANGUAGE_NAMES = {"Auto Detect": "auto"}
LANGUAGE_NAMES.update({name.title(): code for code, name in LANGUAGES.items()})
LANGUAGE_CODES = {v: k for k, v in LANGUAGE_NAMES.items()}  # reverse map

# ---------- App Config ----------
st.set_page_config(
    page_title="🌐 Advanced AI-Powered Translator",
    layout="wide"
)

# ---------- Session State ----------
if "input_text" not in st.session_state:
    st.session_state.input_text = ""
if "translated_text" not in st.session_state:
    st.session_state.translated_text = ""
if "source_lang" not in st.session_state:
    st.session_state.source_lang = "Auto Detect"
if "target_lang" not in st.session_state:
    st.session_state.target_lang = "English"
if "image_text" not in st.session_state:
    st.session_state.image_text = ""
if "image_translation" not in st.session_state:
    st.session_state.image_translation = ""


# ---------- Reset Function ----------
def reset_all():
    st.session_state.input_text = ""
    st.session_state.translated_text = ""
    st.session_state.source_lang = "Auto Detect"
    st.session_state.target_lang = "English"
    st.session_state.image_text = ""
    st.session_state.image_translation = ""


# ---------- Text-to-Speech ----------
def speak_text(text, lang_code):
    try:
        tts = gTTS(text=text, lang=lang_code)
        tts.save("output.mp3")
        st.audio("output.mp3", format="audio/mp3")
    except Exception as e:
        st.error(f"Speech output error: {e}")


# ---------- Main Layout ----------
st.title("🌐 Advanced AI-Powered Language Translator")

tab1, tab2, tab3 = st.tabs(["🎤 Voice Translator", "⌨️ Text Translator", "🖼️ Image Translator"])

# ---------- Voice Translator ----------
with tab1:
    st.subheader("🎤 Speak and Translate")

    col1, col2 = st.columns(2)
    with col1:
        st.session_state.source_lang = st.selectbox("Source Language", list(LANGUAGE_NAMES.keys()), index=0)
    with col2:
        st.session_state.target_lang = st.selectbox("Target Language", list(LANGUAGE_NAMES.keys()), index=list(LANGUAGE_NAMES.keys()).index("English"))

    if st.button("🎙️ Record and Translate"):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("Listening... Please speak clearly.")
            try:
                audio = recognizer.listen(source, timeout=5)
                text = recognizer.recognize_google(audio)

                src_lang_code = LANGUAGE_NAMES[st.session_state.source_lang]
                if src_lang_code == "auto":
                    detected = translator.detect(text)
                    src_lang_code = detected.lang
                    st.info(f"Detected Language: {LANGUAGE_CODES.get(detected.lang, detected.lang)}")

                translated = translator.translate(
                    text,
                    src=src_lang_code,
                    dest=LANGUAGE_NAMES[st.session_state.target_lang]
                )
                st.success(f"**You said:** {text}")
                st.success(f"**Translated:** {translated.text}")
                speak_text(translated.text, LANGUAGE_NAMES[st.session_state.target_lang])
            except Exception as e:
                st.error(f"Error: {e}")

# ---------- Text Translator ----------
with tab2:
    st.subheader("⌨️ Text Translator")

    col1, col2 = st.columns(2)
    with col1:
        st.session_state.source_lang = st.selectbox("Source Language", list(LANGUAGE_NAMES.keys()), index=0, key="text_src")
    with col2:
        st.session_state.target_lang = st.selectbox("Target Language", list(LANGUAGE_NAMES.keys()), index=list(LANGUAGE_NAMES.keys()).index("English"), key="text_tgt")

    st.session_state.input_text = st.text_area("Enter text", st.session_state.input_text)

    if st.button("Translate Text"):
        if st.session_state.input_text.strip():
            import async
            async def translate_text() : 
                src_lang_code = LANGUAGE_NAMES[st.session_state.source_lang]
                if src_lang_code == "auto":
                    detected = await translator.detect(st.session_state.input_text)
                    src_lang_code = detected.lang
                    st.info(f"Detected Language: " f"{LANGUAGE_CODES.get(detected.lang, detected.lang)}")

                translated = await translator.translate(
                    st.session_state.input_text,
                    src=src_lang_code,
                    dest=LANGUAGE_NAMES[st.session_state.target_lang],
            )
                return translated
            try:   
                translated = asynico.run(translate_text())
                st.session_state.translated_text = translated.text
                st.success(f"**Translated:** {translated.text}")
                speak_text(translated.text, LANGUAGE_NAMES[st.session_state.target_lang],)
            except Exception as e: st.error(f"Translation failed: {e}")
        else:
            st.warning("Please enter some text.")

    if st.session_state.translated_text:
        st.download_button("📥 Download Translation", st.session_state.translated_text, file_name="translation.txt")

# ---------- Image Translator ----------
with tab3:
    st.subheader("🖼️ Image Translator")

    uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        try:
            extracted_text = pytesseract.image_to_string(image)
            st.session_state.image_text = extracted_text

            if extracted_text.strip():
                st.text_area("Extracted Text", extracted_text)

                col1, col2 = st.columns(2)
                with col1:
                    st.session_state.source_lang = st.selectbox("Source Language", list(LANGUAGE_NAMES.keys()), index=0, key="img_src")
                with col2:
                    st.session_state.target_lang = st.selectbox("Target Language", list(LANGUAGE_NAMES.keys()), index=list(LANGUAGE_NAMES.keys()).index("English"), key="img_tgt")

                if st.button("Translate Image Text"):
                    src_lang_code = LANGUAGE_NAMES[st.session_state.source_lang]
                    if src_lang_code == "auto":
                        detected = translator.detect(extracted_text)
                        src_lang_code = detected.lang
                        st.info(f"Detected Language: {LANGUAGE_CODES.get(detected.lang, detected.lang)}")

                    translated = translator.translate(
                        extracted_text,
                        src=src_lang_code,
                        dest=LANGUAGE_NAMES[st.session_state.target_lang]
                    )
                    st.session_state.image_translation = translated.text
                    st.success(f"**Translated Text:** {translated.text}")
                    speak_text(translated.text, LANGUAGE_NAMES[st.session_state.target_lang])
            else:
                st.warning("No readable text found in the image.")
        except Exception as e:
            st.error(f"OCR Error: {e}")

# ---------- Reset Button ----------
st.sidebar.button("🔄 Reset All", on_click=reset_all)
