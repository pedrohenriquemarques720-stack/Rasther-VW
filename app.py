# app.py - RASTHER VW - Scanner Profissional Volkswagen
# Versão DEFINITIVA - Todos os erros corrigidos

import streamlit as st
import pandas as pd
import numpy as np
import time
import random
from datetime import datetime

# =============================================
# VERIFICAÇÃO CRÍTICA DO PLOTLY
# =============================================
try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("⚠️ Plotly não disponível - gráficos desativados. Execute: pip install plotly==5.18.0")

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
    st.session_state.real_mode = False
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
    st.session_state.dtc_selecionado = None
    st.session_state.obd_connection = None

# =============================================
# BANCO DE DADOS VOLKSWAGEN EXPANDIDO
# =============================================

MODELOS_VW = {
    'Gol': {
        'anos': '2008-2024',
        'motores': ['1.0 8V', '1.6 8V', '1.0 TSI', '1.6 MSI'],
        'geracoes': ['G4', 'G5', 'G6', 'G7'],
        'imagem': '🚗',
        'codigos': ['G5', 'G6', 'G7']
    },
    'Polo': {
        'anos': '2017-2024',
        'motores': ['1.0 TSI', '1.6 MSI', '200 TSI'],
        'geracoes': ['G6', 'G7'],
        'imagem': '🚘',
        'codigos': ['AW', 'BZ']
    },
    'Virtus': {
        'anos': '2018-2024',
        'motores': ['1.0 TSI', '1.6 MSI'],
        'geracoes': ['G1', 'G2'],
        'imagem': '🚙',
        'codigos': ['A8']
    },
    'T-Cross': {
        'anos': '2019-2024',
        'motores': ['1.0 TSI', '1.4 TSI'],
        'geracoes': ['G1'],
        'imagem': '🚐',
        'codigos': ['A11']
    },
    'Nivus': {
        'anos': '2020-2024',
        'motores': ['1.0 TSI'],
        'geracoes': ['G1'],
        'imagem': '🚗',
        'codigos': ['A12']
    },
    'Taos': {
        'anos': '2021-2024',
        'motores': ['1.4 TSI'],
        'geracoes': ['G1'],
        'imagem': '🚙',
        'codigos': ['A13']
    },
    'Saveiro': {
        'anos': '2010-2024',
        'motores': ['1.6', '1.6 MSI'],
        'geracoes': ['G5', 'G6'],
        'imagem': '🛻',
        'codigos': ['LS']
    },
    'Amarok': {
        'anos': '2010-2024',
        'motores': ['2.0 TDI', '3.0 V6'],
        'geracoes': ['G1'],
        'imagem': '🛻',
        'codigos': ['2H']
    },
    'Jetta': {
        'anos': '2011-2024',
        'motores': ['1.4 TSI', '2.0 TSI', 'GLI'],
        'geracoes': ['G6', 'G7'],
        'imagem': '🚘',
        'codigos': ['162']
    },
    'Tiguan': {
        'anos': '2012-2024',
        'motores': ['2.0 TSI'],
        'geracoes': ['G1', 'G2'],
        'imagem': '🚙',
        'codigos': ['5N']
    }
}

DTC_VW = {
    'P0300': {
        'vw_code': '17916',
        'descricao': 'Falha de ignição aleatória',
        'causa': 'Múltiplas falhas de ignição - geralmente bobinas ou velas',
        'solucao': 'Verificar sistema de ignição completo',
        'procedimento': [
            'Ler contagem de falhas por cilindro',
            'Testar bobinas com multímetro',
            'Verificar velas de ignição',
            'Trocar bobinas com problema'
        ],
        'valor': 600.00,
        'tempo': '2.0 horas',
        'dificuldade': 'Médio'
    },
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
        'dificuldade': 'Fácil'
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
        'dificuldade': 'Fácil'
    },
    'P0303': {
        'vw_code': '17919',
        'descricao': 'Falha de ignição - Cilindro 3',
        'causa': 'Bobina de ignição com defeito',
        'solucao': 'Substituir bobina',
        'valor': 450.00,
        'tempo': '1.5 horas',
        'dificuldade': 'Fácil'
    },
    'P0304': {
        'vw_code': '17920',
        'descricao': 'Falha de ignição - Cilindro 4',
        'causa': 'Bobina de ignição com defeito',
        'solucao': 'Substituir bobina',
        'valor': 450.00,
        'tempo': '1.5 horas',
        'dificuldade': 'Fácil'
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
        'dificuldade': 'Médio'
    },
    'P0430': {
        'vw_code': '16814',
        'descricao': 'Catalisador ineficiente - Banco 2',
        'causa': 'Catalisador ou sonda lambda com defeito',
        'solucao': 'Diagnóstico similar ao P0420',
        'valor': 1850.00,
        'tempo': '3.0 horas',
        'dificuldade': 'Médio'
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
        'dificuldade': 'Médio'
    },
    'P0172': {
        'vw_code': '17536',
        'descricao': 'Mistura rica (Banco 1)',
        'causa': 'Injetores com defeito ou pressão de combustível alta',
        'solucao': 'Verificar injetores e pressão de combustível',
        'valor': 450.00,
        'tempo': '2.0 horas',
        'dificuldade': 'Médio'
    },
    'P0130': {
        'vw_code': '16514',
        'descricao': 'Sonda Lambda - Circuito',
        'causa': 'Sonda lambda com defeito ou fiação danificada',
        'solucao': 'Verificar sonda e fiação',
        'valor': 380.00,
        'tempo': '1.0 hora',
        'dificuldade': 'Médio'
    },
    'P0135': {
        'vw_code': '16519',
        'descricao': 'Sonda Lambda - Aquecimento',
        'causa': 'Resistência de aquecimento queimada',
        'solucao': 'Substituir sonda lambda',
        'valor': 380.00,
        'tempo': '1.0 hora',
        'dificuldade': 'Médio'
    },
    'P0321': {
        'vw_code': '16711',
        'descricao': 'Sensor de Rotação - Sinal',
        'causa': 'Sensor CKP com defeito',
        'solucao': 'Substituir sensor de rotação',
        'valor': 290.00,
        'tempo': '1.0 hora',
        'dificuldade': 'Médio'
    },
    'P0335': {
        'vw_code': '16705',
        'descricao': 'Sensor de Rotação - Circuito',
        'causa': 'Sensor CKP com defeito ou anel fônico danificado',
        'solucao': 'Substituir sensor de rotação',
        'procedimento': [
            'Verificar resistência do sensor (500-900Ω)',
            'Verificar folga do anel fônico',
            'Substituir sensor CKP'
        ],
        'valor': 290.00,
        'tempo': '1.0 hora',
        'dificuldade': 'Médio'
    },
    'P0340': {
        'vw_code': '16717',
        'descricao': 'Sensor de Fase - Circuito',
        'causa': 'Sensor CMP com defeito',
        'solucao': 'Substituir sensor de fase',
        'valor': 320.00,
        'tempo': '1.0 hora',
        'dificuldade': 'Médio'
    },
    'P0401': {
        'vw_code': '16785',
        'descricao': 'EGR - Fluxo insuficiente',
        'causa': 'Válvula EGR entupida',
        'solucao': 'Limpar válvula EGR',
        'valor': 250.00,
        'tempo': '1.5 horas',
        'dificuldade': 'Médio'
    },
    'P0441': {
        'vw_code': '16825',
        'descricao': 'Sistema EVAP - Fluxo incorreto',
        'causa': 'Válvula de purga com defeito',
        'solucao': 'Substituir válvula de purga',
        'valor': 280.00,
        'tempo': '1.0 hora',
        'dificuldade': 'Fácil'
    },
    'P0442': {
        'vw_code': '16826',
        'descricao': 'EVAP - Vazamento pequeno',
        'causa': 'Tampa do combustível mal fechada',
        'solucao': 'Verificar tampa do combustível',
        'valor': 50.00,
        'tempo': '0.2 hora',
        'dificuldade': 'Fácil'
    },
    'P0455': {
        'vw_code': '16839',
        'descricao': 'EVAP - Vazamento grande',
        'causa': 'Mangueiras soltas ou danificadas',
        'solucao': 'Verificar mangueiras do sistema',
        'valor': 180.00,
        'tempo': '1.0 hora',
        'dificuldade': 'Fácil'
    },
    'P0501': {
        'vw_code': '17069',
        'descricao': 'Sensor de Velocidade - Circuito',
        'causa': 'Sensor VSS com defeito',
        'solucao': 'Substituir sensor de velocidade',
        'valor': 220.00,
        'tempo': '1.0 hora',
        'dificuldade': 'Médio'
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
        'dificuldade': 'Fácil'
    },
    'P0506': {
        'vw_code': '17071',
        'descricao': 'Marcha Lenta baixa',
        'causa': 'Corpo de borboleta sujo',
        'solucao': 'Limpar corpo de borboleta',
        'valor': 180.00,
        'tempo': '1.0 hora',
        'dificuldade': 'Fácil'
    },
    'P0507': {
        'vw_code': '17072',
        'descricao': 'Marcha Lenta alta',
        'causa': 'Vazamento de vácuo',
        'solucao': 'Verificar mangueiras de vácuo',
        'valor': 150.00,
        'tempo': '1.0 hora',
        'dificuldade': 'Médio'
    },
    'P0600': {
        'vw_code': '16890',
        'descricao': 'Falha de comunicação serial',
        'causa': 'Problema na rede CAN',
        'solucao': 'Verificar terminações CAN',
        'valor': 380.00,
        'tempo': '2.0 horas',
        'dificuldade': 'Difícil'
    }
}

PROCEDIMENTOS_VW = {
    'reset_flex': {
        'nome': '🔄 Reset Flex Fuel',
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
        'nome': '⚙️ Adaptação de Corpo de Borboleta',
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
        'nome': '🔑 Casamento de Chaves CAN-BUS',
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
        'nome': '⚙️ Reset de Adaptação I-Motion',
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
    },
    'reset_abs': {
        'nome': '🛑 Sangria e Reset ABS',
        'descricao': 'Procedimento para sangria do sistema ABS',
        'motores': ['TODOS'],
        'passos': [
            'Conectar scanner ao veículo',
            'Acessar módulo ABS',
            'Selecionar função "Sangria"',
            'Seguir instruções na tela',
            'Testar sistema após conclusão'
        ],
        'quando': [
            'Após troca de fluido de freio',
            'Entrada de ar no sistema',
            'Substituição de componentes do ABS'
        ],
        'dicas': 'Necessário scanner com função específica'
    }
}

# =============================================
# CSS PERSONALIZADO
# =============================================
st.markdown("""
<style>
    /* Tema Volkswagen profissional */
    .stApp {
        background: #0a0c10;
    }
    
    /* Header */
    .vw-header {
        background: linear-gradient(135deg, #001a33, #0047ab);
        padding: 20px 30px;
        border-radius: 12px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-left: 6px solid #ff6600;
        box-shadow: 0 4px 20px rgba(0,71,171,0.3);
    }
    
    .vw-logo {
        display: flex;
        align-items: center;
        gap: 20px;
    }
    
    .vw-logo h1 {
        color: white;
        font-size: 32px;
        margin: 0;
        text-shadow: 0 0 10px #00ffff;
    }
    
    .vw-logo p {
        color: #00ffff;
        font-size: 14px;
        margin: 0;
        letter-spacing: 1px;
    }
    
    .vw-status {
        background: #1a1d24;
        padding: 10px 25px;
        border-radius: 40px;
        border: 2px solid #00ffff;
        font-weight: bold;
    }
    
    .status-connected { color: #00ff00; }
    .status-disconnected { color: #ff0000; }
    
    /* Connection Bar */
    .connection-bar {
        background: #1a1d24;
        padding: 15px 20px;
        border-radius: 10px;
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
        letter-spacing: 1px;
    }
    
    .conn-value {
        color: #ff6600;
        font-size: 16px;
        font-weight: bold;
        font-family: monospace;
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
        padding: 12px 25px;
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
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        transition: 0.3s;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 20px rgba(0,71,171,0.3);
    }
    
    .metric-value {
        font-size: 36px;
        font-weight: bold;
        color: #00ffff;
        font-family: monospace;
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
    
    /* Cards de solução */
    .solution-card {
        background: linear-gradient(135deg, #1a2a33, #0f1a22);
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #00ffff;
    }
    
    .solution-title {
        color: #ff6600;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px;
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
    
    .solution-price {
        background: #004400;
        padding: 15px;
        border-radius: 8px;
        margin-top: 15px;
    }
    
    .price-value {
        color: #00ff00;
        font-size: 28px;
        font-weight: bold;
    }
    
    /* Cards de procedimento */
    .procedure-card {
        background: #1a1d24;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #ff6600;
        margin: 10px 0;
    }
    
    .procedure-title {
        color: #ff6600;
        font-size: 22px;
        font-weight: bold;
        margin-bottom: 15px;
    }
    
    .procedure-steps {
        background: #0a0c10;
        padding: 15px 25px;
        border-radius: 8px;
        color: #ccc;
        line-height: 1.8;
    }
    
    .procedure-tip {
        background: #332200;
        border-left: 3px solid #ffaa00;
        padding: 10px;
        margin: 15px 0;
        color: #ffaa00;
    }
    
    /* Grid de modelos */
    .model-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
        gap: 20px;
        margin: 20px 0;
    }
    
    .model-card {
        background: #1a1d24;
        border: 1px solid #0047ab;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        transition: 0.3s;
    }
    
    .model-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 20px rgba(0,71,171,0.3);
    }
    
    .model-icon {
        font-size: 48px;
        margin-bottom: 10px;
    }
    
    .model-name {
        color: #ff6600;
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    .model-detail {
        color: #888;
        font-size: 12px;
    }
    
    /* Footer */
    .footer {
        background: #1a1d24;
        padding: 15px;
        border-radius: 10px;
        margin-top: 30px;
        text-align: center;
        color: #888;
        font-size: 12px;
        border-top: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)

# =============================================
# HEADER
# =============================================
status_class = "status-connected" if st.session_state.connected else "status-disconnected"
status_text = "CONECTADO" if st.session_state.connected else "DESCONECTADO"

st.markdown(f"""
<div class="vw-header">
    <div class="vw-logo">
        <div style="font-size: 48px;">🚗</div>
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
        modo = st.radio("Modo", ["Simulação", "Real"], horizontal=True, label_visibility="collapsed")
        st.session_state.real_mode = (modo == "Real")
        
        if st.button("🔌 CONECTAR", use_container_width=True):
            with st.spinner("Conectando..."):
                time.sleep(2)
                st.session_state.connected = True
                st.session_state.vehicle_info = {
                    'modelo': 'Gol 1.6 MSI',
                    'ano': '2024',
                    'motor': 'EA211',
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
pages = ["Dashboard", "Diagnóstico VW", "Procedimentos", "Modelos VW", "Sobre"]

cols = st.columns(len(pages))
for i, page in enumerate(pages):
    with cols[i]:
        if st.button(page, key=f"nav_{page}", use_container_width=True):
            st.session_state.current_page = page
            st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# =============================================
# DADOS SIMULADOS
# =============================================
if st.session_state.connected and not st.session_state.real_mode:
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
        
        # Gráficos (se plotly disponível)
        if PLOTLY_AVAILABLE:
            st.markdown("### 📈 DADOS DO MOTOR EM TEMPO REAL")
            
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('RPM', 'STFT/LTFT', 'Pressão de Óleo', 'Sonda Lambda'),
                specs=[[{}, {}], [{}, {}]]
            )
            
            times = list(range(30))
            fig.add_trace(go.Scatter(x=times, y=[random.randint(750,3500) for _ in range(30)], 
                                    mode='lines', name='RPM', line=dict(color='#0047ab', width=2)), row=1, col=1)
            fig.add_trace(go.Scatter(x=times, y=[random.uniform(-5,15) for _ in range(30)], 
                                    mode='lines', name='STFT', line=dict(color='#00ff00', width=2)), row=1, col=2)
            fig.add_trace(go.Scatter(x=times, y=[random.uniform(-8,18) for _ in range(30)], 
                                    mode='lines', name='LTFT', line=dict(color='#ffff00', width=2)), row=1, col=2)
            fig.add_trace(go.Scatter(x=times, y=[random.uniform(3.5,5.5) for _ in range(30)], 
                                    mode='lines', name='Pressão', line=dict(color='#ff6600', width=2)), row=2, col=1)
            fig.add_trace(go.Scatter(x=times, y=[random.uniform(0.7,0.9) for _ in range(30)], 
                                    mode='lines', name='Lambda', line=dict(color='#ff00ff', width=2)), row=2, col=2)
            
            fig.update_layout(
                height=600,
                showlegend=True,
                paper_bgcolor='#0a0c10',
                plot_bgcolor='#1a1d24',
                font=dict(color='white')
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("📊 Gráficos desativados - Plotly não disponível")
        
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
                # Simular leitura de DTCs
                st.session_state.dtcs = [
                    {'code': 'P0301', 'desc': 'Falha de ignição - Cilindro 1'},
                    {'code': 'P0420', 'desc': 'Catalisador ineficiente'},
                    {'code': 'P0171', 'desc': 'Mistura pobre'},
                    {'code': 'P0335', 'desc': 'Sensor de Rotação'},
                    {'code': 'P0505', 'desc': 'Sistema Marcha Lenta'}
                ]
                st.session_state.dtc_selecionado = None
            
            if st.session_state.dtcs:
                for dtc in st.session_state.dtcs:
                    selected = "dtc-card" + (" selected" if st.session_state.dtc_selecionado == dtc['code'] else "")
                    if st.button(f"{dtc['code']} - {dtc['desc']}", key=f"dtc_{dtc['code']}", use_container_width=True):
                        st.session_state.dtc_selecionado = dtc['code']
        
        with col2:
            st.markdown("### 🛠️ SOLUÇÃO VW")
            
            if st.session_state.dtc_selecionado and st.session_state.dtc_selecionado in DTC_VW:
                info = DTC_VW[st.session_state.dtc_selecionado]
                
                st.markdown(f"""
                <div class="solution-card">
                    <div class="solution-title">{st.session_state.dtc_selecionado}</div>
                    <div style="color: #00ffff; font-size: 16px; margin-bottom: 15px;">Código VW: {info['vw_code']}</div>
                    
                    <div class="solution-section">
                        <div class="solution-label">📝 DESCRIÇÃO</div>
                        <div style="color: white;">{info['descricao']}</div>
                    </div>
                    
                    <div class="solution-section">
                        <div class="solution-label">🔧 CAUSA PROVÁVEL</div>
                        <div style="color: white;">{info['causa']}</div>
                    </div>
                    
                    <div class="solution-section">
                        <div class="solution-label">✅ SOLUÇÃO</div>
                        <div style="color: white;">{info['solucao']}</div>
                    </div>
                    
                    <div class="solution-section">
                        <div class="solution-label">📋 PROCEDIMENTO</div>
                        <ol style="color: white;">
                            {''.join([f'<li>{p}</li>' for p in info.get('procedimento', ['Diagnóstico manual'])])}
                        </ol>
                    </div>
                    
                    <div class="solution-price">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <div class="price-value">R$ {info['valor']:.2f}</div>
                                <div style="color: #888;">Tempo: {info['tempo']}</div>
                            </div>
                            <div>
                                <span style="color: #888;">Dificuldade: {info.get('dificuldade', 'Médio')}</span>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("👆 Selecione um código de falha ao lado")

# =============================================
# PROCEDIMENTOS
# =============================================
elif st.session_state.current_page == "Procedimentos":
    st.markdown("## ⚙️ PROCEDIMENTOS ESPECIAIS VW")
    
    tabs = st.tabs([p['nome'] for p in PROCEDIMENTOS_VW.values()])
    
    for i, (key, proc) in enumerate(PROCEDIMENTOS_VW.items()):
        with tabs[i]:
            st.markdown(f"""
            <div class="procedure-card">
                <div class="procedure-title">{proc['nome']}</div>
                <div style="color: #ccc; margin-bottom: 20px;">{proc['descricao']}</div>
                
                <div class="solution-label">📋 PASSO A PASSO</div>
                <div class="procedure-steps">
                    <ol>
                        {''.join([f'<li>{p}</li>' for p in proc['passos']])}
                    </ol>
                </div>
                
                <div style="margin-top: 20px;">
                    <div class="solution-label">📌 QUANDO REALIZAR</div>
                    <ul style="color: #ccc;">
                        {''.join([f'<li>{q}</li>' for q in proc['quando']])}
                    </ul>
                </div>
                
                <div class="procedure-tip">
                    💡 {proc['dicas']}
                </div>
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
            <div class="model-detail">📅 {info['anos']}</div>
            <div class="model-detail">🔧 {', '.join(info['motores'][:2])}</div>
            <div class="model-detail" style="color: #00ffff;">Código: {info['codigos'][0]}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# =============================================
# SOBRE
# =============================================
elif st.session_state.current_page == "Sobre":
    st.markdown("## ℹ️ SOBRE O RASTHER VW")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("""
        <div style="background: #1a1d24; border: 1px solid #0047ab; border-radius: 10px; padding: 20px; text-align: center;">
            <div style="font-size: 80px;">🚗</div>
            <h3 style="color: #ff6600;">RASTHER VW</h3>
            <p style="color: #00ffff;">v2.0</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        ### Scanner Profissional Volkswagen
        
        **Características:**
        - ✅ Especializado em Volkswagen (Gol, Polo, Virtus, T-Cross, etc.)
        - ✅ 20+ códigos de falha VW com soluções detalhadas
        - ✅ Procedimentos exclusivos (Reset Flex, Adaptação Borboleta)
        - ✅ Banco de dados com 10 modelos VW
        - ✅ Interface profissional tema Volkswagen
        
        **Códigos VW Suportados:**
        - 17917 (P0301) - Falha Cilindro 1
        - 16804 (P0420) - Catalisador
        - 17544 (P0171) - Mistura Pobre
        - 16705 (P0335) - Sensor Rotação
        - 17070 (P0505) - Marcha Lenta
        
        **Desenvolvido para mecânicos especializados em Volkswagen**
        """)

# =============================================
# FOOTER
# =============================================
st.markdown("---")
st.markdown(f"""
<div class="footer">
    <div style="display: flex; justify-content: space-between;">
        <span>🚗 RASTHER VW v2.0 • Especialista Volkswagen</span>
        <span>📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}</span>
        <span>🔧 {len(DTC_VW)} códigos • {len(MODELOS_VW)} modelos • {len(PROCEDIMENTOS_VW)} procedimentos</span>
    </div>
</div>
""", unsafe_allow_html=True)

# =============================================
# ATUALIZAÇÃO AUTOMÁTICA
# =============================================
if st.session_state.connected:
    time.sleep(2)
    st.rerun()
