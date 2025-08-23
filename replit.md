# Smart Attendance System

## Overview

This is a Flask-based smart attendance system that uses facial recognition technology to automatically track student attendance. The system allows administrators to register students with their photos, which are then processed to create facial encodings for recognition. Students can mark their attendance by having their faces recognized through a camera interface, eliminating the need for manual attendance taking.

The system provides comprehensive student management features, attendance tracking, statistical analysis, and generates digital ID cards for registered students. It's designed to be deployed on various platforms including Raspberry Pi devices for classroom deployment.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask web application with SQLAlchemy ORM for database operations
- **Database**: SQLite by default with configurable database URL support for production deployments
- **Authentication**: Session-based admin authentication with password hashing using Werkzeug security utilities
- **File Handling**: Secure file uploads with size limits (16MB) and extension validation for student photos

### Face Recognition Engine
- **Library**: face_recognition library built on dlib for facial encoding and recognition
- **Processing**: OpenCV for image processing and computer vision operations
- **Storage**: Face encodings stored as pickle files in the file system, with photo storage in static uploads directory
- **Validation**: Single face detection validation to ensure photo quality and prevent multiple face conflicts

### Frontend Architecture
- **Templates**: Jinja2 templating with Bootstrap 5 for responsive UI design
- **JavaScript**: Vanilla JavaScript with camera access APIs for real-time face capture
- **Styling**: Custom CSS with gradient backgrounds and modern card-based layouts
- **Charts**: Chart.js integration for attendance statistics and analytics visualization

### Data Models
- **Admin**: User management with hashed passwords for system access control
- **Student**: Complete student profiles with academic information and biometric data references
- **AttendanceRecord**: Time-stamped attendance logs with confidence scores from face recognition
- **SystemSettings**: Configuration storage for system-wide settings and preferences

### API Structure
- **Admin Routes**: Login/logout, dashboard with statistics, and system management
- **Student Management**: Registration, editing, deletion, and bulk operations
- **Attendance**: Real-time face recognition endpoint and attendance record management
- **Utilities**: Face encoding processing, ID card generation, and file validation

### Security Features
- **Session Management**: Secure session handling with configurable secret keys
- **File Validation**: Strict file type checking and secure filename handling
- **Database**: SQL injection protection through SQLAlchemy ORM
- **Proxy Support**: ProxyFix middleware for deployment behind reverse proxies

## External Dependencies

### Core Framework Dependencies
- **Flask**: Web application framework with SQLAlchemy extension for database operations
- **Werkzeug**: WSGI utilities including password hashing and secure file handling

### Computer Vision Libraries
- **face_recognition**: Primary facial recognition library for encoding and matching faces
- **OpenCV (cv2)**: Computer vision library for image processing and camera operations
- **PIL (Pillow)**: Python Imaging Library for image manipulation and processing

### Frontend Libraries
- **Bootstrap 5**: CSS framework delivered via CDN for responsive design
- **Font Awesome**: Icon library for UI enhancement
- **Chart.js**: JavaScript charting library for statistics visualization

### Python Standard Libraries
- **pickle**: Serialization for storing face encodings
- **base64**: Encoding for image data transmission
- **datetime**: Time and date handling for attendance records
- **uuid**: Unique identifier generation for file naming
- **os**: Operating system interface for file and directory operations

### Development and Deployment
- **SQLite**: Default database engine with support for PostgreSQL and other databases
- **Static File Serving**: Flask's built-in static file serving for photos and assets
- **Environment Variables**: Configuration through environment variables for production deployment