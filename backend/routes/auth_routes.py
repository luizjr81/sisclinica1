from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from models import db, User
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

class LoginForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Sua conta está desativada. Entre em contato com o administrador.', 'error')
                return redirect(url_for('auth.login'))
            
            login_user(user, remember=True)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('dashboard'))
        else:
            flash('Usuário ou senha inválidos', 'error')
    
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu do sistema com sucesso.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/api/check-auth')
@login_required
def check_auth():
    return jsonify({
        'authenticated': True,
        'user': {
            'id': current_user.id,
            'username': current_user.username,
            'full_name': current_user.full_name,
            'email': current_user.email
        }
    })