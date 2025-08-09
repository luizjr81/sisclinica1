from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TextAreaField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email
from models import db, Professional, User, Servico
from datetime import datetime
import re

professionals_bp = Blueprint('professionals', __name__)

class ProfessionalForm(FlaskForm):
    full_name = StringField('Nome Completo', validators=[DataRequired(), Length(min=3, max=150)])
    cpf = StringField('CPF', validators=[DataRequired(), Length(min=11, max=14)])
    registro_prof = StringField('Registro Prof.', validators=[Length(max=20)])
    phone = StringField('Telefone', validators=[DataRequired(), Length(min=10, max=15)])
    email = StringField('Email', validators=[Email()])
    birth_date = DateField('Data de Nascimento')
    bio = TextAreaField('Biografia')
    is_active = BooleanField('Ativo')
    submit = SubmitField('Salvar')

def validate_cpf(cpf):
    """Valida CPF brasileiro"""
    cpf = re.sub(r'[^0-9]', '', cpf)
    
    if len(cpf) != 11:
        return False
    
    if cpf == cpf[0] * 11:
        return False
    
    # Calcula o primeiro dígito verificador
    sum_1 = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digit_1 = (sum_1 * 10 % 11) % 10
    
    # Calcula o segundo dígito verificador
    sum_2 = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digit_2 = (sum_2 * 10 % 11) % 10
    
    return cpf[-2:] == f'{digit_1}{digit_2}'

def format_cpf(cpf):
    """Formata CPF para o padrão 000.000.000-00"""
    cpf = re.sub(r'[^0-9]', '', cpf)
    if len(cpf) == 11:
        return f'{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}'
    return cpf

def format_phone(phone):
    """Formata telefone para o padrão (00) 00000-0000"""
    phone = re.sub(r'[^0-9]', '', phone)
    if len(phone) == 11:
        return f'({phone[:2]}) {phone[2:7]}-{phone[7:]}'
    elif len(phone) == 10:
        return f'({phone[:2]}) {phone[2:6]}-{phone[6:]}'
    return phone

# ===== ROTAS DE PROFISSIONAIS =====

# ===== ROTAS DE PROFISSIONAIS =====

@professionals_bp.route('/')
@login_required
def list_professionals():
    if not current_user.has_permission('all'):
        flash('Acesso negado.', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('professionals.html')

@professionals_bp.route('/api/list')
@login_required
def api_list_professionals():
    try:
        search = request.args.get('search', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        
        query = Professional.query
        
        if search:
            search_filter = f'%{search}%'
            query = query.filter(
                db.or_(
                    Professional.full_name.ilike(search_filter),
                    Professional.cpf.like(search_filter),
                    Professional.registro_prof.ilike(search_filter),
                    Professional.email.ilike(search_filter)
                )
            )
        
        pagination = query.order_by(Professional.full_name).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'professionals': [p.to_dict() for p in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page
        })
    except Exception as e:
        return jsonify({'error': f'Erro ao carregar profissionais: {str(e)}'}), 500

@professionals_bp.route('/api/create', methods=['POST'])
@login_required
def api_create_professional():
    if not current_user.has_permission('all'):
        return jsonify({'error': 'Acesso negado'}), 403
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados não recebidos'}), 400
        
        # Validações obrigatórias
        required_fields = ['full_name', 'cpf', 'phone']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        # Formatar e validar CPF
        cpf_formatted = format_cpf(data['cpf'])
        if not validate_cpf(cpf_formatted):
            return jsonify({'error': 'CPF inválido'}), 400
        
        # Verificar CPF único
        if Professional.query.filter_by(cpf=cpf_formatted).first():
            return jsonify({'error': 'CPF já cadastrado'}), 400
        
        # Verificar email único apenas se fornecido
        if data.get('email') and Professional.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email já cadastrado'}), 400
        
        # Verificar REGISTRO PROF único apenas se fornecido
        if data.get('registro_prof') and Professional.query.filter_by(registro_prof=data['registro_prof']).first():
            return jsonify({'error': 'Registro profissional já cadastrado'}), 400
        
        # Formatar telefone
        phone_formatted = format_phone(data['phone'])
        
        # Validar data de nascimento
        birth_date = None
        if data.get('birth_date'):
            try:
                birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Data de nascimento inválida'}), 400
        
        # Criar profissional
        professional = Professional(
            full_name=data['full_name'].strip(),
            cpf=cpf_formatted,
            registro_prof=data.get('registro_prof', '').strip().upper() if data.get('registro_prof') else None,
            phone=phone_formatted,
            email=data.get('email', '').strip().lower() if data.get('email') else None,
            birth_date=birth_date,
            bio=data.get('bio', '').strip(),
            is_active=data.get('is_active', True),
            created_by=current_user.id
        )
        
        # Associar serviços
        service_ids = data.get('service_ids', [])
        if service_ids:
            services = Servico.query.filter(Servico.id.in_(service_ids)).all()
            professional.services = services

        db.session.add(professional)
        db.session.commit()
        
        return jsonify({
            'message': 'Profissional cadastrado com sucesso',
            'professional': professional.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@professionals_bp.route('/api/<int:professional_id>', methods=['GET'])
@login_required
def api_get_professional(professional_id):
    try:
        professional = Professional.query.get_or_404(professional_id)
        return jsonify(professional.to_dict())
    except Exception as e:
        return jsonify({'error': f'Erro ao carregar profissional: {str(e)}'}), 500

@professionals_bp.route('/api/<int:professional_id>', methods=['PUT'])
@login_required
def api_update_professional(professional_id):
    if not current_user.has_permission('all'):
        return jsonify({'error': 'Acesso negado'}), 403
    
    try:
        professional = Professional.query.get_or_404(professional_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados não recebidos'}), 400
        
        # Validações obrigatórias
        required_fields = ['full_name', 'cpf', 'phone']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        cpf_formatted = format_cpf(data['cpf'])
        if not validate_cpf(cpf_formatted):
            return jsonify({'error': 'CPF inválido'}), 400
        
        # Verificar duplicatas apenas para campos obrigatórios
        cpf_existing = Professional.query.filter(
            Professional.cpf == cpf_formatted,
            Professional.id != professional_id
        ).first()
        if cpf_existing:
            return jsonify({'error': 'CPF já cadastrado para outro profissional'}), 400
        
        # Verificar email único apenas se fornecido
        if data.get('email'):
            email_exists = Professional.query.filter(
                Professional.email == data['email'],
                Professional.id != professional_id
            ).first()
            
            if email_exists:
                return jsonify({'error': 'Email já cadastrado para outro profissional'}), 400
        
        # Verificar REGISTRO PROF único apenas se fornecido
        if data.get('registro_prof'):
            registro_exists = Professional.query.filter(
                Professional.registro_prof == data['registro_prof'],
                Professional.id != professional_id
            ).first()
            
            if registro_exists:
                return jsonify({'error': 'Registro profissional já cadastrado para outro profissional'}), 400
        
        # Formatar telefone
        phone_formatted = format_phone(data['phone'])
        
        # Validar data de nascimento
        birth_date = None
        if data.get('birth_date'):
            try:
                birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Data de nascimento inválida'}), 400
        
        # Atualizar profissional
        professional.full_name = data['full_name'].strip()
        professional.cpf = cpf_formatted
        professional.registro_prof = data.get('registro_prof', '').strip().upper() if data.get('registro_prof') else None
        professional.phone = phone_formatted
        professional.email = data.get('email', '').strip().lower() if data.get('email') else None
        professional.birth_date = birth_date
        professional.bio = data.get('bio', '').strip()
        professional.is_active = data.get('is_active', True)
        professional.updated_at = datetime.utcnow()
        
        # Atualizar serviços
        service_ids = data.get('service_ids', [])
        services = Servico.query.filter(Servico.id.in_(service_ids)).all()
        professional.services = services

        db.session.commit()
        
        return jsonify({
            'message': 'Profissional atualizado com sucesso',
            'professional': professional.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao atualizar profissional: {str(e)}'}), 500

@professionals_bp.route('/api/<int:professional_id>', methods=['DELETE'])
@login_required
def api_delete_professional(professional_id):
    if not current_user.has_permission('all'):
        return jsonify({'error': 'Acesso negado'}), 403
    
    try:
        professional = Professional.query.get_or_404(professional_id)
        
        # Se houver conta de usuário vinculada, excluir também
        if professional.user_account:
            db.session.delete(professional.user_account)
        
        db.session.delete(professional)
        db.session.commit()
        
        return jsonify({'message': 'Profissional excluído com sucesso'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao excluir profissional: {str(e)}'}), 500

# ===== GESTÃO DE CONTAS DE USUÁRIO =====

@professionals_bp.route('/api/<int:professional_id>/create-account', methods=['POST'])
@login_required
def api_create_user_account(professional_id):
    if not current_user.has_permission('all'):
        return jsonify({'error': 'Acesso negado'}), 403
    
    try:
        professional = Professional.query.get_or_404(professional_id)
        
        # Verificar se já tem conta
        if professional.user_account:
            return jsonify({'error': 'Profissional já possui conta de usuário'}), 400
        
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username e senha são obrigatórios'}), 400
        
        # Verificar se username já existe
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username já existe'}), 400
        
        # Criar conta de usuário (usar email do profissional se disponível)
        user_email = professional.email if professional.email else f"{username}@clinica.com"
        
        user = User(
            username=username,
            email=user_email,
            full_name=professional.full_name,
            role='professional',
            professional_id=professional.id
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'Conta de usuário criada com sucesso',
            'username': username
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao criar conta: {str(e)}'}), 500

@professionals_bp.route('/api/<int:professional_id>/reset-password', methods=['POST'])
@login_required
def api_reset_password(professional_id):
    if not current_user.has_permission('all'):
        return jsonify({'error': 'Acesso negado'}), 403
    
    try:
        professional = Professional.query.get_or_404(professional_id)
        
        if not professional.user_account:
            return jsonify({'error': 'Profissional não possui conta de usuário'}), 400
        
        data = request.get_json()
        new_password = data.get('password')
        
        if not new_password:
            return jsonify({'error': 'Nova senha é obrigatória'}), 400
        
        professional.user_account.set_password(new_password)
        db.session.commit()
        
        return jsonify({'message': 'Senha alterada com sucesso'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao alterar senha: {str(e)}'}), 500

# ===== ROTAS AUXILIARES =====