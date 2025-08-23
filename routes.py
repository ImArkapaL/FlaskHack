from flask import render_template, request, redirect, url_for, flash, session, jsonify, send_file
from app import app, db
from models import Admin, Student, AttendanceRecord, SystemSettings
from utils import save_face_encoding, recognize_face, generate_id_card, allowed_file
import os
import cv2
import numpy as np
from datetime import datetime, date
import base64
from io import BytesIO
from PIL import Image
import json

@app.route('/')
def index():
    """Default route - show client interface for Raspberry Pi"""
    return redirect(url_for('client'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and admin.check_password(password):
            session['admin_id'] = admin.id
            session['admin_username'] = admin.username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    # Get statistics
    total_students = Student.query.count()
    today_attendance = AttendanceRecord.query.filter_by(date=date.today()).count()
    active_students = Student.query.filter_by(is_active=True).count()
    
    # Get recent attendance records
    recent_attendance = AttendanceRecord.query.order_by(AttendanceRecord.timestamp.desc()).limit(10).all()
    
    return render_template('dashboard.html', 
                         total_students=total_students,
                         today_attendance=today_attendance,
                         active_students=active_students,
                         recent_attendance=recent_attendance)

@app.route('/register_student', methods=['GET', 'POST'])
def register_student():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            # Get form data
            student_id = request.form['student_id']
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            phone = request.form.get('phone', '')
            course = request.form.get('course', '')
            year = request.form.get('year', '')
            section = request.form.get('section', '')
            
            # Check if student already exists
            existing_student = Student.query.filter_by(student_id=student_id).first()
            if existing_student:
                flash('Student ID already exists!', 'error')
                return render_template('register_student.html')
            
            # Handle face image upload
            if 'face_image' not in request.files:
                flash('No face image uploaded', 'error')
                return render_template('register_student.html')
            
            file = request.files['face_image']
            if file.filename == '' or not allowed_file(file.filename):
                flash('Invalid file format. Please upload a valid image.', 'error')
                return render_template('register_student.html')
            
            # Create new student
            student = Student(
                student_id=student_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                course=course,
                year=year,
                section=section
            )
            
            # Save student to database first to get ID
            db.session.add(student)
            db.session.commit()
            
            # Save face encoding
            encoding_result = save_face_encoding(file, student.id)
            if encoding_result['success']:
                student.face_encoding_path = encoding_result['encoding_path']
                student.photo_path = encoding_result['photo_path']
                db.session.commit()
                flash('Student registered successfully!', 'success')
                return redirect(url_for('manage_students'))
            else:
                # Remove student if face encoding failed
                db.session.delete(student)
                db.session.commit()
                flash(f'Face encoding failed: {encoding_result["message"]}', 'error')
                
        except Exception as e:
            db.session.rollback()
            flash(f'Error registering student: {str(e)}', 'error')
    
    return render_template('register_student.html')

@app.route('/manage_students')
def manage_students():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    search = request.args.get('search', '')
    if search:
        students = Student.query.filter(
            (Student.first_name.contains(search)) |
            (Student.last_name.contains(search)) |
            (Student.student_id.contains(search)) |
            (Student.email.contains(search))
        ).all()
    else:
        students = Student.query.all()
    
    return render_template('manage_students.html', students=students, search=search)

@app.route('/attendance_register')
def attendance_register():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    # Get date filter from query params
    filter_date = request.args.get('date', date.today().strftime('%Y-%m-%d'))
    
    # Convert string to date object
    try:
        filter_date_obj = datetime.strptime(filter_date, '%Y-%m-%d').date()
    except:
        filter_date_obj = date.today()
    
    # Get attendance records for the selected date
    attendance_records = AttendanceRecord.query.filter_by(date=filter_date_obj).order_by(AttendanceRecord.timestamp.desc()).all()
    
    return render_template('attendance_register.html', 
                         attendance_records=attendance_records,
                         filter_date=filter_date)

@app.route('/statistics')
def statistics():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    # Get attendance statistics for the last 7 days
    from datetime import timedelta
    from sqlalchemy import func
    
    end_date = date.today()
    start_date = end_date - timedelta(days=6)
    
    # Daily attendance count for the last 7 days
    daily_stats = db.session.query(
        AttendanceRecord.date,
        func.count(AttendanceRecord.id).label('count')
    ).filter(
        AttendanceRecord.date >= start_date
    ).group_by(AttendanceRecord.date).all()
    
    # Course-wise statistics
    course_stats = db.session.query(
        Student.course,
        func.count(Student.id).label('count')
    ).filter(Student.course.isnot(None)).group_by(Student.course).all()
    
    return render_template('statistics.html', 
                         daily_stats=daily_stats,
                         course_stats=course_stats)

@app.route('/client')
def client():
    """Raspberry Pi client interface"""
    return render_template('client.html')

@app.route('/api/recognize_face', methods=['POST'])
def api_recognize_face():
    """API endpoint for face recognition from client"""
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'success': False, 'message': 'No image data provided'})
        
        # Decode base64 image
        image_data = base64.b64decode(data['image'].split(',')[1])
        image = Image.open(BytesIO(image_data))
        
        # Convert PIL image to OpenCV format
        image_array = np.array(image)
        if len(image_array.shape) == 3:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        # Recognize face
        result = recognize_face(image_array)
        
        if result['success']:
            student = Student.query.get(result['student_id'])
            if student:
                # Check if already marked today
                today_record = AttendanceRecord.query.filter_by(
                    student_id=student.id,
                    date=date.today()
                ).first()
                
                if not today_record:
                    # Mark attendance
                    attendance = AttendanceRecord(
                        student_id=student.id,
                        confidence=result['confidence']
                    )
                    db.session.add(attendance)
                    db.session.commit()
                    
                    return jsonify({
                        'success': True,
                        'message': f'Welcome {student.full_name}! Attendance marked.',
                        'student_name': student.full_name,
                        'student_id': student.student_id,
                        'already_marked': False
                    })
                else:
                    return jsonify({
                        'success': True,
                        'message': f'Welcome {student.full_name}! Already marked today.',
                        'student_name': student.full_name,
                        'student_id': student.student_id,
                        'already_marked': True
                    })
        
        return jsonify({'success': False, 'message': 'Face not recognized'})
        
    except Exception as e:
        app.logger.error(f"Face recognition error: {str(e)}")
        return jsonify({'success': False, 'message': 'Recognition failed'})

@app.route('/generate_id_card/<int:student_id>')
def generate_student_id_card(student_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    student = Student.query.get_or_404(student_id)
    return render_template('id_card.html', student=student)

@app.route('/delete_student/<int:student_id>')
def delete_student(student_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    student = Student.query.get_or_404(student_id)
    
    # Delete associated files
    if student.face_encoding_path and os.path.exists(student.face_encoding_path):
        os.remove(student.face_encoding_path)
    if student.photo_path and os.path.exists(student.photo_path):
        os.remove(student.photo_path)
    
    # Delete attendance records
    AttendanceRecord.query.filter_by(student_id=student.id).delete()
    
    # Delete student
    db.session.delete(student)
    db.session.commit()
    
    flash('Student deleted successfully!', 'success')
    return redirect(url_for('manage_students'))

# Initialize default admin user
def create_default_admin():
    with app.app_context():
        if not Admin.query.first():
            admin = Admin(username='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Default admin created: username='admin', password='admin123'")

# Call the function to create default admin
create_default_admin()
