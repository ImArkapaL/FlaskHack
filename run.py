"""
Face Recognition Attendance System
Run this file to start the application
"""
if __name__ == '__main__':
    from api.app import app
    from waitress import serve
    serve(app, host='192.168.1.34', port=8000)