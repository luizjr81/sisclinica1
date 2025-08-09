from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(20), default='admin')  # admin, professional, receptionist
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relacionamento SIMPLES - apenas referência ao profissional (sem FK circular)
    professional_id = db.Column(db.Integer, nullable=True)  # SEM FOREIGN KEY para evitar ciclo
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def has_permission(self, permission):
        """Verifica se o usuário tem uma permissão específica"""
        role_permissions = {
            'admin': ['all'],
            'professional': ['view_patients', 'edit_patients', 'view_appointments', 'edit_appointments', 'view_records'],
            'receptionist': ['view_patients', 'edit_patients', 'view_appointments', 'edit_appointments']
        }
        
        user_permissions = role_permissions.get(self.role, [])
        return 'all' in user_permissions or permission in user_permissions
    
    @property
    def professional(self):
        """Busca o profissional associado sem usar FK"""
        if self.professional_id:
            return Professional.query.get(self.professional_id)
        return None
    
    def __repr__(self):
        return f'<User {self.username}>'

class Servico(db.Model):
    __tablename__ = 'servicos'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=True)
    duration_minutes = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    preparation_instructions = db.Column(db.Text, nullable=True)
    aftercare_instructions = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'duration_minutes': self.duration_minutes,
            'price': self.price,
            'preparation_instructions': self.preparation_instructions,
            'aftercare_instructions': self.aftercare_instructions,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    def __repr__(self):
        return f'<Servico {self.name}>'


class Professional(db.Model):
    __tablename__ = 'professionals'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    registro_prof = db.Column(db.String(20), nullable=True)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    birth_date = db.Column(db.Date)
    photo = db.Column(db.String(255))
    bio = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    creator = db.relationship('User', backref='professionals_created')
    
    @property
    def user_account(self):
        """Busca a conta de usuário associada sem usar FK circular"""
        return User.query.filter_by(professional_id=self.id).first()
    
    @property
    def has_user_account(self):
        """Verifica se tem conta de usuário"""
        return bool(self.user_account)
    
    def __repr__(self):
        return f'<Professional {self.full_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'cpf': self.cpf,
            'registro_prof': self.registro_prof,
            'phone': self.phone,
            'email': self.email,
            'birth_date': self.birth_date.strftime('%Y-%m-%d') if self.birth_date else None,
            'photo': self.photo,
            'bio': self.bio,
            'is_active': self.is_active,
            'has_user_account': self.has_user_account,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

class Patient(db.Model):
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    birth_date = db.Column(db.Date, nullable=True)  # Data de nascimento agora opcional
    phone = db.Column(db.String(15), nullable=False)
    musical_preference = db.Column(db.String(100))
    observations = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relacionamento com o usuário que criou
    creator = db.relationship('User', backref='patients_created')
    
    def __repr__(self):
        return f'<Patient {self.full_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'cpf': self.cpf,
            'birth_date': self.birth_date.strftime('%Y-%m-%d') if self.birth_date else None,
            'phone': self.phone,
            'musical_preference': self.musical_preference,
            'observations': self.observations,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }