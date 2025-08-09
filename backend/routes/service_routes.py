from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, Servico
from datetime import datetime

services_bp = Blueprint('services', __name__)

@services_bp.route('/')
@login_required
def list_services():
    if not current_user.has_permission('all'):
        flash('Acesso negado.', 'error')
        return redirect(url_for('dashboard'))

    return render_template('services.html')

@services_bp.route('/api/list')
@login_required
def api_list_services():
    try:
        search = request.args.get('search', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)

        query = Servico.query

        if search:
            search_filter = f'%{search}%'
            query = query.filter(Servico.name.ilike(search_filter))

        pagination = query.order_by(Servico.name).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify({
            'services': [s.to_dict() for s in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page
        })
    except Exception as e:
        return jsonify({'error': f'Erro ao carregar serviços: {str(e)}'}), 500

@services_bp.route('/api/create', methods=['POST'])
@login_required
def api_create_service():
    if not current_user.has_permission('all'):
        return jsonify({'error': 'Acesso negado'}), 403

    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Dados não recebidos'}), 400

        required_fields = ['name', 'duration_minutes', 'price']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400

        service = Servico(
            name=data['name'].strip(),
            description=data.get('description', '').strip(),
            category=data.get('category', '').strip(),
            duration_minutes=data['duration_minutes'],
            price=data['price'],
            preparation_instructions=data.get('preparation_instructions', '').strip(),
            aftercare_instructions=data.get('aftercare_instructions', '').strip(),
        )

        db.session.add(service)
        db.session.commit()

        return jsonify({
            'message': 'Serviço cadastrado com sucesso',
            'service': service.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@services_bp.route('/api/<int:service_id>', methods=['GET'])
@login_required
def api_get_service(service_id):
    try:
        service = Servico.query.get_or_404(service_id)
        return jsonify(service.to_dict())
    except Exception as e:
        return jsonify({'error': f'Erro ao carregar serviço: {str(e)}'}), 500

@services_bp.route('/api/<int:service_id>', methods=['PUT'])
@login_required
def api_update_service(service_id):
    if not current_user.has_permission('all'):
        return jsonify({'error': 'Acesso negado'}), 403

    try:
        service = Servico.query.get_or_404(service_id)
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Dados não recebidos'}), 400

        required_fields = ['name', 'duration_minutes', 'price']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400

        service.name = data['name'].strip()
        service.description = data.get('description', '').strip()
        service.category = data.get('category', '').strip()
        service.duration_minutes = data['duration_minutes']
        service.price = data['price']
        service.preparation_instructions = data.get('preparation_instructions', '').strip()
        service.aftercare_instructions = data.get('aftercare_instructions', '').strip()
        service.is_active = data.get('is_active', True)

        db.session.commit()

        return jsonify({
            'message': 'Serviço atualizado com sucesso',
            'service': service.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao atualizar serviço: {str(e)}'}), 500

@services_bp.route('/api/<int:service_id>', methods=['DELETE'])
@login_required
def api_delete_service(service_id):
    if not current_user.has_permission('all'):
        return jsonify({'error': 'Acesso negado'}), 403

    try:
        service = Servico.query.get_or_404(service_id)

        db.session.delete(service)
        db.session.commit()

        return jsonify({'message': 'Serviço excluído com sucesso'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao excluir serviço: {str(e)}'}), 500
