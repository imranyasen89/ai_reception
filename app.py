"""
app.py
------
DHQ Hospital Lodhran — AI Receptionist System
Main Streamlit application with full Voice + Camera + Speech-to-Text integration.

Features:
  - Camera-based face detection → auto-welcome
  - Urdu TTS voice prompts at every step
  - Speech-to-text input for patient registration fields
  - Professional kiosk-style UI with Urdu support

Run with:
    streamlit run app.py
"""

import streamlit as st
from datetime import date, datetime
import os

# ─── Local Modules ────────────────────────────────────────────────────────────
import database as db
import voice_assistant as voice
import camera_detection as camera
import speech_input as speech

# ─── Initialize Database ─────────────────────────────────────────────────────
db.init_db()

# ─── Page Configuration ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Receptionist — DHQ Hospital Lodhran",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ═══════════════════════════════════════════════════════════════════════════════
#  CUSTOM CSS — Professional Hospital Theme
# ═══════════════════════════════════════════════════════════════════════════════
def inject_custom_css():
    st.markdown("""
    <style>
    /* ─── Import Google Fonts ─────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;500;600;700&display=swap');

    /* ─── Root Variables ──────────────────────────────────────── */
    :root {
        --primary:         #0e7a6e;
        --primary-light:   #12a394;
        --primary-dark:    #095c54;
        --accent:          #f0c040;
        --accent-glow:     #ffd95e;
        --bg-dark:         #0a1628;
        --bg-card:         #111d33;
        --bg-card-hover:   #162847;
        --text-primary:    #f0f4fc;
        --text-secondary:  #8fa3c4;
        --success:         #2ecc71;
        --danger:          #e74c3c;
        --warning:         #f39c12;
        --border:          rgba(255,255,255,0.06);
        --radius:          16px;
        --radius-sm:       10px;
        --shadow:          0 8px 32px rgba(0,0,0,0.35);
        --font-en:         'Inter', sans-serif;
        --font-ur:         'Noto Nastaliq Urdu', 'Jameel Noori Nastaleeq', serif;
    }

    /* ─── Global Reset ────────────────────────────────────────── */
    .stApp {
        background: linear-gradient(145deg, #060e1a 0%, #0c1a30 40%, #0f1f38 100%) !important;
        color: var(--text-primary) !important;
        font-family: var(--font-en) !important;
    }

    /* ─── Sidebar ─────────────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #081424 0%, #0a1a2e 100%) !important;
        border-right: 1px solid var(--border) !important;
    }
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: var(--accent) !important;
        font-family: var(--font-en) !important;
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown li {
        color: var(--text-secondary) !important;
    }

    /* ─── Headers ─────────────────────────────────────────────── */
    h1, h2, h3 { color: var(--text-primary) !important; font-family: var(--font-en) !important; font-weight: 700 !important; }

    /* ─── Urdu Text ───────────────────────────────────────────── */
    .urdu-text {
        font-family: var(--font-ur) !important;
        direction: rtl;
        text-align: center;
        line-height: 2.4;
    }

    /* ─── Hero Section ────────────────────────────────────────── */
    .hero-container { text-align: center; padding: 40px 20px 20px; }
    .hero-logo {
        width: 120px; height: 120px; border-radius: 50%;
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto 28px; font-size: 52px;
        box-shadow: 0 0 40px rgba(14,122,110,0.35), 0 0 80px rgba(14,122,110,0.15);
        animation: pulse-glow 3s ease-in-out infinite;
    }
    @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 0 40px rgba(14,122,110,0.35), 0 0 80px rgba(14,122,110,0.15); }
        50%      { box-shadow: 0 0 60px rgba(14,122,110,0.50), 0 0 100px rgba(14,122,110,0.25); }
    }
    .hero-salam {
        font-family: var(--font-ur); font-size: 3rem; font-weight: 700;
        color: var(--accent); direction: rtl; margin-bottom: 6px;
        text-shadow: 0 0 30px rgba(240,192,64,0.25); line-height: 2;
    }
    .hero-subtitle {
        font-family: var(--font-ur); font-size: 1.4rem; color: var(--text-secondary);
        direction: rtl; margin-bottom: 10px; line-height: 2;
    }
    .hero-english {
        font-family: var(--font-en); font-size: 1.1rem; color: var(--text-secondary);
        margin-bottom: 30px; letter-spacing: 2px; text-transform: uppercase; font-weight: 500;
    }

    /* ─── Cards ────────────────────────────────────────────────── */
    .info-card {
        background: linear-gradient(145deg, var(--bg-card) 0%, var(--bg-card-hover) 100%);
        border: 1px solid var(--border); border-radius: var(--radius);
        padding: 28px; box-shadow: var(--shadow);
        transition: transform 0.25s, box-shadow 0.25s;
    }
    .info-card:hover { transform: translateY(-3px); box-shadow: 0 12px 40px rgba(0,0,0,0.5); }

    /* ─── Token Card ──────────────────────────────────────────── */
    .token-card {
        background: linear-gradient(160deg, #0d2137 0%, #132d4a 50%, #0f2540 100%);
        border: 2px solid var(--primary); border-radius: 20px;
        padding: 0; overflow: hidden; max-width: 480px; margin: 20px auto;
        box-shadow: 0 10px 50px rgba(14,122,110,0.25), 0 0 80px rgba(14,122,110,0.08);
    }
    .token-header {
        background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary) 100%);
        padding: 22px 30px; text-align: center;
    }
    .token-header h2 { margin: 0; font-size: 1.3rem; font-weight: 700; color: #fff !important; letter-spacing: 1.5px; }
    .token-header p { margin: 4px 0 0; font-size: 0.8rem; color: rgba(255,255,255,0.7); letter-spacing: 1px; }
    .token-body { padding: 30px; }
    .token-row {
        display: flex; justify-content: space-between; padding: 10px 0;
        border-bottom: 1px solid var(--border); align-items: center;
    }
    .token-row:last-child { border-bottom: none; }
    .token-label { font-size: 0.82rem; color: var(--text-secondary); font-weight: 500; text-transform: uppercase; letter-spacing: 0.8px; }
    .token-value { font-size: 1rem; color: var(--text-primary); font-weight: 600; }
    .token-number-big {
        text-align: center; padding: 20px; margin: 15px 0;
        background: rgba(14,122,110,0.12); border-radius: 12px; border: 1px dashed var(--primary);
    }
    .token-number-big span { font-size: 3rem; font-weight: 800; color: var(--accent); letter-spacing: 3px; text-shadow: 0 0 20px rgba(240,192,64,0.3); }
    .token-footer {
        background: rgba(0,0,0,0.2); padding: 14px; text-align: center;
        font-size: 0.75rem; color: var(--text-secondary); letter-spacing: 0.5px;
    }

    /* ─── Stat Cards ──────────────────────────────────────────── */
    .stat-card {
        background: linear-gradient(145deg, var(--bg-card) 0%, var(--bg-card-hover) 100%);
        border: 1px solid var(--border); border-radius: var(--radius);
        padding: 22px; text-align: center; box-shadow: var(--shadow);
    }
    .stat-icon { font-size: 2rem; margin-bottom: 8px; }
    .stat-number { font-size: 2.4rem; font-weight: 800; color: var(--accent); line-height: 1.2; }
    .stat-label { font-size: 0.82rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }

    /* ─── Detail Rows ─────────────────────────────────────────── */
    .detail-row { display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid var(--border); }
    .detail-row:last-child { border-bottom: none; }
    .detail-label { color: var(--text-secondary); font-size: 0.88rem; font-weight: 500; }
    .detail-value { color: var(--text-primary); font-weight: 600; font-size: 0.95rem; }

    /* ─── Streamlit Component Overrides ────────────────────────── */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%) !important;
        color: white !important; border: none !important;
        border-radius: var(--radius-sm) !important; padding: 12px 32px !important;
        font-weight: 600 !important; font-size: 1rem !important;
        letter-spacing: 0.5px !important; transition: all 0.3s !important;
        box-shadow: 0 4px 15px rgba(14,122,110,0.3) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(14,122,110,0.45) !important;
    }
    .stButton > button[kind="primary"] {
        padding: 18px 48px !important; font-size: 1.2rem !important;
        border-radius: var(--radius) !important;
    }

    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        background: var(--bg-card) !important; border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important; color: var(--text-primary) !important;
        padding: 12px 16px !important; font-size: 1rem !important;
    }
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 2px rgba(14,122,110,0.25) !important;
    }
    .stSelectbox > div > div {
        background: var(--bg-card) !important; border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
    }

    /* ─── Voice Input Indicator ───────────────────────────────── */
    .voice-indicator {
        display: inline-flex; align-items: center; gap: 8px;
        padding: 6px 14px; border-radius: 20px; font-size: 0.8rem;
        font-weight: 600; letter-spacing: 0.5px;
    }
    .voice-active {
        background: rgba(46,204,113,0.12); color: #2ecc71;
        border: 1px solid rgba(46,204,113,0.3);
    }
    .voice-inactive {
        background: rgba(231,76,60,0.12); color: #e74c3c;
        border: 1px solid rgba(231,76,60,0.3);
    }

    /* ─── Feature Badge ───────────────────────────────────────── */
    .feature-badge {
        display: inline-block; padding: 3px 10px; border-radius: 20px;
        font-size: 0.7rem; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase;
    }
    .badge-active { background: rgba(46,204,113,0.15); color: #2ecc71; border: 1px solid rgba(46,204,113,0.3); }
    .badge-inactive { background: rgba(231,76,60,0.15); color: #e74c3c; border: 1px solid rgba(231,76,60,0.3); }

    /* ─── Mic Section ─────────────────────────────────────────── */
    .mic-section {
        background: rgba(14,122,110,0.06); border: 1px solid rgba(14,122,110,0.15);
        border-radius: 12px; padding: 12px 16px; margin: 6px 0;
    }
    .mic-label {
        font-size: 0.78rem; color: var(--primary-light); font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 4px;
    }

    /* ─── Scrollbar ───────────────────────────────────────────── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg-dark); }
    ::-webkit-scrollbar-thumb { background: var(--primary-dark); border-radius: 3px; }

    hr { border: none; border-top: 1px solid var(--border); margin: 24px 0; }

    /* ═══════════════════════════════════════════════════════════════
       MOBILE RESPONSIVE — Tablet (≤768px)
    ═══════════════════════════════════════════════════════════════ */
    @media screen and (max-width: 768px) {
        /* Reduce main padding */
        .main .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 1rem !important;
            max-width: 100% !important;
        }

        /* Sidebar collapsed by default on mobile */
        section[data-testid="stSidebar"] {
            min-width: 0 !important;
        }

        /* Hero section — scale down */
        .hero-container { padding: 24px 10px 14px; }
        .hero-logo { width: 90px; height: 90px; font-size: 40px; margin-bottom: 18px; }
        .hero-salam { font-size: 2rem; }
        .hero-subtitle { font-size: 1.1rem; }
        .hero-english { font-size: 0.9rem; letter-spacing: 1px; margin-bottom: 18px; }

        /* Cards — reduce padding */
        .info-card { padding: 18px 14px; }
        .info-card:hover { transform: none; } /* disable hover lift on touch */

        /* Token Card */
        .token-card { max-width: 100%; margin: 12px auto; border-radius: 14px; }
        .token-header { padding: 16px 18px; }
        .token-header h2 { font-size: 1.1rem; letter-spacing: 1px; }
        .token-body { padding: 18px 14px; }
        .token-number-big { padding: 14px; margin: 10px 0; }
        .token-number-big span { font-size: 2.2rem; }
        .token-label { font-size: 0.75rem; }
        .token-value { font-size: 0.9rem; }

        /* Stat Cards */
        .stat-card { padding: 16px 12px; }
        .stat-icon { font-size: 1.6rem; margin-bottom: 4px; }
        .stat-number { font-size: 1.8rem; }
        .stat-label { font-size: 0.72rem; }

        /* Buttons — larger touch targets */
        .stButton > button {
            padding: 14px 20px !important;
            font-size: 0.95rem !important;
            min-height: 48px !important;
            width: 100% !important;
        }
        .stButton > button[kind="primary"] {
            padding: 16px 24px !important;
            font-size: 1.05rem !important;
        }

        /* Input fields — bigger touch targets */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input {
            padding: 14px 14px !important;
            font-size: 1rem !important;
            min-height: 48px !important;
        }

        /* Detail rows — stack on small screens */
        .detail-row {
            flex-direction: column;
            gap: 2px;
            padding: 10px 0;
        }
        .detail-label { font-size: 0.78rem; }
        .detail-value { font-size: 0.9rem; }

        /* Mic section */
        .mic-section { padding: 10px 12px; }

        /* Voice indicator */
        .voice-indicator { font-size: 0.72rem; padding: 5px 10px; }

        /* Tables — scroll horizontally */
        table { font-size: 0.82rem !important; }
        table th, table td { padding: 10px 8px !important; }
    }

    /* ═══════════════════════════════════════════════════════════════
       MOBILE RESPONSIVE — Phone (≤480px)
    ═══════════════════════════════════════════════════════════════ */
    @media screen and (max-width: 480px) {
        .main .block-container {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
            padding-top: 0.5rem !important;
        }

        /* Hero — phone-sized */
        .hero-container { padding: 16px 6px 10px; }
        .hero-logo { width: 72px; height: 72px; font-size: 32px; margin-bottom: 14px; }
        .hero-salam { font-size: 1.6rem; line-height: 1.8; }
        .hero-subtitle { font-size: 0.95rem; line-height: 1.8; }
        .hero-english { font-size: 0.75rem; letter-spacing: 0.5px; margin-bottom: 14px; }

        /* Cards — compact */
        .info-card { padding: 14px 10px; border-radius: 12px; }

        /* Token — full width, compact */
        .token-card { border-radius: 12px; }
        .token-header { padding: 14px 12px; }
        .token-header h2 { font-size: 0.95rem; }
        .token-header p { font-size: 0.7rem; }
        .token-body { padding: 14px 10px; }
        .token-row { flex-direction: column; gap: 2px; padding: 8px 0; }
        .token-number-big span { font-size: 1.8rem; letter-spacing: 1px; }
        .token-footer { padding: 10px; font-size: 0.65rem; }

        /* Stat cards — even more compact */
        .stat-card { padding: 12px 8px; border-radius: 10px; }
        .stat-icon { font-size: 1.3rem; }
        .stat-number { font-size: 1.4rem; }
        .stat-label { font-size: 0.65rem; letter-spacing: 0.5px; }

        /* Buttons — full width always */
        .stButton > button {
            padding: 14px 16px !important;
            font-size: 0.9rem !important;
            border-radius: 10px !important;
        }
        .stButton > button[kind="primary"] {
            padding: 16px 20px !important;
            font-size: 1rem !important;
        }

        /* Headings */
        h1 { font-size: 1.3rem !important; }
        h2 { font-size: 1.1rem !important; }
        h3 { font-size: 1rem !important; }

        /* Patient type cards text */
        .info-card h3 { font-size: 1.05rem !important; }
        .info-card .urdu-text { font-size: 0.9rem !important; }

        /* Feature badges */
        .feature-badge { font-size: 0.6rem; padding: 2px 7px; }
    }

    /* ═══════════════════════════════════════════════════════════════
       TOUCH & ACCESSIBILITY HELPERS
    ═══════════════════════════════════════════════════════════════ */
    /* Prevent text selection on buttons for kiosk */
    .stButton > button { -webkit-user-select: none; user-select: none; }

    /* Ensure tap targets are at least 44px per WCAG */
    @media (pointer: coarse) {
        .stButton > button { min-height: 48px !important; }
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input {
            min-height: 48px !important;
        }
        .stSelectbox > div > div {
            min-height: 48px !important;
        }
        /* Disable hover effects on touch — they feel laggy */
        .info-card:hover { transform: none !important; box-shadow: var(--shadow) !important; }
        .stButton > button:hover { transform: none !important; }
    }
    </style>

    <!-- Viewport meta for mobile scaling -->
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════════
def init_session_state():
    """Initialize all session state variables."""
    defaults = {
        "page":               "welcome",
        "patient_type":       None,
        "current_patient":    None,
        "current_visit":      None,
        "current_doctor":     None,
        "search_result":      None,
        "face_detected":      False,
        "tts_played":         {},          # Track which TTS prompts have been played
        "voice_language":     "urdu",      # Voice input language
        # Voice-captured field values
        "voice_name":         "",
        "voice_age":          "",
        "voice_mobile":       "",
        "voice_cnic":         "",
        "voice_search":       "",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def navigate(page: str):
    """Navigate to a different page and reset TTS tracking for the new page."""
    st.session_state.page = page
    st.session_state.tts_played = {}


def reset_flow():
    """Reset the entire flow back to welcome."""
    keys_to_reset = [
        "page", "patient_type", "current_patient", "current_visit",
        "current_doctor", "search_result", "face_detected", "tts_played",
        "voice_name", "voice_age", "voice_mobile", "voice_cnic", "voice_search",
    ]
    for k in keys_to_reset:
        if k == "page":
            st.session_state[k] = "welcome"
        elif k == "tts_played":
            st.session_state[k] = {}
        elif k in ("face_detected",):
            st.session_state[k] = False
        else:
            st.session_state[k] = None if k in ("patient_type", "current_patient", "current_visit", "current_doctor", "search_result") else ""


# ─── TTS Helper ──────────────────────────────────────────────────────────────
def play_tts(phrase_key: str, once: bool = True, **kwargs):
    """
    Play a TTS phrase. If once=True, only plays once per page load.
    """
    if not voice.is_available():
        return

    tts_id = f"{st.session_state.page}_{phrase_key}"
    if once and st.session_state.tts_played.get(tts_id):
        return

    audio_path = voice.speak_phrase(phrase_key, **kwargs)
    if audio_path:
        voice.play_audio_in_streamlit(audio_path, autoplay=True)
        st.session_state.tts_played[tts_id] = True


# ─── Voice Input Field Helper ────────────────────────────────────────────────
def voice_input_field(label: str, tts_prompt_key: str, field_key: str,
                      field_type: str = "name", placeholder: str = ""):
    """
    Render an input field with an integrated microphone recorder.
    The patient can either type or speak — speech is transcribed and fills the field.

    Args:
        label: Field label text
        tts_prompt_key: Key for the TTS voice prompt
        field_key: Session state key for storing the value
        field_type: Type of field for STT post-processing ('name', 'age', 'mobile', 'cnic')
        placeholder: Placeholder text for the input

    Returns:
        The field value (str)
    """
    # ── Voice Prompt Button ──
    urdu_prompt = voice.get_phrase(tts_prompt_key) if voice.is_available() else ""

    col_label, col_listen = st.columns([4, 1])
    with col_label:
        st.markdown(f"**{label}**")
        if urdu_prompt:
            st.markdown(
                f"<span class='urdu-text' style='font-size:0.9rem; color:#8fa3c4;'>{urdu_prompt}</span>",
                unsafe_allow_html=True
            )
    with col_listen:
        if voice.is_available():
            if st.button("🔊", key=f"tts_btn_{field_key}", help="Listen to prompt"):
                play_tts(tts_prompt_key, once=False)

    # ── Microphone Input ──
    if speech.is_available():
        st.markdown(
            '<div class="mic-section">'
            '<div class="mic-label">🎤 Speak your answer / اپنا جواب بولیں</div>'
            '</div>',
            unsafe_allow_html=True
        )
        audio_data = st.audio_input(
            f"🎤 Record for {label}",
            key=f"mic_{field_key}",
            label_visibility="collapsed"
        )
        if audio_data:
            audio_bytes = audio_data.read()
            if audio_bytes:
                with st.spinner("🔄 Transcribing... / آواز پڑھی جا رہی ہے..."):
                    lang = LANGUAGES_MAP.get(st.session_state.get("voice_language", "urdu"), "urdu")
                    result = speech.transcribe_audio(audio_bytes, language=lang)

                if result["success"]:
                    # Post-process based on field type
                    processed = speech.transcribe_for_field(audio_bytes, field_type=field_type, language=lang)
                    if processed:
                        st.session_state[f"voice_{field_key}"] = processed
                        st.success(f"✅ Recognized: **{processed}**")
                    else:
                        st.session_state[f"voice_{field_key}"] = result["text"]
                        st.success(f"✅ Recognized: **{result['text']}**")
                else:
                    st.warning(f"⚠️ {result['error']}")

    # ── Text Input (with voice value as default) ──
    default_val = st.session_state.get(f"voice_{field_key}", "")
    value = st.text_input(
        label,
        value=default_val,
        placeholder=placeholder,
        key=f"input_{field_key}",
        label_visibility="collapsed"
    )

    return value


# Language mapping for the voice_input_field helper
LANGUAGES_MAP = {
    "urdu": "urdu",
    "english": "english",
    "hindi": "hindi",
}


# ═══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
def render_sidebar():
    with st.sidebar:
        st.markdown("## 🏥 DHQ Hospital")
        st.markdown("**AI Receptionist System**")
        st.markdown("---")

        # Navigation
        st.markdown("### 📋 Navigation")
        if st.button("🏠  Home", use_container_width=True, key="nav_home"):
            reset_flow()
            st.rerun()
        if st.button("📊  Dashboard", use_container_width=True, key="nav_dash"):
            navigate("dashboard")
            st.rerun()
        if st.button("👨‍⚕️  Doctors", use_container_width=True, key="nav_docs"):
            navigate("doctors_list")
            st.rerun()
        if st.button("📋  Today's Visits", use_container_width=True, key="nav_visits"):
            navigate("today_visits")
            st.rerun()

        st.markdown("---")

        # Voice Language Setting
        st.markdown("### 🌐 Voice Language")
        st.session_state.voice_language = st.selectbox(
            "Speech Input Language",
            options=["urdu", "english"],
            index=0,
            key="lang_select",
            label_visibility="collapsed"
        )

        st.markdown("---")

        # System Status
        st.markdown("### ⚙️ System Status")

        tts_ok  = voice.is_available()
        cam_ok  = camera.is_opencv_installed()
        stt_ok  = speech.is_available()

        st.markdown(f"""
        <div style="margin:6px 0;">
            <span style="color:#8fa3c4; font-size:0.82rem;">🔊 Voice TTS:</span>
            <span class="feature-badge badge-{'active' if tts_ok else 'inactive'}">{"✅ Active" if tts_ok else "❌ Missing"}</span>
        </div>
        <div style="margin:6px 0;">
            <span style="color:#8fa3c4; font-size:0.82rem;">📷 Camera:</span>
            <span class="feature-badge badge-{'active' if cam_ok else 'inactive'}">{"✅ Active" if cam_ok else "❌ Missing"}</span>
        </div>
        <div style="margin:6px 0;">
            <span style="color:#8fa3c4; font-size:0.82rem;">🎤 Speech STT:</span>
            <span class="feature-badge badge-{'active' if stt_ok else 'inactive'}">{"✅ Active" if stt_ok else "❌ Missing"}</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown(
            f"<p style='font-size:0.72rem; color:#5a6f8a; text-align:center;'>"
            f"📅 {date.today().strftime('%d %B %Y')}<br>v2.0.0 — Full Voice Build</p>",
            unsafe_allow_html=True
        )


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: Welcome Screen (with Camera Detection)
# ═══════════════════════════════════════════════════════════════════════════════
def page_welcome():
    """Welcome screen with camera-based face detection and voice greeting."""

    # ── Hero ──
    st.markdown("""
    <div class="hero-container">
        <div class="hero-logo">🏥</div>
        <div class="hero-salam">السلام علیکم</div>
        <div class="hero-subtitle">ڈی ایچ کیو ہسپتال لودھراں میں خوش آمدید</div>
        <div class="hero-english">DHQ Hospital Lodhran — AI Receptionist</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Play welcome TTS ──
    play_tts("welcome")

    # ── Camera Face Detection Section ──
    if camera.is_opencv_installed():
        st.markdown("---")
        st.markdown(
            "<h3 style='text-align:center;'>📷 Face Detection / چہرے کی شناخت</h3>"
            "<p style='text-align:center; color:#8fa3c4; font-size:0.9rem;'>"
            "کیمرے کے سامنے آئیں — آپ کا چہرا خود بخود پہچان لیا جائے گا</p>",
            unsafe_allow_html=True
        )

        camera_photo = st.camera_input(
            "📷 Look at the camera for face detection",
            key="welcome_camera",
            label_visibility="collapsed"
        )

        if camera_photo:
            image_bytes = camera_photo.getvalue()
            result = camera.detect_faces_from_bytes(image_bytes)

            if result["detected"]:
                # Show annotated image with face boxes
                st.image(result["annotated_image"], caption=f"✅ {result['face_count']} face(s) detected!", use_container_width=True)

                st.markdown("""
                <div style="
                    background: rgba(46,204,113,0.1); border: 1px solid rgba(46,204,113,0.3);
                    border-radius: 12px; padding: 20px; text-align: center; margin: 10px 0;
                ">
                    <div class="urdu-text" style="font-size:1.5rem; color:#2ecc71;">چہرہ پہچان لیا گیا ✅</div>
                    <div style="color:#f0f4fc; font-size:1rem;">Face Detected — Welcome!</div>
                </div>
                """, unsafe_allow_html=True)

                # Play face detected TTS
                play_tts("face_detected")

                st.session_state.face_detected = True

                # Auto-proceed button
                if st.button("▶️  آگے بڑھیں — Proceed", use_container_width=True, type="primary", key="btn_face_proceed"):
                    navigate("patient_type")
                    st.rerun()
            else:
                st.warning("⚠️ No face detected — please look directly at the camera / براہ کرم کیمرے کی طرف دیکھیں")

    # ── Manual Start Button (always available) ──
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀  شروع کریں  —  Start Without Camera", use_container_width=True, type="primary", key="btn_start"):
            navigate("patient_type")
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: Patient Type Selection
# ═══════════════════════════════════════════════════════════════════════════════
def page_patient_type():
    st.markdown("<h1 style='text-align:center; margin-bottom:5px;'>Patient Registration</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='urdu-text' style='font-size:1.3rem; color:#8fa3c4; margin-bottom:30px;'>"
        "براہ کرم اپنی قسم منتخب کریں</p>",
        unsafe_allow_html=True
    )

    # Play TTS prompt
    play_tts("ask_patient_type")

    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        c1, c2 = st.columns(2, gap="large")

        with c1:
            st.markdown("""
            <div class="info-card" style="text-align:center; padding:40px 20px;">
                <div style="font-size:3.5rem; margin-bottom:12px;">🆕</div>
                <h3 style="margin:0 0 6px; font-size:1.3rem;">New Patient</h3>
                <p class="urdu-text" style="color:#8fa3c4; font-size:1.1rem;">نیا مریض</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Register New Patient", use_container_width=True, type="primary", key="btn_new"):
                st.session_state.patient_type = "new"
                navigate("new_patient")
                st.rerun()

        with c2:
            st.markdown("""
            <div class="info-card" style="text-align:center; padding:40px 20px;">
                <div style="font-size:3.5rem; margin-bottom:12px;">🔄</div>
                <h3 style="margin:0 0 6px; font-size:1.3rem;">Returning Patient</h3>
                <p class="urdu-text" style="color:#8fa3c4; font-size:1.1rem;">پرانا مریض</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Search My Record", use_container_width=True, type="primary", key="btn_returning"):
                st.session_state.patient_type = "returning"
                navigate("returning_patient")
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    c = st.columns([1, 2, 1])[1]
    with c:
        if st.button("⬅  Back to Home", use_container_width=True, key="btn_back_welcome"):
            reset_flow()
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: New Patient Registration (Voice-Guided)
# ═══════════════════════════════════════════════════════════════════════════════
def page_new_patient():
    st.markdown("<h1 style='text-align:center;'>🆕 New Patient Registration</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='urdu-text' style='font-size:1.2rem; color:#8fa3c4; margin-bottom:15px;'>"
        "براہ کرم اپنی معلومات درج کریں — بول کر یا ٹائپ کر کے</p>",
        unsafe_allow_html=True
    )

    # Voice/STT status indicator
    if speech.is_available() and voice.is_available():
        st.markdown(
            '<div style="text-align:center; margin-bottom:20px;">'
            '<span class="voice-indicator voice-active">🎤 Voice Input Active — بولیں یا ٹائپ کریں</span>'
            '</div>',
            unsafe_allow_html=True
        )

    # Play registration prompt TTS
    play_tts("ask_name")

    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)

        # ── Full Name ──
        name = voice_input_field(
            label="👤 Full Name / مکمل نام *",
            tts_prompt_key="ask_name",
            field_key="name",
            field_type="name",
            placeholder="e.g. Muhammad Ahmed"
        )

        st.markdown("---")

        # ── Age ──
        age_str = voice_input_field(
            label="📅 Age / عمر *",
            tts_prompt_key="ask_age",
            field_key="age",
            field_type="age",
            placeholder="e.g. 35"
        )

        st.markdown("---")

        # ── Gender (buttons — not voice) ──
        st.markdown("**⚧ Gender / جنس ***")
        gender = st.selectbox(
            "Gender",
            options=["Male / مرد", "Female / عورت", "Other / دیگر"],
            key="inp_gender",
            label_visibility="collapsed"
        )

        st.markdown("---")

        # ── Mobile Number ──
        mobile = voice_input_field(
            label="📱 Mobile Number / موبائل نمبر *",
            tts_prompt_key="ask_mobile",
            field_key="mobile",
            field_type="mobile",
            placeholder="03001234567"
        )

        st.markdown("---")

        # ── CNIC (optional) ──
        cnic = voice_input_field(
            label="🪪 CNIC (Optional) / شناختی کارڈ",
            tts_prompt_key="ask_cnic",
            field_key="cnic",
            field_type="cnic",
            placeholder="3520112345678"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Submit ──
        if st.button("✅  Register Patient / مریض کا اندراج", use_container_width=True, type="primary", key="btn_register"):
            # Validation
            final_name = name.strip() if name else ""
            final_mobile = mobile.strip() if mobile else ""
            final_cnic = cnic.strip() if cnic else ""

            # Parse age
            try:
                final_age = int(age_str.strip()) if age_str and age_str.strip() else 0
            except ValueError:
                final_age = 0

            if not final_name:
                st.error("❌ Please enter or speak the patient's name / براہ کرم نام درج کریں")
            elif final_age <= 0 or final_age > 150:
                st.error("❌ Please enter a valid age (1-150) / درست عمر درج کریں")
            elif not final_mobile or len(final_mobile) < 10:
                st.error("❌ Please enter a valid mobile number / درست موبائل نمبر درج کریں")
            else:
                gender_val = gender.split(" / ")[0]
                mr_number = db.register_patient(
                    name=final_name,
                    age=final_age,
                    gender=gender_val,
                    mobile=final_mobile,
                    cnic=final_cnic
                )
                patient = db.search_patient_by_mr(mr_number)
                st.session_state.current_patient = patient

                # Play success TTS
                if voice.is_available():
                    audio = voice.speak_phrase("registration_success")
                    if audio:
                        voice.play_audio_in_streamlit(audio, autoplay=True)

                navigate("select_doctor")
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # Back
    st.markdown("<br>", unsafe_allow_html=True)
    c = st.columns([1, 2, 1])[1]
    with c:
        if st.button("⬅  Back", use_container_width=True, key="btn_back_type"):
            navigate("patient_type")
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: Returning Patient Search (Voice-Enabled)
# ═══════════════════════════════════════════════════════════════════════════════
def page_returning_patient():
    st.markdown("<h1 style='text-align:center;'>🔄 Returning Patient</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='urdu-text' style='font-size:1.2rem; color:#8fa3c4; margin-bottom:15px;'>"
        "اپنا ریکارڈ تلاش کریں — بول کر یا ٹائپ کر کے</p>",
        unsafe_allow_html=True
    )

    # Play search prompt
    play_tts("ask_mr_number")

    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)

        search_method = st.radio(
            "Search By / تلاش کا طریقہ",
            options=["MR Number / ایم آر نمبر", "Mobile Number / موبائل نمبر"],
            horizontal=True,
            key="search_method"
        )

        if "MR Number" in search_method:
            search_val = voice_input_field(
                label="🔍 MR Number / ایم آر نمبر",
                tts_prompt_key="ask_mr_number",
                field_key="search",
                field_type="general",
                placeholder="MR202606040001"
            )
        else:
            search_val = voice_input_field(
                label="🔍 Mobile Number / موبائل نمبر",
                tts_prompt_key="ask_search_mobile",
                field_key="search",
                field_type="mobile",
                placeholder="03001234567"
            )

        if st.button("🔎  Search / تلاش کریں", use_container_width=True, type="primary", key="btn_search"):
            if not search_val or not search_val.strip():
                st.error("❌ Please enter or speak a search value")
            else:
                if "MR Number" in search_method:
                    patient = db.search_patient_by_mr(search_val.strip())
                else:
                    patient = db.search_patient_by_mobile(search_val.strip())

                if patient:
                    st.session_state.search_result = patient
                    play_tts("welcome_back")
                else:
                    st.session_state.search_result = "NOT_FOUND"
                    play_tts("not_found")

        # ── Results ──
        sr = st.session_state.search_result
        if sr and sr != "NOT_FOUND":
            patient = sr
            st.markdown(f"""
            <div style="
                background: rgba(46,204,113,0.08); border: 1px solid rgba(46,204,113,0.25);
                border-radius: 12px; padding: 24px; text-align: center; margin: 16px 0;
            ">
                <div class="urdu-text" style="font-size:1.6rem; color:#2ecc71; margin-bottom:8px;">خوش آمدید</div>
                <div style="font-size:1.1rem; color:#f0f4fc; font-weight:600;">Welcome Back, {patient['name']}!</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="info-card" style="margin-top:10px;">
                <div class="detail-row"><span class="detail-label">MR Number</span><span class="detail-value">{patient['mr_number']}</span></div>
                <div class="detail-row"><span class="detail-label">Name</span><span class="detail-value">{patient['name']}</span></div>
                <div class="detail-row"><span class="detail-label">Age</span><span class="detail-value">{patient['age']}</span></div>
                <div class="detail-row"><span class="detail-label">Gender</span><span class="detail-value">{patient['gender']}</span></div>
                <div class="detail-row"><span class="detail-label">Mobile</span><span class="detail-value">{patient['mobile']}</span></div>
                <div class="detail-row"><span class="detail-label">Registered</span><span class="detail-value">{patient['registration_date']}</span></div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("✅  Create New Visit / نئی وزٹ", use_container_width=True, type="primary", key="btn_new_visit"):
                st.session_state.current_patient = patient
                navigate("select_doctor")
                st.rerun()

        elif sr == "NOT_FOUND":
            st.markdown("""
            <div style="
                background: rgba(231,76,60,0.08); border: 1px solid rgba(231,76,60,0.25);
                border-radius: 12px; padding: 24px; text-align: center; margin: 16px 0;
            ">
                <div class="urdu-text" style="font-size:1.4rem; color:#e74c3c;">ریکارڈ موجود نہیں</div>
                <div style="color:#8fa3c4;">No record found. Please register as a new patient.</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🆕  Register as New Patient", use_container_width=True, key="btn_register_fallback"):
                navigate("new_patient")
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # Back
    st.markdown("<br>", unsafe_allow_html=True)
    c = st.columns([1, 2, 1])[1]
    with c:
        if st.button("⬅  Back", use_container_width=True, key="btn_back_type2"):
            st.session_state.search_result = None
            navigate("patient_type")
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: Doctor Selection
# ═══════════════════════════════════════════════════════════════════════════════
def page_select_doctor():
    patient = st.session_state.current_patient
    if not patient:
        navigate("patient_type")
        st.rerun()
        return

    st.markdown("<h1 style='text-align:center;'>👨‍⚕️ Select Doctor</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='urdu-text' style='font-size:1.2rem; color:#8fa3c4; margin-bottom:10px;'>"
        "براہ کرم ڈاکٹر کا انتخاب کریں</p>",
        unsafe_allow_html=True
    )

    play_tts("ask_doctor")

    # Patient banner
    st.markdown(f"""
    <div style="
        background: rgba(14,122,110,0.08); border: 1px solid rgba(14,122,110,0.25);
        border-radius: 12px; padding: 16px 24px; margin-bottom: 24px;
        display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;
    ">
        <div><span style="color:#8fa3c4; font-size:0.85rem;">Patient:</span>
             <strong style="color:#f0f4fc; margin-left:8px;">{patient['name']}</strong></div>
        <div><span style="color:#8fa3c4; font-size:0.85rem;">MR:</span>
             <strong style="color:#f0c040; margin-left:8px;">{patient['mr_number']}</strong></div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        doctors = db.get_all_doctors()
        doctor_options = {f"{d['doctor_name']} — {d['department']} (Room {d['room_number']})": d for d in doctors}

        selected = st.selectbox(
            "🩺 Choose Doctor / ڈاکٹر منتخب کریں",
            options=list(doctor_options.keys()),
            key="doctor_select"
        )

        if selected:
            doctor = doctor_options[selected]

            c1, c2, c3 = st.columns(3)
            dept_icons = {
                "Medicine": "💊", "Cardiology": "❤️", "Gynecology": "👶",
                "Orthopedics": "🦴", "Pediatrics": "🧒", "Dermatology": "🧴",
                "Neurology": "🧠", "ENT": "👂",
            }
            icon = dept_icons.get(doctor['department'], "🩺")

            with c1:
                st.markdown(f"""
                <div class="info-card" style="text-align:center;">
                    <div style="font-size:1.8rem; margin-bottom:6px;">👨‍⚕️</div>
                    <div style="color:#8fa3c4; font-size:0.8rem; text-transform:uppercase;">Doctor</div>
                    <div style="font-weight:700; font-size:1.05rem; margin-top:4px;">{doctor['doctor_name']}</div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div class="info-card" style="text-align:center;">
                    <div style="font-size:1.8rem; margin-bottom:6px;">{icon}</div>
                    <div style="color:#8fa3c4; font-size:0.8rem; text-transform:uppercase;">Department</div>
                    <div style="font-weight:700; font-size:1.05rem; margin-top:4px;">{doctor['department']}</div>
                </div>
                """, unsafe_allow_html=True)
            with c3:
                st.markdown(f"""
                <div class="info-card" style="text-align:center;">
                    <div style="font-size:1.8rem; margin-bottom:6px;">🚪</div>
                    <div style="color:#8fa3c4; font-size:0.8rem; text-transform:uppercase;">Room Number</div>
                    <div style="font-weight:700; font-size:1.3rem; margin-top:4px; color:#f0c040;">{doctor['room_number']}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("🎫  Generate Token / ٹوکن حاصل کریں", use_container_width=True, type="primary", key="btn_gen_token"):
                visit = db.create_visit(mr_number=patient['mr_number'], doctor_id=doctor['doctor_id'])
                st.session_state.current_visit = visit
                st.session_state.current_doctor = doctor
                navigate("token_display")
                st.rerun()

    # Back
    st.markdown("<br>", unsafe_allow_html=True)
    c = st.columns([1, 2, 1])[1]
    with c:
        if st.button("⬅  Back", use_container_width=True, key="btn_back_doc"):
            navigate("patient_type")
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: Token Display (with Voice Guidance)
# ═══════════════════════════════════════════════════════════════════════════════
def page_token_display():
    patient = st.session_state.current_patient
    visit   = st.session_state.current_visit
    doctor  = st.session_state.current_doctor

    if not all([patient, visit, doctor]):
        navigate("welcome")
        st.rerun()
        return

    st.markdown("<h1 style='text-align:center; margin-bottom:5px;'>🎫 Your Token</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='urdu-text' style='font-size:1.3rem; color:#2ecc71; margin-bottom:10px;'>"
        "آپ کا ٹوکن تیار ہے</p>",
        unsafe_allow_html=True
    )

    # Play token ready TTS
    play_tts("token_ready")

    # Room guidance in Urdu
    st.markdown(f"""
    <p class="urdu-text" style="font-size:1.2rem; color:#f0c040; margin-bottom:25px;">
        براہ کرم کمرہ نمبر {doctor['room_number']} تشریف لے جائیں
    </p>
    """, unsafe_allow_html=True)

    # Play room guidance TTS
    play_tts("go_to_room", room=doctor['room_number'])

    # Token Card
    col1, col2, col3 = st.columns([1, 2.5, 1])
    with col2:
        st.markdown(f"""
        <div class="token-card">
            <div class="token-header">
                <h2>🏥 DHQ HOSPITAL LODHRAN</h2>
                <p>ڈی ایچ کیو ہسپتال لودھراں</p>
            </div>
            <div class="token-body">
                <div class="token-number-big">
                    <span>{visit['token_number']}</span>
                </div>
                <div class="token-row">
                    <span class="token-label">MR Number</span>
                    <span class="token-value">{patient['mr_number']}</span>
                </div>
                <div class="token-row">
                    <span class="token-label">Patient Name</span>
                    <span class="token-value">{patient['name']}</span>
                </div>
                <div class="token-row">
                    <span class="token-label">Doctor</span>
                    <span class="token-value">{doctor['doctor_name']}</span>
                </div>
                <div class="token-row">
                    <span class="token-label">Department</span>
                    <span class="token-value">{doctor['department']}</span>
                </div>
                <div class="token-row">
                    <span class="token-label">Room Number</span>
                    <span class="token-value" style="color:#f0c040; font-size:1.2rem;">{doctor['room_number']}</span>
                </div>
                <div class="token-row">
                    <span class="token-label">Visit Date</span>
                    <span class="token-value">{visit['visit_date']}</span>
                </div>
            </div>
            <div class="token-footer">
                Visit ID: {visit['visit_id']}  •  Generated on {datetime.now().strftime('%d %b %Y, %I:%M %p')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Action buttons
    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1, 3, 1])
    with col_b:
        bc1, bc2 = st.columns(2, gap="medium")
        with bc1:
            if st.button("🖨️  Print Token", use_container_width=True, key="btn_print"):
                st.info("🖨️ Print functionality will be connected to a local printer in production.")
        with bc2:
            if st.button("🏠  Back to Home / واپس", use_container_width=True, type="primary", key="btn_home_token"):
                # Play thank you
                if voice.is_available():
                    audio = voice.speak_phrase("thank_you")
                    if audio:
                        voice.play_audio_in_streamlit(audio, autoplay=True)
                reset_flow()
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: Dashboard
# ═══════════════════════════════════════════════════════════════════════════════
def page_dashboard():
    st.markdown("<h1 style='text-align:center;'>📊 Dashboard</h1>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='text-align:center; color:#8fa3c4; margin-bottom:30px;'>"
        f"Overview for {date.today().strftime('%A, %d %B %Y')}</p>",
        unsafe_allow_html=True
    )

    stats = db.get_stats()

    c1, c2, c3, c4 = st.columns(4, gap="medium")
    for col, icon, num, label in [
        (c1, "👥", stats['total_patients'],      "Total Patients"),
        (c2, "📋", stats['today_visits'],        "Today's Visits"),
        (c3, "🆕", stats['today_registrations'], "New Today"),
        (c4, "👨‍⚕️", stats['total_doctors'],      "Doctors"),
    ]:
        with col:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-icon">{icon}</div>
                <div class="stat-number">{num}</div>
                <div class="stat-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📋 Today's Visits")

    visits = db.get_today_visits()
    if visits:
        rows = ""
        for v in visits:
            rows += f"<tr><td>{v['token_number']}</td><td>{v['patient_name']}</td><td>{v['mr_number']}</td><td>{v['doctor_name']}</td><td>{v['department']}</td><td>Room {v['room_number']}</td></tr>"

        st.markdown(f"""
        <div style="overflow-x:auto;">
        <table style="width:100%; border-collapse:collapse; background:var(--bg-card); border-radius:12px; overflow:hidden;">
            <thead><tr style="background:rgba(14,122,110,0.15);">
                <th style="padding:14px 16px; text-align:left; color:#f0c040; font-size:0.82rem; text-transform:uppercase;">Token</th>
                <th style="padding:14px 16px; text-align:left; color:#f0c040; font-size:0.82rem; text-transform:uppercase;">Patient</th>
                <th style="padding:14px 16px; text-align:left; color:#f0c040; font-size:0.82rem; text-transform:uppercase;">MR#</th>
                <th style="padding:14px 16px; text-align:left; color:#f0c040; font-size:0.82rem; text-transform:uppercase;">Doctor</th>
                <th style="padding:14px 16px; text-align:left; color:#f0c040; font-size:0.82rem; text-transform:uppercase;">Dept</th>
                <th style="padding:14px 16px; text-align:left; color:#f0c040; font-size:0.82rem; text-transform:uppercase;">Room</th>
            </tr></thead>
            <tbody>{rows}</tbody>
        </table></div>
        <style>
        table tbody tr {{ border-bottom: 1px solid rgba(255,255,255,0.05); }}
        table tbody tr:hover {{ background: rgba(14,122,110,0.06); }}
        table tbody td {{ padding: 12px 16px; font-size: 0.92rem; color: #f0f4fc; }}
        </style>
        """, unsafe_allow_html=True)
    else:
        st.info("No visits recorded today yet.")


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: Doctors List
# ═══════════════════════════════════════════════════════════════════════════════
def page_doctors_list():
    st.markdown("<h1 style='text-align:center;'>👨‍⚕️ Available Doctors</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='urdu-text' style='font-size:1.1rem; color:#8fa3c4; margin-bottom:25px;'>ہمارے دستیاب ڈاکٹرز</p>",
        unsafe_allow_html=True
    )

    doctors = db.get_all_doctors()
    dept_icons = {
        "Medicine": "💊", "Cardiology": "❤️", "Gynecology": "👶",
        "Orthopedics": "🦴", "Pediatrics": "🧒", "Dermatology": "🧴",
        "Neurology": "🧠", "ENT": "👂",
    }

    cols = st.columns(3, gap="medium")
    for i, doc in enumerate(doctors):
        with cols[i % 3]:
            icon = dept_icons.get(doc['department'], "🩺")
            st.markdown(f"""
            <div class="info-card" style="text-align:center; margin-bottom:20px; padding:24px;">
                <div style="font-size:2.2rem; margin-bottom:8px;">{icon}</div>
                <h3 style="margin:0 0 4px; font-size:1.1rem;">{doc['doctor_name']}</h3>
                <div style="color:#12a394; font-weight:600; font-size:0.9rem; margin-bottom:10px;">{doc['department']}</div>
                <div style="background:rgba(240,192,64,0.1); border:1px solid rgba(240,192,64,0.2); border-radius:8px; padding:8px; display:inline-block;">
                    <span style="color:#8fa3c4; font-size:0.8rem;">Room</span>
                    <span style="color:#f0c040; font-weight:700; font-size:1.1rem; margin-left:6px;">{doc['room_number']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: Today's Visits
# ═══════════════════════════════════════════════════════════════════════════════
def page_today_visits():
    st.markdown("<h1 style='text-align:center;'>📋 Today's Visits</h1>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='text-align:center; color:#8fa3c4; margin-bottom:25px;'>{date.today().strftime('%A, %d %B %Y')}</p>",
        unsafe_allow_html=True
    )

    visits = db.get_today_visits()
    if not visits:
        st.info("📭 No visits recorded today.")
        return

    for v in visits:
        st.markdown(f"""
        <div class="info-card" style="margin-bottom:16px; padding:20px 24px;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
                <div>
                    <span style="background:rgba(14,122,110,0.15); color:#12a394; padding:4px 12px; border-radius:6px; font-weight:700; font-size:1.1rem; margin-right:12px;">{v['token_number']}</span>
                    <strong style="font-size:1.05rem;">{v['patient_name']}</strong>
                    <span style="color:#8fa3c4; margin-left:8px; font-size:0.85rem;">({v['mr_number']})</span>
                </div>
                <div>
                    <span style="color:#8fa3c4; font-size:0.85rem;">{v['doctor_name']}</span>
                    <span style="color:#5a6f8a; margin:0 6px;">•</span>
                    <span style="color:#8fa3c4; font-size:0.85rem;">{v['department']}</span>
                    <span style="color:#5a6f8a; margin:0 6px;">•</span>
                    <span style="color:#f0c040; font-weight:600;">Room {v['room_number']}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN ROUTER
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    inject_custom_css()
    init_session_state()
    render_sidebar()

    page = st.session_state.page
    pages = {
        "welcome":           page_welcome,
        "patient_type":      page_patient_type,
        "new_patient":       page_new_patient,
        "returning_patient": page_returning_patient,
        "select_doctor":     page_select_doctor,
        "token_display":     page_token_display,
        "dashboard":         page_dashboard,
        "doctors_list":      page_doctors_list,
        "today_visits":      page_today_visits,
    }
    pages.get(page, page_welcome)()


if __name__ == "__main__":
    main()
