// Configuração CSRF para requisições AJAX
function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta) {
        return meta.content;
    }
    
    // Fallback: tentar pegar do cookie
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrf_token') {
            return decodeURIComponent(value);
        }
    }
    
    return null;
}

// Configurar fetch para incluir CSRF token
const originalFetch = window.fetch;
window.fetch = function(url, options = {}) {
    // Só adicionar CSRF para métodos que não sejam GET
    if (options.method && options.method.toUpperCase() !== 'GET') {
        const token = getCsrfToken();
        
        if (token) {
            options.headers = {
                ...options.headers,
                'X-CSRFToken': token
            };
        }
        
        // Para requisições JSON, garantir que o Content-Type está correto
        if (options.body && typeof options.body === 'string') {
            options.headers = {
                ...options.headers,
                'Content-Type': 'application/json'
            };
        }
    }
    
    return originalFetch.call(this, url, options);
};

// Toggle Sidebar
document.addEventListener('DOMContentLoaded', function() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            
            // Salvar preferência
            localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
        });
        
        // Restaurar preferência
        if (localStorage.getItem('sidebarCollapsed') === 'true') {
            sidebar.classList.add('collapsed');
        }
    }
    
    // Mobile menu
    if (window.innerWidth <= 768) {
        sidebar?.classList.add('collapsed');
        
        // Adicionar overlay para mobile
        const overlay = document.createElement('div');
        overlay.className = 'sidebar-overlay';
        document.body.appendChild(overlay);
        
        overlay.addEventListener('click', function() {
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
        });
        
        sidebarToggle?.addEventListener('click', function(e) {
            e.preventDefault();
            sidebar.classList.toggle('active');
            overlay.classList.toggle('active');
        });
    }
});

// Funções utilitárias
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
}

function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

// Validações aprimoradas
function validateCPF(cpf) {
    // Remove caracteres não numéricos
    cpf = cpf.replace(/[^\d]+/g, '');
    
    if (cpf.length !== 11 || /^(\d)\1{10}$/.test(cpf)) {
        return false;
    }
    
    let sum = 0;
    let remainder;
    
    for (let i = 1; i <= 9; i++) {
        sum += parseInt(cpf.substring(i - 1, i)) * (11 - i);
    }
    
    remainder = (sum * 10) % 11;
    if (remainder === 10 || remainder === 11) remainder = 0;
    if (remainder !== parseInt(cpf.substring(9, 10))) return false;
    
    sum = 0;
    for (let i = 1; i <= 10; i++) {
        sum += parseInt(cpf.substring(i - 1, i)) * (12 - i);
    }
    
    remainder = (sum * 10) % 11;
    if (remainder === 10 || remainder === 11) remainder = 0;
    if (remainder !== parseInt(cpf.substring(10, 11))) return false;
    
    return true;
}

function validatePhone(phone) {
    // Remove caracteres não numéricos
    const numbers = phone.replace(/\D/g, '');
    // Aceita 10 ou 11 dígitos (com ou sem o 9 no celular)
    return numbers.length === 10 || numbers.length === 11;
}

// Função para aplicar máscara de CPF
function maskCPF(input) {
    let value = input.value.replace(/\D/g, '');
    
    if (value.length <= 11) {
        value = value.replace(/(\d{3})(\d)/, '$1.$2');
        value = value.replace(/(\d{3})(\d)/, '$1.$2');
        value = value.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
    }
    
    input.value = value;
}

// Função para aplicar máscara de telefone
function maskPhone(input) {
    let value = input.value.replace(/\D/g, '');
    
    if (value.length <= 11) {
        if (value.length <= 10) {
            value = value.replace(/(\d{2})(\d)/, '($1) $2');
            value = value.replace(/(\d{4})(\d)/, '$1-$2');
        } else {
            value = value.replace(/(\d{2})(\d)/, '($1) $2');
            value = value.replace(/(\d{5})(\d)/, '$1-$2');
        }
    }
    
    input.value = value;
}

// Animações suaves ao carregar elementos
function animateOnScroll() {
    const elements = document.querySelectorAll('.animate-on-scroll');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
            }
        });
    }, { threshold: 0.1 });
    
    elements.forEach(element => {
        observer.observe(element);
    });
}

// Inicializar animações
if ('IntersectionObserver' in window) {
    animateOnScroll();
}

// Função para criar notificações toast aprimorada
function showToast(message, type = 'info', duration = 5000) {
    // Remover toasts existentes do mesmo tipo
    const existingToasts = document.querySelectorAll(`.toast-${type}`);
    existingToasts.forEach(toast => toast.remove());
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const icon = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    }[type] || 'info-circle';
    
    toast.innerHTML = `
        <i class="fas fa-${icon}"></i>
        <span>${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    document.body.appendChild(toast);
    
    // Animar entrada
    setTimeout(() => toast.classList.add('show'), 100);
    
    // Remover automaticamente
    setTimeout(() => {
        if (toast.parentElement) {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }
    }, duration);
    
    return toast;
}

// Função para fazer requisições AJAX com melhor tratamento de erro
async function makeRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || `HTTP ${response.status}: ${response.statusText}`);
        }
        
        return { success: true, data };
    } catch (error) {
        console.error('Erro na requisição:', error);
        return { success: false, error: error.message };
    }
}

// Adicionar estilos para toast aprimorados
const style = document.createElement('style');
style.textContent = `
    .toast {
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        padding: 16px 20px;
        border-radius: 10px;
        box-shadow: 0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23);
        display: flex;
        align-items: center;
        gap: 12px;
        transform: translateX(400px);
        transition: transform 0.3s ease;
        z-index: 3000;
        max-width: 400px;
        margin-bottom: 10px;
    }
    
    .toast.show {
        transform: translateX(0);
    }
    
    .toast-success {
        border-left: 4px solid #4caf50;
    }
    
    .toast-error {
        border-left: 4px solid #f44336;
    }
    
    .toast-warning {
        border-left: 4px solid #ff9800;
    }
    
    .toast-info {
        border-left: 4px solid #2196f3;
    }
    
    .toast i:first-child {
        font-size: 20px;
        flex-shrink: 0;
    }
    
    .toast-success i:first-child {
        color: #4caf50;
    }
    
    .toast-error i:first-child {
        color: #f44336;
    }
    
    .toast-warning i:first-child {
        color: #ff9800;
    }
    
    .toast-info i:first-child {
        color: #2196f3;
    }
    
    .toast span {
        flex: 1;
        word-break: break-word;
    }
    
    .toast-close {
        background: transparent;
        border: none;
        font-size: 14px;
        color: #666;
        cursor: pointer;
        padding: 4px;
        flex-shrink: 0;
    }
    
    .toast-close:hover {
        color: #333;
    }
    
    .sidebar-overlay {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        z-index: 999;
    }
    
    .sidebar-overlay.active {
        display: block;
    }
    
    @media (max-width: 768px) {
        .toast {
            right: 10px;
            left: 10px;
            max-width: none;
        }
    }
`;
document.head.appendChild(style);