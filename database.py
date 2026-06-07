"""
database.py
-----------
DHQ Hospital Lodhran - AI Receptionist
Database management module using SQLite.
Handles all CRUD operations for Patients, Doctors, and Visits.
"""

import sqlite3
import os
from datetime import date, datetime

# ─── Configuration ───────────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), "dhq_hospital.db")


# ─── Connection Helper ────────────────────────────────────────────────────────
def get_connection():
    """Return a SQLite connection with row_factory for dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ─── Database Initialization ──────────────────────────────────────────────────
def init_db():
    """
    Create all required tables if they don't exist and seed sample doctors.
    Called once at application startup.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # ── Patients Table ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            patient_id        INTEGER PRIMARY KEY AUTOINCREMENT,
            mr_number         TEXT UNIQUE NOT NULL,
            name              TEXT NOT NULL,
            age               INTEGER NOT NULL,
            gender            TEXT NOT NULL,
            mobile            TEXT NOT NULL,
            cnic              TEXT,
            registration_date TEXT NOT NULL
        )
    """)

    # ── Doctors Table ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            doctor_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_name  TEXT NOT NULL,
            department   TEXT NOT NULL,
            room_number  TEXT NOT NULL
        )
    """)

    # ── Visits Table ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS visits (
            visit_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            mr_number    TEXT NOT NULL,
            doctor_id    INTEGER NOT NULL,
            visit_date   TEXT NOT NULL,
            token_number TEXT NOT NULL,
            FOREIGN KEY (mr_number)  REFERENCES patients(mr_number),
            FOREIGN KEY (doctor_id)  REFERENCES doctors(doctor_id)
        )
    """)

    conn.commit()

    # ── Seed Doctors (only if table is empty) ──
    cursor.execute("SELECT COUNT(*) FROM doctors")
    if cursor.fetchone()[0] == 0:
        sample_doctors = [
            ("Dr. Ahmed Raza",   "Medicine",     "12"),
            ("Dr. Ali Hassan",   "Cardiology",   "20"),
            ("Dr. Sana Malik",   "Gynecology",   "15"),
            ("Dr. Bilal Ashraf", "Orthopedics",  "08"),
            ("Dr. Farrukh Khan", "Pediatrics",   "05"),
            ("Dr. Nadia Iqbal",  "Dermatology",  "22"),
            ("Dr. Usman Tariq",  "Neurology",    "18"),
            ("Dr. Ayesha Bano",  "ENT",          "09"),
        ]
        cursor.executemany(
            "INSERT INTO doctors (doctor_name, department, room_number) VALUES (?, ?, ?)",
            sample_doctors
        )
        conn.commit()

    conn.close()


# ─── MR Number Generation ─────────────────────────────────────────────────────
def generate_mr_number():
    """
    Generate a unique MR number in format: MR + YYYYMMDD + 4-digit serial.
    Example: MR202606040001
    """
    today = date.today().strftime("%Y%m%d")
    conn = get_connection()
    cursor = conn.cursor()

    # Count patients registered today to create sequential serial
    cursor.execute(
        "SELECT COUNT(*) FROM patients WHERE mr_number LIKE ?",
        (f"MR{today}%",)
    )
    count = cursor.fetchone()[0]
    conn.close()

    serial = str(count + 1).zfill(4)
    return f"MR{today}{serial}"


# ─── Token Number Generation ──────────────────────────────────────────────────
def generate_token(doctor_id: int):
    """
    Generate a sequential token for a given doctor today.
    Format: A-001, A-002, ...
    """
    today = date.today().isoformat()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COUNT(*) FROM visits
        WHERE doctor_id = ? AND visit_date = ?
        """,
        (doctor_id, today)
    )
    count = cursor.fetchone()[0]
    conn.close()

    serial = str(count + 1).zfill(3)
    return f"A-{serial}"


# ─── Patient CRUD ─────────────────────────────────────────────────────────────
def register_patient(name: str, age: int, gender: str, mobile: str, cnic: str = "") -> str:
    """
    Register a new patient and return the generated MR number.
    """
    mr_number = generate_mr_number()
    reg_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO patients (mr_number, name, age, gender, mobile, cnic, registration_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (mr_number, name.strip(), age, gender, mobile.strip(), cnic.strip(), reg_date)
    )
    conn.commit()
    conn.close()

    return mr_number


def search_patient_by_mr(mr_number: str):
    """Search and return a patient dict by MR number, or None."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM patients WHERE mr_number = ?",
        (mr_number.strip().upper(),)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def search_patient_by_mobile(mobile: str):
    """Search and return a patient dict by mobile number, or None."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM patients WHERE mobile = ?",
        (mobile.strip(),)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_patients():
    """Return a list of all registered patients."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients ORDER BY registration_date DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── Doctor Queries ───────────────────────────────────────────────────────────
def get_all_doctors():
    """Return a list of all doctors."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM doctors ORDER BY doctor_id")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_doctor_by_id(doctor_id: int):
    """Return a doctor dict by ID, or None."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM doctors WHERE doctor_id = ?", (doctor_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


# ─── Visit CRUD ───────────────────────────────────────────────────────────────
def create_visit(mr_number: str, doctor_id: int) -> dict:
    """
    Create a new visit record and return visit details including token number.
    """
    token = generate_token(doctor_id)
    visit_date = date.today().isoformat()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO visits (mr_number, doctor_id, visit_date, token_number)
        VALUES (?, ?, ?, ?)
        """,
        (mr_number, doctor_id, visit_date, token)
    )
    visit_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {
        "visit_id":    visit_id,
        "mr_number":   mr_number,
        "doctor_id":   doctor_id,
        "visit_date":  visit_date,
        "token_number": token,
    }


def get_visits_by_mr(mr_number: str):
    """Return all visits for a given MR number with doctor info."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT v.*, d.doctor_name, d.department, d.room_number
        FROM visits v
        JOIN doctors d ON v.doctor_id = d.doctor_id
        WHERE v.mr_number = ?
        ORDER BY v.visit_date DESC
        """,
        (mr_number,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_today_visits():
    """Return all visits created today (for dashboard/admin view)."""
    today = date.today().isoformat()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT v.*, p.name AS patient_name, d.doctor_name, d.department, d.room_number
        FROM visits v
        JOIN patients p ON v.mr_number  = p.mr_number
        JOIN doctors  d ON v.doctor_id  = d.doctor_id
        WHERE v.visit_date = ?
        ORDER BY v.visit_id DESC
        """,
        (today,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_stats():
    """Return basic statistics for the dashboard."""
    today = date.today().isoformat()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM patients")
    total_patients = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM visits WHERE visit_date = ?", (today,))
    today_visits = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM doctors")
    total_doctors = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM patients WHERE registration_date LIKE ?",
        (f"{today}%",)
    )
    today_registrations = cursor.fetchone()[0]

    conn.close()
    return {
        "total_patients":      total_patients,
        "today_visits":        today_visits,
        "total_doctors":       total_doctors,
        "today_registrations": today_registrations,
    }
