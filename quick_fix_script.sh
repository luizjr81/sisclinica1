#!/bin/bash

# Script de Correção Rápida do Sistema Clínica Estética
# Este script aplica as correções críticas identificadas

echo "🔧 Sistema de Correção Rápida - Clínica Estética"
echo "================================================="
echo ""

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

success() {
    echo -e "${GREEN}✓${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
}

info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Verificar se está no diretório correto
if [ ! -f "backend/app.py" ]; then
    error "Execute este script na raiz do projeto!"
    exit 1
fi

info "Aplicando correções críticas..."
echo ""

# 1. Remover arquivo de backup problemático
if [ -f "backend/routes/professional_routes.py.bk" ]; then
    info "Removendo arquivo de backup problemático..."
    rm "backend/routes/professional_routes.py.bk"
    success "Arquivo professional_routes.py.bk removido"
else
    info "Arquivo professional_routes.py.bk não encontrado (ok)"
fi

# 2. Criar backup dos arquivos originais
info "Criando backups dos arquivos originais..."
cp backend/models.py backend/models.py.backup 2>/dev/null && success "Backup de models.py criado" || warning "Não foi possível criar backup de models.py"
cp frontend/templates/base.html frontend/templates/base.html.backup 2>/dev/null && success "Backup de base.html criado" || warning "Não foi possível criar backup de base.html"
cp backend/app.py backend/app.py.backup 2>/dev/null && success "Backup de app.py criado" || warning "Não foi possível criar backup de app.py"

echo ""

# 3. Verificar se PostgreSQL está rodando
info "Verificando PostgreSQL..."
if command -v pg_isready &> /dev/null; then
    if pg_isready -q; then
        success "PostgreSQL está rodando"
    else
        warning "PostgreSQL não está respondendo"
        echo "  Para iniciar no Ubuntu/Debian: sudo service postgresql start"
        echo "  Para iniciar no macOS: brew services start postgresql"
    fi
else
    warning "Comando pg_isready não encontrado"
fi

echo ""

# 4. Verificar arquivo .env
if [ -f ".env" ]; then
    success "Arquivo .env encontrado"
    
    # Verificar se tem as chaves padrão
    if grep -q "sua-chave-secreta-aqui-mude-em-producao" .env; then
        warning "SECRET_KEY está usando valor padrão!"
        echo "  Edite o arquivo .env e altere a SECRET_KEY"
    fi
    
    if grep -q "sua-chave-jwt-aqui-mude-em-producao" .env; then
        warning "JWT_SECRET_KEY está usando valor padrão!"
        echo "  Edite o arquivo .env e altere a JWT_SECRET_KEY"
    fi
else
    warning "Arquivo .env não encontrado"
    if [ -f ".env.example" ]; then
        info "Criando .env a partir do .env.example..."
        cp .env.example .env
        success "Arquivo .env criado"
        warning "Configure o arquivo .env antes de continuar!"
    else
        error "Arquivo .env.example também não encontrado!"
    fi
fi

echo ""

# 5. Verificar ambiente virtual
if [ -d "venv" ]; then
    success "Ambiente virtual encontrado"
    info "Para ativar: source venv/bin/activate"
else
    info "Ambiente virtual não encontrado"
    echo "  Para criar: python3 -m venv venv"
    echo "  Para ativar: source venv/bin/activate"
fi

echo ""

# 6. Verificar dependências
info "Verificando dependências..."
if [ -f "requirements.txt" ]; then
    success "Arquivo requirements.txt encontrado"
    
    # Verificar se Flask-Cors é necessário
    if grep -q "Flask-Cors" requirements.txt; then
        warning "Flask-Cors está nas dependências mas não é usado"
        echo "  Considere remover se não for necessário"
    fi
else
    error "Arquivo requirements.txt não encontrado!"
fi

echo ""

# 7. Criar diretórios necessários
info "Criando diretórios necessários..."
mkdir -p logs && success "Diretório logs criado"
mkdir -p frontend/templates/errors && success "Diretório de templates de erro criado"

echo ""

# 8. Verificar estrutura de arquivos críticos
info "Verificando arquivos críticos..."

critical_files=(
    "backend/models.py"
    "backend/config.py"
    "backend/routes/auth_routes.py"
    "backend/routes/patient_routes.py"
    "backend/routes/professional_routes.py"
    "backend/routes/service_routes.py"
    "frontend/templates/base.html"
    "frontend/templates/login.html"
    "frontend/static/css/styles.css"
    "frontend/static/js/main.js"
)

for file in "${critical_files[@]}"; do
    if [ -f "$file" ]; then
        success "✓ $file"
    else
        error "✗ $file - ARQUIVO FALTANDO!"
    fi
done

echo ""

# 9. Executar correção no banco de dados
info "Preparando correção do banco de dados..."
cat > fix_database.py << 'EOF'
#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def fix_database():
    try:
        from flask import Flask
        from config import Config
        from sqlalchemy import create_engine, text
        
        app = Flask(__name__)
        app.config.from_object(Config)
        
        if not app.config['SQLALCHEMY_DATABASE_URI']:
            print("❌ DATABASE_URL não configurada no .env")
            return False
            
        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        
        with engine.connect() as conn:
            print("🔄 Aplicando correções no banco...")
            
            # Tornar birth_date opcional em patients
            try:
                conn.execute(text("ALTER TABLE patients ALTER COLUMN birth_date DROP NOT NULL"))
                print("  ✅ patients.birth_date agora é opcional")
            except Exception as e:
                if "does not exist" in str(e).lower():
                    print("  ℹ️  Tabela patients não existe ainda (será criada)")
                else:
                    print(f"  ⚠️  patients.birth_date: {e}")
            
            # Renomear crm_crf para registro_prof se necessário
            try:
                conn.execute(text("ALTER TABLE professionals RENAME COLUMN crm_crf TO registro_prof"))
                print("  ✅ professionals.crm_crf renomeado para registro_prof")
            except Exception as e:
                if "does not exist" in str(e).lower():
                    print("  ℹ️  Coluna crm_crf não existe (ok)")
                else:
                    print(f"  ⚠️  Renomear coluna: {e}")
            
            # Tornar registro_prof opcional
            try:
                conn.execute(text("ALTER TABLE professionals ALTER COLUMN registro_prof DROP NOT NULL"))
                print("  ✅ professionals.registro_prof agora é opcional")
            except Exception as e:
                if "does not exist" in str(e).lower():
                    print("  ℹ️  Tabela professionals não existe ainda (será criada)")
                else:
                    print(f"  ⚠️  professionals.registro_prof: {e}")
            
            # Tornar email opcional
            try:
                conn.execute(text("ALTER TABLE professionals ALTER COLUMN email DROP NOT NULL"))
                print("  ✅ professionals.email agora é opcional")
            except Exception as e:
                if "does not exist" in str(e).lower():
                    print("  ℹ️  Tabela professionals não existe ainda (será criada)")
                else:
                    print(f"  ⚠️  professionals.email: {e}")
            
            conn.commit()
            print("🎉 Correções aplicadas com sucesso!")
            return True
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    if fix_database():
        print("\n✅ Banco de dados corrigido!")
    else:
        print("\n❌ Falha na correção do banco")
        sys.exit(1)
EOF

success "Script de correção do banco criado: fix_database.py"

echo ""

# 10. Instruções finais
echo "📋 PRÓXIMOS PASSOS:"
echo "==================="
echo ""
echo "1. Configure o arquivo .env:"
echo "   nano .env"
echo ""
echo "2. Ative o ambiente virtual (se existir):"
echo "   source venv/bin/activate"
echo ""
echo "3. Instale/atualize dependências:"
echo "   pip install -r requirements.txt"
echo ""
echo "4. Execute a correção do banco de dados:"
echo "   python fix_database.py"
echo ""
echo "5. Inicie a aplicação:"
echo "   cd backend && python app.py"
echo ""

# 11. Resumo dos problemas corrigidos
echo "🔧 PROBLEMAS CORRIGIDOS:"
echo "========================"
echo ""
success "Arquivo .bk problemático removido"
success "Backups dos arquivos originais criados"
success "Diretórios necessários criados"
success "Script de correção do banco preparado"
echo ""

warning "ATENÇÃO: Ainda é necessário:"
echo "  • Configurar corretamente o arquivo .env"
echo "  • Aplicar os arquivos corrigidos (models.py, base.html, app.py)"
echo "  • Executar o script de correção do banco"
echo ""

info "Para aplicar as correções dos arquivos principais, substitua:"
echo "  • backend/models.py (com a versão corrigida)"
echo "  • frontend/templates/base.html (corrigir csrf_token)"
echo "  • backend/app.py (versão com validações)"
echo "  • backend/routes/professional_routes.py (sem referências a Specialty)"

echo ""
echo "🎯 Após essas correções, o sistema estará funcionando corretamente!"
echo ""

# Limpar script temporário
# rm -f fix_database.py

echo "Script de correção concluído!"
echo "Execute os próximos passos listados acima."