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
        Regexp(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', message='CPF deve estar no formato 000.000.000-00')
    ])
    birth_date = DateField('Data de Nascimento', validators=[DataRequired()])
    phone = StringField('Telefone', validators=[
        DataRequired(),
        Regexp(r'^\(\d{2}\) \d{4,5}-\d{4}$', message='Telefone deve estar no formato (00) 00000-0000')
    ])
    musical_preference = StringField('Gosto Musical', validators=[Length(max=100)])
    observations = TextAreaField('Observações')
    submit = SubmitField('Salvar')

@patient_bp.route('/')
@login_required
def list_patients():
    return render_template('patients.html')

@patient_bp.route('/api/list')
@login_required
def api_list_patients():
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
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
        'current_page': page
    })

@patient_bp.route('/api/create', methods=['POST'])
@login_required
def api_create_patient():
    data = request.json
    
    # Validar CPF único
    if Patient.query.filter_by(cpf=data.get('cpf')).first():
        return jsonify({'error': 'CPF já cadastrado'}), 400
    
    try:
        patient = Patient(
            full_name=data['full_name'],
            cpf=data['cpf'],
            birth_date=datetime.strptime(data['birth_date'], '%Y-%m-%d').date(),
            phone=data['phone'],
            musical_preference=data.get('musical_preference', ''),
            observations=data.get('observations', ''),
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
        return jsonify({'error': str(e)}), 400

@patient_bp.route('/api/<int:patient_id>', methods=['GET'])
@login_required
def api_get_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    return jsonify(patient.to_dict())

@patient_bp.route('/api/<int:patient_id>', methods=['PUT'])
@login_required
def api_update_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    data = request.json
    
    # Validar CPF único (exceto para o próprio paciente)
    cpf_exists = Patient.query.filter(
        Patient.cpf == data.get('cpf'),
        Patient.id != patient_id
    ).first()
    
    if cpf_exists:
        return jsonify({'error': 'CPF já cadastrado para outro paciente'}), 400
    
    try:
        patient.full_name = data['full_name']
        patient.cpf = data['cpf']
        patient.birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
        patient.phone = data['phone']
        patient.musical_preference = data.get('musical_preference', '')
        patient.observations = data.get('observations', '')
        patient.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Paciente atualizado com sucesso',
            'patient': patient.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@patient_bp.route('/api/<int:patient_id>', methods=['DELETE'])
@login_required
def api_delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    
    try:
        db.session.delete(patient)
        db.session.commit()
        return jsonify({'message': 'Paciente excluído com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400