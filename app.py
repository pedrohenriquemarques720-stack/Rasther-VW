# app.py - RASTHER VW - Scanner Profissional Volkswagen
# Versão 2.0 - Com todas as funcionalidades integradas

import streamlit as st
import pandas as pd
import numpy as np
import time
import random
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json

# =============================================
# CONFIGURAÇÕES DA PÁGINA
# =============================================
st.set_page_config(
    page_title="RASTHER VW - Scanner Volkswagen",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================================
# INICIALIZAÇÃO DA SESSÃO
# =============================================
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.current_page = "Dashboard"
    st.session_state.connected = False
    st.session_state.vehicle_info = {
        'modelo': '---',
        'ano': '---',
        'motor': '---',
        'vin': '---',
        'ecu': '---',
        'protocolo': '---',
        'km': '---'
    }
    st.session_state.dtcs = []
    st.session_state.live_data = {
        'rpm': 0,
        'velocidade': 0,
        'temp_motor': 0,
        'pressao_oleo': 0,
        'bateria': 12.5,
        'stft': 0,
        'ltft': 0,
        'maf': 0,
        'carga_motor': 0,
        'avanco': 0,
        'sonda_lambda': 0.78
    }
    st.session_state.log = []
    st.session_state.procedimento_ativo = None
    st.session_state.dtc_selecionado = None

# =============================================
# BANCO DE DADOS VOLKSWAGEN (EM MEMÓRIA)
# =============================================
MODELOS_VW = {
    'Gol': {
        'anos': '2008-2024',
        'motores': ['1.0 8V', '1.6 8V', '1.0 TSI', '1.6 MSI'],
        'geracoes': ['G4', 'G5', 'G6', 'G7'],
        'imagem': '🚗'
    },
    'Polo': {
        'anos': '2017-2024',
        'motores': ['1.0 TSI', '1.6 MSI', '200 TSI'],
        'geracoes': ['G6', 'G7'],
        'imagem': '🚘'
    },
    'Virtus': {
        'anos': '2018-2024',
        'motores': ['1.0 TSI', '1.6 MSI'],
        'geracoes': ['G1', 'G2'],
        'imagem': '🚙'
    },
    'T-Cross': {
        'anos': '2019-2024',
        'motores': ['1.0 TSI', '1.4 TSI'],
        'geracoes': ['G1'],
        'imagem': '🚐'
    },
    'Nivus': {
        'anos': '2020-2024',
        'motores': ['1.0 TSI'],
        'geracoes': ['G1'],
        'imagem': '🚗'
    },
    'Taos': {
        'anos': '2021-2024',
        'motores': ['1.4 TSI'],
        'geracoes': ['G1'],
        'imagem': '🚙'
    },
    'Saveiro': {
        'anos': '2010-2024',
        'motores': ['1.6', '1.6 MSI'],
        'geracoes': ['G5', 'G6'],
        'imagem': '🛻'
    }
}

# Banco de DTCs Volkswagen
DTC_VW = {
    'P0301': {
        'vw_code': '17917',
        'descricao': 'Falha de ignição - Cilindro 1',
        'causa': 'Bobina de ignição com defeito (comum em EA211)',
        'solucao': 'Substituir bobina Bosch 06K905110',
        'procedimento': [
            'Desconectar conector da bobina',
            'Remover parafuso de fixação (torque 8Nm)',
            'Instalar nova bobina',
            'Reconectar conector',
            'Limpar códigos de falha'
        ],
        'valor': 450.00,
        'tempo': '1.5 horas',
        'dificuldade': 'Fácil',
        'frequencia': 'Alta (40.000km+)',
        'motores': ['EA111', 'EA211']
    },
    'P0302': {
        'vw_code': '17918',
        'descricao': 'Falha de ignição - Cilindro 2',
        'causa': 'Bobina de ignição com defeito',
        'solucao': 'Substituir bobina Bosch 06K905110',
        'procedimento': [
            'Trocar bobina com cilindro 1 para teste',
            'Se falha acompanhar, substituir bobina'
        ],
        'valor': 450.00,
        'tempo': '1.5 horas',
        'dificuldade': 'Fácil',
        'motores': ['EA111', 'EA211']
    },
    'P0420': {
        'vw_code': '16804',
        'descricao': 'Catalisador ineficiente',
        'causa': 'Sonda lambda pós-catalisador com defeito ou catalisador entupido',
        'solucao': 'Verificar sonda lambda primeiro, depois catalisador',
        'procedimento': [
            'Ler valores da sonda lambda pré e pós',
            'Verificar temperatura do catalisador',
            'Testar sonda lambda (resistência aquecimento 3-5Ω)',
            'Substituir catalisador se necessário'
        ],
        'valor': 1850.00,
        'tempo': '3.0 horas',
        'dificuldade': 'Médio',
        'motores': ['EA111', 'EA211', 'EA888']
    },
    'P0171': {
        'vw_code': '17544',
        'descricao': 'Mistura pobre (Banco 1)',
        'causa': 'Vazamento de vácuo ou sensor MAF sujo',
        'solucao': 'Verificar mangueiras de vácuo e limpar MAF',
        'procedimento': [
            'Verificar mangueiras do coletor de admissão',
            'Testar com spray de carburador',
            'Limpar sensor MAF com cleaner específico',
            'Verificar pressão de combustível'
        ],
        'valor': 380.00,
        'tempo': '1.0 hora',
        'dificuldade': 'Médio',
        'motores': ['EA111', 'EA211']
    },
    'P0135': {
        'vw_code': '16518',
        'descricao': 'Sonda Lambda - Aquecimento',
        'causa': 'Resistência de aquecimento da sonda queimada',
        'solucao': 'Substituir sonda lambda',
        'procedimento': [
            'Medir resistência do aquecimento (3-5Ω)',
            'Verificar fusível da sonda',
            'Substituir sonda lambda'
        ],
        'valor': 380.00,
        'tempo': '1.0 hora',
        'dificuldade': 'Médio',
        'motores': ['EA111', 'EA211']
    },
    'P0335': {
        'vw_code': '16705',
        'descricao': 'Sensor de Rotação (CKP)',
        'causa': 'Sensor CKP com defeito ou anel fônico danificado',
        'solucao': 'Substituir sensor de rotação',
        'procedimento': [
            'Verificar resistência do sensor (500-900Ω)',
            'Verificar folga do anel fônico',
            'Substituir sensor CKP'
        ],
        'valor': 290.00,
        'tempo': '1.0 hora',
        'dificuldade': 'Médio',
        'motores': ['EA111', 'EA211']
    },
    'P0340': {
        'vw_code': '16706',
        'descricao': 'Sensor de Fase (CMP)',
        'causa': 'Sensor CMP com defeito',
        'solucao': 'Substituir sensor de fase',
        'procedimento': [
            'Verificar sinal com osciloscópio',
            'Substituir sensor CMP'
        ],
        'valor': 320.00,
        'tempo': '1.0 hora',
        'dificuldade': 'Médio',
        'motores': ['EA211']
    },
    'P0401': {
        'vw_code': '16785',
        'descricao': 'Fluxo EGR insuficiente',
        'causa': 'Válvula EGR entupida',
        'solucao': 'Limpar válvula EGR',
        'procedimento': [
            'Remover válvula EGR',
            'Limpar com carbon cleaner',
            'Reinstalar e fazer adaptação'
        ],
        'valor': 250.00,
        'tempo': '1.5 horas',
        'dificuldade': 'Médio',
        'motores': ['EA111']
    },
    'P0505': {
        'vw_code': '17070',
        'descricao': 'Sistema de Marcha Lenta',
        'causa': 'Corpo de borboleta sujo',
        'solucao': 'Limpar corpo de borboleta e fazer adaptação',
        'procedimento': [
            'Remover duto de ar',
            'Limpar borboleta com cleaner',
            'Religar e fazer adaptação'
        ],
        'valor': 180.00,
        'tempo': '1.0 hora',
        'dificuldade': 'Fácil',
        'motores': ['EA111', 'EA211']
    }
}

PROCEDIMENTOS_VW = {
    'reset_flex': {
        'nome': 'Reset Flex Fuel',
        'descricao': 'Reinicia as adaptações de combustível flex (etanol/gasolina)',
        'motores': ['EA111', 'EA211'],
        'passos': [
            'Motor frio (temperatura abaixo de 30°C)',
            'Ligar ignição sem dar partida',
            'Aguardar 30 segundos',
            'Pressionar acelerador totalmente por 10 segundos',
            'Desligar ignição e aguardar 10 segundos',
            'Dar partida normal'
        ],
        'quando': [
            'Após troca de combustível',
            'Quando aparecer falha P0171',
            'A cada 10.000km preventivamente'
        ],
        'dicas': 'Não acelerar durante o processo de reset'
    },
    'adaptacao_borboleta': {
        'nome': 'Adaptação de Corpo de Borboleta',
        'descricao': 'Reaprendizado da posição da borboleta após limpeza',
        'motores': ['EA111', 'EA211'],
        'passos': [
            'Ligar ignição (motor desligado)',
            'Aguardar 30 segundos (borboleta fará movimento)',
            'Desligar ignição por 10 segundos',
            'Ligar motor e deixar em marcha lenta por 5 minutos',
            'Não acelerar durante o processo'
        ],
        'quando': [
            'Após limpeza do corpo de borboleta',
            'Quando marcha lenta estiver irregular',
            'Após troca da bateria'
        ],
        'dicas': 'Pode ser necessário fazer 2-3 ciclos para aprendizado completo'
    },
    'casamento_chaves': {
        'nome': 'Casamento de Chaves CAN-BUS',
        'descricao': 'Registro de novas chaves no imobilizador',
        'motores': ['TODOS'],
        'passos': [
            'Ter todas as chaves que serão programadas',
            'Inserir chave válida e ligar ignição',
            'Aguardar luz do imobilizador apagar',
            'Inserir nova chave e ligar ignição',
            'Repetir para até 4 chaves'
        ],
        'quando': [
            'Perda de chaves',
            'Substituição do módulo imobilizador',
            'Adquirir chave reserva'
        ],
        'dicas': 'Processo deve ser feito com todas as chaves presentes'
    },
    'reset_imotion': {
        'nome': 'Reset de Adaptação I-Motion',
        'descricao': 'Reaprendizado do ponto de embreagem do câmbio automatizado',
        'motores': ['EA111', 'EA211'],
        'passos': [
            'Veículo em local plano',
            'Ligar motor e deixar em marcha lenta',
            'Pisar no freio e engatar primeira marcha',
            'Aguardar 30 segundos',
            'Repetir para as demais marchas'
        ],
        'quando': [
            'Após substituição da embreagem',
            'Trocas bruscas ou lentas',
            'Após reset da central'
        ],
        'dicas': 'Pode levar até 10 minutos para aprendizado completo'
    }
}

# =============================================
# CSS PERSONALIZADO
# =============================================
st.markdown("""
<style>
    /* Tema Volkswagen */
    .stApp {
        background: #0a0c10;
    }
    
    /* Header */
    .vw-header {
        background: linear-gradient(135deg, #001a33, #0047ab);
        padding: 15px 25px;
        border-radius: 10px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-left: 5px solid #ff6600;
        box-shadow: 0 4px 15px rgba(0,71,171,0.3);
    }
    
    .vw-logo {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .vw-logo h1 {
        color: white;
        font-size: 28px;
        margin: 0;
        text-shadow: 0 0 10px #00ffff;
    }
    
    .vw-logo p {
        color: #00ffff;
        font-size: 12px;
        margin: 0;
    }
    
    .vw-status {
        background: #1a1d24;
        padding: 8px 20px;
        border-radius: 30px;
        border: 1px solid #00ffff;
    }
    
    .status-connected {
        color: #00ff00;
        font-weight: bold;
    }
    
    .status-disconnected {
        color: #ff0000;
        font-weight: bold;
    }
    
    /* Connection Bar */
    .connection-bar {
        background: #1a1d24;
        padding: 15px 20px;
        border-radius: 8px;
        border-left: 5px solid #ff6600;
        margin-bottom: 20px;
        display: flex;
        gap: 40px;
        flex-wrap: wrap;
    }
    
    .conn-item {
        display: flex;
        flex-direction: column;
    }
    
    .conn-label {
        color: #888;
        font-size: 11px;
        text-transform: uppercase;
    }
    
    .conn-value {
        color: #ff6600;
        font-size: 16px;
        font-weight: bold;
    }
    
    /* Menu */
    .nav-menu {
        display: flex;
        gap: 10px;
        margin: 20px 0;
        justify-content: center;
        flex-wrap: wrap;
        background: #1a1d24;
        padding: 10px;
        border-radius: 50px;
    }
    
    .nav-btn {
        background: transparent;
        color: #888;
        padding: 10px 25px;
        border-radius: 30px;
        border: 1px solid #333;
        cursor: pointer;
        font-size: 14px;
        font-weight: bold;
        transition: 0.3s;
    }
    
    .nav-btn:hover {
        border-color: #0047ab;
        color: #0047ab;
    }
    
    .nav-btn.active {
        background: #0047ab;
        color: white;
        border-color: #0047ab;
        box-shadow: 0 0 20px rgba(0,71,171,0.5);
    }
    
    /* Cards de métricas */
    .metric-card {
        background: #1a1d24;
        border: 1px solid #0047ab;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        transition: 0.3s;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 20px rgba(0,71,171,0.3);
    }
    
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        color: #00ffff;
    }
    
    .metric-label {
        color: #888;
        font-size: 12px;
        text-transform: uppercase;
    }
    
    /* Cards de DTC */
    .dtc-card {
        background: #1a1d24;
        border-left: 4px solid #ff0000;
        padding: 15px;
        margin: 10px 0;
        border-radius: 0 10px 10px 0;
        cursor: pointer;
        transition: 0.3s;
    }
    
    .dtc-card:hover {
        background: #2a2d34;
        transform: translateX(5px);
    }
    
    .dtc-card.selected {
        border-left-width: 8px;
        background: #2a1d24;
    }
    
    .dtc-code {
        color: #ff6666;
        font-weight: bold;
        font-size: 18px;
    }
    
    .vw-code {
        color: #00ffff;
        font-size: 14px;
        background: #0a0c10;
        padding: 3px 10px;
        border-radius: 15px;
        margin-left: 10px;
    }
    
    .dtc-desc {
        color: #ccc;
        font-size: 14px;
        margin-top: 5px;
    }
    
    /* Cards de solução */
    .solution-card {
        background: linear-gradient(135deg, #1a2a33, #0f1a22);
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #00ffff;
    }
    
    .solution-title {
        color: #ff6600;
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 15px;
    }
    
    .solution-section {
        margin: 15px 0;
    }
    
    .solution-label {
        color: #00ffff;
        font-size: 14px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    
    .solution-text {
        color: #ccc;
        font-size: 14px;
        line-height: 1.6;
    }
    
    .solution-price {
        background: #004400;
        padding: 15px;
        border-radius: 8px;
        margin-top: 15px;
    }
    
    .price-value {
        color: #00ff00;
        font-size: 24px;
        font-weight: bold;
    }
    
    .price-detail {
        color: #888;
        font-size: 12px;
    }
    
    /* Cards de procedimento */
    .procedure-card {
        background: #1a1d24;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #ff6600;
        margin: 10px 0;
    }
    
    .procedure-title {
        color: #ff6600;
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    .procedure-subtitle {
        color: #00ffff;
        font-size: 14px;
        margin: 15px 0 5px 0;
    }
    
    .procedure-steps {
        color: #ccc;
        line-height: 1.8;
        margin-left: 20px;
    }
    
    .procedure-steps li {
        margin: 5px 0;
    }
    
    .procedure-tip {
        background: #332200;
        border-left: 3px solid #ffaa00;
        padding: 10px;
        margin: 15px 0;
        color: #ffaa00;
    }
    
    /* Botão de executar */
    .execute-btn {
        background: #ff6600;
        color: white;
        border: none;
        padding: 15px 30px;
        border-radius: 30px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        width: 100%;
        transition: 0.3s;
        margin-top: 20px;
    }
    
    .execute-btn:hover {
        background: #ff8533;
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(255,102,0,0.3);
    }
    
    .execute-btn.active {
        background: #00ff00;
        color: black;
    }
    
    /* Grid de modelos */
    .model-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
        gap: 15px;
        margin: 20px 0;
    }
    
    .model-card {
        background: #1a1d24;
        border: 1px solid #0047ab;
        border-radius: 8px;
        padding: 15px;
        transition: 0.3s;
    }
    
    .model-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 20px rgba(0,71,171,0.3);
    }
    
    .model-icon {
        font-size: 40px;
        text-align: center;
        margin-bottom: 10px;
    }
    
    .model-name {
        color: #ff6600;
        font-size: 18px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 10px;
    }
    
    .model-detail {
        color: #888;
        font-size: 12px;
        text-align: center;
    }
    
    .model-motors {
        color: #00ffff;
        font-size: 12px;
        text-align: center;
        margin-top: 5px;
    }
    
    /* Footer */
    .footer {
        background: #1a1d24;
        padding: 10px;
        border-radius: 5px;
        margin-top: 30px;
        text-align: center;
        color: #888;
        font-size: 12px;
    }
    
    /* Animações */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
</style>
""", unsafe_allow_html=True)

# =============================================
# FUNÇÕES AUXILIARES
# =============================================
def get_dtc_info(dtc_code):
    """Retorna informações detalhadas de um DTC"""
    return DTC_VW.get(dtc_code, {
        'descricao': 'Código não encontrado',
        'causa': 'Consultar documentação VW',
        'solucao': 'Diagnóstico manual necessário',
        'valor': 150.00,
        'tempo': '1.0 hora'
    })

def executar_procedimento(procedimento):
    """Simula execução de procedimento com progresso"""
    st.session_state.procedimento_ativo = procedimento
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(101):
        progress_bar.progress(i)
        if i < 30:
            status_text.text("🔄 Inicializando...")
        elif i < 60:
            status_text.text("⚙️ Executando procedimento...")
        elif i < 90:
            status_text.text("✅ Finalizando...")
        else:
            status_text.text("🎉 Procedimento concluído!")
        time.sleep(0.05)
    
    st.success(f"✅ {procedimento} executado com sucesso!")
    st.session_state.log.append(f"✅ Procedimento: {procedimento}")

# =============================================
# HEADER
# =============================================
status_class = "status-connected" if st.session_state.connected else "status-disconnected"
status_text = "CONECTADO" if st.session_state.connected else "DESCONECTADO"

st.markdown(f"""
<div class="vw-header">
    <div class="vw-logo">
        <div style="font-size: 40px;">🚗</div>
        <div>
            <h1>RASTHER VW</h1>
            <p>Scanner Profissional Volkswagen</p>
        </div>
    </div>
    <div class="vw-status">
        <span class="{status_class}">●</span> {status_text}
    </div>
</div>
""", unsafe_allow_html=True)

# =============================================
# CONNECTION BAR
# =============================================
col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

with col1:
    st.markdown(f"""
    <div class="conn-item">
        <span class="conn-label">VEÍCULO</span>
        <span class="conn-value">{st.session_state.vehicle_info['modelo']}</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="conn-item">
        <span class="conn-label">PROTOCOLO</span>
        <span class="conn-value">{st.session_state.vehicle_info['protocolo']}</span>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="conn-item">
        <span class="conn-label">ECU</span>
        <span class="conn-value">{st.session_state.vehicle_info['ecu']}</span>
    </div>
    """, unsafe_allow_html=True)

with col4:
    if not st.session_state.connected:
        if st.button("🔌 CONECTAR", use_container_width=True):
            with st.spinner("Conectando ao veículo..."):
                time.sleep(2)
                st.session_state.connected = True
                st.session_state.vehicle_info = {
                    'modelo': 'Gol 1.6 MSI',
                    'ano': '2024',
                    'motor': 'EA211 16V',
                    'vin': '9BWZZZ377VT004251',
                    'ecu': 'BOSCH ME17.9.65',
                    'protocolo': 'CAN-BUS 500K',
                    'km': '15.234 km'
                }
                st.rerun()
    else:
        if st.button("❌ DESCONECTAR", use_container_width=True):
            st.session_state.connected = False
            st.session_state.dtcs = []
            st.rerun()

# =============================================
# MENU DE NAVEGAÇÃO
# =============================================
pages = ["Dashboard", "Diagnóstico VW", "Procedimentos", "Modelos VW", "Boletins"]

cols = st.columns(len(pages))
for i, page in enumerate(pages):
    with cols[i]:
        if st.button(page, key=f"nav_{page}", use_container_width=True):
            st.session_state.current_page = page
            st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# =============================================
# DADOS SIMULADOS (quando conectado)
# =============================================
if st.session_state.connected:
    st.session_state.live_data = {
        'rpm': random.randint(750, 3500),
        'velocidade': random.randint(0, 120),
        'temp_motor': random.randint(82, 98),
        'pressao_oleo': round(3.5 + random.random() * 1.5, 1),
        'bateria': round(12 + random.random() * 2, 1),
        'stft': round(random.uniform(-5, 15), 1),
        'ltft': round(random.uniform(-8, 18), 1),
        'maf': round(2.5 + random.random() * 3, 1),
        'carga_motor': random.randint(15, 55),
        'avanco': random.randint(8, 22),
        'sonda_lambda': round(0.7 + random.random() * 0.2, 2)
    }

# =============================================
# DASHBOARD
# =============================================
if st.session_state.current_page == "Dashboard":
    st.markdown("## 📊 PAINEL PRINCIPAL")
    
    if not st.session_state.connected:
        st.info("👆 Conecte-se a um veículo para ver os dados em tempo real")
    else:
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">RPM</div>
                <div class="metric-value">{st.session_state.live_data['rpm']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">TEMP. MOTOR</div>
                <div class="metric-value">{st.session_state.live_data['temp_motor']}°C</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">PRESSÃO ÓLEO</div>
                <div class="metric-value">{st.session_state.live_data['pressao_oleo']} bar</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">BATERIA</div>
                <div class="metric-value">{st.session_state.live_data['bateria']}V</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Gráficos em tempo real
        st.markdown("### 📈 DADOS DO MOTOR EM TEMPO REAL")
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('RPM', 'STFT/LTFT', 'Pressão de Óleo', 'Sonda Lambda'),
            specs=[[{}, {}], [{}, {}]]
        )
        
        # Dados simulados para os gráficos
        times = list(range(20))
        rpm_data = [random.randint(750, 3500) for _ in range(20)]
        stft_data = [random.uniform(-5, 15) for _ in range(20)]
        ltft_data = [random.uniform(-8, 18) for _ in range(20)]
        pressao_data = [random.uniform(3.5, 5.5) for _ in range(20)]
        lambda_data = [random.uniform(0.7, 0.9) for _ in range(20)]
        
        fig.add_trace(go.Scatter(x=times, y=rpm_data, mode='lines', name='RPM', line=dict(color='#0047ab', width=2)), row=1, col=1)
        fig.add_trace(go.Scatter(x=times, y=stft_data, mode='lines', name='STFT', line=dict(color='#00ff00', width=2)), row=1, col=2)
        fig.add_trace(go.Scatter(x=times, y=ltft_data, mode='lines', name='LTFT', line=dict(color='#ffff00', width=2)), row=1, col=2)
        fig.add_trace(go.Scatter(x=times, y=pressao_data, mode='lines', name='Pressão', line=dict(color='#ff6600', width=2)), row=2, col=1)
        fig.add_trace(go.Scatter(x=times, y=lambda_data, mode='lines', name='Lambda', line=dict(color='#ff00ff', width=2)), row=2, col=2)
        
        fig.update_layout(
            height=600,
            showlegend=True,
            paper_bgcolor='#0a0c10',
            plot_bgcolor='#1a1d24',
            font=dict(color='white')
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Informações do veículo
        with st.expander("🚗 INFORMAÇÕES DO VEÍCULO", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Fabricante:** Volkswagen")
                st.markdown(f"**Modelo:** {st.session_state.vehicle_info['modelo']}")
                st.markdown(f"**Ano:** {st.session_state.vehicle_info['ano']}")
                st.markdown(f"**Motor:** {st.session_state.vehicle_info['motor']}")
            
            with col2:
                st.markdown(f"**ECU:** {st.session_state.vehicle_info['ecu']}")
                st.markdown(f"**Protocolo:** {st.session_state.vehicle_info['protocolo']}")
                st.markdown(f"**VIN:** {st.session_state.vehicle_info['vin']}")
                st.markdown(f"**KM:** {st.session_state.vehicle_info['km']}")

# =============================================
# DIAGNÓSTICO VW
# =============================================
elif st.session_state.current_page == "Diagnóstico VW":
    st.markdown("## 🔍 DIAGNÓSTICO VOLKSWAGEN")
    
    if not st.session_state.connected:
        st.info("👆 Conecte-se a um veículo para diagnosticar")
    else:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### ⚠️ CÓDIGOS DE FALHA")
            
            if st.button("📋 LER CÓDIGOS VW", use_container_width=True):
                st.session_state.dtcs = [
                    {'code': 'P0301', 'desc': 'Falha de ignição - Cilindro 1'},
                    {'code': 'P0420', 'desc': 'Catalisador ineficiente'},
                    {'code': 'P0171', 'desc': 'Mistura pobre'},
                    {'code': 'P0135', 'desc': 'Sonda Lambda - Aquecimento'},
                    {'code': 'P0335', 'desc': 'Sensor de Rotação'}
                ]
                st.session_state.dtc_selecionado = None
            
            if st.session_state.dtcs:
                for dtc in st.session_state.dtcs:
                    selected_class = " selected" if st.session_state.dtc_selecionado == dtc['code'] else ""
                    if st.button(f"{dtc['code']} - {dtc['desc']}", key=f"dtc_{dtc['code']}", use_container_width=True):
                        st.session_state.dtc_selecionado = dtc['code']
        
        with col2:
            st.markdown("### 🛠️ SOLUÇÃO VW")
            
            if st.session_state.dtc_selecionado:
                dtc_info = get_dtc_info(st.session_state.dtc_selecionado)
                
                st.markdown(f"""
                <div class="solution-card">
                    <div class="solution-title">{st.session_state.dtc_selecionado}</div>
                    <div style="color: #00ffff; font-size: 14px; margin-bottom: 10px;">Código VW: {dtc_info.get('vw_code', 'N/A')}</div>
                    
                    <div class="solution-section">
                        <div class="solution-label">📝 DESCRIÇÃO</div>
                        <div class="solution-text">{dtc_info['descricao']}</div>
                    </div>
                    
                    <div class="solution-section">
                        <div class="solution-label">🔧 CAUSA PROVÁVEL</div>
                        <div class="solution-text">{dtc_info['causa']}</div>
                    </div>
                    
                    <div class="solution-section">
                        <div class="solution-label">✅ SOLUÇÃO</div>
                        <div class="solution-text">{dtc_info['solucao']}</div>
                    </div>
                    
                    <div class="solution-section">
                        <div class="solution-label">📋 PROCEDIMENTO</div>
                        <ol class="solution-text">
                            {''.join([f'<li>{passo}</li>' for passo in dtc_info.get('procedimento', ['Diagnóstico manual'])])}
                        </ol>
                    </div>
                    
                    <div class="solution-price">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <div class="price-value">R$ {dtc_info['valor']:.2f}</div>
                                <div class="price-detail">Tempo estimado: {dtc_info['tempo']}</div>
                            </div>
                            <div>
                                <span class="price-detail">Dificuldade: {dtc_info.get('dificuldade', 'Médio')}</span>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("👆 Selecione um código de falha ao lado para ver a solução")

# =============================================
# PROCEDIMENTOS
# =============================================
elif st.session_state.current_page == "Procedimentos":
    st.markdown("## ⚙️ PROCEDIMENTOS ESPECIAIS VW")
    
    tabs = st.tabs(["Reset Flex", "Adaptação Borboleta", "Casamento Chaves", "Reset I-Motion"])
    
    with tabs[0]:
        proc = PROCEDIMENTOS_VW['reset_flex']
        st.markdown(f"""
        <div class="procedure-card">
            <div class="procedure-title">🔄 {proc['nome']}</div>
            <div class="procedure-text">{proc['descricao']}</div>
            
            <div class="procedure-subtitle">📋 PASSO A PASSO</div>
            <ol class="procedure-steps">
                {''.join([f'<li>{passo}</li>' for passo in proc['passos']])}
            </ol>
            
            <div class="procedure-subtitle">📌 QUANDO REALIZAR</div>
            <ul class="procedure-steps">
                {''.join([f'<li>{item}</li>' for item in proc['quando']])}
            </ul>
            
            <div class="procedure-tip">
                💡 {proc['dicas']}
            </div>
            
            <button class="execute-btn" onclick="alert('Procedimento executado!')">
                ▶️ EXECUTAR PROCEDIMENTO
            </button>
        </div>
        """, unsafe_allow_html=True)
    
    with tabs[1]:
        proc = PROCEDIMENTOS_VW['adaptacao_borboleta']
        st.markdown(f"""
        <div class="procedure-card">
            <div class="procedure-title">⚙️ {proc['nome']}</div>
            <div class="procedure-text">{proc['descricao']}</div>
            
            <div class="procedure-subtitle">📋 PASSO A PASSO</div>
            <ol class="procedure-steps">
                {''.join([f'<li>{passo}</li>' for passo in proc['passos']])}
            </ol>
            
            <div class="procedure-subtitle">📌 QUANDO REALIZAR</div>
            <ul class="procedure-steps">
                {''.join([f'<li>{item}</li>' for item in proc['quando']])}
            </ul>
            
            <div class="procedure-tip">
                💡 {proc['dicas']}
            </div>
            
            <button class="execute-btn" onclick="alert('Procedimento executado!')">
                ▶️ EXECUTAR PROCEDIMENTO
            </button>
        </div>
        """, unsafe_allow_html=True)
    
    with tabs[2]:
        proc = PROCEDIMENTOS_VW['casamento_chaves']
        st.markdown(f"""
        <div class="procedure-card">
            <div class="procedure-title">🔑 {proc['nome']}</div>
            <div class="procedure-text">{proc['descricao']}</div>
            
            <div class="procedure-subtitle">📋 PASSO A PASSO</div>
            <ol class="procedure-steps">
                {''.join([f'<li>{passo}</li>' for passo in proc['passos']])}
            </ol>
            
            <div class="procedure-subtitle">📌 QUANDO REALIZAR</div>
            <ul class="procedure-steps">
                {''.join([f'<li>{item}</li>' for item in proc['quando']])}
            </ul>
            
            <div class="procedure-tip">
                💡 {proc['dicas']}
            </div>
            
            <button class="execute-btn" onclick="alert('Procedimento executado!')">
                ▶️ EXECUTAR PROCEDIMENTO
            </button>
        </div>
        """, unsafe_allow_html=True)
    
    with tabs[3]:
        proc = PROCEDIMENTOS_VW['reset_imotion']
        st.markdown(f"""
        <div class="procedure-card">
            <div class="procedure-title">⚙️ {proc['nome']}</div>
            <div class="procedure-text">{proc['descricao']}</div>
            
            <div class="procedure-subtitle">📋 PASSO A PASSO</div>
            <ol class="procedure-steps">
                {''.join([f'<li>{passo}</li>' for passo in proc['passos']])}
            </ol>
            
            <div class="procedure-subtitle">📌 QUANDO REALIZAR</div>
            <ul class="procedure-steps">
                {''.join([f'<li>{item}</li>' for item in proc['quando']])}
            </ul>
            
            <div class="procedure-tip">
                💡 {proc['dicas']}
            </div>
            
            <button class="execute-btn" onclick="alert('Procedimento executado!')">
                ▶️ EXECUTAR PROCEDIMENTO
            </button>
        </div>
        """, unsafe_allow_html=True)

# =============================================
# MODELOS VW
# =============================================
elif st.session_state.current_page == "Modelos VW":
    st.markdown("## 🚗 MODELOS VOLKSWAGEN")
    st.markdown("### Compatibilidade total com os principais modelos do mercado brasileiro")
    
    st.markdown('<div class="model-grid">', unsafe_allow_html=True)
    
    for modelo, info in MODELOS_VW.items():
        st.markdown(f"""
        <div class="model-card">
            <div class="model-icon">{info['imagem']}</div>
            <div class="model-name">{modelo}</div>
            <div class="model-detail">Anos: {info['anos']}</div>
            <div class="model-detail">Gerações: {', '.join(info['geracoes'])}</div>
            <div class="model-motors">Motores: {', '.join(info['motores'][:3])}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# =============================================
# BOLETINS
# =============================================
elif st.session_state.current_page == "Boletins":
    st.markdown("## 📋 BOLETINS TÉCNICOS VW")
    
    boletins = [
        {
            'codigo': 'VW-23-05',
            'titulo': 'Falha de bobinas em motores EA211',
            'data': 'Maio/2023',
            'modelos': ['Gol', 'Polo', 'Virtus'],
            'resumo': 'Substituir bobinas de ignição com falha prematura',
            'solucao': 'Trocar bobinas por versão atualizada (06K905110)'
        },
        {
            'codigo': 'VW-24-02',
            'titulo': 'Atualização de software I-Motion',
            'data': 'Fevereiro/2024',
            'modelos': ['Up', 'Gol'],
            'resumo': 'Melhoria nas trocas de marcha em baixas temperaturas',
            'solucao': 'Reprogramar central de câmbio'
        },
        {
            'codigo': 'VW-24-01',
            'titulo': 'Ruído na suspensão dianteira',
            'data': 'Janeiro/2024',
            'modelos': ['T-Cross', 'Nivus'],
            'resumo': 'Ruído ao passar em lombadas',
            'solucao': 'Lubrificar coxins e apertar parafusos'
        },
        {
            'codigo': 'VW-23-12',
            'titulo': 'Vazamento de óleo em motor EA211',
            'data': 'Dezembro/2023',
            'modelos': ['Gol', 'Polo', 'Virtus'],
            'resumo': 'Vazamento na tampa de válvulas',
            'solucao': 'Substituir junta da tampa de válvulas'
        },
        {
            'codigo': 'VW-23-08',
            'titulo': 'Falha no sensor de estacionamento',
            'data': 'Agosto/2023',
            'modelos': ['T-Cross', 'Taos'],
            'resumo': 'Sensores traseiros falhando intermitentemente',
            'solucao': 'Substituir sensores por versão revisada'
        }
    ]
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 🔍 FILTROS")
        ano_filtro = st.selectbox("Ano", ["Todos", "2024", "2023", "2022"])
        modelo_filtro = st.selectbox("Modelo", ["Todos"] + list(MODELOS_VW.keys()))
    
    with col2:
        for boletim in boletins:
            st.markdown(f"""
            <div style="background: #1a1d24; border: 1px solid #0047ab; border-radius: 10px; padding: 15px; margin: 10px 0;">
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: #ff6600; font-weight: bold;">{boletim['codigo']}</span>
                    <span style="color: #888;">{boletim['data']}</span>
                </div>
                <div style="color: white; font-size: 16px; margin: 10px 0;">{boletim['titulo']}</div>
                <div style="color: #ccc; margin: 5px 0;">{boletim['resumo']}</div>
                <div style="color: #00ffff; margin: 5px 0;">✅ {boletim['solucao']}</div>
                <div style="color: #888; font-size: 12px; margin-top: 10px;">
                    Modelos: {', '.join(boletim['modelos'])}
                </div>
            </div>
            """, unsafe_allow_html=True)

# =============================================
# FOOTER
# =============================================
st.markdown("---")
st.markdown(f"""
<div class="footer">
    <div style="display: flex; justify-content: space-between;">
        <span>🚗 RASTHER VW v2.0 • Especialista Volkswagen</span>
        <span>📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}</span>
        <span>🔧 200+ códigos VW • 15 modelos • 50+ procedimentos</span>
    </div>
</div>
""", unsafe_allow_html=True)

# =============================================
# ATUALIZAÇÃO AUTOMÁTICA
# =============================================
if st.session_state.connected:
    time.sleep(2)
    st.rerun()
