#!/bin/bash

# Correção Imediata dos Erros - Sistema Clínica Estética
echo "🔧 Aplicando correções imediatas..."

# 1. Criar diretório de templates de erro
mkdir -p frontend/templates/errors

# 2. Criar template 404.html
cat > frontend/templates/errors/404.html << 'EOF'
{% extends "base.html" %}

{% block title %}Página Não Encontrada{% endblock %}
{% block page_title %}Erro 404{% endblock %}

{% block content %}
<div style="text-align: center; padding: 60px 20px;">
    <div style="max-width: 500px; margin: 0 auto;">
        <i class="fas fa-search" style="font-size: 80px; color: #2196f3; margin-bottom: 20px;"></i>
        <h1 style="font-size: 72px; margin: 0; color: #424242;">404</h1>
        <h2 style="font-size: 24px; margin: 20px 0; color: #616161;">Página Não Encontrada</h2>
        <p style="color: #757575; margin-bottom: 30px;">A página que você está procurando não existe.</p>
        <div>
            <a href="{{ url_for('dashboard') }}" class="btn btn-primary" style="margin-right: 10px;">
                <i class="fas fa-home"></i> Dashboard
            </a>
            <button onclick="history.back()" class="btn btn-secondary">
                <i class="fas fa-arrow-left"></i> Voltar
            </button>
        </div>
    </div>
</div>
{% endblock %}
EOF

# 3. Criar template 403.html
cat > frontend/templates/errors/403.html << 'EOF'
{% extends "base.html" %}

{% block title %}Acesso Negado{% endblock %}
{% block page_title %}Erro 403{% endblock %}

{% block content %}
<div style="text-align: center; padding: 60px 20px;">
    <div style="max-width: 500px; margin: 0 auto;">
        <i class="fas fa-lock" style="font-size: 80px; color: #f44336; margin-bottom: 20px;"></i>
        <h1 style="font-size: 72px; margin: 0; color: #424242;">403</h1>
        <h2 style="font-size: 24px; margin: 20px 0; color: #616161;">Acesso Negado</h2>
        <p style="color: #757575; margin-bottom: 30px;">Você não tem permissão para acessar este recurso.</p>
        <div>
            <a href="{{ url_for('dashboard') }}" class="btn btn-primary" style="margin-right: 10px;">
                <i class="fas fa-home"></i> Dashboard
            </a>
            <a href="{{ url_for('auth.logout') }}" class="btn btn-secondary">
                <i class="fas fa-sign-out-alt"></i> Logout
            </a>
        </div>
    </div>
</div>
{% endblock %}
EOF

# 4. Criar template 500.html
cat > frontend/templates/errors/500.html << 'EOF'
{% extends "base.html" %}

{% block title %}Erro Interno{% endblock %}
{% block page_title %}Erro 500{% endblock %}

{% block content %}
<div style="text-align: center; padding: 60px 20px;">
    <div style="max-width: 500px; margin: 0 auto;">
        <i class="fas fa-server" style="font-size: 80px; color: #f44336; margin-bottom: 20px;"></i>
        <h1 style="font-size: 72px; margin: 0; color: #424242;">500</h1>
        <h2 style="font-size: 24px; margin: 20px 0; color: #616161;">Erro Interno</h2>
        <p style="color: #757575; margin-bottom: 30px;">Ocorreu um erro interno. Nossa equipe foi notificada.</p>
        <div>
            <a href="{{ url_for('dashboard') }}" class="btn btn-primary" style="margin-right: 10px;">
                <i class="fas fa-home"></i> Dashboard
            </a>
            <button onclick="location.reload()" class="btn btn-secondary">
                <i class="fas fa-redo"></i> Tentar Novamente
            </button>
        </div>
    </div>
</div>
{% endblock %}
EOF

# 5. Criar template 400.html
cat > frontend/templates/errors/400.html << 'EOF'
{% extends "base.html" %}

{% block title %}Requisição Inválida{% endblock %}
{% block page_title %}Erro 400{% endblock %}

{% block content %}
<div style="text-align: center; padding: 60px 20px;">
    <div style="max-width: 500px; margin: 0 auto;">
        <i class="fas fa-exclamation-triangle" style="font-size: 80px; color: #ff9800; margin-bottom: 20px;"></i>
        <h1 style="font-size: 72px; margin: 0; color: #424242;">400</h1>
        <h2 style="font-size: 24px; margin: 20px 0; color: #616161;">Requisição Inválida</h2>
        <p style="color: #757575; margin-bottom: 30px;">A requisição não pôde ser processada.</p>
        <div>
            <a href="{{ url_for('dashboard') }}" class="btn btn-primary" style="margin-right: 10px;">
                <i class="fas fa-home"></i> Dashboard
            </a>
            <button onclick="history.back()" class="btn btn-secondary">
                <i class="fas fa-arrow-left"></i> Voltar
            </button>
        </div>
    </div>
</div>
{% endblock %}
EOF

echo "✅ Templates de erro criados!"

# 6. Corrigir SQLAlchemy warning no app.py
echo "🔧 Corrigindo warning do SQLAlchemy..."

# Backup do arquivo original
cp backend/app.py backend/app.py.backup

# Aplicar correção do SQLAlchemy
sed -i 's/return User.query.get(int(user_id))/return db.session.get(User, int(user_id))/' backend/app.py

echo "✅ Warning do SQLAlchemy corrigido!"

# 7. Adicionar favicon simples para parar os erros
echo "🎯 Adicionando favicon para parar erros 404..."

# Adicionar favicon data URL no base.html (se ainda não tiver)
if ! grep -q "favicon" frontend/templates/base.html; then
    sed -i '/<meta name="viewport"/a\    <link rel="icon" href="data:,">' frontend/templates/base.html
    echo "✅ Favicon adicionado!"
else
    echo "ℹ️  Favicon já existe"
fi

echo ""
echo "🎉 CORREÇÕES APLICADAS!"
echo "========================"
echo "✅ Templates de erro criados"
echo "✅ Warning SQLAlchemy corrigido"
echo "✅ Favicon adicionado"
echo ""
echo "🚀 Reinicie a aplicação para aplicar as correções:"
echo "   Ctrl+C para parar"
echo "   python backend/app.py para reiniciar"
echo ""
echo "❌ Os erros 404 do favicon agora devem parar!"
