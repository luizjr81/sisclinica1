from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp
from models import db, Patient
from datetime import datetime
import re

patient_bp = Blueprint('patients', __name__)

class PatientForm(FlaskForm):
    full_name = StringField('Nome Completo', validators=[DataRequired(), Length(min=3, max=150)])
    cpf = StringField('CPF', validators=[
        DataRequired(),
        Length(min=11, max=14)  # Permitir CPF com ou sem máscara
    ])
    birth_date = DateField('Data de Nascimento', validators=[DataRequired()])
    phone = StringField('Telefone', validators=[
        DataRequired(),
        Length(min=10, max=15)  # Permitir telefone com ou sem máscara
    ])
    musical_preference = StringField('Gosto Musical', validators=[Length(max=100)])
    observations = TextAreaField('Observações')
    submit = SubmitField('Salvar')

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

@patient_bp.route('/')
@login_required
def list_patients():
    return render_template('patients.html')

@patient_bp.route('/api/list')
@login_required
def api_list_patients():
    try:
        search = request.args.get('search', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)  # Máximo 100 por página
        
        query = Patient.query
        
        if search:
            search_filter = f'%{search}%'
            query = query.filter(
                db.or_(
                    Patient.full_name.ilike(search_filter),
                    Patient.cpf.like(search_filter),
                    Patient.phone.like(search_filter)
                )
            )
        
        pagination = query.order_by(Patient.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'patients': [p.to_dict() for p in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page
        })
    except Exception as e:
        return jsonify({'error': f'Erro ao carregar pacientes: {str(e)}'}), 500

@patient_bp.route('/api/create', methods=['POST'])
@login_required
def api_create_patient():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados não recebidos'}), 400
        
        # Validações obrigatórias
        required_fields = ['full_name', 'cpf', 'birth_date', 'phone']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        # Formatar e validar CPF
        cpf_formatted = format_cpf(data['cpf'])
        if not validate_cpf(cpf_formatted):
            return jsonify({'error': 'CPF inválido'}), 400
        
        # Verificar CPF único
        if Patient.query.filter_by(cpf=cpf_formatted).first():
            return jsonify({'error': 'CPF já cadastrado'}), 400
        
        # Formatar telefone
        phone_formatted = format_phone(data['phone'])
        
        # Validar data de nascimento
        try:
            birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Data de nascimento inválida'}), 400
        
        # Criar paciente
        patient = Patient(
            full_name=data['full_name'].strip(),
            cpf=cpf_formatted,
            birth_date=birth_date,
            phone=phone_formatted,
            musical_preference=data.get('musical_preference', '').strip(),
            observations=data.get('observations', '').strip(),
            created_by=current_user.id
        )
        
        db.session.add(patient)
        db.session.commit()
        
        return jsonify({
            'message': 'Paciente cadastrado com sucesso',
            'patient': patient.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@patient_bp.route('/api/<int:patient_id>', methods=['GET'])
@login_required
def api_get_patient(patient_id):
    try:
        patient = Patient.query.get_or_404(patient_id)
        return jsonify(patient.to_dict())
    except Exception as e:
        return jsonify({'error': f'Erro ao carregar paciente: {str(e)}'}), 500

@patient_bp.route('/api/<int:patient_id>', methods=['PUT'])
@login_required
def api_update_patient(patient_id):
    try:
        patient = Patient.query.get_or_404(patient_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados não recebidos'}), 400
        
        # Validações obrigatórias
        required_fields = ['full_name', 'cpf', 'birth_date', 'phone']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        # Formatar e validar CPF
        cpf_formatted = format_cpf(data['cpf'])
        if not validate_cpf(cpf_formatted):
            return jsonify({'error': 'CPF inválido'}), 400
        
        # Verificar CPF único (exceto para o próprio paciente)
        cpf_exists = Patient.query.filter(
            Patient.cpf == cpf_formatted,
            Patient.id != patient_id
        ).first()
        
        if cpf_exists:
            return jsonify({'error': 'CPF já cadastrado para outro paciente'}), 400
        
        # Formatar telefone
        phone_formatted = format_phone(data['phone'])
        
        # Validar data de nascimento
        try:
            birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Data de nascimento inválida'}), 400
        
        # Atualizar paciente
        patient.full_name = data['full_name'].strip()
        patient.cpf = cpf_formatted
        patient.birth_date = birth_date
        patient.phone = phone_formatted
        patient.musical_preference = data.get('musical_preference', '').strip()
        patient.observations = data.get('observations', '').strip()
        patient.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Paciente atualizado com sucesso',
            'patient': patient.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao atualizar paciente: {str(e)}'}), 500

@patient_bp.route('/api/<int:patient_id>', methods=['DELETE'])
@login_required
def api_delete_patient(patient_id):
    try:
        patient = Patient.query.get_or_404(patient_id)
        
        db.session.delete(patient)
        db.session.commit()
        
        return jsonify({'message': 'Paciente excluído com sucesso'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao excluir paciente: {str(e)}'}), 500