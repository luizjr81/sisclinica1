from flask import Blueprint, request, jsonify, render_template, abort
from flask_login import login_required, current_user
from models import db, Atendimento, Patient, Professional, Servico
from datetime import datetime

atendimento_bp = Blueprint('atendimento', __name__)

@atendimento_bp.route('/novo')
@login_required
def novo_atendimento_form():
    patient_id = request.args.get('patient_id')
    if not patient_id:
        abort(404, "Paciente não especificado.")

    patient = Patient.query.get_or_404(patient_id)
    # Supondo que o usuário logado é um profissional
    professional = current_user.professional if hasattr(current_user, 'professional') else None

    # Apenas para simplificar; em um caso real, pode ser necessário buscar todos os profissionais
    if not professional:
        professionals = Professional.query.filter_by(is_active=True).all()
    else:
        professionals = [professional]

    return render_template('atendimento_form.html', patient=patient, professionals=professionals, current_professional=professional)


@atendimento_bp.route('/api/create', methods=['POST'])
@login_required
def api_create_atendimento():
    data = request.get_json()

    required_fields = ['patient_id', 'professional_id', 'service_ids', 'data_atendimento']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Campos obrigatórios ausentes'}), 400

    if not data['service_ids']:
        return jsonify({'error': 'Pelo menos um serviço deve ser selecionado'}), 400

    try:
        patient = Patient.query.get(data['patient_id'])
        professional = Professional.query.get(data['professional_id'])
        if not patient or not professional:
            return jsonify({'error': 'Paciente ou Profissional não encontrado'}), 404

        services = Servico.query.filter(Servico.id.in_(data['service_ids'])).all()
        if len(services) != len(data['service_ids']):
            return jsonify({'error': 'Um ou mais serviços não foram encontrados'}), 404

        new_atendimento = Atendimento(
            patient_id=data['patient_id'],
            professional_id=data['professional_id'],
            data_atendimento=datetime.fromisoformat(data['data_atendimento']),
            anotacoes=data.get('anotacoes', ''),
            valor_cobrado=data.get('valor_cobrado')
        )

        new_atendimento.servicos.extend(services)

        db.session.add(new_atendimento)
        db.session.commit()

        return jsonify({
            'message': 'Atendimento registrado com sucesso!',
            'atendimento': new_atendimento.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@atendimento_bp.route('/api/patient/<int:patient_id>')
@login_required
def api_get_atendimentos_by_patient(patient_id):
    # Adicionar verificação de permissão se necessário
    # Ex: Apenas o profissional vinculado ou admin pode ver

    try:
        atendimentos = Atendimento.query.filter_by(patient_id=patient_id).order_by(Atendimento.data_atendimento.desc()).all()

        if not atendimentos:
            return jsonify([])

        return jsonify([atendimento.to_dict() for atendimento in atendimentos])

    except Exception as e:
        return jsonify({'error': f'Erro ao buscar atendimentos: {str(e)}'}), 500
