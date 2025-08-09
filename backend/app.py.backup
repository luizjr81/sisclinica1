from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from config import Config
from models import db, User, Servico
import os
import logging
from logging.handlers import RotatingFileHandler

def validate_config(app):
    """Valida as configurações críticas da aplicação"""
    errors = []
    
    if not app.config['SECRET_KEY']:
        errors.append("SECRET_KEY não foi configurada")
    elif app.config['SECRET_KEY'] == 'sua-chave-secreta-aqui-mude-em-producao':
        errors.append("SECRET_KEY está usando o valor padrão - altere no arquivo .env")
    
    if not app.config['SQLALCHEMY_DATABASE_URI']:
        errors.append("DATABASE_URL não foi configurada")
    
    if not app.config['JWT_SECRET_KEY']:
        errors.append("JWT_SECRET_KEY não foi configurada")
    elif app.config['JWT_SECRET_KEY'] == 'sua-chave-jwt-aqui-mude-em-producao':
        errors.append("JWT_SECRET_KEY está usando o valor padrão - altere no arquivo .env")
    
    if errors:
        error_msg = "Erros de configuração encontrados:\n"
        for error in errors:
            error_msg += f"  • {error}\n"
        error_msg += "\nPor favor, configure o arquivo .env corretamente e reinicie a aplicação."
        raise ValueError(error_msg)

def setup_logging(app):
    """Configura o sistema de logging"""
    if not app.debug and not app.testing:
        # Criar diretório de logs se não existir
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # Configurar handler de arquivo com rotação
        file_handler = RotatingFileHandler('logs/clinica.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('🏥 Sistema Clínica Estética iniciado')

def create_app():
    app = Flask(__name__, 
                template_folder='../frontend/templates',
                static_folder='../frontend/static')
    
    app.config.from_object(Config)
    
    # Validar configurações críticas
    try:
        validate_config(app)
    except ValueError as e:
        print(f"❌ Erro de configuração: {e}")
        raise
    
    # Configurar logging
    setup_logging(app)
    
    # Inicializar extensões
    db.init_app(app)
    
    # Configurar CSRF com exceções para API
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
        return User.query.get(int(user_id))
    
    # Registrar blueprints
    from routes.auth_routes import auth_bp
    from routes.patient_routes import patient_bp
    from routes.professional_routes import professionals_bp
    from routes.service_routes import services_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(patient_bp, url_prefix='/patients')
    app.register_blueprint(professionals_bp, url_prefix='/professionals')
    app.register_blueprint(services_bp, url_prefix='/services')
    
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
    
    # Context processor para disponibilizar csrf_token e user nos templates
    @app.context_processor
    def inject_csrf_token():
        from flask_wtf.csrf import generate_csrf
        return dict(csrf_token=generate_csrf)
    
    @app.context_processor
    def inject_user_permissions():
        """Disponibiliza funções de permissão nos templates"""
        def has_permission(permission):
            if current_user.is_authenticated:
                return current_user.has_permission(permission)
            return False
        
        return dict(has_permission=has_permission)
    
    # Tratamento de erros melhorado
    @app.errorhandler(400)
    def bad_request(error):
        app.logger.warning(f'Bad request: {error}')
        if 'application/json' in str(error):
            return {'error': 'Requisição inválida'}, 400
        return render_template('errors/400.html'), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        app.logger.warning(f'Unauthorized access: {error}')
        if 'application/json' in str(error):
            return {'error': 'Não autorizado'}, 401
        return redirect(url_for('auth.login'))
    
    @app.errorhandler(403)
    def forbidden(error):
        app.logger.warning(f'Forbidden access: {error}')
        if 'application/json' in str(error):
            return {'error': 'Acesso negado'}, 403
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def not_found(error):
        app.logger.info(f'Page not found: {error}')
        if 'application/json' in str(error):
            return {'error': 'Recurso não encontrado'}, 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Internal server error: {error}')
        db.session.rollback()
        if 'application/json' in str(error):
            return {'error': 'Erro interno do servidor'}, 500
        return render_template('errors/500.html'), 500
    
    # Criar tabelas do banco e dados iniciais
    with app.app_context():
        try:
            db.create_all()
            
            # Criar usuário admin padrão se não existir
            if not User.query.filter_by(username='admin').first():
                # Usar senha do ambiente ou padrão
                admin_password = os.environ.get('ADMIN_DEFAULT_PASSWORD', 'admin123')
                
                admin = User(
                    username='admin',
                    email='admin@clinica.com',
                    full_name='Administrador',
                    role='admin'
                )
                admin.set_password(admin_password)
                db.session.add(admin)
                
                app.logger.info("✅ Usuário admin criado com sucesso!")
                print("✅ Usuário admin criado com sucesso!")
                print("   Username: admin")
                print(f"   Password: {admin_password}")
                if admin_password == 'admin123':
                    print("   ⚠️  ALTERE ESTA SENHA EM PRODUÇÃO!")
            
            db.session.commit()
            app.logger.info("✅ Banco de dados inicializado com sucesso!")
            print("✅ Banco de dados inicializado com sucesso!")
            
        except Exception as e:
            app.logger.error(f"❌ Erro ao inicializar banco de dados: {e}")
            print(f"❌ Erro ao inicializar banco de dados: {e}")
            print("   Verifique se o PostgreSQL está rodando e as configurações no .env estão corretas")
            raise
    
    return app

if __name__ == '__main__':
    try:
        app = create_app()
        print("🏥 Sistema Clínica Estética")
        print("=" * 50)
        print("🚀 Servidor iniciando...")
        print("📍 URL: http://localhost:5000")
        print("👤 Login: admin / admin123")
        print("📋 Módulos disponíveis:")
        print("   • Pacientes")
        print("   • Profissionais")
        print("   • Serviços")
        print("=" * 50)
        
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except Exception as e:
        print(f"❌ Erro ao iniciar aplicação: {e}")
        print("\n🔧 Verifique:")
        print("   1. Se o arquivo .env existe e está configurado")
        print("   2. Se o PostgreSQL está rodando")
        print("   3. Se as dependências estão instaladas: pip install -r requirements.txt")
        exit(1)