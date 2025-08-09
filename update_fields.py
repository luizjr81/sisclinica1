#!/usr/bin/env python3
"""
Script para atualizar campos dos modelos:
- Pacientes: birth_date opcional
- Profissionais: registro_prof e email opcionais (renomear crm_crf)
"""

import os
import sys
from sqlalchemy import text

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def run_fields_migration():
    print("🔄 Atualizando campos dos modelos...")
    print("=" * 50)
    
    try:
        from flask import Flask
        from config import Config
        from sqlalchemy import create_engine
        
        app = Flask(__name__)
        app.config.from_object(Config)
        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        
        with engine.connect() as conn:
            print("📝 Atualizando tabela patients...")
            
            # 1. Tornar birth_date opcional em patients
            try:
                conn.execute(text("ALTER TABLE patients ALTER COLUMN birth_date DROP NOT NULL"))
                print("  ✅ birth_date agora é opcional")
            except Exception as e:
                print(f"  ⚠️  birth_date: {e}")
            
            print("📝 Atualizando tabela professionals...")
            
            # 2. Renomear crm_crf para registro_prof
            try:
                conn.execute(text("ALTER TABLE professionals RENAME COLUMN crm_crf TO registro_prof"))
                print("  ✅ crm_crf renomeado para registro_prof")
            except Exception as e:
                if "does not exist" in str(e):
                    # Coluna pode já ter sido renomeada ou não existir
                    print("  ℹ️  Coluna crm_crf não encontrada (pode já estar como registro_prof)")
                else:
                    print(f"  ⚠️  Erro ao renomear: {e}")
            
            # 3. Tornar registro_prof opcional
            try:
                conn.execute(text("ALTER TABLE professionals ALTER COLUMN registro_prof DROP NOT NULL"))
                print("  ✅ registro_prof agora é opcional")
            except Exception as e:
                print(f"  ⚠️  registro_prof: {e}")
            
            # 4. Tornar email opcional
            try:
                conn.execute(text("ALTER TABLE professionals ALTER COLUMN email DROP NOT NULL"))
                print("  ✅ email agora é opcional")
            except Exception as e:
                print(f"  ⚠️  email: {e}")
            
            conn.commit()
            
        print("\n🎉 Atualização concluída!")
        print("✅ Agora você pode:")
        print("   • Cadastrar pacientes sem data de nascimento")
        print("   • Cadastrar profissionais sem registro prof. e email")
        print("   • Campo CRM/CRF agora é 'Registro Prof.'")
        
    except Exception as e:
        print(f"❌ Erro durante a atualização: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    if not os.path.exists('backend/models.py'):
        print("❌ Execute este script na raiz do projeto!")
        sys.exit(1)
    
    if not os.path.exists('.env'):
        print("❌ Arquivo .env não encontrado!")
        sys.exit(1)
    
    success = run_fields_migration()
    
    if success:
        print("\n✨ Atualização concluída! Reinicie a aplicação para usar as novas configurações.")
    else:
        print("\n❌ Atualização falhou. Verifique os erros acima.")
        sys.exit(1)