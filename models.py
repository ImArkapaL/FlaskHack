from api.app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))
    class_name = db.Column(db.String(20), nullable=False)
    section = db.Column(db.String(10), nullable=False)
    father_name = db.Column(db.String(100))
    mother_name = db.Column(db.String(100))
    address = db.Column(db.Text)
    face_encoding_path = db.Column(db.String(255))
    photo_path = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    attendance_records = db.relationship('AttendanceRecord', backref='student', lazy=True)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class AttendanceRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    date = db.Column(db.Date, default=datetime.now().date)
    status = db.Column(db.String(20), default='present')
    confidence = db.Column(db.Float)
    photo_path = db.Column(db.String(255))
    
    def __repr__(self):
        return f'<AttendanceRecord {self.id} - {self.date}>'

class SystemSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    setting_name = db.Column(db.String(50), unique=True, nullable=False)
    setting_value = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)