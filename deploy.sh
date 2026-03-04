#!/bin/bash
# deploy.sh - Script de deploy automático para o Streamlit Cloud

echo "🚀 RASTHER VW - DEPLOY AUTOMÁTICO"
echo "==================================="

# 1. Verificar se git está instalado
if ! command -v git &> /dev/null; then
    echo "❌ Git não encontrado. Instale git primeiro."
    exit 1
fi

# 2. Verificar se python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado"
    exit 1
fi

# 3. Executar verificação pré-deploy
echo "🔍 Executando verificação pré-deploy..."
python3 deploy_check.py

if [ $? -ne 0 ]; then
    echo "❌ Verificação falhou. Corrija os erros antes de continuar."
    exit 1
fi

# 4. Configurar git se necessário
if [ ! -d .git ]; then
    echo "📁 Inicializando repositório git..."
    git init
fi

# 5. Adicionar arquivos
echo "📦 Adicionando arquivos ao git..."
git add .

# 6. Commit
read -p "📝 Mensagem do commit: " msg
git commit -m "$msg"

# 7. Verificar remote
if ! git remote | grep -q origin; then
    read -p "🌐 URL do repositório GitHub: " url
    git remote add origin $url
fi

# 8. Push
echo "📤 Enviando para o GitHub..."
git push -u origin main

echo ""
echo "✅ DEPLOY CONCLUÍDO!"
echo "🌐 Acesse: https://streamlit.io/cloud"
echo "📊 Conecte seu repositório e faça o deploy"
