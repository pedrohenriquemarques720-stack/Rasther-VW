# app.py - RASTHER VW - Scanner Profissional Volkswagen
# Versão 2.0 - Com todas as funcionalidades

import streamlit as st
import pandas as pd
import numpy as np
import time
import random
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

# =============================================
# BANCO DE DADOS VOLKSWAGEN
# =============================================
MODELOS_VW = {
    'Gol': {'anos': '2008-2024', 'motores': ['1.0', '1.6', '1.0 TSI'], 'imagem': '🚗'},
    'Polo': {'anos': '2017-2024', 'motores': ['1.0 TSI', '1.6', '200 TSI'], 'imagem': '🚘'},
    'Virtus': {'anos': '2018-2024', 'motores': ['1.0 TSI', '1.6'], 'imagem': '🚙'},
    'T-Cross': {'anos': '2019-2024', 'motores': ['1.0 TSI', '1.4 TSI'], 'imagem': '🚐'},
    'Nivus': {'anos': '2020-2024', 'motores': ['1.0 TSI'], 'imagem': '🚗'},
    'Taos': {'anos': '2021-2024', 'motores': ['1.4 TSI'], 'imagem': '🚙'},
    'Saveiro': {'anos': '2010-2024', 'motores': ['1.6'], 'imagem': '🛻'}
}

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
    }
}

PROCEDIMENTOS_VW = {
    'reset_flex': {
        'nome': 'Reset Flex Fuel',
        'descricao': 'Reinicia as adaptações de combustível flex (etanol/gasolina)',
        'passos': [
            'Motor frio (temperatura abaixo de 30°C)',
            'Ligar ignição sem dar partida',
            'Aguardar 30 segundos',
            'Pressionar acelerador totalmente por 10 segundos',
            'Desligar ignição e aguardar 10 segundos',
            'Dar partida normal'
        ],
        'quando': 'Após troca de combustível ou falha P0171',
        'dicas': 'Não acelerar durante o processo'
    },
    'adaptacao_borboleta': {
        'nome': 'Adaptação de Corpo de Borboleta',
        'descricao': 'Reaprendizado da posição da borboleta após limpeza',
        'passos': [
            'Ligar ignição (motor desligado)',
            'Aguardar 30 segundos (borboleta fará movimento)',
            'Desligar ignição por 10 segundos',
            'Ligar motor e deixar em marcha lenta por 5 minutos',
            'Não acelerar durante o processo'
        ],
        'quando': 'Após limpeza do corpo de borboleta',
        'dicas': 'Pode ser necessário 2-3 ciclos'
    }
}

# =============================================
# CSS PERSONALIZADO
# =============================================
st.markdown("""
<style>
    .stApp { background: #0a0c10; }
    
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
    
    .status-connected { color: #00ff00; font-weight: bold; }
    .status-disconnected { color: #ff0000; font-weight: bold; }
    
    .connection-bar {
        background: #1a1d24;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #ff6600;
        margin-bottom: 20px;
        display: flex;
        gap: 30px;
    }
    
    .conn-item { display: flex; flex-direction: column; }
    .conn-label { color: #888; font-size: 11px; }
    .conn-value { color: #ff6600; font-size: 16px; font-weight: bold; }
    
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
    
    .nav-btn:hover { border-color: #0047ab; color: #0047ab; }
    .nav-btn.active { background: #0047ab; color: white; }
    
    .metric-card {
        background: #1a1d24;
        border: 1px solid #0047ab;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
    }
    
    .metric-value { font-size: 32px; font-weight: bold; color: #00ffff; }
    .metric-label { color: #888; font-size: 12px; }
    
    .dtc-card {
        background: #1a1d24;
        border-left: 4px solid #ff0000;
        padding: 10px;
        margin: 5px 0;
        border-radius: 0 5px 5px 0;
        cursor: pointer;
    }
    
    .dtc-card:hover { background: #2a2d34; }
    .dtc-code { color: #ff6666; font-weight: bold; font-size: 16px; }
    .vw-code { color: #00ffff; font-size: 12px; margin-left: 10px; }
    
    .solution-card {
        background: #1a2a33;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #00ffff;
    }
    
    .procedure-card {
        background: #1a1d24;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #ff6600;
        margin: 10px 0;
    }
    
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
        if st.button("🔌 CONECTAR", use_container_width=True):
            with st.spinner("Conectando ao veículo..."):
                time.sleep(2)
                st.session_state.connected = True
                st.session_state.vehicle_info = {
                    'modelo': 'Gol 1.6 MSI',
                    'ano': '2024',
                    'motor': 'EA211',
                    'vin': '9BWZZZ377VT004251',
                    'ecu': 'BOSCH ME17.9.65',
                    'protocolo': 'CAN-BUS',
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
pages = ["Dashboard", "Diagnóstico VW", "Procedimentos", "Modelos VW"]

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
        st.info("👆 Conecte-se a um veículo para ver os dados")
    else:
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
        
        # Gráficos
        st.markdown("### 📈 DADOS DO MOTOR")
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('RPM', 'STFT/LTFT', 'Pressão de Óleo', 'Sonda Lambda')
        )
        
        times = list(range(20))
        fig.add_trace(go.Scatter(x=times, y=[random.randint(750,3500) for _ in range(20)], 
                                 mode='lines', name='RPM', line=dict(color='#0047ab')), row=1, col=1)
        fig.add_trace(go.Scatter(x=times, y=[random.uniform(-5,15) for _ in range(20)], 
                                 mode='lines', name='STFT', line=dict(color='#00ff00')), row=1, col=2)
        fig.add_trace(go.Scatter(x=times, y=[random.uniform(-8,18) for _ in range(20)], 
                                 mode='lines', name='LTFT', line=dict(color='#ffff00')), row=1, col=2)
        fig.add_trace(go.Scatter(x=times, y=[random.uniform(3.5,5.5) for _ in range(20)], 
                                 mode='lines', name='Pressão', line=dict(color='#ff6600')), row=2, col=1)
        fig.add_trace(go.Scatter(x=times, y=[random.uniform(0.7,0.9) for _ in range(20)], 
                                 mode='lines', name='Lambda', line=dict(color='#ff00ff')), row=2, col=2)
        
        fig.update_layout(height=500, showlegend=True, 
                         paper_bgcolor='#0a0c10', plot_bgcolor='#1a1d24',
                         font=dict(color='white'))
        st.plotly_chart(fig, use_container_width=True)

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
                    {'code': 'P0301', 'desc': 'Falha de ignição - Cilindro 1'},
                    {'code': 'P0420', 'desc': 'Catalisador ineficiente'},
                    {'code': 'P0171', 'desc': 'Mistura pobre'}
                ]
            
            if st.session_state.dtcs:
                for dtc in st.session_state.dtcs:
                    if st.button(f"{dtc['code']} - {dtc['desc']}", key=f"dtc_{dtc['code']}", use_container_width=True):
                        st.session_state.dtc_selecionado = dtc['code']
        
        with col2:
            st.markdown("### 🛠️ SOLUÇÃO VW")
            
            if st.session_state.dtc_selecionado and st.session_state.dtc_selecionado in DTC_VW:
                info = DTC_VW[st.session_state.dtc_selecionado]
                st.markdown(f"""
                <div class="solution-card">
                    <h3 style="color:#ff6600;">{st.session_state.dtc_selecionado}</h3>
                    <p><strong>Código VW:</strong> {info['vw_code']}</p>
                    <p><strong>Causa:</strong> {info['causa']}</p>
                    <p><strong>Solução:</strong> {info['solucao']}</p>
                    <p><strong>Procedimento:</strong></p>
                    <ol>
                        {''.join([f'<li>{p}</li>' for p in info['procedimento']])}
                    </ol>
                    <p><strong>Valor estimado:</strong> R$ {info['valor']:.2f}</p>
                    <p><strong>Tempo:</strong> {info['tempo']}</p>
                </div>
                """, unsafe_allow_html=True)

# =============================================
# PROCEDIMENTOS
# =============================================
elif st.session_state.current_page == "Procedimentos":
    st.markdown("## ⚙️ PROCEDIMENTOS VW")
    
    tabs = st.tabs(["Reset Flex", "Adaptação Borboleta"])
    
    for i, (key, proc) in enumerate(PROCEDIMENTOS_VW.items()):
        with tabs[i]:
            st.markdown(f"""
            <div class="procedure-card">
                <h3 style="color:#ff6600;">{proc['nome']}</h3>
                <p>{proc['descricao']}</p>
                <h4>Passo a passo:</h4>
                <ol>
                    {''.join([f'<li>{p}</li>' for p in proc['passos']])}
                </ol>
                <p><strong>Quando realizar:</strong> {proc['quando']}</p>
                <p><strong>Dica:</strong> {proc['dicas']}</p>
            </div>
            """, unsafe_allow_html=True)

# =============================================
# MODELOS VW
# =============================================
elif st.session_state.current_page == "Modelos VW":
    st.markdown("## 🚗 MODELOS VOLKSWAGEN")
    
    cols = st.columns(3)
    for i, (modelo, info) in enumerate(MODELOS_VW.items()):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background:#1a1d24; border:1px solid #0047ab; border-radius:8px; padding:15px; margin:5px; text-align:center;">
                <div style="font-size:40px;">{info['imagem']}</div>
                <h4 style="color:#ff6600;">{modelo}</h4>
                <p>📅 {info['anos']}</p>
                <p>🔧 {', '.join(info['motores'])}</p>
            </div>
            """, unsafe_allow_html=True)

# =============================================
# FOOTER
# =============================================
st.markdown("---")
st.markdown(f"""
<div class="footer">
    RASTHER VW v2.0 • Especialista Volkswagen • {datetime.now().strftime('%d/%m/%Y %H:%M')}
</div>
""", unsafe_allow_html=True)

# =============================================
# ATUALIZAÇÃO AUTOMÁTICA
# =============================================
if st.session_state.connected:
    time.sleep(2)
    st.rerun()
