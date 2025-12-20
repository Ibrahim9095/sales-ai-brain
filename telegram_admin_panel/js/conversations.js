// js/dashboard.js

class TelegramDashboard {
    constructor() {
        this.apiBase = 'http://localhost:8000/api';
        this.wsBase = 'ws://localhost:8000/ws';
        
        // State
        this.currentChat = null;
        this.activeChats = [];
        this.currentChatIndex = 0;
        this.autoSwitchTime = 30; // saniyə
        this.autoSwitchTimer = this.autoSwitchTime;
        this.websocket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        
        // Template messages
        this.templates = {
            uzr: "Üzr istəyirik narazılığınıza görə. Problem dərhal araşdırılır və həll ediləcək.",
            endirim: "Xüsusi təklif: Bu mesajla birlikdə 15% endirim qazanırsınız!",
            operator: "Operator sizinlə əlaqə saxlayacaq. Zəhmət olmasa gözləyin.",
            teklif: "Sizin üçün xüsusi təklifimiz var. Ətraflı məlumat üçün mesaj yazın."
        };
        
        // Initialize
        this.init();
    }
    
    async init() {
        console.log('[DASHBOARD] Telegram Dashboard başladı...');
        
        // Real-time saat
        this.updateTime();
        setInterval(() => this.updateTime(), 1000);
        
        // Auto switch timer
        this.startAutoSwitchTimer();
        
        // Event listeners
        this.setupEventListeners();
        
        // WebSocket connection
        this.connectWebSocket();
        
        // Load initial data
        await this.loadActiveChats();
        
        // Auto refresh every 3 seconds
        setInterval(() => this.loadActiveChats(), 3000);
    }
    
    // ===== REAL-TIME FUNCTIONS =====
    updateTime() {
        const now = new Date();
        const timeStr = now.toLocaleTimeString('az-AZ', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        
        document.getElementById('time-display').textContent = timeStr;
        document.getElementById('last-update-time').textContent = timeStr;
    }
    
    startAutoSwitchTimer() {
        setInterval(() => {
            this.autoSwitchTimer--;
            document.getElementById('auto-switch-timer').textContent = this.autoSwitchTimer;
            
            if (this.autoSwitchTimer <= 0) {
                this.autoSwitchTimer = this.autoSwitchTime;
                this.switchToNextChat();
            }
        }, 1000);
    }
    
    resetAutoSwitchTimer() {
        this.autoSwitchTimer = this.autoSwitchTime;
        document.getElementById('auto-switch-timer').textContent = this.autoSwitchTimer;
    }
    
    // ===== WEBSOCKET CONNECTION =====
    connectWebSocket() {
        try {
            this.websocket = new WebSocket(this.wsBase);
            
            this.websocket.onopen = () => {
                console.log('[WEBSOCKET] Canlı bağlantı quruldu');
                this.reconnectAttempts = 0;
                this.updateConnectionStatus(true);
                
                if (this.currentChat) {
                    this.subscribeToChat(this.currentChat);
                }
            };
            
            this.websocket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                } catch (error) {
                    console.error('WebSocket parse xətası:', error);
                }
            };
            
            this.websocket.onerror = (error) => {
                console.error('[WEBSOCKET] Xəta:', error);
                this.updateConnectionStatus(false);
            };
            
            this.websocket.onclose = () => {
                console.log('[WEBSOCKET] Bağlantı kəsildi');
                this.updateConnectionStatus(false);
                this.attemptReconnect();
            };
            
        } catch (error) {
            console.error('WebSocket bağlantı xətası:', error);
            this.attemptReconnect();
        }
    }
    
    updateConnectionStatus(connected) {
        const statusDot = document.getElementById('status-dot');
        const statusText = document.getElementById('connection-text');
        
        if (connected) {
            statusDot.classList.add('connected');
            statusText.textContent = 'CANLI BAĞLANTI';
            statusText.style.color = '#4dff91';
        } else {
            statusDot.classList.remove('connected');
            statusText.textContent = 'BAĞLANTI KƏSİLDİ';
            statusText.style.color = '#ff416c';
        }
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = Math.min(1000 * this.reconnectAttempts, 10000);
            
            console.log(`[RECONNECT] ${delay/1000}s sonra yenidən bağlanır...`);
            
            setTimeout(() => {
                this.connectWebSocket();
            }, delay);
        }
    }
    
    subscribeToChat(userId) {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify({
                type: 'subscribe',
                user_id: userId
            }));
        }
    }
    
    unsubscribeFromChat() {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify({
                type: 'unsubscribe'
            }));
        }
    }
    
    handleWebSocketMessage(data) {
        console.log('[WEBSOCKET]', data.type);
        
        switch (data.type) {
            case 'new_message':
                this.handleNewMessage(data.data);
                break;
            case 'high_risk_alert':
                this.handleHighRiskAlert(data.data);
                break;
            case 'bot_status_changed':
                this.handleBotStatusChanged(data.data);
                break;
            case 'activity_update':
                this.loadActiveChats();
                break;
        }
    }
    
    // ===== MESSAGE HANDLERS =====
    handleNewMessage(messageData) {
        console.log('[NEW MESSAGE]', messageData.username, ':', messageData.message.substring(0, 50));
        
        if (this.currentChat === messageData.user_id) {
            this.addMessageToChat(messageData);
        }
        
        if (messageData.risk_score > 60) {
            this.showAlert('warning',
                `⚠️ ${messageData.username} - ${messageData.risk_score}% risk`,
                messageData.message);
        }
        
        this.updateChatInList(messageData);
    }
    
    handleHighRiskAlert(alertData) {
        console.log('[HIGH RISK ALERT]', alertData.username, '-', alertData.risk_score + '%');
        
        this.showAlert('danger',
            `🚨 YÜKSƏK RİSK: ${alertData.username}`,
            `${alertData.risk_score}% risk: ${alertData.message}`);
        
        this.playAlertSound();
    }
    
    handleBotStatusChanged(data) {
        console.log('[BOT STATUS]', data.user_id, '->', data.status);
        this.loadActiveChats();
    }
    
    // ===== CHAT MANAGEMENT =====
    async loadActiveChats() {
        try {
            const response = await fetch(`${this.apiBase}/chats/active`);
            const data = await response.json();
            
            if (data.success && data.chats) {
                this.activeChats = data.chats;
                this.displayChatsList();
                this.updateStats();
                
                if (!this.currentChat && this.activeChats.length > 0) {
                    this.openChat(this.activeChats[0].user_id);
                    this.currentChatIndex = 0;
                }
            }
        } catch (error) {
            console.error('Chats yüklənmə xətası:', error);
            this.showAlert('warning', 'Bağlantı xətası', 'Serverə bağlanıla bilmir');
        }
    }
    
    displayChatsList() {
        const container = document.getElementById('chats-list');
        const activeChatsCount = document.getElementById('active-chats-count');
        
        activeChatsCount.textContent = this.activeChats.length;
        
        if (this.activeChats.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-comment-slash"></i>
                    <p>Aktiv söhbət yoxdur</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.activeChats.map((chat, index) => {
            const isActive = this.currentChat === chat.user_id;
            const riskClass = this.getRiskClass(chat.risk_score);
            const initials = this.getInitials(chat.username);
            
            return `
                <div class="chat-item ${riskClass} ${isActive ? 'active' : ''}" 
                     data-index="${index}"
                     data-user-id="${chat.user_id}">
                    <div class="chat-avatar-small">
                        ${initials}
                    </div>
                    <div class="chat-details">
                        <div class="chat-name">${chat.username}</div>
                        <div class="chat-preview">${this.truncate(chat.last_message, 35)}</div>
                        <div class="chat-meta">
                            <span>${chat.risk_score}% risk</span>
                            <span>${this.getTimeAgo(chat.last_time)}</span>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        // Add click events
        document.querySelectorAll('.chat-item').forEach(item => {
            item.addEventListener('click', () => {
                const index = parseInt(item.getAttribute('data-index'));
                const userId = item.getAttribute('data-user-id');
                this.currentChatIndex = index;
                this.openChat(userId);
                this.resetAutoSwitchTimer();
            });
        });
    }
    
    async openChat(userId) {
        if (this.currentChat) {
            this.unsubscribeFromChat();
        }
        
        this.currentChat = userId;
        
        // Update active state
        document.querySelectorAll('.chat-item.active').forEach(item => {
            item.classList.remove('active');
        });
        
        const activeItem = document.querySelector(`[data-user-id="${userId}"]`);
        if (activeItem) {
            activeItem.classList.add('active');
        }
        
        this.subscribeToChat(userId);
        await this.loadChatDetails(userId);
    }
    
    async loadChatDetails(userId) {
        try {
            const response = await fetch(`${this.apiBase}/chats/${userId}/full`);
            const data = await response.json();
            
            if (data.success) {
                this.displayChatDetails(data);
            }
        } catch (error) {
            console.error('Chat detalları xətası:', error);
        }
    }
    
    displayChatDetails(chatData) {
        const riskClass = this.getRiskClass(chatData.stats.max_risk);
        const initials = this.getInitials(chatData.username);
        
        // Update current chat display
        document.getElementById('current-username').textContent = chatData.username;
        document.getElementById('current-chat-meta').textContent = 
            `Risk: ${chatData.stats.max_risk}% • Mesaj: ${chatData.stats.total} • Son: ${chatData.stats.last_activity}`;
        
        // Update main chat header
        document.getElementById('main-username').textContent = chatData.username;
        document.getElementById('main-risk').textContent = chatData.stats.max_risk + '%';
        document.getElementById('main-messages').textContent = chatData.stats.total;
        document.getElementById('main-time').textContent = chatData.stats.last_activity;
        
        // Update avatar
        document.getElementById('main-avatar').innerHTML = initials;
        document.getElementById('main-avatar').style.background = 
            riskClass === 'danger' ? 'linear-gradient(45deg, #ff416c, #ff4b2b)' :
            riskClass === 'warning' ? 'linear-gradient(45deg, #ffa62e, #ffd166)' :
            'linear-gradient(45deg, #00adb5, #4dff91)';
        
        // Display messages
        this.displayMessages(chatData.messages);
    }
    
    displayMessages(messages) {
        const container = document.getElementById('chat-messages');
        
        if (messages.length === 0) {
            container.innerHTML = `
                <div class="welcome-screen">
                    <div class="welcome-icon">
                        <i class="fas fa-comments"></i>
                    </div>
                    <h3>MESAJ YOXDUR</h3>
                    <p>Bu müştəri ilə hələ söhbət başlamayıb</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = messages.map(msg => {
            const senderClass = msg.is_admin ? 'admin' : msg.is_bot ? 'bot' : 'user';
            const riskClass = this.getRiskClass(msg.risk_score);
            const showRisk = msg.risk_score > 50 && !msg.is_admin && !msg.is_bot;
            
            return `
                <div class="message ${senderClass}">
                    <div class="message-bubble">
                        <div class="message-sender">${msg.sender}</div>
                        <div class="message-text">${msg.text}</div>
                        ${showRisk ? `
                            <div class="risk-indicator ${riskClass}">
                                ${msg.risk_score}% risk
                            </div>
                        ` : ''}
                        <span class="message-time">${this.formatTime(msg.time)}</span>
                    </div>
                </div>
            `;
        }).join('');
        
        // Scroll to bottom
        setTimeout(() => {
            container.scrollTop = container.scrollHeight;
        }, 100);
    }
    
    addMessageToChat(messageData) {
        const container = document.getElementById('chat-messages');
        
        if (container.querySelector('.welcome-screen')) {
            container.innerHTML = '';
        }
        
        const senderClass = messageData.is_admin ? 'admin' : messageData.is_bot ? 'bot' : 'user';
        const riskClass = this.getRiskClass(messageData.risk_score);
        const showRisk = messageData.risk_score > 50 && !messageData.is_admin && !messageData.is_bot;
        
        const messageHTML = `
            <div class="message ${senderClass}">
                <div class="message-bubble">
                    <div class="message-sender">${messageData.username}</div>
                    <div class="message-text">${messageData.message}</div>
                    ${showRisk ? `
                        <div class="risk-indicator ${riskClass}">
                            ${messageData.risk_score}% risk
                        </div>
                    ` : ''}
                    <span class="message-time">${this.formatTime(messageData.timestamp)}</span>
                </div>
            </div>
        `;
        
        container.innerHTML += messageHTML;
        
        setTimeout(() => {
            container.scrollTop = container.scrollHeight;
        }, 100);
    }
    
    updateChatInList(messageData) {
        const chatItem = document.querySelector(`[data-user-id="${messageData.user_id}"]`);
        if (chatItem) {
            const preview = chatItem.querySelector('.chat-preview');
            if (preview) {
                preview.textContent = this.truncate(messageData.message, 35);
            }
            
            const time = chatItem.querySelector('.chat-meta span:last-child');
            if (time) {
                time.textContent = this.getTimeAgo(messageData.timestamp);
            }
            
            // Update risk class
            const riskClass = this.getRiskClass(messageData.risk_score);
            chatItem.classList.remove('danger', 'warning', 'success');
            chatItem.classList.add(riskClass);
            
            // Update avatar color
            const avatar = chatItem.querySelector('.chat-avatar-small');
            if (avatar) {
                avatar.style.background = 
                    riskClass === 'danger' ? 'linear-gradient(45deg, #ff416c, #ff4b2b)' :
                    riskClass === 'warning' ? 'linear-gradient(45deg, #ffa62e, #ffd166)' :
                    'linear-gradient(45deg, #00adb5, #4dff91)';
            }
        }
    }
    
    // ===== ACTIONS =====
    async startIntervention() {
        if (!this.currentChat) {
            this.showAlert('warning', 'Xəbərdarlıq', 'Əvvəlcə söhbət seçin');
            return;
        }
        
        if (!confirm('🚨 MÜDAXİLƏ BAŞLATSIN?\nBot dayandırılacaq və müştəriyə operator bağlanacaq.')) {
            return;
        }
        
        try {
            // Stop bot
            await fetch(`${this.apiBase}/bot/stop`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ user_id: this.currentChat })
            });
            
            // Send operator message
            await fetch(`${this.apiBase}/admin/send-message`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    user_id: this.currentChat,
                    message: '👨‍💼 Operator sizinlə əlaqə saxlayır... Lütfən gözləyin.',
                    admin_name: 'Operator'
                })
            });
            
            this.showAlert('success', 'Müdaxilə başladıldı', 'Müştəriyə operator bağlanır...');
            await this.loadActiveChats();
        } catch (error) {
            console.error('Müdaxilə xətası:', error);
            this.showAlert('danger', 'Xəta', 'Müdaxilə başladıla bilmir');
        }
    }
    
    async sendAutoResponse() {
        if (!this.currentChat) {
            this.showAlert('warning', 'Xəbərdarlıq', 'Əvvəlcə söhbət seçin');
            return;
        }
        
        const responses = [
            "Hörmətli müştəri, sorğunuz qeydə alındı. Tezliklə cavab verəcəyik.",
            "Kömək üçün təşəkkür edirik. Məsələniz həll edilir.",
            "Sizin üçün xüsusi təklif hazırladıq. Gözləyin...",
            "Başa düşürük narazılığınızı. Dərhal həll edirik."
        ];
        
        const randomResponse = responses[Math.floor(Math.random() * responses.length)];
        
        try {
            await fetch(`${this.apiBase}/admin/send-message`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    user_id: this.currentChat,
                    message: randomResponse,
                    admin_name: 'Dəstək'
                })
            });
            
            this.showAlert('success', 'Cavab göndərildi', 'Avtomatik cavab müştəriyə göndərildi');
        } catch (error) {
            console.error('Cavab göndərmə xətası:', error);
            this.showAlert('danger', 'Xəta', 'Mesaj göndərilə bilmir');
        }
    }
    
    async sendTemplate(templateKey) {
        if (!this.currentChat) {
            this.showAlert('warning', 'Xəbərdarlıq', 'Əvvəlcə söhbət seçin');
            return;
        }
        
        const message = this.templates[templateKey];
        if (!message) return;
        
        try {
            await fetch(`${this.apiBase}/admin/send-message`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    user_id: this.currentChat,
                    message: message,
                    admin_name: 'Operator'
                })
            });
            
            this.showAlert('success', 'Mesaj göndərildi', 'Şablon mesajı müştəriyə göndərildi');
        } catch (error) {
            console.error('Template göndərmə xətası:', error);
            this.showAlert('danger', 'Xəta', 'Mesaj göndərilə bilmir');
        }
    }
    
    // ===== NAVIGATION =====
    switchToNextChat() {
        if (this.activeChats.length === 0) return;
        
        this.currentChatIndex = (this.currentChatIndex + 1) % this.activeChats.length;
        const nextChat = this.activeChats[this.currentChatIndex];
        
        this.openChat(nextChat.user_id);
        this.resetAutoSwitchTimer();
    }
    
    switchToPrevChat() {
        if (this.activeChats.length === 0) return;
        
        this.currentChatIndex = (this.currentChatIndex - 1 + this.activeChats.length) % this.activeChats.length;
        const prevChat = this.activeChats[this.currentChatIndex];
        
        this.openChat(prevChat.user_id);
        this.resetAutoSwitchTimer();
    }
    
    // ===== STATS =====
    updateStats() {
        const totalActive = this.activeChats.length;
        const dangerChats = this.activeChats.filter(c => c.risk_score > 80).length;
        const warningChats = this.activeChats.filter(c => c.risk_score > 60 && c.risk_score <= 80).length;
        const botActive = this.activeChats.filter(c => !c.bot_stopped).length;
        
        document.getElementById('stat-active').textContent = totalActive;
        document.getElementById('stat-danger').textContent = dangerChats;
        document.getElementById('stat-warning').textContent = warningChats;
        document.getElementById('stat-bot').textContent = botActive;
    }
    
    // ===== UTILITIES =====
    getRiskClass(score) {
        if (score > 80) return 'danger';
        if (score > 60) return 'warning';
        return 'success';
    }
    
    getTimeAgo(timestamp) {
        if (!timestamp) return 'bilinmir';
        
        const now = new Date();
        const past = new Date(timestamp);
        const diff = now - past;
        const minutes = Math.floor(diff / 60000);
        
        if (minutes < 1) return 'indi';
        if (minutes < 60) return `${minutes} dəq`;
        if (minutes < 1440) return `${Math.floor(minutes / 60)} saat`;
        return `${Math.floor(minutes / 1440)} gün`;
    }
    
    formatTime(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleTimeString('az-AZ', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    
    truncate(text, length) {
        if (!text) return 'Mesaj yoxdur';
        if (text.length <= length) return text;
        return text.substring(0, length) + '...';
    }
    
    getInitials(username) {
        return username.charAt(0).toUpperCase();
    }
    
    showAlert(type, title, message) {
        const container = document.getElementById('alert-container');
        
        const alert = document.createElement('div');
        alert.className = `alert ${type}`;
        alert.innerHTML = `
            <div class="alert-header">
                <i class="fas fa-${type === 'danger' ? 'fire' : 
                                 type === 'warning' ? 'exclamation-triangle' : 
                                 type === 'success' ? 'check-circle' : 'info-circle'}"></i>
                <span>${title}</span>
            </div>
            <div class="alert-message">${message}</div>
        `;
        
        container.appendChild(alert);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateX(100%)';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    }
    
    playAlertSound() {
        try {
            const audio = new Audio('/static/sounds/alert.mp3');
            audio.volume = 0.3;
            audio.play().catch(e => console.log('Səs çalına bilmir'));
        } catch (error) {
            console.log('Səs faylı tapılmadı');
        }
    }
    
    // ===== EVENT LISTENERS =====
    setupEventListeners() {
        // Navigation buttons
        document.getElementById('prev-chat-btn').addEventListener('click', () => {
            this.switchToPrevChat();
        });
        
        document.getElementById('next-chat-btn').addEventListener('click', () => {
            this.switchToNextChat();
        });
        
        // Fullscreen button
        document.getElementById('fullscreen-btn').addEventListener('click', () => {
            const container = document.getElementById('live-chat-container');
            
            if (!document.fullscreenElement) {
                if (container.requestFullscreen) {
                    container.requestFullscreen();
                }
            } else {
                if (document.exitFullscreen) {
                    document.exitFullscreen();
                }
            }
        });
        
        // Action buttons
        document.getElementById('intervention-btn').addEventListener('click', () => {
            this.startIntervention();
        });
        
        document.getElementById('auto-response-btn').addEventListener('click', () => {
            this.sendAutoResponse();
        });
        
        document.getElementById('emergency-btn').addEventListener('click', () => {
            if (this.currentChat) {
                this.startIntervention();
            } else {
                this.showAlert('warning', 'Xəbərdarlıq', 'Əvvəlcə söhbət seçin');
            }
        });
        
        document.getElementById('offer-btn').addEventListener('click', () => {
            this.sendTemplate('teklif');
        });
        
        document.getElementById('resolve-btn').addEventListener('click', () => {
            if (this.currentChat) {
                if (confirm('Bu söhbəti HƏLL EDİLDİ kimi qeyd etmək istəyirsiniz?')) {
                    this.showAlert('success', 'Uğurlu', 'Söhbət həll edildi kimi qeyd edildi');
                }
            } else {
                this.showAlert('warning', 'Xəbərdarlıq', 'Əvvəlcə söhbət seçin');
            }
        });
        
        // Template buttons
        document.querySelectorAll('.template-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const template = e.currentTarget.getAttribute('data-template');
                this.sendTemplate(template);
            });
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && document.fullscreenElement) {
                document.exitFullscreen();
            }
            if (e.key === 'ArrowLeft') {
                this.switchToPrevChat();
            }
            if (e.key === 'ArrowRight') {
                this.switchToNextChat();
            }
            if (e.key === ' ' && this.currentChat) {
                e.preventDefault();
                this.sendAutoResponse();
            }
        });
    }
}

// App-i başlat
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new TelegramDashboard();
});