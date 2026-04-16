import bcrypt
from database import get_db

def create_doctor(full_name, email, password, hospital):
    conn = get_db()
    cursor = conn.cursor()

    # Check if email already exists
    existing = cursor.execute(
        'SELECT id FROM doctors WHERE email = ?', (email,)
    ).fetchone()

    if existing:
        conn.close()
        return None, 'Email already registered. Please log in.'

    # Hash the password securely
    password_hash = bcrypt.hashpw(
        password.encode('utf-8'), bcrypt.gensalt()
    ).decode('utf-8')

    cursor.execute(
        'INSERT INTO doctors (full_name, email, password_hash, hospital) VALUES (?, ?, ?, ?)',
        (full_name, email, password_hash, hospital)
    )
    conn.commit()
    doctor_id = cursor.lastrowid
    conn.close()
    return doctor_id, None

def verify_doctor(email, password):
    conn = get_db()
    cursor = conn.cursor()

    doctor = cursor.execute(
        'SELECT * FROM doctors WHERE email = ?', (email,)
    ).fetchone()
    conn.close()

    if not doctor:
        return None, 'No account found with this email.'

    if not bcrypt.checkpw(password.encode('utf-8'), doctor['password_hash'].encode('utf-8')):
        return None, 'Incorrect password.'

    return dict(doctor), None