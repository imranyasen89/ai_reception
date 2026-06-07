"""
speech_input.py
---------------
DHQ Hospital Lodhran - AI Receptionist
Speech-to-Text module using SpeechRecognition library.
Supports Urdu (ur-PK) and English (en-US) transcription via Google Speech API (free).
"""

import tempfile
import os

# ─── Availability Check ──────────────────────────────────────────────────────
STT_AVAILABLE = False
try:
    import speech_recognition as sr
    STT_AVAILABLE = True
except ImportError:
    pass


# ─── Language Configuration ──────────────────────────────────────────────────
LANGUAGES = {
    "urdu":    "ur-PK",
    "english": "en-US",
    "hindi":   "hi-IN",
}

DEFAULT_LANGUAGE = "urdu"


# ─── Core Transcription ──────────────────────────────────────────────────────
def transcribe_audio(audio_bytes: bytes, language: str = "urdu") -> dict:
    """
    Transcribe audio bytes (WAV format) to text.

    Args:
        audio_bytes: Raw audio data in WAV format (from st.audio_input)
        language: Language key ('urdu', 'english', 'hindi')

    Returns:
        dict with keys:
            - success (bool): Whether transcription succeeded
            - text (str): Transcribed text (empty on failure)
            - error (str): Error message if any
    """
    if not STT_AVAILABLE:
        return {
            "success": False,
            "text": "",
            "error": "SpeechRecognition library is not installed. Run: pip install SpeechRecognition"
        }

    if not audio_bytes:
        return {"success": False, "text": "", "error": "No audio data provided"}

    # Get language code
    lang_code = LANGUAGES.get(language, LANGUAGES[DEFAULT_LANGUAGE])

    try:
        # Save audio bytes to a temporary WAV file
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav", prefix="dhq_stt_")
        tmp_path = tmp.name
        tmp.write(audio_bytes)
        tmp.close()

        # Initialize recognizer
        recognizer = sr.Recognizer()

        # Adjust for ambient noise and recognize
        with sr.AudioFile(tmp_path) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.3)
            audio_data = recognizer.record(source)

        # Transcribe using Google Speech Recognition (free, no API key)
        text = recognizer.recognize_google(audio_data, language=lang_code)

        # Clean up temp file
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

        return {"success": True, "text": text.strip(), "error": ""}

    except sr.UnknownValueError:
        return {
            "success": False,
            "text": "",
            "error": "آواز سمجھ نہیں آئی — براہ کرم دوبارہ بولیں (Could not understand speech — please try again)"
        }
    except sr.RequestError as e:
        return {
            "success": False,
            "text": "",
            "error": f"انٹرنیٹ کنکشن کی خرابی (Speech service error): {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "text": "",
            "error": f"Error: {str(e)}"
        }
    finally:
        # Ensure cleanup
        try:
            if 'tmp_path' in dir() and os.path.exists(tmp_path):
                os.unlink(tmp_path)
        except (OSError, UnboundLocalError):
            pass


def transcribe_for_field(audio_bytes: bytes, field_type: str = "name", language: str = "urdu") -> str:
    """
    Transcribe audio for a specific form field, with post-processing.

    Args:
        audio_bytes: Raw WAV audio data
        field_type: Type of field ('name', 'age', 'mobile', 'cnic', 'general')
        language: Language code

    Returns:
        Processed text string, or empty string on failure.
    """
    result = transcribe_audio(audio_bytes, language)

    if not result["success"]:
        return ""

    text = result["text"].strip()

    # ── Post-processing based on field type ──
    if field_type == "age":
        # Extract numbers from spoken text
        text = _extract_number(text)

    elif field_type == "mobile":
        # Clean up phone number — keep only digits
        text = _extract_digits(text)

    elif field_type == "cnic":
        # Clean up CNIC — keep only digits
        text = _extract_digits(text)

    elif field_type == "name":
        # Capitalize name properly
        if text and all(c.isascii() for c in text):
            text = text.title()

    return text


def _extract_number(text: str) -> str:
    """Extract a numeric value from spoken text."""
    # Urdu number words mapping
    urdu_numbers = {
        "ایک": "1", "دو": "2", "تین": "3", "چار": "4", "پانچ": "5",
        "چھ": "6", "سات": "7", "آٹھ": "8", "نو": "9", "دس": "10",
        "گیارہ": "11", "بارہ": "12", "تیرہ": "13", "چودہ": "14", "پندرہ": "15",
        "سولہ": "16", "سترہ": "17", "اٹھارہ": "18", "انیس": "19", "بیس": "20",
        "پچیس": "25", "تیس": "30", "پینتیس": "35", "چالیس": "40",
        "پینتالیس": "45", "پچاس": "50", "پچپن": "55", "ساٹھ": "60",
        "پینسٹھ": "65", "ستر": "70", "پچہتر": "75", "اسی": "80",
        "پچاسی": "85", "نوے": "90", "پچانوے": "95", "سو": "100",
    }

    # Check if text matches an Urdu number word
    for word, num in urdu_numbers.items():
        if word in text:
            return num

    # Try to extract digits from text
    digits = ''.join(c for c in text if c.isdigit())
    if digits:
        return digits

    # English number words
    english_numbers = {
        "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
        "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
        "eleven": "11", "twelve": "12", "thirteen": "13", "fourteen": "14",
        "fifteen": "15", "sixteen": "16", "seventeen": "17", "eighteen": "18",
        "nineteen": "19", "twenty": "20", "thirty": "30", "forty": "40",
        "fifty": "50", "sixty": "60", "seventy": "70", "eighty": "80",
        "ninety": "90", "hundred": "100",
    }
    for word, num in english_numbers.items():
        if word in text.lower():
            return num

    return text


def _extract_digits(text: str) -> str:
    """Extract only digits from text."""
    digits = ''.join(c for c in text if c.isdigit())
    return digits


def is_available() -> bool:
    """Check if SpeechRecognition is available."""
    return STT_AVAILABLE
