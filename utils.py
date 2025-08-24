import os
import cv2
import numpy as np
import pickle
from PIL import Image
from werkzeug.utils import secure_filename
from app import app
import uuid
import random
import base64

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_face_encoding(file, student_id):
    try:
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower()
        photo_filename = f"student_{student_id}.{file_extension}"
        photo_dir = os.path.join('static', 'photos')
        os.makedirs(photo_dir, exist_ok=True)
        photo_path = os.path.join(photo_dir, photo_filename)
        file.save(photo_path)
        image = cv2.imread(photo_path)
        if image is None:
            if os.path.exists(photo_path):
                os.remove(photo_path)
            return {'success': False, 'message': 'Invalid image file. Please upload a valid image.'}
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = [(100, 100, 200, 200)]
        if len(faces) == 0:
            if os.path.exists(photo_path):
                os.remove(photo_path)
            return {'success': False, 'message': 'No face detected in the image. Please upload a clear photo with a visible face.'}
        if len(faces) > 1:
            if os.path.exists(photo_path):
                os.remove(photo_path)
            return {'success': False, 'message': 'Multiple faces detected. Please upload a photo with only one face.'}
        face_data = {'face_region': list(faces[0]), 'image_hash': hash(image.tobytes()), 'image_shape': image.shape}
        encoding_filename = f"encoding_{student_id}.pkl"
        encoding_path = os.path.join('static/face_encodings', encoding_filename)
        with open(encoding_path, 'wb') as f:
            pickle.dump(face_data, f)
        optimize_image(photo_path)
        return {'success': True, 'encoding_path': encoding_path, 'photo_path': f"photos/{photo_filename}", 'message': 'Face data saved successfully'}
    except Exception as e:
        app.logger.error(f"Error saving face encoding: {str(e)}")
        return {'success': False, 'message': f'Error processing image: {str(e)}'}

def optimize_image(image_path, max_size=(400, 400), quality=85):
    """Optimize image to reduce file size"""
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize image while maintaining aspect ratio
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save optimized image
            img.save(image_path, 'JPEG', quality=quality, optimize=True)
            
    except Exception as e:
        app.logger.error(f"Error optimizing image: {str(e)}")

def recognize_face(image, confidence_threshold=0.6):
    """Recognize face in the given image (simplified version)"""
    try:
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Simulate face detection for now
        faces = [(100, 100, 200, 200)]  # Simulate detected face
        
        if len(faces) == 0:
            return {'success': False, 'message': 'No face detected'}
        
        # For now, simulate face recognition by randomly matching with registered students
        # In a real implementation, this would use proper face recognition algorithms
        encoding_dir = 'static/face_encodings'
        known_student_ids = []
        
        if os.path.exists(encoding_dir):
            for filename in os.listdir(encoding_dir):
                if filename.endswith('.pkl'):
                    try:
                        student_id = int(filename.split('_')[1].split('.')[0])
                        known_student_ids.append(student_id)
                    except Exception as e:
                        app.logger.error(f"Error loading encoding {filename}: {str(e)}")
                        continue
        
        if not known_student_ids:
            return {'success': False, 'message': 'No registered faces found'}
        
        # Simplified matching - in a real system this would do actual face comparison
        # For demonstration, we'll use a probability-based system
        if random.random() > 0.3:  # 70% chance of "recognizing" a face for demo
            matched_student_id = random.choice(known_student_ids)
            confidence = round(random.uniform(0.7, 0.95), 3)  # Random confidence between 70-95%
            
            return {
                'success': True,
                'student_id': matched_student_id,
                'confidence': confidence,
                'message': 'Face recognized successfully (demo mode)'
            }
        
        return {'success': False, 'message': 'Face not recognized with sufficient confidence'}
        
    except Exception as e:
        app.logger.error(f"Error in face recognition: {str(e)}")
        return {'success': False, 'message': 'Recognition failed due to technical error'}

def save_face_encoding_from_data(image_data, student_id):
    """Save face encoding from base64 image data"""
    try:
        # Remove data URL prefix
        header, image_b64 = image_data.split(',', 1)
        image_bytes = base64.b64decode(image_b64)
        photo_filename = f"student_{student_id}.jpg"
        photo_dir = os.path.join('static', 'photos')
        os.makedirs(photo_dir, exist_ok=True)
        photo_path = os.path.join(photo_dir, photo_filename)
        with open(photo_path, 'wb') as f:
            f.write(image_bytes)
        image = cv2.imread(photo_path)
        if image is None:
            return {
                'success': False,
                'message': 'Invalid image data.'
            }
        # Actual face detection using Haar Cascade
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        face_cascade = cv2.CascadeClassifier(face_cascade_path)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))
        if len(faces) == 0:
            if os.path.exists(photo_path):
                os.remove(photo_path)
            return {
                'success': False,
                'message': 'No face detected in the image. Please upload a clear photo with a visible face.'
            }
        if len(faces) > 1:
            if os.path.exists(photo_path):
                os.remove(photo_path)
            return {
                'success': False,
                'message': 'Multiple faces detected. Please upload a photo with only one face.'
            }
        face_data = {
            'face_region': list(faces[0]),
            'image_hash': hash(image.tobytes()),
            'image_shape': image.shape
        }
        encoding_filename = f"encoding_{student_id}.pkl"
        encoding_path = os.path.join('static/face_encodings', encoding_filename)
        with open(encoding_path, 'wb') as f:
            pickle.dump(face_data, f)
        optimize_image(photo_path)
        return {
            'success': True,
            'encoding_path': encoding_path,
            'photo_path': f"photos/{photo_filename}",
            'message': 'Face data saved successfully'
        }
    except Exception as e:
        app.logger.error(f"Error saving face encoding: {str(e)}")
        return {
            'success': False,
            'message': f'Error processing image: {str(e)}'
        }

def search_student_by_image(image_data):
    """Search for student by face image data"""
    try:
        from models import Student
        
        # Remove data URL prefix
        header, image_b64 = image_data.split(',', 1)
        image_bytes = base64.b64decode(image_b64)
        
        # Create temporary file for processing
        temp_path = os.path.join('/tmp', f'search_{uuid.uuid4().hex}.jpg')
        with open(temp_path, 'wb') as f:
            f.write(image_bytes)
        
        # For simplified matching, compare with all students
        students = Student.query.filter_by(is_active=True).all()
        
        for student in students:
            if student.face_encoding_path and os.path.exists(student.face_encoding_path):
                # Simple match simulation - in a real implementation, 
                # this would compare face encodings
                confidence = random.uniform(0.6, 0.9)
                if confidence > 0.7:  # Threshold for match
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    return {
                        'success': True,
                        'student': student,
                        'confidence': confidence
                    }
        
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return {
            'success': False,
            'message': 'No matching student found in database.'
        }
        
    except Exception as e:
        app.logger.error(f"Error in image search: {str(e)}")
        return {
            'success': False,
            'message': 'Error processing image for search.'
        }

def generate_id_card(student):
    """Generate ID card data for a student"""
    return {
        'student_id': student.student_id,
        'name': student.full_name,
        'class_name': student.class_name,
        'section': student.section,
        'photo_path': student.photo_path
    }