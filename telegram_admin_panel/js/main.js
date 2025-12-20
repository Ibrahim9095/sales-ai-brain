// brain/telegram_admin_panel/js/main.js

// Ümumi utility funksiyalar
class AppUtilities {
    static formatNumber(num) {
        return new Intl.NumberFormat('az-AZ').format(num);
    }
    
    static formatDate(date) {
        return new Date(date).toLocaleDateString('az-AZ', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    
    static showLoading(element) {
        element.classList.add('loading');
        element.disabled = true;
    }
    
    static hideLoading(element) {
        element.classList.remove('loading');
        element.disabled = false;
    }
    
    static debounce(func, wait) {
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
}

// Notification sistemi
class NotificationSystem {
    static show(type, message, duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `app-notification ${type}`;
        notification.innerHTML = `
            <div class="notification-icon">
                <i class="fas fa-${this.getIcon(type)}"></i>
            </div>
            <div class="notification-content">
                <div class="notification-title">${this.getTitle(type)}</div>
                <div class="notification-message">${message}</div>
            </div>
            <button class="notification-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        document.body.appendChild(notification);
        
        // Animasiya
        setTimeout(() => notification.classList.add('show'), 10);
        
        // Auto close
        if (duration > 0) {
            setTimeout(() => {
                notification.classList.remove('show');
                setTimeout(() => notification.remove(), 300);
            }, duration);
        }
    }
    
    static getIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'times-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
    
    static getTitle(type) {
        const titles = {
            success: 'Uğurlu',
            error: 'Xəta',
            warning: 'Xəbərdarlıq',
            info: 'Məlumat'
        };
        return titles[type] || 'Bildiriş';
    }
}

// API client
class APIClient {
    constructor(baseURL = 'http://localhost:8000/api') {
        this.baseURL = baseURL;
    }
    
    async get(endpoint) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`);
            return await response.json();
        } catch (error) {
            console.error(`GET ${endpoint} error:`, error);
            throw error;
        }
    }
    
    async post(endpoint, data) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            return await response.json();
        } catch (error) {
            console.error(`POST ${endpoint} error:`, error);
            throw error;
        }
    }
}

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Premium AI Dashboard yükləndi');
    
    // Make utilities global
    window.AppUtils = AppUtilities;
    window.Notify = NotificationSystem;
    window.API = new APIClient();
    
    // Auto refresh buttons
    document.querySelectorAll('.btn-refresh').forEach(btn => {
        btn.addEventListener('click', function() {
            this.classList.add('rotating');
            setTimeout(() => this.classList.remove('rotating'), 1000);
        });
    });
    
    // Initialize page specific modules
    const currentPage = window.location.pathname.split('/').pop();
    
    switch(currentPage) {
        case 'dashboard.html':
            // Dashboard özəlləşdirmələri
            break;
        case 'conversations.html':
            // Conversations özəlləşdirmələri
            break;
        case 'analytics.html':
            // Analytics özəlləşdirmələri
            break;
    }
});