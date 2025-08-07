#!/bin/bash

# Script de configuração do projeto Clínica Estética
# Este script cria a estrutura de diretórios e move os arquivos para seus locais corretos

echo "========================================="
echo "   Setup do Sistema Clínica Estética     "
echo "========================================="
echo ""

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Função para exibir mensagens de sucesso
success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Função para exibir mensagens de erro
error() {
    echo -e "${RED}✗${NC} $1"
}

# Função para exibir mensagens de info
info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Verificar se está no diretório correto
info "Verificando diretório atual..."
CURRENT_DIR=$(pwd)
echo "Diretório atual: $CURRENT_DIR"
echo ""

# Criar estrutura de diretórios
info "Criando estrutura de diretórios..."

# Backend
mkdir -p backend/routes
mkdir -p backend/utils

# Frontend
mkdir -p frontend/static/css
mkdir -p frontend/static/js
mkdir -p frontend/templates

success "Estrutura de diretórios criada!"
echo ""


# Criar arquivo .env se não existir
if [ ! -f ".env" ]; then
    info "Criando arquivo .env a partir do .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        success "Arquivo .env criado! Por favor, edite-o com suas configurações."
    else
        error "Arquivo .env.example não encontrado!"
    fi
else
    info "Arquivo .env já existe."
fi

echo ""

# Verificar se Python está instalado
info "Verificando instalação do Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    success "Python instalado: $PYTHON_VERSION"
else
    error "Python 3 não está instalado! Por favor, instale o Python 3.8 ou superior."
fi

echo ""

# Verificar se PostgreSQL está instalado
info "Verificando instalação do PostgreSQL..."
if command -v psql &> /dev/null; then
    PSQL_VERSION=$(psql --version)
    success "PostgreSQL instalado: $PSQL_VERSION"
else
    error "PostgreSQL não está instalado! Por favor, instale o PostgreSQL 12 ou superior."
fi

echo ""

# Criar ambiente virtual
info "Deseja criar um ambiente virtual Python? (recomendado) [s/N]"
read -r CREATE_VENV

if [[ "$CREATE_VENV" =~ ^[Ss]$ ]]; then
    info "Criando ambiente virtual..."
    python3 -m venv venv
    success "Ambiente virtual criado!"
    
    echo ""
    info "Para ativar o ambiente virtual, execute:"
    echo "  source venv/bin/activate"
    
    echo ""
    info "Deseja instalar as dependências agora? [s/N]"
    read -r INSTALL_DEPS
    
    if [[ "$INSTALL_DEPS" =~ ^[Ss]$ ]]; then
        info "Ativando ambiente virtual e instalando dependências..."
        source venv/bin/activate
        pip install -r requirements.txt
        success "Dependências instaladas!"
    fi
fi

echo ""
echo "========================================="
success "Setup concluído com sucesso!"
echo "========================================="
echo ""
info "Próximos passos:"
echo "  1. Configure o PostgreSQL e crie o banco de dados:"
echo "     sudo -u postgres psql"
echo "     CREATE DATABASE clinica_estetica;"
echo "     CREATE USER seu_usuario WITH PASSWORD 'sua_senha';"
echo "     GRANT ALL PRIVILEGES ON DATABASE clinica_estetica TO seu_usuario;"
echo ""
echo "  2. Edite o arquivo .env com suas configurações:"
echo "     nano .env"
echo ""
echo "  3. Ative o ambiente virtual (se criado):"
echo "     source venv/bin/activate"
echo ""
echo "  4. Execute a aplicação:"
echo "     cd backend"
echo "     python3 app.py"
echo ""
info "A aplicação estará disponível em http://localhost:5000"
echo ""

# Tornar o script não mais necessário
info "Este script de setup pode ser removido após a execução:"
echo "  rm setup_project.sh"
echo ""