from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
from database import init_db, get_db
from auth import create_doctor, verify_doctor
from analysis import compute_risk
from quantum import quantum_optimize
import os, json


app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

app.config['JWT_SECRET_KEY'] = 'namma-vaidya-secret-key-2025'
jwt = JWTManager(app)

# ── Serve frontend pages ──────────────────────────────────────
@app.route('/')
def serve_login():
    return send_from_directory('../frontend', 'login.html')

@app.route('/dashboard')
def serve_dashboard():
    return send_from_directory('../frontend', 'dashboard.html')

# ── Auth routes ───────────────────────────────────────────────
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    doctor_id, error = create_doctor(
        data.get('full_name'),
        data.get('email'),
        data.get('password'),
        data.get('hospital', '')
    )
    if error:
        return jsonify({'error': error}), 400

    token = create_access_token(identity=str(doctor_id))
    return jsonify({'token': token, 'message': 'Account created!'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    doctor, error = verify_doctor(data.get('email'), data.get('password'))
    if error:
        return jsonify({'error': error}), 401

    token = create_access_token(identity=str(doctor['id']))
    return jsonify({
        'token': token,
        'doctor': {
            'full_name': doctor['full_name'],
            'email': doctor['email'],
            'hospital': doctor['hospital']
        }
    }), 200

# ── Analysis route ────────────────────────────────────────────
@app.route('/api/analyse', methods=['POST'])
@jwt_required()
def analyse():
    doctor_id = int(get_jwt_identity())
    data = request.get_json()

    result = compute_risk(
        int(data.get('age', 0)),
        data.get('symptoms', ''),
        data.get('medical_history', ''),
        data.get('duration', ''),
        data.get('spo2', '')
    )

    # Quantum-inspired optimization pass
    quantum_result = quantum_optimize(result['risk_score'])
    result['quantum'] = quantum_result

    # Save record to database

    conn = get_db()
    conn.execute('''
        INSERT INTO patient_records
        (doctor_id, patient_name, age, gender, symptoms,
         bp, pulse, temperature, spo2, medical_history, duration,
         risk_score, risk_level, condition_class, severity_level, grade, treatment)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    ''', (
        doctor_id,
        data.get('patient_name'), data.get('age'), data.get('gender'),
        data.get('symptoms'), data.get('bp'), data.get('pulse'),
        data.get('temperature'), data.get('spo2'),
        data.get('medical_history'), data.get('duration'),
        result['risk_score'], result['risk_level'],
        result['condition_class'], result['severity_level'],
        result['grade'], json.dumps(result['treatments'])
    ))
    conn.commit()
    conn.close()

    return jsonify(result), 200

# ── Patient history route ─────────────────────────────────────
@app.route('/api/records', methods=['GET'])
@jwt_required()
def get_records():
    doctor_id = int(get_jwt_identity())
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM patient_records WHERE doctor_id = ? ORDER BY created_at DESC LIMIT 20',
        (doctor_id,)
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows]), 200

# ── Doctor profile ────────────────────────────────────────────
@app.route('/api/me', methods=['GET'])
@jwt_required()
def get_me():
    doctor_id = int(get_jwt_identity())
    conn = get_db()
    doc = conn.execute(
        'SELECT id, full_name, email, hospital, created_at FROM doctors WHERE id = ?',
        (doctor_id,)
    ).fetchone()
    conn.close()
    return jsonify(dict(doc)), 200

# ── Run ───────────────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    print("🚀 Namma Vaidya server running at http://localhost:5000")
    app.run(debug=True, port=5000)