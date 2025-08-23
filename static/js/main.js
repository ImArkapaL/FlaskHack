// Main JavaScript for Smart Attendance System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initializeTooltips();
    
    // Add fade-in animation to cards
    addFadeInAnimation();
    
    // Initialize form validations
    initializeFormValidation();
    
    // Auto-hide alerts after 5 seconds
    autoHideAlerts();
});

// Initialize Bootstrap tooltips
function initializeTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Add fade-in animation to cards
function addFadeInAnimation() {
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

// Initialize form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        });
    });
}

// Auto-hide alerts
function autoHideAlerts() {
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

// Utility function to format dates
function formatDate(dateString) {
    const options = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

// Utility function to format time
function formatTime(dateString) {
    const options = { 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit' 
    };
    return new Date(dateString).toLocaleTimeString(undefined, options);
}

// Function to show loading state on buttons
function showButtonLoading(button, loadingText = 'Loading...') {
    const originalText = button.innerHTML;
    button.disabled = true;
    button.innerHTML = `<i class="fas fa-spinner fa-spin me-1"></i>${loadingText}`;
    
    return function() {
        button.disabled = false;
        button.innerHTML = originalText;
    };
}

// Function to show toast notifications
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toastId = 'toast-' + Date.now();
    const toastHTML = `
        <div id="${toastId}" class="toast align-items-center text-white bg-${type} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
    
    // Remove toast element after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

// Create toast container if it doesn't exist
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

// Function to confirm actions
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Function to copy text to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showToast('Copied to clipboard!', 'success');
    }, function(err) {
        showToast('Failed to copy text', 'danger');
    });
}

// Function to validate file size and type
function validateFile(file, maxSizeMB = 5, allowedTypes = ['image/jpeg', 'image/png', 'image/gif']) {
    const maxSize = maxSizeMB * 1024 * 1024; // Convert to bytes
    
    if (file.size > maxSize) {
        return {
            valid: false,
            message: `File size must be less than ${maxSizeMB}MB`
        };
    }
    
    if (!allowedTypes.includes(file.type)) {
        return {
            valid: false,
            message: 'Invalid file type. Please upload an image file.'
        };
    }
    
    return { valid: true };
}

// Function to preview image files
function previewImage(input, previewElement) {
    if (input.files && input.files[0]) {
        const file = input.files[0];
        const validation = validateFile(file);
        
        if (!validation.valid) {
            showToast(validation.message, 'danger');
            input.value = '';
            return;
        }
        
        const reader = new FileReader();
        reader.onload = function(e) {
            previewElement.src = e.target.result;
            previewElement.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }
}

// Function to animate numbers (counter effect)
function animateNumber(element, start, end, duration = 1000) {
    const startTimestamp = performance.now();
    const step = (timestamp) => {
        const elapsed = timestamp - startTimestamp;
        const progress = Math.min(elapsed / duration, 1);
        const current = Math.floor(progress * (end - start) + start);
        element.textContent = current;
        
        if (progress < 1) {
            requestAnimationFrame(step);
        }
    };
    requestAnimationFrame(step);
}

// Function to debounce input events
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Global error handler
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    showToast('An unexpected error occurred. Please try again.', 'danger');
});

// Global unhandled promise rejection handler
window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
    showToast('An unexpected error occurred. Please try again.', 'danger');
});
