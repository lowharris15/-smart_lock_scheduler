/* Common functions for the Smart Lock Scheduler application */

// Helper function to format dates consistently across the application
function formatDate(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        weekday: 'long',
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Helper function to show notifications to the user
function showNotification(message, type = 'info') {
    // Create the notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show notification-toast`;
    notification.role = 'alert';
    
    // Add the message and dismiss button
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Add to the notification container or create one if it doesn't exist
    let container = document.getElementById('notification-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        container.className = 'position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1050';
        document.body.appendChild(container);
    }
    
    // Add the notification to the container
    container.appendChild(notification);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 5000);
}

// Helper function for making API requests
async function apiRequest(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(endpoint, options);
        
        // Handle non-OK responses
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.description || 'An error occurred with the API request');
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Request Error:', error);
        showNotification(error.message, 'danger');
        throw error;
    }
}

// Copy text to clipboard function
function copyToClipboard(text) {
    // Create a temporary input element
    const input = document.createElement('input');
    input.style.position = 'fixed';
    input.style.opacity = 0;
    input.value = text;
    document.body.appendChild(input);
    
    // Select and copy the text
    input.select();
    input.setSelectionRange(0, 99999);
    document.execCommand('copy');
    
    // Remove the temporary element
    document.body.removeChild(input);
    
    // Show a notification
    showNotification('Copied to clipboard!', 'success');
}

// Add event handlers when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add copy button functionality for access codes
    document.body.addEventListener('click', function(event) {
        // Check if the clicked element has the copy-code class
        if (event.target.classList.contains('copy-code-btn')) {
            const code = event.target.getAttribute('data-code');
            if (code) {
                copyToClipboard(code);
            }
        }
    });
    
    // Check for session storage messages (e.g., redirects with messages)
    const sessionMessage = sessionStorage.getItem('notification');
    const sessionMessageType = sessionStorage.getItem('notificationType');
    
    if (sessionMessage) {
        showNotification(sessionMessage, sessionMessageType || 'info');
        sessionStorage.removeItem('notification');
        sessionStorage.removeItem('notificationType');
    }
}); 