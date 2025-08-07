// Configuração CSRF para requisições AJAX
function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.content : '';
}

// Configurar AJAX com CSRF
if (typeof fetch !== 'undefined') {
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        if (args[1] && args[1].method && args[1].method.toUpperCase() !== 'GET') {
            args[1].headers = {
                ...args[1].headers,
                'X-CSRFToken': getCsrfToken()
            };
        }
        return originalFetch.apply(this, args);
    };
}

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

// Validações
function validateCPF(cpf) {
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
    const phoneRegex = /^\(\d{2}\) \d{4,5}-\d{4}$/;
    return phoneRegex.test(phone);
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

// Função para criar notificações toast
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(toast);
    
    // Animar entrada
    setTimeout(() => toast.classList.add('show'), 100);
    
    // Remover após 5 segundos
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

// Adicionar estilos para toast
const style = document.createElement('style');
style.textContent = `
    .toast {
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        padding: 16px 24px;
        border-radius: 10px;
        box-shadow: 0 3px 6px rgba(0,0,0,0.16);
        display: flex;
        align-items: center;
        gap: 12px;
        transform: translateX(400px);
        transition: transform 0.3s ease;
        z-index: 3000;
        max-width: 350px;
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
    
    .toast-info {
        border-left: 4px solid #2196f3;
    }
    
    .toast i {
        font-size: 20px;
    }
    
    .toast-success i {
        color: #4caf50;
    }
    
    .toast-error i {
        color: #f44336;
    }
    
    .toast-info i {
        color: #2196f3;
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