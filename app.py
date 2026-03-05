# app.py - RASTHER VW PROFESSIONAL
# Interface estilo Car Scanner / RASTHER 3S

import streamlit as st
import pandas as pd
import numpy as np
import time
import random
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_option_menu import option_menu

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
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #1a1d24;
    }
    ::-webkit-scrollbar-thumb {
        background: #0047ab;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #ff6600;
    }
    
    /* Header principal */
    .main-header {
        background: linear-gradient(90deg, #001a33, #0047ab);
        padding: 10px 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-left: 5px solid #ff6600;
        box-shadow: 0 4px 15px rgba(0,71,171,0.3);
    }
    
    .header-title {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .header-title h1 {
        color: white;
        font-size: 28px;
        margin: 0;
        font-weight: 700;
        letter-spacing: 2px;
    }
    
    .header-title p {
        color: #00ffff;
        font-size: 12px;
        margin: 0;
        letter-spacing: 1px;
    }
    
    .header-status {
        background: #0a0c10;
        padding: 8px 20px;
        border-radius: 30px;
        border: 1px solid #00ffff;
        font-family: monospace;
        font-size: 14px;
    }
    
    .status-online { color: #00ff00; }
    .status-offline { color: #ff0000; }
    
    /* Connection bar */
    .connection-bar {
        background: #1a1d24;
        padding: 12px 20px;
        border-radius: 8px;
        margin-bottom: 20px;
        display: flex;
        gap: 30px;
        border-left: 4px solid #ff6600;
    }
    
    .conn-item {
        display: flex;
        flex-direction: column;
    }
    
    .conn-label {
        color: #888;
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .conn-value {
        color: #ff6600;
        font-size: 16px;
        font-weight: bold;
        font-family: monospace;
    }
    
    /* Medidores estilo scanner */
    .gauge-container {
        background: #1a1d24;
        border: 2px solid #0047ab;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,71,171,0.2);
    }
    
    .gauge-value {
        font-size: 48px;
        font-weight: bold;
        color: #00ffff;
        font-family: monospace;
        text-shadow: 0 0 20px #00ffff;
    }
    
    .gauge-label {
        color: #888;
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    .gauge-unit {
        color: #ff6600;
        font-size: 16px;
        margin-left: 5px;
    }
    
    /* Cards de diagnóstico */
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
        font-family: monospace;
    }
    
    .dtc-vw {
        color: #00ffff;
        font-size: 14px;
        background: #0a0c10;
        padding: 3px 10px;
        border-radius: 15px;
        margin-left: 10px;
    }
    
    /* Cards de procedimentos */
    .procedure-card {
        background: #1a1d24;
        border: 1px solid #ff6600;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    
    .procedure-title {
        color: #ff6600;
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 15px;
        border-bottom: 1px solid #ff6600;
        padding-bottom: 5px;
    }
    
    /* Botões */
    .vw-button {
        background: #0047ab;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 30px;
        font-weight: bold;
        cursor: pointer;
        transition: 0.3s;
        width: 100%;
        margin: 5px 0;
    }
    
    .vw-button:hover {
        background: #ff6600;
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(255,102,0,0.3);
    }
    
    /* Tabelas */
    .data-table {
        background: #1a1d24;
        border: 1px solid #0047ab;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    
    .data-table th {
        color: #00ffff;
        font-weight: bold;
        padding: 10px;
    }
    
    .data-table td {
        color: white;
        padding: 5px 10px;
        border-bottom: 1px solid #333;
    }
    
    /* Progress bars */
    .progress-container {
        background: #333;
        height: 8px;
        border-radius: 4px;
        margin: 5px 0;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #00ff00, #ffff00, #ff0000);
        border-radius: 4px;
        transition: width 0.3s;
    }
</style>
""", unsafe_allow_html=True)

# =============================================
# BANCO DE DADOS VW
# =============================================
MODELOS_VW = {
    'Gol': '🚗 2008-2024 | EA111/EA211',
    'Polo': '🚘 2017-2024 | EA211',
    'Virtus': '🚙 2018-2024 | EA211',
    'T-Cross': '🚐 2019-2024 | EA211',
    'Nivus': '🚗 2020-2024 | EA211',
    'Taos': '🚙 2021-2024 | EA211',
    'Saveiro': '🛻 2010-2024 | EA111',
    'Amarok': '🛻 2010-2024 | V6 TDI',
    'Jetta': '🚘 2011-2024 | EA888',
    'Tiguan': '🚙 2012-2024 | EA888'
}

DTC_VW = {
    'P0301': {
        'vw': '17917',
        'desc': 'Falha de ignição - Cilindro 1',
        'causa': 'Bobina EA211 com defeito',
        'solucao': 'Trocar bobina Bosch 06K905110',
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
        'solucao': 'Verificar sonda lambda',
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
    }
}

PROCEDIMENTOS = {
    'Flex Fuel': [
        'Motor frio (<30°C)',
        'Ligar ignição (sem partida)',
        'Aguardar 30s',
        'Acelerador 100% por 10s',
        'Desligar 10s',
        'Dar partida'
    ],
    'Adaptação Borboleta': [
        'Ligar ignição',
        'Aguardar 30s',
        'Desligar 10s',
        'Ligar motor',
        'Marcha lenta 5min'
    ]
}

# =============================================
# SIDEBAR - MENU PRINCIPAL
# =============================================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Volkswagen_logo_2019.svg/1200px-Volkswagen_logo_2019.svg.png", 
             width=150)
    st.markdown("---")
    
    selected = option_menu(
        menu_title="RASTHER VW",
        options=["Dashboard", "Diagnóstico", "Procedimentos", "Modelos", "Configurações"],
        icons=["speedometer2", "exclamation-triangle", "gear", "car-front", "sliders"],
        menu_icon="tools",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#1a1d24"},
            "icon": {"color": "#ff6600", "font-size": "16px"},
            "nav-link": {"color": "#888", "font-size": "14px", "text-align": "left", "margin": "0px"},
            "nav-link-selected": {"background-color": "#0047ab", "color": "white"},
        }
    )
    
    st.markdown("---")
    
    # Status da conexão
    if 'connected' not in st.session_state:
        st.session_state.connected = False
        st.session_state.vehicle = {
            'modelo': 'Gol 1.6 MSI',
            'ano': '2024',
            'motor': 'EA211',
            'vin': '9BWZZZ377VT004251',
            'km': '15.234'
        }
        st.session_state.dtcs = []
    
    conn_color = "#00ff00" if st.session_state.connected else "#ff0000"
    conn_text = "ONLINE" if st.session_state.connected else "OFFLINE"
    
    st.markdown(f"""
    <div style="background:#0a0c10; padding:10px; border-radius:8px; text-align:center;">
        <span style="color:{conn_color};">●</span> 
        <span style="color:white;">{conn_text}</span><br>
        <span style="color:#888;">{st.session_state.vehicle['modelo']}</span>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.connected:
        if st.button("🔌 CONECTAR", use_container_width=True):
            st.session_state.connected = True
            st.rerun()
    else:
        if st.button("❌ DESCONECTAR", use_container_width=True):
            st.session_state.connected = False
            st.rerun()

# =============================================
# HEADER PRINCIPAL
# =============================================
st.markdown(f"""
<div class="main-header">
    <div class="header-title">
        <div style="font-size:40px;">🚗</div>
        <div>
            <h1>RASTHER VW PRO</h1>
            <p>SCANNER VOLKSWAGEN PROFISSIONAL</p>
        </div>
    </div>
    <div class="header-status">
        <span class="{'status-online' if st.session_state.connected else 'status-offline'}">●</span>
        {st.session_state.vehicle['modelo']} • {st.session_state.vehicle['km']} km
    </div>
</div>
""", unsafe_allow_html=True)

# =============================================
# CONNECTION BAR
# =============================================
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
</div>
""", unsafe_allow_html=True)

# =============================================
# DASHBOARD
# =============================================
if selected == "Dashboard":
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
        
        # Medidores principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="gauge-container">
                <div class="gauge-value">{rpm}</div>
                <div class="gauge-label">RPM <span class="gauge-unit">rpm</span></div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="gauge-container">
                <div class="gauge-value">{temp}°C</div>
                <div class="gauge-label">TEMPERATURA</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="gauge-container">
                <div class="gauge-value">{pressao}</div>
                <div class="gauge-label">PRESSÃO ÓLEO <span class="gauge-unit">bar</span></div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="gauge-container">
                <div class="gauge-value">{bateria}V</div>
                <div class="gauge-label">BATERIA</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Gráficos
        st.markdown("### 📈 DADOS EM TEMPO REAL")
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('RPM', 'Fuel Trim', 'MAF', 'Carga Motor'),
            specs=[[{}, {}], [{}, {}]]
        )
        
        times = list(range(30))
        rpm_data = [random.randint(750, 3500) for _ in range(30)]
        stft_data = [random.uniform(-10, 10) for _ in range(30)]
        ltft_data = [random.uniform(-10, 10) for _ in range(30)]
        maf_data = [random.uniform(2, 8) for _ in range(30)]
        carga_data = [random.randint(15, 85) for _ in range(30)]
        
        fig.add_trace(go.Scatter(x=times, y=rpm_data, mode='lines', 
                                 name='RPM', line=dict(color='#00ffff', width=2)), row=1, col=1)
        fig.add_trace(go.Scatter(x=times, y=stft_data, mode='lines', 
                                 name='STFT', line=dict(color='#00ff00', width=2)), row=1, col=2)
        fig.add_trace(go.Scatter(x=times, y=ltft_data, mode='lines', 
                                 name='LTFT', line=dict(color='#ffff00', width=2)), row=1, col=2)
        fig.add_trace(go.Scatter(x=times, y=maf_data, mode='lines', 
                                 name='MAF', line=dict(color='#ff00ff', width=2)), row=2, col=1)
        fig.add_trace(go.Scatter(x=times, y=carga_data, mode='lines', 
                                 name='Carga', line=dict(color='#ff6600', width=2)), row=2, col=2)
        
        fig.update_layout(
            height=500,
            showlegend=True,
            paper_bgcolor='#0a0c10',
            plot_bgcolor='#1a1d24',
            font=dict(color='white')
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Dados em tabela
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 PARÂMETROS DO MOTOR")
            data = {
                'Parâmetro': ['RPM', 'Temperatura', 'Pressão Óleo', 'Bateria', 'Carga Motor'],
                'Valor': [rpm, f"{temp}°C", f"{pressao} bar", f"{bateria}V", f"{carga}%"],
                'Normal': ['750-6800', '82-105', '3.5-5.5', '12-15', '15-85']
            }
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("### 🔧 SISTEMA DE COMBUSTÍVEL")
            data2 = {
                'Parâmetro': ['STFT', 'LTFT', 'MAF', 'Sonda Lambda'],
                'Valor': [f"{stft}%", f"{ltft}%", f"{maf} g/s", f"{random.uniform(0.7,0.9):.2f}V"],
                'Normal': ['±10%', '±10%', '2.5-8', '0.1-0.9V']
            }
            df2 = pd.DataFrame(data2)
            st.dataframe(df2, use_container_width=True, hide_index=True)

# =============================================
# DIAGNÓSTICO
# =============================================
elif selected == "Diagnóstico":
    st.markdown("## 🔍 DIAGNÓSTICO VOLKSWAGEN")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### ⚠️ CÓDIGOS DE FALHA")
        
        if st.button("📋 LER CÓDIGOS", use_container_width=True):
            st.session_state.dtcs = list(DTC_VW.keys())[:3]
        
        if st.button("✅ LIMPAR CÓDIGOS", use_container_width=True):
            st.session_state.dtcs = []
        
        if st.session_state.dtcs:
            for code in st.session_state.dtcs:
                info = DTC_VW[code]
                st.markdown(f"""
                <div class="dtc-card" onclick="alert('Selecionado')">
                    <div style="display: flex; justify-content: space-between;">
                        <span class="dtc-code">{code}</span>
                        <span class="dtc-vw">VW: {info['vw']}</span>
                    </div>
                    <div style="color: #ccc;">{info['desc']}</div>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🛠️ DETALHES")
        
        if st.session_state.dtcs:
            code = st.session_state.dtcs[0]
            info = DTC_VW[code]
            
            st.markdown(f"""
            <div style="background:#1a2a33; padding:20px; border-radius:10px; border:1px solid #00ffff;">
                <h3 style="color:#ff6600;">{code}</h3>
                <p style="color:#00ffff;">VW: {info['vw']}</p>
                <p><strong>Descrição:</strong> {info['desc']}</p>
                <p><strong>Causa:</strong> {info['causa']}</p>
                <p><strong>Solução:</strong> {info['solucao']}</p>
                <p><strong>Orçamento:</strong> R$ {info['valor']} • {info['tempo']}</p>
            </div>
            """, unsafe_allow_html=True)

# =============================================
# PROCEDIMENTOS
# =============================================
elif selected == "Procedimentos":
    st.markdown("## ⚙️ PROCEDIMENTOS VW")
    
    tabs = st.tabs(list(PROCEDIMENTOS.keys()))
    
    for i, (nome, passos) in enumerate(PROCEDIMENTOS.items()):
        with tabs[i]:
            st.markdown(f"""
            <div class="procedure-card">
                <div class="procedure-title">{nome}</div>
                <div style="color:white; margin-bottom:20px;">
                    <strong>Passo a passo:</strong>
                    <ol>
                        {''.join([f'<li>{p}</li>' for p in passos])}
                    </ol>
                </div>
                <button class="vw-button">▶️ EXECUTAR PROCEDIMENTO</button>
            </div>
            """, unsafe_allow_html=True)

# =============================================
# MODELOS
# =============================================
elif selected == "Modelos":
    st.markdown("## 🚗 MODELOS VW COMPATÍVEIS")
    
    cols = st.columns(3)
    for i, (modelo, info) in enumerate(MODELOS_VW.items()):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background:#1a1d24; border:1px solid #0047ab; border-radius:10px; padding:20px; margin:5px; text-align:center;">
                <div style="font-size:48px;">{info[0]}</div>
                <h4 style="color:#ff6600;">{modelo}</h4>
                <p style="color:#888;">{info[2:]}</p>
            </div>
            """, unsafe_allow_html=True)

# =============================================
# CONFIGURAÇÕES
# =============================================
elif selected == "Configurações":
    st.markdown("## ⚙️ CONFIGURAÇÕES")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔌 CONEXÃO")
        st.radio("Protocolo", ["CAN 11-bit", "CAN 29-bit", "KWP2000", "Automático"], index=3)
        st.number_input("Timeout (ms)", 500, 5000, 2000, 100)
    
    with col2:
        st.markdown("### 🎨 INTERFACE")
        st.selectbox("Tema", ["Dark", "Light", "Automotive"])
        st.checkbox("Modo especialista", value=True)
    
    st.markdown("---")
    st.markdown("### ℹ️ SOBRE")
    st.info("RASTHER VW PRO v2.0 • Scanner Volkswagen Profissional")

# =============================================
# FOOTER
# =============================================
st.markdown("---")
st.markdown(f"""
<div style="text-align:center; color:#888; font-size:12px; padding:10px;">
    RASTHER VW PRO • {len(DTC_VW)} códigos VW • {len(MODELOS_VW)} modelos compatíveis • {datetime.now().strftime('%d/%m/%Y %H:%M')}
</div>
""", unsafe_allow_html=True)
