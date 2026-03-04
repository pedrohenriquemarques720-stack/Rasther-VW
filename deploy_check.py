# deploy_check.py - Verificação completa antes do deploy

import subprocess
import sys
import importlib
import os
import json

def check_deployment():
    """Verifica se o app está pronto para deploy no Streamlit Cloud"""
    
    print("🔍 VERIFICANDO RASTHER VW PARA DEPLOY")
    print("=" * 60)
    errors = []
    warnings = []
    
    # 1. Verificar versão do Python
    print("\n📌 VERIFICANDO PYTHON")
    python_version = sys.version_info
    if python_version.major == 3 and python_version.minor >= 8:
        print(f"  ✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        errors.append(f"Python {python_version.major}.{python_version.minor} não suportado (mínimo 3.8)")
    
    # 2. Verificar dependências
    print("\n📦 VERIFICANDO DEPENDÊNCIAS")
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
    print("\n📄 VERIFICANDO REQUIREMENTS.TXT")
    if os.path.exists('requirements.txt'):
        with open('requirements.txt', 'r') as f:
            content = f.read()
            for package in required:
                if package not in content:
                    warnings.append(f"{package} pode estar faltando no requirements.txt")
                    print(f"  ⚠️ {package} não encontrado no requirements.txt")
                else:
                    print(f"  ✅ {package} OK")
    else:
        errors.append("requirements.txt não encontrado")
    
    # 4. Verificar app.py
    print("\n🔧 VERIFICANDO APP.PY")
    if os.path.exists('app.py'):
        with open('app.py', 'r') as f:
            content = f.read()
            
            # Verificações essenciais
            checks = {
                'st.set_page_config': 'Configuração da página',
                'st.session_state': 'Estado da sessão',
                'st.markdown': 'Renderização CSS',
                'st.button': 'Botões interativos',
                'st.columns': 'Layout responsivo'
            }
            
            for code, desc in checks.items():
                if code in content:
                    print(f"  ✅ {desc}")
                else:
                    warnings.append(f"{desc} pode estar ausente")
                    print(f"  ⚠️ {desc}")
    else:
        errors.append("app.py não encontrado")
    
    # 5. Verificar arquivos de configuração do Streamlit
    print("\n⚙️ VERIFICANDO CONFIGURAÇÕES STREAMLIT")
    if os.path.exists('.streamlit/config.toml'):
        print("  ✅ .streamlit/config.toml encontrado")
    else:
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
        print("  ✅ .streamlit/config.toml criado")
    
    # 6. Resumo final
    print("\n" + "=" * 60)
    if errors:
        print(f"❌ ERROS ENCONTRADOS ({len(errors)}):")
        for e in errors:
            print(f"   • {e}")
    else:
        print("✅ Nenhum erro encontrado")
    
    if warnings:
        print(f"\n⚠️ AVISOS ({len(warnings)}):")
        for w in warnings:
            print(f"   • {w}")
    
    print("\n📊 STATUS DO DEPLOY:")
    if not errors:
        print("   ✅ Pronto para deploy no Streamlit Cloud!")
        print("\n   Próximos passos:")
        print("   1. git add .")
        print("   2. git commit -m 'Versão final RASTHER VW'")
        print("   3. git push")
        print("   4. Acesse https://streamlit.io/cloud")
        print("   5. Conecte seu repositório")
        return True
    else:
        print("   ❌ Corrija os erros antes do deploy")
        return False

if __name__ == "__main__":
    check_deployment()
