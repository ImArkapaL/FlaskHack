// Client-side JavaScript for Raspberry Pi interface

class AttendanceClient {
    constructor() {
        this.video = document.getElementById('video');
        this.canvas = document.getElementById('canvas');
        this.captureBtn = document.getElementById('captureBtn');
        this.statusMessage = document.getElementById('statusMessage');
        this.loadingSpinner = document.getElementById('loadingSpinner');
        
        this.isProcessing = false;
        this.stream = null;
        
        this.init();
    }
    
    async init() {
        await this.setupCamera();
        this.setupEventListeners();
        this.showStatus('Ready to capture. Please look at the camera.', 'info');
    }
    
    async setupCamera() {
        try {
            // Request camera access
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                    facingMode: 'user'
                }
            });
            
            this.video.srcObject = this.stream;
            
            this.video.addEventListener('loadedmetadata', () => {
                this.video.play();
                this.showStatus('Camera ready. Position your face in the frame.', 'info');
            });
            
        } catch (error) {
            console.error('Error accessing camera:', error);
            this.showStatus('Camera access denied or not available. Please check your camera permissions.', 'error');
            this.captureBtn.disabled = true;
        }
    }
    
    setupEventListeners() {
        this.captureBtn.addEventListener('click', () => {
            if (!this.isProcessing) {
                this.captureAndRecognize();
            }
        });
        
        // Enable automatic capture every 3 seconds
        setInterval(() => {
            if (!this.isProcessing) {
                this.captureAndRecognize();
            }
        }, 3000);
        
        // Initial automatic capture after 2 seconds
        setTimeout(() => {
            if (!this.isProcessing) {
                this.captureAndRecognize();
            }
        }, 2000);
    }
    
    async captureAndRecognize() {
        if (this.isProcessing) return;
        
        this.isProcessing = true;
        this.captureBtn.disabled = true;
        this.showLoading(true);
        this.showStatus('Processing face recognition...', 'info');
        
        try {
            // Capture image from video
            const imageData = this.captureImage();
            
            if (!imageData) {
                throw new Error('Failed to capture image');
            }
            
            // Send image to server for recognition
            const result = await this.sendImageToServer(imageData);
            
            if (result.success) {
                this.showStatus(result.message, 'success');
                
                // Show additional info if available
                if (result.student_name && result.student_id) {
                    setTimeout(() => {
                        this.showStatus(
                            `Welcome ${result.student_name} (${result.student_id})!`, 
                            'success'
                        );
                    }, 2000);
                }
                
                // Auto-reset after 6 seconds for successful recognition
                setTimeout(() => {
                    this.resetInterface();
                }, 6000);
                
            } else {
                // Don't show error for scanning - just keep scanning silently
                this.showStatus('Scanning for faces...', 'info');
                setTimeout(() => {
                    this.resetInterface();
                }, 1000);
            }
            
        } catch (error) {
            console.error('Recognition error:', error);
            this.showStatus('Scanning...', 'info');
            setTimeout(() => {
                this.resetInterface();
            }, 1000);
        }
    }
    
    captureImage() {
        try {
            const canvas = this.canvas;
            const context = canvas.getContext('2d');
            
            // Set canvas dimensions to match video
            canvas.width = this.video.videoWidth;
            canvas.height = this.video.videoHeight;
            
            // Draw video frame to canvas
            context.drawImage(this.video, 0, 0, canvas.width, canvas.height);
            
            // Convert to base64
            return canvas.toDataURL('image/jpeg', 0.8);
            
        } catch (error) {
            console.error('Error capturing image:', error);
            return null;
        }
    }
    
    async sendImageToServer(imageData) {
        try {
            const response = await fetch('/recognize_face', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    image: imageData
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
            
        } catch (error) {
            console.error('Error sending image to server:', error);
            throw error;
        }
    }
    
    showStatus(message, type) {
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        
        const classes = {
            success: 'success-message',
            error: 'error-message',
            info: 'info-message'
        };
        
        this.statusMessage.innerHTML = `
            <div class="${classes[type]}">
                <i class="${icons[type]} status-icon"></i>
                <div>${message}</div>
            </div>
        `;
    }
    
    showLoading(show) {
        if (show) {
            this.loadingSpinner.style.display = 'block';
            this.captureBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
        } else {
            this.loadingSpinner.style.display = 'none';
            this.captureBtn.innerHTML = '<i class="fas fa-camera me-2"></i>Capture for Attendance';
        }
    }
    
    resetInterface() {
        this.isProcessing = false;
        this.captureBtn.disabled = false;
        this.showLoading(false);
        this.showStatus('Ready to capture. Please look at the camera.', 'info');
    }
    
    destroy() {
        // Clean up resources
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
        }
    }
}

// Initialize the attendance client when the page loads
document.addEventListener('DOMContentLoaded', () => {
    const client = new AttendanceClient();
    
    // Handle page unload
    window.addEventListener('beforeunload', () => {
        client.destroy();
    });
});

// Utility functions for client
function showNetworkError() {
    document.getElementById('statusMessage').innerHTML = `
        <div class="error-message">
            <i class="fas fa-wifi status-icon"></i>
            <div>Network connection error. Please check your connection.</div>
        </div>
    `;
}

function showServerError() {
    document.getElementById('statusMessage').innerHTML = `
        <div class="error-message">
            <i class="fas fa-server status-icon"></i>
            <div>Server error. Please contact administrator.</div>
        </div>
    `;
}

// Auto-refresh page every hour to prevent memory leaks
setTimeout(() => {
    window.location.reload();
}, 3600000); // 1 hour
