import os
import cv2
import face_recognition
import numpy as np
import pickle
from PIL import Image
from werkzeug.utils import secure_filename
from app import app
import uuid

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_face_encoding(file, student_id):
    """Save face encoding and photo for a student"""
    try:
        # Create filename with student ID
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower()
        photo_filename = f"student_{student_id}.{file_extension}"
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_filename)
        
        # Save the uploaded photo
        file.save(photo_path)
        
        # Load image for face recognition
        image = face_recognition.load_image_file(photo_path)
        
        # Find face encodings
        face_encodings = face_recognition.face_encodings(image)
        
        if len(face_encodings) == 0:
            # Clean up the saved photo
            if os.path.exists(photo_path):
                os.remove(photo_path)
            return {
                'success': False,
                'message': 'No face detected in the image. Please upload a clear photo with a visible face.'
            }
        
        if len(face_encodings) > 1:
            # Clean up the saved photo
            if os.path.exists(photo_path):
                os.remove(photo_path)
            return {
                'success': False,
                'message': 'Multiple faces detected. Please upload a photo with only one face.'
            }
        
        # Save face encoding
        encoding_filename = f"encoding_{student_id}.pkl"
        encoding_path = os.path.join('static/face_encodings', encoding_filename)
        
        with open(encoding_path, 'wb') as f:
            pickle.dump(face_encodings[0], f)
        
        # Optimize image size to save storage
        optimize_image(photo_path)
        
        return {
            'success': True,
            'encoding_path': encoding_path,
            'photo_path': photo_path,
            'message': 'Face encoding saved successfully'
        }
        
    except Exception as e:
        app.logger.error(f"Error saving face encoding: {str(e)}")
        return {
            'success': False,
            'message': f'Error processing image: {str(e)}'
        }

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
    """Recognize face in the given image"""
    try:
        # Convert BGR to RGB for face_recognition
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Find face encodings in the image
        face_locations = face_recognition.face_locations(rgb_image)
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
        
        if len(face_encodings) == 0:
            return {'success': False, 'message': 'No face detected'}
        
        # Load all known face encodings
        known_encodings = []
        known_student_ids = []
        
        encoding_dir = 'static/face_encodings'
        if os.path.exists(encoding_dir):
            for filename in os.listdir(encoding_dir):
                if filename.endswith('.pkl'):
                    try:
                        student_id = int(filename.split('_')[1].split('.')[0])
                        encoding_path = os.path.join(encoding_dir, filename)
                        
                        with open(encoding_path, 'rb') as f:
                            encoding = pickle.load(f)
                            known_encodings.append(encoding)
                            known_student_ids.append(student_id)
                    except Exception as e:
                        app.logger.error(f"Error loading encoding {filename}: {str(e)}")
                        continue
        
        if not known_encodings:
            return {'success': False, 'message': 'No registered faces found'}
        
        # Compare faces
        for face_encoding in face_encodings:
            # Calculate face distances
            face_distances = face_recognition.face_distance(known_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            best_distance = face_distances[best_match_index]
            
            # Convert distance to confidence (lower distance = higher confidence)
            confidence = 1 - best_distance
            
            if confidence >= confidence_threshold:
                return {
                    'success': True,
                    'student_id': known_student_ids[best_match_index],
                    'confidence': round(confidence, 3),
                    'message': 'Face recognized successfully'
                }
        
        return {'success': False, 'message': 'Face not recognized with sufficient confidence'}
        
    except Exception as e:
        app.logger.error(f"Error in face recognition: {str(e)}")
        return {'success': False, 'message': 'Recognition failed due to technical error'}

def generate_id_card(student):
    """Generate ID card data for a student"""
    return {
        'student_id': student.student_id,
        'name': student.full_name,
        'course': student.course,
        'year': student.year,
        'section': student.section,
        'photo_path': student.photo_path
    }
