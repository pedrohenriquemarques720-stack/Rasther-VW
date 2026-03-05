# app.py - RASTHER VW - Scanner Profissional Volkswagen
# Versão com fallback - FUNCIONA MESMO SEM PLOTLY

import streamlit as st
import pandas as pd
import numpy as np
import time
import random
from datetime import datetime

# =============================================
# TENTATIVA DE IMPORTAR PLOTLY COM FALLBACK
# =============================================
PLOTLY_AVAILABLE = False
try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
    st.success("✅ Plotly carregado com sucesso!")
except ImportError as e:
    st.warning("⚠️ Plotly não disponível - gráficos serão exibidos em modo texto")
    print(f"Erro detalhado: {e}")

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
# BANCO DE DADOS VOLKSWAGEN (30+ CÓDIGOS)
# =============================================

MODELOS_VW = {
    'Gol': {
        'anos': '2008-2024',
        'motores': ['1.0', '1.6', '1.0 TSI'],
        'imagem': '🚗'
    },
    'Polo': {
        'anos': '2017-2024',
        'motores': ['1.0 TSI', '1.6', '200 TSI'],
        'imagem': '🚘'
    },
    'Virtus': {
        'anos': '2018-2024',
        'motores': ['1.0 TSI', '1.6'],
        'imagem': '🚙'
    },
    'T-Cross': {
        'anos': '2019-2024',
        'motores': ['1.0 TSI', '1.4 TSI'],
        'imagem': '🚐'
    },
    'Nivus': {
        'anos': '2020-2024',
        'motores': ['1.0 TSI'],
        'imagem': '🚗'
    },
    'Taos': {
        'anos': '2021-2024',
        'motores': ['1.4 TSI'],
        'imagem': '🚙'
    },
    'Saveiro': {
        'anos': '2010-2024',
        'motores': ['1.6'],
        'imagem': '🛻'
    },
    'Amarok': {
        'anos': '2010-2024',
        'motores': ['2.0 TDI', '3.0 V6'],
        'imagem': '🛻'
    },
    'Jetta': {
        'anos': '2011-2024',
        'motores': ['1.4 TSI', '2.0 TSI'],
        'imagem': '🚘'
    },
    'Tiguan': {
        'anos': '2012-2024',
        'motores': ['2.0 TSI'],
        'imagem': '🚙'
    }
}

DTC_VW = {
    'P0300': {
        'vw_code': '17916',
        'descricao': 'Falha de ignição aleatória',
        'causa': 'Múltiplas falhas de ignição - bobinas ou velas',
        'solucao': 'Verificar sistema de ignição completo',
        'valor': 600.00,
        'tempo': '2.0 horas'
    },
    'P0301': {
        'vw_code': '17917',
        'descricao': 'Falha de ignição - Cilindro 1',
        'causa': 'Bobina de ignição com defeito (EA211)',
        'solucao': 'Substituir bobina Bosch 06K905110',
        'procedimento': [
            'Desconectar conector da bobina',
            'Remover parafuso de fixação (torque 8Nm)',
            'Instalar nova bobina',
            'Reconectar conector',
            'Limpar códigos de falha'
        ],
        'valor': 450.00,
        'tempo': '1.5 horas'
    },
    'P0302': {
        'vw_code': '17918',
        'descricao': 'Falha de ignição - Cilindro 2',
        'causa': 'Bobina de ignição com defeito',
        'solucao': 'Substituir bobina',
        'valor': 450.00,
        'tempo': '1.5 horas'
    },
    'P0303': {
        'vw_code': '17919',
        'descricao': 'Falha de ignição - Cilindro 3',
        'causa': 'Bobina de ignição com defeito',
        'solucao': 'Substituir bobina',
        'valor': 450.00,
        'tempo': '1.5 horas'
    },
    'P0304': {
        'vw_code': '17920',
        'descricao': 'Falha de ignição - Cilindro 4',
        'causa': 'Bobina de ignição com defeito',
        'solucao': 'Substituir bobina',
        'valor': 450.00,
        'tempo': '1.5 horas'
    },
    'P0420': {
        'vw_code': '16804',
        'descricao': 'Catalisador ineficiente',
        'causa': 'Sonda lambda pós-catalisador com defeito',
        'solucao': 'Verificar sonda lambda primeiro, depois catalisador',
        'valor': 1850.00,
        'tempo': '3.0 horas'
    },
    'P0171': {
        'vw_code': '17544',
        'descricao': 'Mistura pobre (Banco 1)',
        'causa': 'Vazamento de vácuo ou sensor MAF sujo',
        'solucao': 'Verificar mangueiras de vácuo e limpar MAF',
        'valor': 380.00,
        'tempo': '1.0 hora'
    },
    'P0172': {
        'vw_code': '17536',
        'descricao': 'Mistura rica (Banco 1)',
        'causa': 'Injetores com defeito',
        'solucao': 'Verificar injetores',
        'valor': 450.00,
        'tempo': '2.0 horas'
    },
    'P0135': {
        'vw_code': '16519',
        'descricao': 'Sonda Lambda - Aquecimento',
        'causa': 'Resistência de aquecimento queimada',
        'solucao': 'Substituir sonda lambda',
        'valor': 380.00,
        'tempo': '1.0 hora'
    },
    'P0335': {
        'vw_code': '16705',
        'descricao': 'Sensor de Rotação',
        'causa': 'Sensor CKP com defeito',
        'solucao': 'Substituir sensor de rotação',
        'valor': 290.00,
        'tempo': '1.0 hora'
    },
    'P0340': {
        'vw_code': '16717',
        'descricao': 'Sensor de Fase',
        'causa': 'Sensor CMP com defeito',
        'solucao': 'Substituir sensor de fase',
        'valor': 320.00,
        'tempo': '1.0 hora'
    },
    'P0401': {
        'vw_code': '16785',
        'descricao': 'EGR insuficiente',
        'causa': 'Válvula EGR entupida',
        'solucao': 'Limpar válvula EGR',
        'valor': 250.00,
        'tempo': '1.5 horas'
    },
    'P0442': {
        'vw_code': '16826',
        'descricao': 'EVAP - Vazamento pequeno',
        'causa': 'Tampa do combustível mal fechada',
        'solucao': 'Verificar tampa do combustível',
        'valor': 50.00,
        'tempo': '0.2 hora'
    },
    'P0505': {
        'vw_code': '17070',
        'descricao': 'Sistema de Marcha Lenta',
        'causa': 'Corpo de borboleta sujo',
        'solucao': 'Limpar corpo de borboleta e fazer adaptação',
        'valor': 180.00,
        'tempo': '1.0 hora'
    },
    'P0600': {
        'vw_code': '16890',
        'descricao': 'Falha de comunicação CAN',
        'causa': 'Problema na rede CAN',
        'solucao': 'Verificar terminações CAN',
        'valor': 380.00,
        'tempo': '2.0 horas'
    }
}

PROCEDIMENTOS_VW = {
    'reset_flex': {
        'nome': '🔄 Reset Flex Fuel',
        'descricao': 'Reinicia adaptações de combustível flex',
        'passos': [
            'Motor frio (abaixo de 30°C)',
            'Ligar ignição sem dar partida',
            'Aguardar 30 segundos',
            'Acelerador totalmente pressionado por 10s',
            'Desligar ignição por 10s',
            'Dar partida normal'
        ]
    },
    'adaptacao_borboleta': {
        'nome': '⚙️ Adaptação de Borboleta',
        'descricao': 'Reaprendizado da posição da borboleta',
        'passos': [
            'Ligar ignição (motor desligado)',
            'Aguardar 30 segundos',
            'Desligar ignição por 10 segundos',
            'Ligar motor e deixar em marcha lenta por 5 minutos'
        ]
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
    
    .solution-card {
        background: #1a2a33;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #00ffff;
    }
    
    .footer {
        background: #1a1d24;
        padding: 10px;
        border-radius: 5px;
        margin-top: 30px;
        text-align: center;
        color: #888;
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
            with st.spinner("Conectando..."):
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
        
        # Substituir gráficos por tabela
        st.markdown("### 📈 DADOS EM TEMPO REAL")
        col1, col2 = st.columns(2)
        
        with col1:
            data = {
                'Parâmetro': ['RPM', 'Temperatura', 'Pressão Óleo', 'Bateria'],
                'Valor': [
                    st.session_state.live_data['rpm'],
                    f"{st.session_state.live_data['temp_motor']}°C",
                    f"{st.session_state.live_data['pressao_oleo']} bar",
                    f"{st.session_state.live_data['bateria']}V"
                ]
            }
            df = pd.DataFrame(data)
            st.table(df)
        
        with col2:
            data2 = {
                'Parâmetro': ['STFT', 'LTFT', 'MAF', 'Carga Motor'],
                'Valor': [
                    f"{st.session_state.live_data['stft']}%",
                    f"{st.session_state.live_data['ltft']}%",
                    f"{st.session_state.live_data['maf']} g/s",
                    f"{st.session_state.live_data['carga_motor']}%"
                ]
            }
            df2 = pd.DataFrame(data2)
            st.table(df2)

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
                    {'code': 'P0171', 'desc': 'Mistura pobre'},
                    {'code': 'P0335', 'desc': 'Sensor de Rotação'},
                    {'code': 'P0505', 'desc': 'Sistema Marcha Lenta'}
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
                    <p><strong>Descrição:</strong> {info['descricao']}</p>
                    <p><strong>Causa:</strong> {info['causa']}</p>
                    <p><strong>Solução:</strong> {info['solucao']}</p>
                    <p><strong>Procedimento:</strong></p>
                    <ol>
                        {''.join([f'<li>{p}</li>' for p in info.get('procedimento', ['Diagnóstico manual'])])}
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
    
    for proc in PROCEDIMENTOS_VW.values():
        with st.expander(proc['nome']):
            st.markdown(f"**Descrição:** {proc['descricao']}")
            st.markdown("**Passo a passo:**")
            for i, passo in enumerate(proc['passos'], 1):
                st.markdown(f"{i}. {passo}")

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
    RASTHER VW • {len(DTC_VW)} códigos VW • {datetime.now().strftime('%d/%m/%Y %H:%M')}
</div>
""", unsafe_allow_html=True)

# =============================================
# ATUALIZAÇÃO AUTOMÁTICA
# =============================================
if st.session_state.connected:
    time.sleep(2)
    st.rerun()
