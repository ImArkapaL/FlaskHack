// Client-side JavaScript for Raspberry Pi interface

class AttendanceClient {
    constructor() {
        this.video = document.getElementById('video');
        this.canvas = document.getElementById('canvas');
        this.statusMessage = document.getElementById('statusMessage');
        this.isPaused = false;
        this.captureInterval = null;
        this.initCamera();
    }

    initCamera() {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(stream => {
                this.video.srcObject = stream;
                this.startAutoCapture();
            })
            .catch(err => {
                this.statusMessage.textContent = 'Camera access denied.';
                this.statusMessage.className = 'status-message error-message';
            });
    }

    startAutoCapture() {
        this.captureInterval = setInterval(() => {
            if (!this.isPaused) {
                this.captureAndSend();
            }
        }, 5000);
    }

    pauseAfterAttendance() {
        this.isPaused = true;
        setTimeout(() => {
            this.isPaused = false;
            this.statusMessage.textContent = 'Ready for next attendance.';
            this.statusMessage.className = 'status-message info-message';
        }, 10000);
    }

    captureAndSend() {
        this.canvas.width = this.video.videoWidth;
        this.canvas.height = this.video.videoHeight;
        this.canvas.getContext('2d').drawImage(this.video, 0, 0);
        const imageData = this.canvas.toDataURL('image/jpeg');
        this.statusMessage.textContent = 'Processing...';
        this.statusMessage.className = 'status-message info-message';
        fetch('/api/recognize_face', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: imageData })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                if (data.student_name && data.student_name.trim() !== "") {
                    this.statusMessage.textContent = `Attendance marked for: ${data.student_name}`;
                    this.statusMessage.className = 'status-message success-message';
                    this.pauseAfterAttendance();
                } else {
                    this.statusMessage.textContent = '';
                    this.statusMessage.className = 'status-message';
                }
            } else {
                this.statusMessage.textContent = data.message || '';
                this.statusMessage.className = 'status-message error-message';
            }
        })
        .catch(() => {
            this.statusMessage.textContent = 'Error sending image.';
            this.statusMessage.className = 'status-message error-message';
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new AttendanceClient();
});