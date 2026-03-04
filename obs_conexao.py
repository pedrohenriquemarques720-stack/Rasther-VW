# obd_conexao.py - Conexão real com veículo via OBD-II

import obd
import serial
import serial.tools.list_ports
import time
import threading
from typing import Dict, Optional, List
import streamlit as st

class ConexaoOBDReal:
    """
    Classe para conexão real com veículo via OBD-II
    Suporta ELM327, STN2120 e adaptadores compatíveis
    """
    
    def __init__(self):
        self.connection = None
        self.connected = False
        self.porta_encontrada = None
        self.dados_em_tempo_real = {}
        self.thread_leitura = None
        self.rodando = False
        
    def scan_ports(self) -> List[Dict]:
        """Escaneia portas seriais disponíveis"""
        ports = []
        for port in serial.tools.list_ports.comports():
            port_info = {
                'device': port.device,
                'description': port.description,
                'hwid': port.hwid,
                'tipo': 'USB' if 'USB' in port.description.upper() else 'Desconhecido'
            }
            ports.append(port_info)
        return ports
    
    def auto_detect_elm327(self) -> Optional[str]:
        """Detecta automaticamente adaptador ELM327"""
        for port in serial.tools.list_ports.comports():
            if 'USB' in port.description.upper() or 'ELM' in port.description.upper():
                try:
                    # Testa conexão rápida
                    test_conn = obd.OBD(port.device, timeout=1)
                    if test_conn.is_connected():
                        test_conn.close()
                        return port.device
                except:
                    continue
        return None
    
    def conectar(self, porta: str = None, baudrate: int = 38400) -> bool:
        """
        Conecta ao veículo via OBD-II
        
        Args:
            porta: Porta COM (ex: COM3, /dev/ttyUSB0). Se None, auto-detect
            baudrate: Taxa de comunicação (padrão 38400)
        """
        try:
            if porta is None:
                porta = self.auto_detect_elm327()
                if not porta:
                    st.error("❌ Nenhum adaptador ELM327 encontrado")
                    return False
            
            with st.spinner(f"Conectando em {porta}..."):
                self.connection = obd.OBD(porta, baudrate=baudrate, timeout=2)
                
                if self.connection.is_connected():
                    self.connected = True
                    self.porta_encontrada = porta
                    
                    # Obtém informações do veículo
                    self.vehicle_info = self._get_vehicle_info()
                    
                    # Inicia thread de leitura contínua
                    self._start_data_stream()
                    
                    st.success(f"✅ Conectado! Protocolo: {self.connection.protocol_name()}")
                    return True
                else:
                    st.error("❌ Falha na conexão")
                    return False
                    
        except Exception as e:
            st.error(f"❌ Erro na conexão: {e}")
            return False
    
    def _get_vehicle_info(self) -> Dict:
        """Obtém informações básicas do veículo"""
        info = {
            'protocolo': self.connection.protocol_name(),
            'vin': 'N/A',
            'el
