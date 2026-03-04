# app.py - RASTHER VW - Scanner Especializado em Volkswagen

import streamlit as st
import pandas as pd
import numpy as np
import time
import random
import json
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
        'temp_oleo': 0,
        'pressao_oleo': 0,
        'bateria': 12.5,
        'stft': 0,
        'ltft': 0,
        'maf': 0,
        'o2': 0.78,
        'carga_motor': 0,
        'avanco_ignicao': 0
    }
    st.session_state.log = []
    st.session_state.ultimo_diagnostico = None

# =============================================
# CARREGAR CSS PERSONALIZADO
# =============================================
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# =============================================
# HEADER PERSONALIZADO VW
# =============================================
st.markdown("""
<div class="vw-header">
    <div class="vw-logo">
        <div class="vw-icon">🚗</div>
        <div class="vw-title">
            <h1>RASTHER VW</h1>
            <p>Scanner Profissional Volkswagen</p>
        </div>
    </div>
    <div class="vw-status" id="status-indicator">
        <span class="status-led"></span>
        <span class="status-text">DESCONECTADO</span>
    </div>
</div>
""", unsafe_allow_html=True)

# =============================================
# BARRA DE CONEXÃO
# =============================================
col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

with col1:
    st.markdown("""
    <div class="vw-connection-item">
        <span class="conn-label">VEÍCULO</span>
        <span class="conn-value" id="vehicle-model">---</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="vw-connection-item">
        <span class="conn-label">PROTOCOLO</span>
        <span class="conn-value" id="protocol">CAN-BUS VW</span>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="vw-connection-item">
        <span class="conn-label">ECU</span>
        <span class="conn-value" id="ecu">---</span>
    </div>
    """, unsafe_allow_html=True)

with col4:
    if st.button("🔌 CONECTAR", key="connect_btn"):
        st.session_state.connected = True
        st.rerun()

# =============================================
# MENU DE NAVEGAÇÃO VW
# =============================================
st.markdown("""
<div class="vw-nav">
    <button class="vw-nav-btn active" onclick="changePage('Dashboard')">📊 DASHBOARD</button>
    <button class="vw-nav-btn" onclick="changePage('Diagnóstico')">🔍 DIAGNÓSTICO VW</button>
    <button class="vw-nav-btn" onclick="changePage('Procedimentos')">⚙️ PROCEDIMENTOS</button>
    <button class="vw-nav-btn" onclick="changePage('Adaptações')">🔄 ADAPTAÇÕES</button>
    <button class="vw-nav-btn" onclick="changePage('Boletins')">📋 BOLETINS</button>
</div>
""", unsafe_allow_html=True)

# =============================================
# CONTEÚDO PRINCIPAL
# =============================================

if st.session_state.current_page == "Dashboard":
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="vw-metric-card">
            <div class="metric-label">RPM</div>
            <div class="metric-value">{st.session_state.live_data['rpm']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="vw-metric-card">
            <div class="metric-label">TEMP. MOTOR</div>
            <div class="metric-value">{st.session_state.live_data['temp_motor']}°C</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="vw-metric-card">
            <div class="metric-label">PRESSÃO ÓLEO</div>
            <div class="metric-value">{st.session_state.live_data['pressao_oleo']} bar</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="vw-metric-card">
            <div class="metric-label">BATERIA</div>
            <div class="metric-value">{st.session_state.live_data['bateria']}V</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Gráficos VW
    st.markdown("### 📊 DADOS DO MOTOR EA211")
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('RPM x Tempo', 'STFT/LTFT', 'Pressão Óleo', 'Sonda Lambda'),
        specs=[[{}, {}], [{}, {}]]
    )
    
    # Simular dados
    times = list(range(20))
    rpm_data = [random.randint(750, 3500) for _ in range(20)]
    stft_data = [random.uniform(-5, 15) for _ in range(20)]
    ltft_data = [random.uniform(-8, 18) for _ in range(20)]
    pressao_data = [random.uniform(3.5, 5.5) for _ in range(20)]
    o2_data = [random.uniform(0.7, 0.9) for _ in range(20)]
    
    fig.add_trace(go.Scatter(x=times, y=rpm_data, mode='lines', name='RPM', line=dict(color='#0047ab')), row=1, col=1)
    fig.add_trace(go.Scatter(x=times, y=stft_data, mode='lines', name='STFT', line=dict(color='#00ff00')), row=1, col=2)
    fig.add_trace(go.Scatter(x=times, y=ltft_data, mode='lines', name='LTFT', line=dict(color='#ffff00')), row=1, col=2)
    fig.add_trace(go.Scatter(x=times, y=pressao_data, mode='lines', name='Pressão', line=dict(color='#ff6600')), row=2, col=1)
    fig.add_trace(go.Scatter(x=times, y=o2_data, mode='lines', name='Lambda', line=dict(color='#ff00ff')), row=2, col=2)
    
    fig.update_layout(height=600, showlegend=True, paper_bgcolor='#0a0c10', plot_bgcolor='#1a1d24', font=dict(color='white'))
    st.plotly_chart(fig, use_container_width=True)
    
    # Informações do veículo
    with st.expander("🚗 INFORMAÇÕES DO VEÍCULO", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Modelo:** Gol 1.6 MSI 2024")
            st.markdown("**Motor:** EA211 16V")
            st.markdown("**Câmbio:** MQ200 Manual")
        
        with col2:
            st.markdown("**ECU:** Bosch ME17.9.65")
            st.markdown("**Protocolo:** CAN 500kbps")
            st.markdown("**VIN:** 9BWZZZ377VT004251")
        
        with col3:
            st.markdown("**Data de fabricação:** 03/2024")
            st.markdown("**KM:** 15.234 km")
            st.markdown("**Última visita:** 15/02/2026")

elif st.session_state.current_page == "Diagnóstico":
    st.markdown("## 🔍 DIAGNÓSTICO ESPECIALIZADO VW")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⚠️ CÓDIGOS DE FALHA")
        
        if st.button("📋 LER CÓDIGOS VW", use_container_width=True):
            st.session_state.dtcs = [
                {'code': 'P0301', 'desc': 'Falha de ignição - Cilindro 1', 'vw_code': '17917', 'severity': 'critical'},
                {'code': 'P0420', 'desc': 'Catalisador ineficiente', 'vw_code': '16804', 'severity': 'warning'},
                {'code': 'P0171', 'desc': 'Mistura pobre', 'vw_code': '17544', 'severity': 'warning'}
            ]
        
        if st.session_state.dtcs:
            for dtc in st.session_state.dtcs:
                color = "#ff0000" if dtc['severity'] == 'critical' else "#ffaa00"
                st.markdown(f"""
                <div class="vw-dtc-card" style="border-left-color: {color};">
                    <div style="display: flex; justify-content: space-between;">
                        <span class="dtc-code">{dtc['code']}</span>
                        <span class="vw-code">VW: {dtc['vw_code']}</span>
                    </div>
                    <div class="dtc-desc">{dtc['desc']}</div>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🛠️ SOLUÇÃO VW")
        
        if st.session_state.dtcs:
            st.markdown("""
            <div class="vw-solution-card">
                <h4>P0301 - Falha Cilindro 1</h4>
                <p><strong>Problema comum em EA211:</strong> Bobina de ignição com defeito</p>
                <p><strong>Solução:</strong> Substituir bobina (Bosch 06K905110)</p>
                <p><strong>Procedimento:</strong></p>
                <ol>
                    <li>Remover conector da bobina</li>
                    <li>Remover parafuso de fixação (torque 8Nm)</li>
                    <li>Instalar nova bobina</li>
                    <li>Limpar códigos de falha</li>
                </ol>
                <p><strong>Valor estimado:</strong> R$ 450,00</p>
                <p><strong>Dica VW:</strong> Verificar também as velas (trocar a cada 40.000km)</p>
            </div>
            """, unsafe_allow_html=True)

elif st.session_state.current_page == "Procedimentos":
    st.markdown("## ⚙️ PROCEDIMENTOS ESPECIAIS VW")
    
    tabs = st.tabs(["Reset Flex", "Adaptação Borboleta", "Casamento de Chaves", "Reset I-Motion"])
    
    with tabs[0]:
        st.markdown("""
        <div class="vw-procedure-card">
            <h3>🔄 RESET FLEX FUEL - EA111/EA211</h3>
            <p>Procedimento para resetar adaptações de combustível flex</p>
            
            <h4>Passo a passo:</h4>
            <ol>
                <li>Motor frio (temperatura abaixo de 30°C)</li>
                <li>Ligar ignição sem dar partida</li>
                <li>Aguardar 30 segundos</li>
                <li>Pressionar acelerador totalmente por 10 segundos</li>
                <li>Desligar ignição e aguardar 10 segundos</li>
                <li>Dar partida normal</li>
            </ol>
            
            <h4>Comando via scanner:</h4>
            <code>PID 0xF101 - Reset Adaptação Flex</code>
            
            <h4>Observações:</h4>
            <p>• Realizar após troca de combustível</p>
            <p>• Recomendado a cada 10.000km</p>
            <p>• Pode ser necessário em casos de falha P0171</p>
            
            <button class="vw-execute-btn">▶️ EXECUTAR PROCEDIMENTO</button>
        </div>
        """, unsafe_allow_html=True)
    
    with tabs[1]:
        st.markdown("""
        <div class="vw-procedure-card">
            <h3>⚙️ ADAPTAÇÃO DE CORPO DE BORBOLETA</h3>
            <p>Reaprendizado da posição da borboleta após limpeza</p>
            
            <h4>Passo a passo:</h4>
            <ol>
                <li>Ligar ignição (motor desligado)</li>
                <li>Aguardar 30 segundos - borboleta fará movimento</li>
                <li>Desligar ignição por 10 segundos</li>
                <li>Ligar motor e deixar em marcha lenta por 5 minutos</li>
                <li>Não acelerar durante o processo</li>
            </ol>
            
            <h4>Via scanner:</h4>
            <code>PID 0xF104 - Reset Corpo de Borboleta</code>
            
            <button class="vw-execute-btn">▶️ EXECUTAR ADAPTAÇÃO</button>
        </div>
        """, unsafe_allow_html=True)