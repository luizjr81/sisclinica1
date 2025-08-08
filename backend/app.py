from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from config import Config
from models import db, User
import os

def create_app():
    app = Flask(__name__, 
                template_folder='../frontend/templates',
                static_folder='../frontend/static')
    
    app.config.from_object(Config)
    
    if not app.config['SECRET_KEY'] or app.config['SECRET_KEY'] == 'sua-chave-secreta-aqui-mude-em-producao':
        raise ValueError("A SECRET_KEY não foi configurada ou está usando o valor padrão. Por favor, crie um arquivo .env, defina uma chave segura e reinicie a aplicação.")

    # Inicializar extensões
    db.init_app(app)
    csrf = CSRFProtect(app)
    bcrypt = Bcrypt(app)
    jwt = JWTManager(app)
    
    # Configurar Login Manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
    
    # Registrar blueprints
    from routes.auth_routes import auth_bp
    from routes.patient_routes import patient_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(patient_bp, url_prefix='/patients')
    
    # Rotas principais
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return redirect(url_for('auth.login'))
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        return render_template('dashboard.html')
    
    # Criar tabelas do banco
    with app.app_context():
        db.create_all()
        
        # Criar usuário admin padrão se não existir
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@clinica.com',
                full_name='Administrador'
            )
            admin.set_password('admin123')  # Mudar em produção!
            db.session.add(admin)
            db.session.commit()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)