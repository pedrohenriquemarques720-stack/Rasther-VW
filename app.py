# app.py - RASTHER VW PROFESSIONAL
# Interface profissional sem dependências externas

import streamlit as st
import pandas as pd
import numpy as np
import time
import random
from datetime import datetime

# =============================================
# CONFIGURAÇÕES DA PÁGINA
# =============================================
st.set_page_config(
    page_title="RASTHER VW PRO",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================
# INICIALIZAÇÃO DA SESSÃO
# =============================================
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.connected = False
    st.session_state.current_tab = "Dashboard"
    st.session_state.vehicle = {
        'modelo': 'Gol 1.6 MSI',
        'ano': '2024',
        'motor': 'EA211 16V',
        'vin': '9BWZZZ377VT004251',
        'km': '15.234'
    }
    st.session_state.dtcs = []
    st.session_state.selected_dtc = None
    st.session_state.live_data = {
        'rpm': 0,
        'temp': 0,
        'pressao': 0,
        'bateria': 12.5,
        'stft': 0,
        'ltft': 0,
        'maf': 0,
        'carga': 0,
        'velocidade': 0
    }

# =============================================
# CSS PROFISSIONAL (ESTILO RASTHER)
# =============================================
st.markdown("""
<style>
    /* Tema profissional automotivo */
    .stApp {
        background: #0a0c10;
    }
    
    /* Remove branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Sidebar customizada */
    .css-1d391kg {
        background-color: #1a1d24 !important;
    }
    
    /* Menu lateral profissional */
    .sidebar-menu {
        background: #1a1d24;
        padding: 20px 0;
        border-right: 2px solid #ff6600;
        height: 100vh;
    }
    
    .menu-item {
        padding: 15px 25px;
        margin: 5px 0;
        color: #888;
        cursor: pointer;
        transition: 0.3s;
        border-left: 3px solid transparent;
        font-size: 16px;
    }
    
    .menu-item:hover {
        background: #2a2d34;
        color: #00ffff;
        border-left-color: #00ffff;
    }
    
    .menu-item.active {
        background: #0047ab;
        color: white;
        border-left-color: #ff6600;
        font-weight: bold;
    }
    
    .menu-icon {
        margin-right: 15px;
        font-size: 20px;
    }
    
    /* Header principal */
    .main-header {
        background: linear-gradient(90deg, #001a33, #0047ab);
        padding: 15px 25px;
        border-radius: 12px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-left: 6px solid #ff6600;
        box-shadow: 0 4px 20px rgba(0,71,171,0.3);
    }
    
    .header-title h1 {
        color: white;
        font-size: 28px;
        margin: 0;
        font-weight: 700;
        letter-spacing: 2px;
        text-shadow: 0 0 15px #00ffff;
    }
    
    .header-title p {
        color: #00ffff;
        font-size: 12px;
        margin: 0;
    }
    
    .header-status {
        background: #0a0c10;
        padding: 10px 25px;
        border-radius: 30px;
        border: 2px solid #00ffff;
        font-family: monospace;
        font-size: 14px;
    }
    
    .status-online { color: #00ff00; font-weight: bold; }
    .status-offline { color: #ff0000; font-weight: bold; }
    
    /* Connection Bar */
    .connection-bar {
        background: #1a1d24;
        padding: 15px 25px;
        border-radius: 10px;
        margin-bottom: 25px;
        display: flex;
        gap: 40px;
        border-left: 5px solid #ff6600;
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
    
    /* Cards de métricas estilo scanner */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin: 20px 0;
    }
    
    .metric-card {
        background: #1a1d24;
        border: 2px solid #0047ab;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        transition: 0.3s;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0,71,171,0.4);
        border-color: #ff6600;
    }
    
    .metric-value {
        font-size: 42px;
        font-weight: bold;
        color: #00ffff;
        font-family: monospace;
        text-shadow: 0 0 20px #00ffff;
    }
    
    .metric-label {
        color: #888;
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-top: 10px;
    }
    
    .metric-unit {
        color: #ff6600;
        font-size: 14px;
        margin-left: 5px;
    }
    
    /* Progress bars estilo scanner */
    .progress-container {
        background: #333;
        height: 10px;
        border-radius: 5px;
        margin: 15px 0;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #00ff00, #ffff00, #ff0000);
        border-radius: 5px;
        transition: width 0.3s;
    }
    
    /* Cards de DTC */
    .dtc-card {
        background: #1a1d24;
        border-left: 5px solid #ff0000;
        padding: 20px;
        margin: 15px 0;
        border-radius: 0 15px 15px 0;
        cursor: pointer;
        transition: 0.3s;
    }
    
    .dtc-card:hover {
        background: #2a2d34;
        transform: translateX(5px);
        border-left-color: #ff6600;
    }
    
    .dtc-code {
        color: #ff6666;
        font-weight: bold;
        font-size: 22px;
        font-family: monospace;
    }
    
    .dtc-vw {
        color: #00ffff;
        font-size: 14px;
        background: #0a0c10;
        padding: 5px 15px;
        border-radius: 20px;
        margin-left: 15px;
    }
    
    .dtc-desc {
        color: #ccc;
        font-size: 16px;
        margin-top: 10px;
    }
    
    /* Solução card */
    .solution-card {
        background: #1a2a33;
        padding: 25px;
        border-radius: 15px;
        border: 2px solid #00ffff;
        margin: 15px 0;
    }
    
    .solution-title {
        color: #ff6600;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px;
        border-bottom: 2px solid #ff6600;
        padding-bottom: 10px;
    }
    
    .solution-price {
        background: #004400;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
    }
    
    .price-value {
        color: #00ff00;
        font-size: 28px;
        font-weight: bold;
    }
    
    /* Procedure cards */
    .procedure-card {
        background: #1a1d24;
        padding: 25px;
        border-radius: 15px;
        border: 2px solid #ff6600;
        margin: 15px 0;
    }
    
    .procedure-title {
        color: #ff6600;
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 15px;
    }
    
    .procedure-steps {
        background: #0a0c10;
        padding: 20px 35px;
        border-radius: 10px;
        color: white;
        line-height: 2;
    }
    
    /* Botões */
    .vw-button {
        background: linear-gradient(135deg, #0047ab, #002b5c);
        color: white;
        border: none;
        padding: 15px 30px;
        border-radius: 30px;
        font-weight: bold;
        cursor: pointer;
        width: 100%;
        margin: 10px 0;
        transition: 0.3s;
        font-size: 16px;
    }
    
    .vw-button:hover {
        background: #ff6600;
        transform: translateY(-2px);
        box-shadow: 0 5px 25px rgba(255,102,0,0.4);
    }
    
    /* Tabelas */
    .data-table {
        background: #1a1d24;
        border: 2px solid #0047ab;
        border-radius: 10px;
        padding: 15px;
        margin: 15px 0;
    }
    
    .data-table th {
        color: #00ffff;
        padding: 10px;
        text-align: left;
    }
    
    .data-table td {
        color: white;
        padding: 8px 10px;
        border-bottom: 1px solid #333;
    }
    
    /* Model cards */
    .model-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 20px;
        margin: 20px 0;
    }
    
    .model-card {
        background: #1a1d24;
        border: 2px solid #0047ab;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        transition: 0.3s;
    }
    
    .model-card:hover {
        transform: translateY(-5px);
        border-color: #ff6600;
    }
    
    .model-icon {
        font-size: 48px;
        margin-bottom: 10px;
    }
    
    .model-name {
        color: #ff6600;
        font-size: 18px;
        font-weight: bold;
    }
    
    .model-info {
        color: #888;
        font-size: 12px;
        margin-top: 5px;
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
    }
</style>
""", unsafe_allow_html=True)

# =============================================
# BANCO DE DADOS VW
# =============================================
MODELOS_VW = {
    'Gol': {'icon': '🚗', 'anos': '2008-2024', 'motores': 'EA111/EA211'},
    'Polo': {'icon': '🚘', 'anos': '2017-2024', 'motores': 'EA211'},
    'Virtus': {'icon': '🚙', 'anos': '2018-2024', 'motores': 'EA211'},
    'T-Cross': {'icon': '🚐', 'anos': '2019-2024', 'motores': 'EA211'},
    'Nivus': {'icon': '🚗', 'anos': '2020-2024', 'motores': 'EA211'},
    'Taos': {'icon': '🚙', 'anos': '2021-2024', 'motores': 'EA211'},
    'Saveiro': {'icon': '🛻', 'anos': '2010-2024', 'motores': 'EA111'},
    'Amarok': {'icon': '🛻', 'anos': '2010-2024', 'motores': 'V6 TDI'},
    'Jetta': {'icon': '🚘', 'anos': '2011-2024', 'motores': 'EA888'},
    'Tiguan': {'icon': '🚙', 'anos': '2012-2024', 'motores': 'EA888'}
}

DTC_VW = {
    'P0301': {
        'vw': '17917',
        'desc': 'Falha de ignição - Cilindro 1',
        'causa': 'Bobina EA211 com defeito',
        'solucao': 'Trocar bobina Bosch 06K905110',
        'procedimento': [
            'Desconectar conector da bobina',
            'Remover parafuso (8Nm)',
            'Instalar nova bobina',
            'Reconectar',
            'Limpar códigos'
        ],
        'valor': 450,
        'tempo': '1.5h'
    },
    'P0302': {
        'vw': '17918',
        'desc': 'Falha de ignição - Cilindro 2',
        'causa': 'Bobina com defeito',
        'solucao': 'Trocar bobina',
        'valor': 450,
        'tempo': '1.5h'
    },
    'P0420': {
        'vw': '16804',
        'desc': 'Catalisador ineficiente',
        'causa': 'Sonda lambda ou catalisador',
        'solucao': 'Verificar sonda lambda primeiro',
        'valor': 1850,
        'tempo': '3h'
    },
    'P0171': {
        'vw': '17544',
        'desc': 'Mistura pobre',
        'causa': 'Vazamento de vácuo',
        'solucao': 'Verificar mangueiras',
        'valor': 380,
        'tempo': '1h'
    },
    'P0335': {
        'vw': '16705',
        'desc': 'Sensor de rotação',
        'causa': 'Sensor CKP com defeito',
        'solucao': 'Trocar sensor',
        'valor': 290,
        'tempo': '1h'
    },
    'P0505': {
        'vw': '17070',
        'desc': 'Marcha lenta',
        'causa': 'Borboleta suja',
        'solucao': 'Limpar borboleta',
        'valor': 180,
        'tempo': '1h'
    }
}

PROCEDIMENTOS = {
    'Reset Flex Fuel': [
        'Motor frio (<30°C)',
        'Ligar ignição (sem partida)',
        'Aguardar 30 segundos',
        'Acelerador 100% por 10 segundos',
        'Desligar ignição por 10 segundos',
        'Dar partida normal'
    ],
    'Adaptação Borboleta': [
        'Ligar ignição (motor desligado)',
        'Aguardar 30 segundos',
        'Desligar por 10 segundos',
        'Ligar motor',
        'Marcha lenta por 5 minutos'
    ],
    'Casamento de Chaves': [
        'Ter todas as chaves',
        'Inserir chave válida',
        'Ligar ignição',
        'Aguardar luz imobilizador',
        'Inserir nova chave',
        'Repetir para até 4 chaves'
    ]
}

# =============================================
# SIDEBAR - MENU LATERAL PROFISSIONAL
# =============================================
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:20px;">
        <div style="font-size:60px;">🚗</div>
        <h2 style="color:#ff6600;">RASTHER VW</h2>
        <p style="color:#00ffff;">PROFESSIONAL</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Menu de navegação
    menu_options = ["Dashboard", "Diagnóstico", "Procedimentos", "Modelos", "Config"]
    menu_icons = ["📊", "🔍", "⚙️", "🚗", "⚡"]
    
    for i, (option, icon) in enumerate(zip(menu_options, menu_icons)):
        active = "active" if st.session_state.get('current_tab') == option else ""
        if st.button(f"{icon} {option}", key=f"menu_{option}", use_container_width=True):
            st.session_state.current_tab = option
            st.rerun()
    
    st.markdown("---")
    
    # Status da conexão
    if st.session_state.connected:
        st.success("🟢 VEÍCULO CONECTADO")
        st.info(f"📌 {st.session_state.vehicle['modelo']}")
    else:
        st.warning("🔴 DESCONECTADO")
    
    # Botão de conexão
    if not st.session_state.connected:
        if st.button("🔌 CONECTAR", use_container_width=True):
            st.session_state.connected = True
            st.rerun()
    else:
        if st.button("❌ DESCONECTAR", use_container_width=True):
            st.session_state.connected = False
            st.session_state.dtcs = []
            st.rerun()

# =============================================
# HEADER PRINCIPAL
# =============================================
status_class = "status-online" if st.session_state.connected else "status-offline"
status_text = "ONLINE" if st.session_state.connected else "OFFLINE"

st.markdown(f"""
<div class="main-header">
    <div class="header-title">
        <h1>RASTHER VW PRO</h1>
        <p>SCANNER VOLKSWAGEN PROFISSIONAL</p>
    </div>
    <div class="header-status">
        <span class="{status_class}">●</span> {status_text} • v2.0
    </div>
</div>
""", unsafe_allow_html=True)

# =============================================
# CONNECTION BAR
# =============================================
if st.session_state.connected:
    st.markdown(f"""
    <div class="connection-bar">
        <div class="conn-item">
            <span class="conn-label">VEÍCULO</span>
            <span class="conn-value">{st.session_state.vehicle['modelo']}</span>
        </div>
        <div class="conn-item">
            <span class="conn-label">MOTOR</span>
            <span class="conn-value">{st.session_state.vehicle['motor']}</span>
        </div>
        <div class="conn-item">
            <span class="conn-label">PROTOCOLO</span>
            <span class="conn-value">CAN 500k</span>
        </div>
        <div class="conn-item">
            <span class="conn-label">VIN</span>
            <span class="conn-value">{st.session_state.vehicle['vin'][:8]}...</span>
        </div>
        <div class="conn-item">
            <span class="conn-label">KM</span>
            <span class="conn-value">{st.session_state.vehicle['km']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =============================================
# DASHBOARD
# =============================================
if st.session_state.current_tab == "Dashboard":
    st.markdown("## 📊 PAINEL DE CONTROLE")
    
    if not st.session_state.connected:
        st.warning("⚠️ Conecte-se a um veículo para visualizar dados")
    else:
        # Gerar dados simulados
        rpm = random.randint(750, 6500)
        temp = random.randint(82, 105)
        pressao = round(3.5 + random.random() * 2, 1)
        bateria = round(12 + random.random() * 2, 1)
        stft = round(random.uniform(-10, 10), 1)
        ltft = round(random.uniform(-10, 10), 1)
        maf = round(2.5 + random.random() * 5, 1)
        carga = random.randint(15, 85)
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{rpm}</div>
                <div class="metric-label">RPM <span class="metric-unit">rpm</span></div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{temp}°C</div>
                <div class="metric-label">TEMPERATURA</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{pressao}</div>
                <div class="metric-label">PRESSÃO ÓLEO <span class="metric-unit">bar</span></div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{bateria}V</div>
                <div class="metric-label">BATERIA</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Barras de progresso estilo scanner
        st.markdown("### 📊 PARÂMETROS EM TEMPO REAL")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="data-table">
                <h4 style="color:#00ffff;">Combustível</h4>
                <div style="margin:15px 0;">
                    <div style="display:flex; justify-content:space-between;">
                        <span>STFT</span>
                        <span>{stft}%</span>
                    </div>
                    <div class="progress-container">
                        <div class="progress-fill" style="width:{stft+15}%;"></div>
                    </div>
                </div>
                <div style="margin:15px 0;">
                    <div style="display:flex; justify-content:space-between;">
                        <span>LTFT</span>
                        <span>{ltft}%</span>
                    </div>
                    <div class="progress-container">
                        <div class="progress-fill" style="width:{ltft+15}%;"></div>
                    </div>
                </div>
                <div style="margin:15px 0;">
                    <div style="display:flex; justify-content:space-between;">
                        <span>MAF</span>
                        <span>{maf} g/s</span>
                    </div>
                    <div class="progress-container">
                        <div class="progress-fill" style="width:{maf*10}%;"></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="data-table">
                <h4 style="color:#00ffff;">Motor</h4>
                <div style="margin:15px 0;">
                    <div style="display:flex; justify-content:space-between;">
                        <span>Carga Motor</span>
                        <span>{carga}%</span>
                    </div>
                    <div class="progress-container">
                        <div class="progress-fill" style="width:{carga}%;"></div>
                    </div>
                </div>
                <div style="margin:15px 0;">
                    <div style="display:flex; justify-content:space-between;">
                        <span>Temperatura</span>
                        <span>{temp}°C</span>
                    </div>
                    <div class="progress-container">
                        <div class="progress-fill" style="width:{temp}%;"></div>
                    </div>
                </div>
                <div style="margin:15px 0;">
                    <div style="display:flex; justify-content:space-between;">
                        <span>Pressão Óleo</span>
                        <span>{pressao} bar</span>
                    </div>
                    <div class="progress-container">
                        <div class="progress-fill" style="width:{pressao*20}%;"></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Tabela de parâmetros
        st.markdown("### 📋 DADOS COMPLETOS")
        
        data = {
            'Parâmetro': ['RPM', 'Velocidade', 'Temperatura', 'Pressão Óleo', 'Bateria', 'STFT', 'LTFT', 'MAF', 'Carga Motor'],
            'Valor': [rpm, f"{random.randint(0,120)} km/h", f"{temp}°C", f"{pressao} bar", f"{bateria}V", f"{stft}%", f"{ltft}%", f"{maf} g/s", f"{carga}%"],
            'Referência': ['750-6800', '0-200', '82-105', '3.5-5.5', '12-15', '±10', '±10', '2.5-8', '15-85'],
            'Status': ['✅' if 750 <= rpm <= 6800 else '⚠️' for _ in range(9)]
        }
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)

# =============================================
# DIAGNÓSTICO
# =============================================
elif st.session_state.current_tab == "Diagnóstico":
    st.markdown("## 🔍 DIAGNÓSTICO VOLKSWAGEN")
    
    if not st.session_state.connected:
        st.warning("⚠️ Conecte-se a um veículo para diagnosticar")
    else:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### ⚠️ CÓDIGOS DE FALHA")
            
            if st.button("📋 LER CÓDIGOS", use_container_width=True):
                st.session_state.dtcs = list(DTC_VW.keys())[:4]
                st.session_state.selected_dtc = None
            
            if st.button("✅ LIMPAR CÓDIGOS", use_container_width=True):
                st.session_state.dtcs = []
                st.session_state.selected_dtc = None
            
            if st.session_state.dtcs:
                for code in st.session_state.dtcs:
                    info = DTC_VW[code]
                    if st.button(f"{code} - {info['desc'][:30]}...", key=f"btn_{code}", use_container_width=True):
                        st.session_state.selected_dtc = code
        
        with col2:
            if st.session_state.selected_dtc and st.session_state.selected_dtc in DTC_VW:
                info = DTC_VW[st.session_state.selected_dtc]
                
                st.markdown(f"""
                <div class="solution-card">
                    <div class="solution-title">{st.session_state.selected_dtc}</div>
                    <p style="color:#00ffff;">Código VW: {info['vw']}</p>
                    <p><strong>Descrição:</strong> {info['desc']}</p>
                    <p><strong>Causa:</strong> {info['causa']}</p>
                    <p><strong>Solução:</strong> {info['solucao']}</p>
                    
                    <div style="margin:20px 0;">
                        <strong>Procedimento:</strong>
                        <ol>
                            {''.join([f'<li>{p}</li>' for p in info.get('procedimento', ['Diagnóstico manual'])])}
                        </ol>
                    </div>
                    
                    <div class="solution-price">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span class="price-value">R$ {info['valor']}</span>
                            <span style="color:#888;">Tempo: {info['tempo']}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# =============================================
# PROCEDIMENTOS
# =============================================
elif st.session_state.current_tab == "Procedimentos":
    st.markdown("## ⚙️ PROCEDIMENTOS VW")
    
    tabs = st.tabs(list(PROCEDIMENTOS.keys()))
    
    for i, (nome, passos) in enumerate(PROCEDIMENTOS.items()):
        with tabs[i]:
            st.markdown(f"""
            <div class="procedure-card">
                <div class="procedure-title">{nome}</div>
                <div class="procedure-steps">
                    <ol>
                        {''.join([f'<li>{p}</li>' for p in passos])}
                    </ol>
                </div>
                <button class="vw-button" onclick="alert('Procedimento iniciado')">
                    ▶️ EXECUTAR PROCEDIMENTO
                </button>
            </div>
            """, unsafe_allow_html=True)

# =============================================
# MODELOS
# =============================================
elif st.session_state.current_tab == "Modelos":
    st.markdown("## 🚗 MODELOS VW COMPATÍVEIS")
    
    cols = st.columns(3)
    for i, (modelo, info) in enumerate(MODELOS_VW.items()):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="model-card">
                <div class="model-icon">{info['icon']}</div>
                <div class="model-name">{modelo}</div>
                <div class="model-info">📅 {info['anos']}</div>
                <div class="model-info">🔧 {info['motores']}</div>
            </div>
            """, unsafe_allow_html=True)

# =============================================
# CONFIGURAÇÕES
# =============================================
elif st.session_state.current_tab == "Config":
    st.markdown("## ⚙️ CONFIGURAÇÕES")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔌 CONEXÃO")
        protocolo = st.selectbox("Protocolo", ["Automático", "CAN 11-bit", "CAN 29-bit", "KWP2000"], index=0)
        baudrate = st.selectbox("Baudrate", ["500k", "250k", "125k"], index=0)
        timeout = st.slider("Timeout (ms)", 500, 5000, 2000, 100)
    
    with col2:
        st.markdown("### 🎨 INTERFACE")
        tema = st.selectbox("Tema", ["Dark Profissional", "Light", "Automotive"])
        linguagem = st.selectbox("Idioma", ["Português", "English", "Español"])
        st.checkbox("Modo especialista", value=True)
        st.checkbox("Logs detalhados", value=False)
    
    st.markdown("### 💾 SOBRE O SISTEMA")
    st.info("""
    **RASTHER VW PRO v2.0**
    - Scanner Volkswagen Profissional
    - 30+ códigos de falha VW
    - 10+ modelos compatíveis
    - Atualizações via OTA
    """)

# =============================================
# FOOTER
# =============================================
st.markdown("---")
st.markdown(f"""
<div class="footer">
    <div style="display:flex; justify-content:space-between;">
        <span>🚗 RASTHER VW PRO • Scanner Volkswagen</span>
        <span>{datetime.now().strftime('%d/%m/%Y %H:%M')}</span>
        <span>v2.0 • {len(DTC_VW)} códigos</span>
    </div>
</div>
""", unsafe_allow_html=True)

# =============================================
# ATUALIZAÇÃO AUTOMÁTICA
# =============================================
if st.session_state.connected:
    time.sleep(2)
    st.rerun()
