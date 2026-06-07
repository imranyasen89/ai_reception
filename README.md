# 🏥 AI Receptionist — DHQ Hospital Lodhran

**ڈی ایچ کیو ہسپتال لودھراں — AI ریسیپشنسٹ سسٹم**

A professional, Urdu-enabled Hospital AI Receptionist System built with Python Streamlit. Designed as a kiosk-style application for patient registration, doctor selection, and token generation.

---

## 📁 Project Structure

```
ai_receptionist/
├── app.py                  # Main Streamlit application
├── database.py             # SQLite database management
├── voice_assistant.py      # Optional Urdu TTS (Edge-TTS)
├── camera_detection.py     # Optional person detection (OpenCV)
├── requirements.txt        # Python dependencies
├── dhq_hospital.db         # SQLite database (auto-created on first run)
└── README.md               # This file
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 🎯 Features

| Feature                  | Status     | Description                              |
|--------------------------|------------|------------------------------------------|
| Welcome Screen           | ✅ Active  | Urdu greeting with hospital branding     |
| New Patient Registration | ✅ Active  | Full form with MR# auto-generation       |
| Returning Patient Search | ✅ Active  | Search by MR# or Mobile number           |
| Doctor Selection         | ✅ Active  | Dropdown with department/room display    |
| Token Generation         | ✅ Active  | Sequential tokens per doctor per day     |
| Professional Token Card  | ✅ Active  | Printable token with all visit details   |
| Dashboard                | ✅ Active  | Live statistics and today's visits       |
| Urdu Voice (TTS)         | 🔧 Optional| Install `edge-tts` to enable             |
| Camera Detection         | 🔧 Optional| Install `opencv-python` to enable        |

---

## 🔧 Optional Features

### Urdu Voice Assistant

```bash
pip install edge-tts
```

### Camera Person Detection

```bash
pip install opencv-python
```

---

## 🗄️ Database

SQLite database (`dhq_hospital.db`) is auto-created on first run with:

- **patients** — Patient registration records
- **doctors** — Pre-seeded with 8 sample doctors
- **visits** — Visit records with token numbers

---

## 📝 Notes

- This is a **proof-of-concept/demo** version
- Designed for future integration with Hospital Management Information Systems (HIMS)
- Print functionality is a placeholder for local printer connection
- Voice and camera features gracefully degrade if libraries are not installed

---

## 📄 License

Demo project — Free to use and modify.
