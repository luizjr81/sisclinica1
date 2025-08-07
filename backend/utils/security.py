from functools import wraps
from flask import request, jsonify
from flask_login import current_user
import re

def validate_cpf(cpf):
    """Valida CPF brasileiro"""
    # Remove caracteres não numéricos
    cpf = re.sub(r'[^0-9]', '', cpf)
    
    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        return False
    
    # Calcula o primeiro dígito verificador
    sum_1 = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digit_1 = (sum_1 * 10 % 11) % 10
    
    # Calcula o segundo dígito verificador
    sum_2 = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digit_2 = (sum_2 * 10 % 11) % 10
    
    # Verifica se os dígitos verificadores estão corretos
    return cpf[-2:] == f'{digit_1}{digit_2}'

def validate_phone(phone):
    """Valida telefone brasileiro"""
    # Pattern para (XX) XXXXX-XXXX ou (XX) XXXX-XXXX
    pattern = r'^\(\d{2}\) \d{4,5}-\d{4}$'
    return bool(re.match(pattern, phone))

def sanitize_input(text):
    """Sanitiza entrada de texto para prevenir XSS"""
    if not text:
        return text
    
    # Remove tags HTML
    text = re.sub(r'<[^>]+>', '', text)
    
    # Escapa caracteres especiais
    replacements = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;',
        '/': '&#x2F;'
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text

def require_login(f):
    """Decorator para rotas que requerem autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Autenticação necessária'}), 401
        return f(*args, **kwargs)
    return decorated_function

def validate_password(password):
    """Valida força da senha"""
    if len(password) < 8:
        return False, "A senha deve ter pelo menos 8 caracteres"
    
    if not re.search(r'[A-Z]', password):
        return False, "A senha deve conter pelo menos uma letra maiúscula"
    
    if not re.search(r'[a-z]', password):
        return False, "A senha deve conter pelo menos uma letra minúscula"
    
    if not re.search(r'[0-9]', password):
        return False, "A senha deve conter pelo menos um número"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "A senha deve conter pelo menos um caractere especial"
    
    return True, "Senha válida"

def rate_limit(max_requests=60, window=60):
    """Decorator para limitar taxa de requisições"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Implementação básica - em produção, use Redis ou similar
            # Por enquanto, apenas retorna a função
            return f(*args, **kwargs)
        return decorated_function
    return decorator