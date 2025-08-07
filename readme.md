# Sistema de Gestão para Clínica de Estética

Sistema modular e responsivo para gerenciamento de clínicas de estética, desenvolvido com Python, Flask, PostgreSQL e design profissional.

## 🚀 Características

- **Design Profissional**: Interface moderna e intuitiva com cores suaves adequadas para clínicas de estética
- **100% Responsivo**: Funciona perfeitamente em desktop, tablet e mobile
- **Arquitetura Modular**: Sistema não-monolítico, facilitando manutenção e escalabilidade
- **Segurança**: Autenticação segura, proteção CSRF, validação de dados e sanitização de inputs
- **Gestão de Pacientes**: Cadastro completo com campos personalizados incluindo gosto musical
- **Dashboard Intuitivo**: Visualização rápida de estatísticas e informações importantes

## 📋 Pré-requisitos

- Python 3.8 ou superior
- PostgreSQL 12 ou superior
- pip (gerenciador de pacotes Python)

## 🔧 Instalação

1. **Clone o repositório**
```bash
git clone https://github.com/seu-usuario/clinica-estetica.git
cd clinica-estetica
```

2. **Crie um ambiente virtual**
```bash
python -m venv venv

# No Windows
venv\Scripts\activate

# No Linux/Mac
source venv/bin/activate
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Configure o banco de dados PostgreSQL**
```sql
CREATE DATABASE clinica_estetica;
CREATE USER seu_usuario WITH PASSWORD 'sua_senha';
GRANT ALL PRIVILEGES ON DATABASE clinica_estetica TO seu_usuario;
```

5. **Configure as variáveis de ambiente**
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

6. **Execute a aplicação**
```bash
cd backend
python app.py
```

A aplicação estará disponível em `http://localhost:5000`

## 🔐 Credenciais Padrão

- **Usuário**: admin
- **Senha**: admin123

⚠️ **IMPORTANTE**: Altere essas credenciais imediatamente em produção!

## 📁 Estrutura do Projeto

```
clinica-estetica/
├── backend/                 # Backend Flask
│   ├── app.py              # Aplicação principal
│   ├── config.py           # Configurações
│   ├── models.py           # Modelos do banco
│   ├── auth.py             # Autenticação
│   ├── routes/             # Rotas da API
│   │   ├── auth_routes.py  # Rotas de autenticação
│   │   └── patient_routes.py # Rotas de pacientes
│   └── utils/              # Utilitários
│       └── security.py     # Funções de segurança
├── frontend/               # Frontend
│   ├── static/             # Arquivos estáticos
│   │   ├── css/           # Estilos
│   │   └── js/            # JavaScript
│   └── templates/          # Templates HTML
└── requirements.txt        # Dependências
```

## 🛡️ Segurança Implementada

- **Autenticação**: Sistema de login seguro com Flask-Login
- **Proteção CSRF**: Todas as requisições POST/PUT/DELETE protegidas
- **Validação de CPF**: Validação completa do CPF brasileiro
- **Sanitização**: Todos os inputs são sanitizados para prevenir XSS
- **Senhas**: Hashing seguro com bcrypt
- **Sessões**: Configurações seguras de cookies e sessões

## 🎨 Personalização

### Cores
As cores podem ser personalizadas no arquivo `styles.css` alterando as variáveis CSS:

```css
:root {
    --primary: #e91e63;        /* Rosa principal */
    --primary-dark: #c2185b;   /* Rosa escuro */
    --primary-light: #f8bbd0;  /* Rosa claro */
}
```

### Logo e Nome
Altere o nome da clínica nos templates:
- `base.html`: Linha com `<span>Clínica Bella</span>`
- `login.html`: Linha com `<h1>Clínica Bella</h1>`

## 📱 Funcionalidades

### Dashboard
- Visualização de estatísticas gerais
- Ações rápidas para principais funções
- Lista de pacientes recentes
- Próximos agendamentos (preparado para implementação)

### Gestão de Pacientes
- Cadastro completo com validação
- Busca por nome, CPF ou telefone
- Edição de dados
- Exclusão com confirmação
- Campos personalizados (gosto musical, observações)

## 🚧 Próximas Implementações

- [ ] Sistema de agendamentos
- [ ] Prontuário eletrônico
- [ ] Gestão financeira
- [ ] Relatórios e gráficos
- [ ] Notificações por email/SMS
- [ ] Integração com WhatsApp
- [ ] Backup automático

## 🤝 Contribuindo

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para suporte, envie um email para suporte@clinicabella.com.br ou abra uma issue no GitHub.

## ⚡ Performance

- Consultas otimizadas com SQLAlchemy
- Paginação implementada para grandes volumes de dados
- Cache de assets estáticos
- Lazy loading de componentes não críticos

## 🔒 Backup e Recuperação

### Backup do Banco de Dados
```bash
pg_dump -U usuario -d clinica_estetica > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restaurar Backup
```bash
psql -U usuario -d clinica_estetica < backup_arquivo.sql
```

---

Desenvolvido com ❤️ para clínicas de estética modernas