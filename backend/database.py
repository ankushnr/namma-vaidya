import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'nammavaidya.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Doctors table (login accounts)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            hospital TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Patient records table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patient_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_id INTEGER NOT NULL,
            patient_name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            symptoms TEXT,
            bp TEXT,
            pulse TEXT,
            temperature TEXT,
            spo2 TEXT,
            medical_history TEXT,
            duration TEXT,
            risk_score INTEGER,
            risk_level TEXT,
            condition_class TEXT,
            severity_level TEXT,
            grade TEXT,
            treatment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (doctor_id) REFERENCES doctors(id)
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Database initialised successfully.")