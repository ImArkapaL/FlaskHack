# Face Recognition Attendance System - Setup Instructions

## Files You Need

Copy all the following files from your Replit project:

### Core Application Files:
- `app.py` - Main Flask application
- `models.py` - Database models
- `routes.py` - All routes and API endpoints
- `utils.py` - Utility functions for face processing
- `run.py` - Application runner (created for you)

### Frontend Files:
- `templates/` - All HTML templates (entire folder)
- `static/` - All CSS, JavaScript, and uploaded files (entire folder)

### Configuration Files:
- `setup_requirements.txt` - Rename this to `requirements.txt`

## Environment Setup

1. **Create a Python virtual environment:**
   ```bash
   python -m venv attendance_system
   source attendance_system/bin/activate  # On Windows: attendance_system\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables:**
   ```bash
   export SESSION_SECRET="your-secret-key-change-this-in-production"
   ```
   
   Or create a `.env` file:
   ```
   SESSION_SECRET=your-secret-key-change-this-in-production
   ```

## Database Setup

The application uses SQLite by default. On first run, it will:
- Create `attendance.db` in the project root
- Set up all necessary tables
- Create a default admin user (username: `admin`, password: `admin123`)

## Directory Structure

Make sure you have these directories:
```
your_project/
├── app.py
├── models.py
├── routes.py
├── utils.py
├── run.py
├── requirements.txt
├── attendance.db (created automatically)
├── static/
│   ├── css/
│   ├── js/
│   ├── uploads/ (created automatically)
│   └── face_encodings/ (created automatically)
└── templates/
    ├── base.html
    ├── login.html
    ├── dashboard.html
    ├── client.html
    └── ... (all other templates)
```

## Running the Application

1. **Development mode:**
   ```bash
   python run.py
   ```

2. **Production mode with Gunicorn:**
   ```bash
   gunicorn --bind 0.0.0.0:5000 --workers 4 main:app
   ```
   
   (Note: Create `main.py` with `from app import app` for Gunicorn)

## Access the Application

- **Admin Dashboard:** http://localhost:5000/login
  - Username: `admin`
  - Password: `admin123`

- **Face Recognition Client:** http://localhost:5000/client
  - Camera interface for attendance marking

## Important Notes

1. **Camera Permissions:** The face recognition client needs camera access
2. **HTTPS:** For camera access in production, serve over HTTPS
3. **Security:** Change the default admin password immediately
4. **Database:** The current setup uses a simplified face recognition system (no actual face matching libraries due to complexity)

## Troubleshooting

1. **Camera not working:** Ensure HTTPS in production
2. **Database errors:** Delete `attendance.db` to reset
3. **Import errors:** Check all dependencies are installed
4. **Permission errors:** Ensure upload directories are writable

## Production Deployment

For production deployment:
1. Set `SESSION_SECRET` environment variable
2. Use a production WSGI server like Gunicorn
3. Configure a reverse proxy (nginx)
4. Set up SSL/TLS certificates
5. Change default admin credentials