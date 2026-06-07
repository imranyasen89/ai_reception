"""
voice_assistant.py
------------------
DHQ Hospital Lodhran - AI Receptionist
Urdu Voice Assistant using Edge-TTS.
Generates speech audio files for patient interaction prompts.
"""

import os
import asyncio
import tempfile
import hashlib

# ─── TTS Availability ─────────────────────────────────────────────────────────
TTS_AVAILABLE = False
try:
    import edge_tts
    TTS_AVAILABLE = True
except ImportError:
    pass


# ─── Voice Configuration ─────────────────────────────────────────────────────
URDU_VOICE_FEMALE = "ur-PK-UzmaNeural"     # Female Urdu voice (default)
URDU_VOICE_MALE   = "ur-PK-AsadNeural"     # Male Urdu voice
VOICE_RATE        = "-5%"                   # Slightly slower for clarity
VOICE_VOLUME      = "+10%"                  # Slightly louder for kiosk

# Cache directory for generated audio
CACHE_DIR = os.path.join(os.path.dirname(__file__), ".voice_cache")


# ─── Predefined Urdu Phrases ─────────────────────────────────────────────────
PHRASES = {
    # Welcome & Greetings
    "welcome":
        "السلام علیکم، ڈی ایچ کیو ہسپتال لودھراں میں خوش آمدید",
    "welcome_back":
        "خوش آمدید، آپ کا ریکارڈ مل گیا ہے",
    "thank_you":
        "شکریہ، اللہ آپ کو صحت عطا فرمائے",

    # Patient Type
    "ask_patient_type":
        "کیا آپ نئے مریض ہیں یا پرانے؟ براہ کرم بٹن دبائیں",

    # Registration Prompts
    "ask_name":
        "براہ کرم اپنا پورا نام بتائیں",
    "ask_age":
        "براہ کرم اپنی عمر بتائیں",
    "ask_gender":
        "براہ کرم اپنی جنس منتخب کریں",
    "ask_mobile":
        "براہ کرم اپنا موبائل نمبر بتائیں",
    "ask_cnic":
        "اگر آپ چاہیں تو اپنا شناختی کارڈ نمبر بتائیں",

    # Search
    "ask_mr_number":
        "براہ کرم اپنا ایم آر نمبر بتائیں",
    "ask_search_mobile":
        "براہ کرم اپنا موبائل نمبر بتائیں تاکہ ریکارڈ تلاش کیا جا سکے",

    # Doctor & Token
    "ask_doctor":
        "براہ کرم ڈاکٹر کا انتخاب کریں",
    "token_ready":
        "آپ کا ٹوکن تیار ہے",
    "go_to_room":
        "براہ کرم کمرہ نمبر {room} تشریف لے جائیں",

    # Errors
    "not_found":
        "ریکارڈ موجود نہیں، براہ کرم نیا رجسٹریشن کریں",
    "registration_success":
        "آپ کا رجسٹریشن کامیابی سے ہو گیا ہے",

    # Camera
    "face_detected":
        "السلام علیکم، میں آپ کو دیکھ سکتی ہوں، خوش آمدید",
    "look_at_camera":
        "براہ کرم کیمرے کی طرف دیکھیں",
}


# ─── Audio Cache Management ──────────────────────────────────────────────────
def _ensure_cache_dir():
    """Create cache directory if it doesn't exist."""
    os.makedirs(CACHE_DIR, exist_ok=True)


def _get_cache_path(text: str, voice: str) -> str:
    """Generate a cache file path based on text and voice hash."""
    key = hashlib.md5(f"{text}_{voice}".encode()).hexdigest()
    return os.path.join(CACHE_DIR, f"tts_{key}.mp3")


# ─── Core TTS Engine ─────────────────────────────────────────────────────────
async def _generate_audio_async(text: str, voice: str, output_path: str) -> bool:
    """
    Generate speech audio using Edge-TTS (async).
    Returns True on success, False on failure.
    """
    try:
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=VOICE_RATE,
            volume=VOICE_VOLUME,
        )
        await communicate.save(output_path)
        return True
    except Exception as e:
        print(f"[Voice Assistant] TTS generation error: {e}")
        return False


def speak(text: str, voice: str = None, use_cache: bool = True) -> str | None:
    """
    Convert text to speech and return path to the generated .mp3 file.

    Args:
        text: Text to speak (Urdu or English)
        voice: Edge-TTS voice name (defaults to Urdu female)
        use_cache: If True, reuse previously generated audio for the same text

    Returns:
        Absolute path to .mp3 file, or None on failure.
    """
    if not TTS_AVAILABLE:
        return None

    if not text or not text.strip():
        return None

    voice = voice or URDU_VOICE_FEMALE

    # Check cache first
    if use_cache:
        _ensure_cache_dir()
        cache_path = _get_cache_path(text, voice)
        if os.path.exists(cache_path) and os.path.getsize(cache_path) > 0:
            return cache_path
        output_path = cache_path
    else:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3", prefix="dhq_tts_")
        output_path = tmp.name
        tmp.close()

    # Generate audio
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(_generate_audio_async(text, voice, output_path))
        loop.close()

        if success and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return output_path
        return None

    except Exception as e:
        print(f"[Voice Assistant] Error: {e}")
        return None


def speak_phrase(key: str, voice: str = None, **kwargs) -> str | None:
    """
    Speak a predefined phrase by its key. Supports format placeholders.

    Examples:
        speak_phrase("welcome")
        speak_phrase("go_to_room", room="12")

    Returns:
        Path to .mp3 file, or None.
    """
    phrase = PHRASES.get(key, "")
    if not phrase:
        return None

    if kwargs:
        try:
            phrase = phrase.format(**kwargs)
        except KeyError:
            pass

    return speak(phrase, voice=voice)


def get_phrase(key: str, **kwargs) -> str:
    """
    Get a predefined Urdu phrase text (without generating audio).

    Args:
        key: Phrase key from PHRASES dict.
        **kwargs: Format arguments.

    Returns:
        The phrase string.
    """
    phrase = PHRASES.get(key, "")
    if kwargs:
        try:
            phrase = phrase.format(**kwargs)
        except KeyError:
            pass
    return phrase


def speak_custom(text: str, voice: str = None) -> str | None:
    """
    Speak custom text (not from predefined phrases).
    Useful for dynamic messages like patient names.
    """
    return speak(text, voice=voice, use_cache=False)


# ─── Streamlit Integration ───────────────────────────────────────────────────
def play_audio_in_streamlit(audio_path: str, autoplay: bool = True):
    """
    Play an audio file in Streamlit with optional autoplay.
    Must be called within a Streamlit context.

    Args:
        audio_path: Path to the .mp3 file
        autoplay: Whether to autoplay (requires user interaction in some browsers)
    """
    try:
        import streamlit as st
        if audio_path and os.path.exists(audio_path):
            with open(audio_path, "rb") as f:
                audio_bytes = f.read()
            st.audio(audio_bytes, format="audio/mp3", autoplay=autoplay)
    except Exception as e:
        print(f"[Voice Assistant] Streamlit playback error: {e}")


# ─── Utility ─────────────────────────────────────────────────────────────────
def is_available() -> bool:
    """Check if Edge-TTS is installed and available."""
    return TTS_AVAILABLE


def clear_cache():
    """Clear all cached audio files."""
    if os.path.exists(CACHE_DIR):
        for f in os.listdir(CACHE_DIR):
            try:
                os.unlink(os.path.join(CACHE_DIR, f))
            except OSError:
                pass


def get_available_phrases() -> list:
    """Return list of all available phrase keys."""
    return list(PHRASES.keys())
