// Camera utility functions for face recognition

class CameraManager {
    constructor() {
        this.stream = null;
        this.video = null;
        this.canvas = null;
        this.isInitialized = false;
    }
    
    async initialize(videoElement, canvasElement) {
        this.video = videoElement;
        this.canvas = canvasElement;
        
        try {
            await this.requestCameraPermission();
            await this.startVideoStream();
            this.isInitialized = true;
            return { success: true };
        } catch (error) {
            console.error('Camera initialization failed:', error);
            return { success: false, error: error.message };
        }
    }
    
    async requestCameraPermission() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            throw new Error('Camera API not supported');
        }
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 640, max: 1280 },
                    height: { ideal: 480, max: 720 },
                    frameRate: { ideal: 30, max: 60 },
                    facingMode: 'user'
                },
                audio: false
            });
            this.video.srcObject = this.stream;
            return new Promise((resolve, reject) => {
                this.video.onloadedmetadata = () => {
                    this.video.play();
                    resolve();
                };
            });
        } catch (error) {
            // Show a clear message to the user if permission is denied
            alert(handleCameraError(error));
            throw error;
        }
    }
    
    async startVideoStream() {
        try {
            const constraints = {
                video: {
                    width: { ideal: 640, max: 1280 },
                    height: { ideal: 480, max: 720 },
                    frameRate: { ideal: 30, max: 60 },
                    facingMode: 'user' // Front camera for selfies
                },
                audio: false
            };
            
            this.stream = await navigator.mediaDevices.getUserMedia(constraints);
            this.video.srcObject = this.stream;
            
            return new Promise((resolve, reject) => {
                this.video.onloadedmetadata = () => {
                    this.video.play();
                    resolve();
                };
                
                this.video.onerror = () => {
                    reject(new Error('Video loading failed'));
                };
            });
            
        } catch (error) {
            if (error.name === 'NotAllowedError') {
                throw new Error('Camera access denied by user');
            } else if (error.name === 'NotFoundError') {
                throw new Error('No camera device found');
            } else if (error.name === 'NotReadableError') {
                throw new Error('Camera is already in use by another application');
            } else {
                throw new Error('Failed to access camera: ' + error.message);
            }
        }
    }
    
    captureFrame() {
        if (!this.isInitialized || !this.video || !this.canvas) {
            throw new Error('Camera not initialized');
        }
        
        const context = this.canvas.getContext('2d');
        
        // Set canvas size to match video dimensions
        this.canvas.width = this.video.videoWidth;
        this.canvas.height = this.video.videoHeight;
        
        // Draw current video frame to canvas
        context.drawImage(this.video, 0, 0);
        
        // Return image data as base64
        return this.canvas.toDataURL('image/jpeg', 0.8);
    }
    
    captureBlob(quality = 0.8) {
        if (!this.isInitialized) {
            throw new Error('Camera not initialized');
        }
        
        const context = this.canvas.getContext('2d');
        this.canvas.width = this.video.videoWidth;
        this.canvas.height = this.video.videoHeight;
        
        context.drawImage(this.video, 0, 0);
        
        return new Promise((resolve) => {
            this.canvas.toBlob(resolve, 'image/jpeg', quality);
        });
    }
    
    getVideoStats() {
        if (!this.video) return null;
        
        return {
            width: this.video.videoWidth,
            height: this.video.videoHeight,
            readyState: this.video.readyState,
            currentTime: this.video.currentTime
        };
    }
    
    switchCamera() {
        // Switch between front and back camera if available
        return this.startVideoStream();
    }
    
    stopVideoStream() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => {
                track.stop();
            });
            this.stream = null;
        }
        
        if (this.video) {
            this.video.srcObject = null;
        }
        
        this.isInitialized = false;
    }
    
    takeSnapshot(filename = 'snapshot.jpg') {
        if (!this.isInitialized) {
            throw new Error('Camera not initialized');
        }
        
        const imageData = this.captureFrame();
        
        // Create download link
        const link = document.createElement('a');
        link.href = imageData;
        link.download = filename;
        link.click();
    }
    
    // Check if browser supports required features
    static isSupported() {
        return !!(
            navigator.mediaDevices &&
            navigator.mediaDevices.getUserMedia &&
            window.HTMLCanvasElement
        );
    }
    
    // Get available camera devices
    static async getAvailableDevices() {
        try {
            const devices = await navigator.mediaDevices.enumerateDevices();
            return devices.filter(device => device.kind === 'videoinput');
        } catch (error) {
            console.error('Error getting camera devices:', error);
            return [];
        }
    }
}

// Face detection utilities
class FaceDetector {
    constructor() {
        this.isLoaded = false;
    }
    
    // Basic face detection using canvas and image data
    detectFaces(imageData) {
        // This is a simplified face detection
        // In a real implementation, you might use a library like face-api.js
        return new Promise((resolve) => {
            // Simulate face detection
            setTimeout(() => {
                const faceDetected = Math.random() > 0.3; // 70% chance of detection
                resolve({
                    faces: faceDetected ? [{ confidence: 0.85 }] : [],
                    success: faceDetected
                });
            }, 100);
        });
    }
    
    // Validate image quality for face recognition
    validateImageQuality(imageData) {
        return new Promise((resolve) => {
            const img = new Image();
            img.onload = () => {
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                canvas.width = img.width;
                canvas.height = img.height;
                ctx.drawImage(img, 0, 0);
                
                // Basic quality checks
                const checks = {
                    resolution: img.width >= 200 && img.height >= 200,
                    brightness: true, // Simplified - would analyze pixel data
                    sharpness: true,  // Simplified - would check edge detection
                    overall: true
                };
                
                resolve(checks);
            };
            img.src = imageData;
        });
    }
}

// Export classes for use in other scripts
window.CameraManager = CameraManager;
window.FaceDetector = FaceDetector;

// Utility function to check camera permissions
async function checkCameraPermission() {
    try {
        const result = await navigator.permissions.query({ name: 'camera' });
        return result.state; // 'granted', 'denied', or 'prompt'
    } catch (error) {
        console.warn('Permission API not supported');
        return 'unknown';
    }
}

// Utility function to handle camera errors
function handleCameraError(error) {
    const errorMessages = {
        'NotAllowedError': 'Camera access was denied. Please allow camera access and try again.',
        'NotFoundError': 'No camera device was found. Please connect a camera and try again.',
        'NotReadableError': 'Camera is already in use by another application.',
        'OverconstrainedError': 'Camera settings are not supported by your device.',
        'SecurityError': 'Camera access is not allowed due to security restrictions.',
        'AbortError': 'Camera access was aborted.',
        'NotSupportedError': 'Camera is not supported on this device.'
    };
    
    return errorMessages[error.name] || `Camera error: ${error.message}`;
}