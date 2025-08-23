#!/usr/bin/env python3
"""
Face Recognition Attendance System
Run this file to start the application
"""

if __name__ == '__main__':
    from app import app
    app.run(host='0.0.0.0', port=5000, debug=True)