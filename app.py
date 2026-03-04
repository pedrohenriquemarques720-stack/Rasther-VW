# app.py - RASTHER VW - Versão simplificada sem plotly

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
        'maf': 0
    }
    st.session_state.log = []

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
    }
    
    .status-disconnected {
        color: #ff0000;
    }
    
    /* Connection Bar */
    .connection-bar {
        background: #1a1d24;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #ff6600;
        margin-bottom: 20px;
        display: flex;
        gap: 30px;
    }
    
    .conn-item {
        display: flex;
        flex-direction: column;
    }
    
    .conn-label {
        color: #888;
        font-size: 11px;
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
    }
    
    .nav-btn {
        background: #1a1d24;
        color: #888;
        padding: 10px 20px;
        border-radius: 30px;
        border: 1px solid #333;
        cursor: pointer;
    }
    
    .nav-btn:hover {
        border-color: #0047ab;
        color: #0047ab;
    }
    
    .nav-btn.active {
        background: #0047ab;
        color: white;
    }
    
    /* Cards de métricas */
    .metric-card {
        background: #1a1d24;
        border: 1px solid #0047ab;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
    }
    
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        color: #00ffff;
    }
    
    .metric-label {
        color: #888;
        font-size: 12px;
    }
    
    /* DTC Cards */
    .dtc-card {
        background: #1a1d24;
        border-left: 4px solid #ff0000;
        padding: 10px;
        margin: 5px 0;
        border-radius: 0 5px 5px 0;
    }
    
    .dtc-code {
        color: #ff6666;
        font-weight: bold;
        font-size: 16px;
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
        if st.button("🔌 CONECTAR"):
            with st.spinner("Conectando..."):
                time.sleep(2)
                st.session_state.connected = True
                st.session_state.vehicle_info = {
                    'modelo': 'Gol 1.6',
                    'ano': '2024',
                    'motor': 'EA211',
                    'vin': '9BWZZZ377VT004251',
                    'ecu': 'BOSCH ME17.9.65',
                    'protocolo': 'CAN-BUS',
                    'km': '15.234 km'
                }
                st.rerun()
    else:
        if st.button("❌ DESCONECTAR"):
            st.session_state.connected = False
            st.rerun()

# =============================================
# MENU DE NAVEGAÇÃO
# =============================================
pages = ["Dashboard", "Diagnóstico VW", "Procedimentos", "Boletins"]

cols = st.columns(len(pages))
for i, page in enumerate(pages):
    with cols[i]:
        if st.button(page, key=f"nav_{page}"):
            st.session_state.current_page = page
            st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# =============================================
# DADOS SIMULADOS
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
        'maf': round(2.5 + random.random() * 3, 1)
    }

# =============================================
# DASHBOARD
# =============================================
if st.session_state.current_page == "Dashboard":
    st.markdown("## 📊 PAINEL PRINCIPAL")
    
    if not st.session_state.connected:
        st.info("👆 Conecte-se a um veículo para ver os dados")
    else:
        # Métricas
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
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ⚠️ CÓDIGOS DE FALHA")
            
            if st.button("📋 LER CÓDIGOS VW", use_container_width=True):
                st.session_state.dtcs = [
                    {'code': 'P0301', 'vw_code': '17917', 'desc': 'Falha de ignição - Cilindro 1'},
                    {'code': 'P0420', 'vw_code': '16804', 'desc': 'Catalisador ineficiente'},
                    {'code': 'P0171', 'vw_code': '17544', 'desc': 'Mistura pobre'}
                ]
            
            if st.session_state.dtcs:
                for dtc in st.session_state.dtcs:
                    st.markdown(f"""
                    <div class="dtc-card">
                        <div style="display: flex; gap: 10px;">
                            <span class="dtc-code">{dtc['code']}</span>
                            <span style="color: #00ffff;">VW: {dtc['vw_code']}</span>
                        </div>
                        <div style="color: #ccc;">{dtc['desc']}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### 🛠️ SOLUÇÃO VW")
            
            if st.session_state.dtcs:
                st.markdown("""
                **P0301 - Falha Cilindro 1**
                
                **Causa comum:** Bobina de ignição com defeito (EA211)
                
                **Solução:** Substituir bobina Bosch 06K905110
                
                **Procedimento:**
                1. Remover conector da bobina
                2. Remover parafuso (torque 8Nm)
                3. Instalar nova bobina
                4. Limpar códigos de falha
                
                **Valor estimado:** R$ 450,00
                """)

# =============================================
# PROCEDIMENTOS
# =============================================
elif st.session_state.current_page == "Procedimentos":
    st.markdown("## ⚙️ PROCEDIMENTOS VW")
    
    tabs = st.tabs(["Reset Flex", "Adaptação Borboleta", "Casamento de Chaves"])
    
    with tabs[0]:
        st.markdown("""
        ### 🔄 RESET FLEX FUEL (EA111/EA211)
        
        **Passo a passo:**
        1. Motor frio (abaixo de 30°C)
        2. Ligar ignição sem dar partida
        3. Aguardar 30 segundos
        4. Acelerador totalmente pressionado por 10s
        5. Desligar ignição por 10s
        6. Dar partida normal
        
        **Quando realizar:** Após troca de combustível ou falha P0171
        """)
    
    with tabs[1]:
        st.markdown("""
        ### ⚙️ ADAPTAÇÃO CORPO DE BORBOLETA
        
        **Passo a passo:**
        1. Ligar ignição (motor desligado)
        2. Aguardar 30 segundos (borboleta se move)
        3. Desligar ignição por 10s
        4. Ligar motor e deixar em marcha lenta por 5min
        
        **Quando realizar:** Após limpeza da borboleta
        """)

# =============================================
# BOLETINS
# =============================================
elif st.session_state.current_page == "Boletins":
    st.markdown("## 📋 BOLETINS TÉCNICOS VW")
    
    boletins = [
        {
            'codigo': 'VW-23-05',
            'titulo': 'Falha de bobinas EA211',
            'data': '05/2023',
            'modelos': ['Gol', 'Polo', 'Virtus']
        },
        {
            'codigo': 'VW-24-02',
            'titulo': 'Atualização de software I-Motion',
            'data': '02/2024',
            'modelos': ['Up', 'Gol']
        },
        {
            'codigo': 'VW-24-01',
            'titulo': 'Ruído na suspensão dianteira',
            'data': '01/2024',
            'modelos': ['T-Cross', 'Nivus']
        }
    ]
    
    for boletim in boletins:
        st.markdown(f"""
        <div style="background: #1a1d24; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <div style="color: #ff6600; font-weight: bold;">{boletim['codigo']}</div>
            <div style="color: white;">{boletim['titulo']}</div>
            <div style="color: #888; font-size: 12px;">Data: {boletim['data']}</div>
            <div style="color: #00ffff; font-size: 12px;">Modelos: {', '.join(boletim['modelos'])}</div>
        </div>
        """, unsafe_allow_html=True)

# =============================================
# FOOTER
# =============================================
st.markdown("---")
st.markdown(f"""
<div class="footer">
    RASTHER VW v1.0 • Especialista Volkswagen • {datetime.now().strftime('%d/%m/%Y %H:%M')}
</div>
""", unsafe_allow_html=True)

# =============================================
# ATUALIZAÇÃO AUTOMÁTICA
# =============================================
if st.session_state.connected:
    time.sleep(2)
    st.rerun()
