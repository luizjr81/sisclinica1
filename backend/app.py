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
    
    # Configurar CSRF com exceções para API
    csrf = CSRFProtect(app)
    
    # Exceções CSRF para endpoints específicos (se necessário)
    # csrf.exempt('patients.api_create_patient')
    # csrf.exempt('patients.api_update_patient')
    # csrf.exempt('patients.api_delete_patient')
    
    bcrypt = Bcrypt(app)
    jwt = JWTManager(app)
    
    # Configurar Login Manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
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
    
    # Context processor para disponibilizar csrf_token nos templates
    @app.context_processor
    def inject_csrf_token():
        from flask_wtf.csrf import generate_csrf
        return dict(csrf_token=generate_csrf)
    
    # Tratamento de erros
    @app.errorhandler(400)
    def bad_request(error):
        if 'application/json' in str(error):
            return {'error': 'Requisição inválida'}, 400
        return render_template('errors/400.html'), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        if 'application/json' in str(error):
            return {'error': 'Não autorizado'}, 401
        return redirect(url_for('auth.login'))
    
    @app.errorhandler(403)
    def forbidden(error):
        if 'application/json' in str(error):
            return {'error': 'Token CSRF inválido ou ausente'}, 403
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def not_found(error):
        if 'application/json' in str(error):
            return {'error': 'Recurso não encontrado'}, 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        if 'application/json' in str(error):
            return {'error': 'Erro interno do servidor'}, 500
        return render_template('errors/500.html'), 500
    
    # Criar tabelas do banco e usuário admin
    with app.app_context():
        try:
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
                print("✅ Usuário admin criado com sucesso!")
                print("   Username: admin")
                print("   Password: admin123")
                print("   ⚠️  ALTERE ESTA SENHA EM PRODUÇÃO!")
            
            print("✅ Banco de dados inicializado com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro ao inicializar banco de dados: {e}")
            print("   Verifique se o PostgreSQL está rodando e as configurações no .env estão corretas")
    
    return app

if __name__ == '__main__':
    try:
        app = create_app()
        print("🏥 Sistema Clínica Estética")
        print("=" * 50)
        print("🚀 Servidor iniciando...")
        print("📍 URL: http://localhost:5000")
        print("👤 Login: admin / admin123")
        print("=" * 50)
        
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except Exception as e:
        print(f"❌ Erro ao iniciar aplicação: {e}")
        print("\n🔧 Verifique:")
        print("   1. Se o arquivo .env existe e está configurado")
        print("   2. Se o PostgreSQL está rodando")
        print("   3. Se as dependências estão instaladas: pip install -r requirements.txt")