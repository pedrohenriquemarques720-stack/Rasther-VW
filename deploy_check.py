# deploy_check.py - Verificação completa antes do deploy no Streamlit Cloud

import subprocess
import sys
import importlib
import os
import json
from datetime import datetime

def check_deployment():
    """Verifica se o app está pronto para deploy no Streamlit Cloud"""
    
    print("=" * 60)
    print("🔍 RASTHER VW - VERIFICAÇÃO PRÉ-DEPLOY")
    print("=" * 60)
    
    errors = []
    warnings = []
    
    # 1. Verificar versão do Python
    print("\n📌 PYTHON")
    python_version = sys.version_info
    if python_version.major == 3 and python_version.minor >= 8:
        print(f"  ✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        errors.append(f"Python {python_version.major}.{python_version.minor} não suportado (mínimo 3.8)")
    
    # 2. Verificar dependências instaladas
    print("\n📦 DEPENDÊNCIAS INSTALADAS")
    required = {
        'streamlit': '1.28.0',
        'pandas': '2.0.3',
        'numpy': '1.24.3',
        'plotly': '5.18.0'
    }
    
    for package, min_version in required.items():
        try:
            module = importlib.import_module(package)
            version = getattr(module, '__version__', 'desconhecida')
            print(f"  ✅ {package} {version}")
        except ImportError:
            errors.append(f"{package} não instalado")
            print(f"  ❌ {package}")
    
    # 3. Verificar requirements.txt
    print("\n📄 REQUIREMENTS.TXT")
    if os.path.exists('requirements.txt'):
        with open('requirements.txt', 'r') as f:
            content = f.read()
            for package in required:
                if package not in content:
                    warnings.append(f"{package} pode estar faltando no requirements.txt")
                    print(f"  ⚠️ {package}")
                else:
                    print(f"  ✅ {package}")
    else:
        # Criar requirements.txt automaticamente
        with open('requirements.txt', 'w') as f:
            f.write("""streamlit==1.28.0
pandas==2.0.3
numpy==1.24.3
plotly==5.18.0
python-obd==0.7.1
pyserial==3.5
""")
        print("  ✅ requirements.txt criado automaticamente")
    
    # 4. Verificar app.py
    print("\n🔧 APP.PY")
    if os.path.exists('app.py'):
        with open('app.py', 'r') as f:
            content = f.read()
            
            checks = {
                'st.set_page_config': 'Configuração da página',
                'st.session_state': 'Estado da sessão',
                'st.markdown': 'Renderização CSS',
                'st.button': 'Botões interativos',
                'st.columns': 'Layout responsivo',
                'import plotly': 'Biblioteca de gráficos'
            }
            
            for code, desc in checks.items():
                if code in content:
                    print(f"  ✅ {desc}")
                else:
                    warnings.append(f"{desc} pode estar ausente")
                    print(f"  ⚠️ {desc}")
    else:
        errors.append("app.py não encontrado")
    
    # 5. Criar configuração do Streamlit
    print("\n⚙️ CONFIGURAÇÕES STREAMLIT")
    os.makedirs('.streamlit', exist_ok=True)
    with open('.streamlit/config.toml', 'w') as f:
        f.write("""
[theme]
primaryColor = "#0047ab"
backgroundColor = "#0a0c10"
secondaryBackgroundColor = "#1a1d24"
textColor = "#ffffff"
font = "sans serif"

[server]
maxUploadSize = 10
enableXsrfProtection = true
enableCORS = false
""")
    print("  ✅ .streamlit/config.toml criado/verificado")
    
    # 6. Criar .gitignore
    print("\n📁 GITIGNORE")
    with open('.gitignore', 'w') as f:
        f.write("""
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/

# Streamlit
.streamlit/secrets.toml

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
""")
    print("  ✅ .gitignore criado")
    
    # 7. Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO DA VERIFICAÇÃO")
    print("=" * 60)
    
    if errors:
        print(f"\n❌ ERROS ({len(errors)}):")
        for e in errors:
            print(f"   • {e}")
    else:
        print("\n✅ Nenhum erro encontrado!")
    
    if warnings:
        print(f"\n⚠️ AVISOS ({len(warnings)}):")
        for w in warnings:
            print(f"   • {w}")
    
    print("\n" + "=" * 60)
    if not errors:
        print("✅ PRONTO PARA DEPLOY NO STREAMLIT CLOUD!")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("   1. git init")
        print("   2. git add .")
        print("   3. git commit -m 'Versão inicial RASTHER VW'")
        print("   4. git remote add origin https://github.com/SEU-USUARIO/rasther-vw.git")
        print("   5. git push -u origin main")
        print("   6. Acesse https://streamlit.io/cloud")
        print("   7. Conecte seu repositório")
    else:
        print("❌ Corrija os erros antes do deploy")
    
    return len(errors) == 0

if __name__ == "__main__":
    check_deployment()
