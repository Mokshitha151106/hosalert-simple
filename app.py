from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==================== DATABASE MODELS ====================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # nurse or family
    name = db.Column(db.String(100), nullable=False)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    room_number = db.Column(db.String(20))
    disease = db.Column(db.String(200))
    nurse_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    name = db.Column(db.String(100))
    dosage = db.Column(db.String(50))
    time = db.Column(db.String(10))  # HH:MM format
    status = db.Column(db.String(20), default='pending')

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicine.id'))
    message = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')

# ==================== ROUTES ====================

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/dashboard')
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username'], password=data['password']).first()
    if user:
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        return jsonify({'success': True, 'role': user.role})
    return jsonify({'success': False, 'message': 'Invalid credentials'})

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    return render_template('dashboard.html')

@app.route('/api/patients')
def get_patients():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    patients = Patient.query.all()
    result = []
    for p in patients:
        result.append({
            'id': p.id,
            'name': p.name,
            'age': p.age,
            'room_number': p.room_number,
            'disease': p.disease
        })
    return jsonify(result)

@app.route('/api/medicines/<int:patient_id>')
def get_medicines(patient_id):
    medicines = Medicine.query.filter_by(patient_id=patient_id).all()
    result = []
    for m in medicines:
        result.append({
            'id': m.id,
            'name': m.name,
            'dosage': m.dosage,
            'time': m.time,
            'status': m.status
        })
    return jsonify(result)

@app.route('/api/alerts')
def get_alerts():
    alerts = Alert.query.filter_by(status='active').order_by(Alert.created_at.desc()).limit(20).all()
    result = []
    for a in alerts:
        patient = Patient.query.get(a.patient_id)
        result.append({
            'id': a.id,
            'patient_name': patient.name if patient else 'Unknown',
            'message': a.message,
            'time': a.created_at.strftime('%H:%M:%S')
        })
    return jsonify(result)

@app.route('/api/alerts/<int:alert_id>/acknowledge', methods=['POST'])
def acknowledge_alert(alert_id):
    alert = Alert.query.get(alert_id)
    if alert:
        alert.status = 'acknowledged'
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ==================== CREATE SAMPLE DATA ====================

def create_sample_data():
    # Create nurse
    if not User.query.filter_by(username='nurse').first():
        nurse = User(username='nurse', password='nurse123', role='nurse', name='Head Nurse')
        db.session.add(nurse)
        
        # Create patient
        patient = Patient(name='Rajesh Kumar', age=65, room_number='101', disease='Hypertension', nurse_id=1)
        db.session.add(patient)
        db.session.commit()
        
        # Create medicine
        medicine = Medicine(patient_id=1, name='Amlodipine', dosage='5mg', time='09:00', status='pending')
        db.session.add(medicine)
        
        # Create alert
        alert = Alert(patient_id=1, medicine_id=1, message='Medication due: Amlodipine 5mg for Rajesh Kumar')
        db.session.add(alert)
        db.session.commit()

# ==================== RUN APP ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_sample_data()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
