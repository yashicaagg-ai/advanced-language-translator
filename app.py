import pytesseract
# Set the path to tesseract.exe
pytesseract.pytesseract.tesseract_cmd = "C:\\Users\\Piyus\\Downloads\\tesseract-ocr-w64-setup-5.5.0.20241111(2).exe"
import streamlit as st
import asyncio
import speech_recognition as sr
from googletrans import Translator, LANGUAGES
from gtts import gTTS
import pytesseract
from PIL import Image
import os
import io
from pydub import AudioSegment
from streamlit_mic_recorder import mic_recorder

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
        st.session_state.source_lang = st.selectbox(
            "Source Language",
            list(LANGUAGE_NAMES.keys()),
            index=0,
            key="speech_source_lang"
        )

    with col2:
        language_keys = list(LANGUAGE_NAMES.keys())
        english_index = (
            language_keys.index("English")
            if "English" in language_keys else 0
        )

        st.session_state.target_lang = st.selectbox(
            "Target Language",
            language_keys,
            index=english_index,
            key="speech_target_lang"
        )

    st.write("Click Start Recording, speak, and then stop recording.")

    audio_data = mic_recorder(
        start_prompt="🎙️ Start Recording",
        stop_prompt="⏹️ Stop Recording",
        just_once=True,
        use_container_width=True,
        key="Speech_recorder"
    )


if audio_data and audio_data.get("bytes"):
    try:
        recognizer = sr.Recognizer()
        audio_bytes = audio_data["bytes"]

        # Convert browser-recorded audio to WAV
        try:
            audio_segment = AudioSegment.from_file(
                io.BytesIO(audio_bytes)
            )
            wav_buffer = io.BytesIO()
            audio_segment.export(
                wav_buffer,
                format="wav"
            )
            wav_buffer.seek(0)

        except Exception as audio_error:
            st.error(
                f"Could not convert recording to WAV: {audio_error}"
            )
            st.stop()

        # Recognize speech from converted WAV audio
        with sr.AudioFile(wav_buffer) as source:
            audio = recognizer.record(source)

        text = recognizer.recognize_google(audio)
        st.success(f"**You said:** {text}")

        src_lang_code = LANGUAGE_NAMES[
            st.session_state.source_lang
        ]
        dest_lang_code = LANGUAGE_NAMES[
            st.session_state.target_lang
        ]

        # Detect source language when Auto is selected
        if src_lang_code == "auto":
            detected = translator.detect(text)
            src_lang_code = detected.lang

            st.info(
                "Detected Language: "
                + LANGUAGE_CODES.get(
                    detected.lang, detected.lang
                )
            )

        # Translate recognized text
        translated = translator.translate(
            text,
            src=src_lang_code,
            dest=dest_lang_code
        )

        st.success(f"**Translated:** {translated.text}")

        # Speak translated result
        speak_text(translated.text, dest_lang_code)

    except sr.UnknownValueError:
        st.error("Sorry, I could not understand the audio.")

    except sr.RequestError as e:
        st.error(f"Speech recognition service error: {e}")

    except Exception as e:
        st.error(f"Translation or recording error: {e}")



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
                translated = asyncio.run(translate_text())
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

    uploaded_file = st.file_uploader(
        "Upload an image",
        type=["png", "jpg", "jpeg"],
        key="image_uploader"
    )

    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file).convert("RGB")

            st.image(
                image,
                caption="Uploaded Image",
                use_container_width=True
            )

            # Set the correct Tesseract path
            import os
            import shutil

            if os.name == "nt":
                pytesseract.pytesseract.tesseract_cmd = (
                    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
                )
            else:
                pytesseract.pytesseract.tesseract_cmd = (
                    shutil.which("tesseract") or "/usr/bin/tesseract"
                )

            # Extract text from image
            extracted_text = pytesseract.image_to_string(image)

            st.session_state.image_text = extracted_text

            if extracted_text.strip():
                st.text_area(
                    "Extracted Text",
                    extracted_text,
                    key="extracted_image_text"
                )

                col1, col2 = st.columns(2)

                language_keys = list(LANGUAGE_NAMES.keys())

                with col1:
                    source_lang = st.selectbox(
                        "Source Language",
                        language_keys,
                        index=0,
                        key="img_src"
                    )

                with col2:
                    english_index = (
                        language_keys.index("English")
                        if "English" in language_keys else 0
                    )

                    target_lang = st.selectbox(
                        "Target Language",
                        language_keys,
                        index=english_index,
                        key="img_tgt"
                    )

                if st.button(
                    "Translate Image Text",
                    key="translate_image"
                ):
                    try:
                        src_lang_code = LANGUAGE_NAMES[source_lang]
                        dest_lang_code = LANGUAGE_NAMES[target_lang]
                        if src_lang_code == "auto":
                            detected = asyncio.run(translator.detect(extracted_text))
                            st.info(
                                "Detected Language: " 
                                + LANGUAGE_CODES.get(detected.lang, detected.lang)
                            )
                        src_lang_code = detected.lang
                        translated = await translator.translate(
                            
                                extracted_text,
                                src=src_lang_code,
                                dest=dest_lang_code
                            
                        )

                        st.session_state.image_translation = translated.text

                        st.success(
                            f"**Translated Text:** {translated.text}"
                        )

                        speak_text(translated.text, dest_lang_code)

                    except Exception as e:
                        st.error(f"Translation error: {e}")

            else:
                st.warning(
                    "No readable text found in the image. "
                    "Please upload a clearer image."
                )

        except Exception as e:
            st.error(f"OCR Error: {e}")



# ---------- Reset Button ----------
st.sidebar.button("🔄 Reset All", on_click=reset_all)
