# obd_conexao.py - Conexão real com veículo via OBD-II

import obd
import serial
import serial.tools.list_ports
import time
import threading
from typing import Dict, Optional, List, Any
from datetime import datetime
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
        self.dados = {
            'rpm': 0,
            'velocidade': 0,
            'temp_motor': 0,
            'pressao_oleo': 0,
            'bateria': 0,
            'stft': 0,
            'ltft': 0,
            'maf': 0,
            'carga_motor': 0,
            'avanco': 0,
            'sonda_lambda': 0,
            'timestamps': []
        }
        self.thread_leitura = None
        self.rodando = False
        self.vehicle_info = {
            'protocolo': '---',
            'vin': '---',
            'fabricante': '---',
            'modelo': '---',
            'ano': '---'
        }
        
    def scan_ports(self) -> List[Dict]:
        """Escaneia portas seriais disponíveis"""
        ports = []
        try:
            for port in serial.tools.list_ports.comports():
                port_info = {
                    'device': port.device,
                    'description': port.description,
                    'hwid': port.hwid,
                    'tipo': 'USB' if 'USB' in port.description.upper() else 'Serial'
                }
                ports.append(port_info)
        except Exception as e:
            st.error(f"Erro ao escanear portas: {e}")
        return ports
    
    def auto_detect_elm327(self) -> Optional[str]:
        """Detecta automaticamente adaptador ELM327"""
        try:
            for port in serial.tools.list_ports.comports():
                if 'USB' in port.description.upper() or 'ELM' in port.description.upper():
                    # Testa conexão rápida
                    test_conn = obd.OBD(port.device, timeout=1)
                    if test_conn.is_connected():
                        test_conn.close()
                        return port.device
        except Exception as e:
            st.error(f"Erro na detecção: {e}")
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
                with st.spinner("🔍 Procurando adaptador ELM327..."):
                    porta = self.auto_detect_elm327()
                    if not porta:
                        st.error("❌ Nenhum adaptador ELM327 encontrado")
                        return False
                    st.success(f"✅ Adaptador encontrado em {porta}")
            
            with st.spinner(f"📡 Conectando em {porta}..."):
                self.connection = obd.OBD(porta, baudrate=baudrate, timeout=2)
                
                if self.connection.is_connected():
                    self.connected = True
                    self.porta_encontrada = porta
                    
                    # Obtém informações do veículo
                    self._get_vehicle_info()
                    
                    # Inicia thread de leitura contínua
                    self._start_data_stream()
                    
                    st.success(f"✅ Conectado! Protocolo: {self.connection.protocol_name()}")
                    return True
                else:
                    st.error("❌ Falha na conexão. Verifique o cabo.")
                    return False
                    
        except Exception as e:
            st.error(f"❌ Erro na conexão: {e}")
            return False
    
    def _get_vehicle_info(self):
        """Obtém informações básicas do veículo"""
        try:
            self.vehicle_info['protocolo'] = self.connection.protocol_name()
            
            # Tenta ler VIN
            vin_response = self.connection.query(obd.commands.VIN)
            if vin_response.value:
                self.vehicle_info['vin'] = str(vin_response.value)
                
            # Tenta identificar fabricante pelo VIN
            if self.vehicle_info['vin'].startswith('9BW'):
                self.vehicle_info['fabricante'] = 'Volkswagen'
                
        except Exception as e:
            print(f"Erro ao obter informações: {e}")
    
    def _start_data_stream(self):
        """Inicia thread de leitura contínua"""
        self.rodando = True
        self.thread_leitura = threading.Thread(target=self._data_loop)
        self.thread_leitura.daemon = True
        self.thread_leitura.start()
    
    def _data_loop(self):
        """Loop principal de leitura de dados"""
        while self.rodando and self.connected:
            try:
                # RPM
                rpm = self.connection.query(obd.commands.RPM)
                if rpm.value:
                    self.dados['rpm'] = int(rpm.value.magnitude)
                
                # Velocidade
                speed = self.connection.query(obd.commands.SPEED)
                if speed.value:
                    self.dados['velocidade'] = int(speed.value.magnitude)
                
                # Temperatura do motor
                temp = self.connection.query(obd.commands.COOLANT_TEMP)
                if temp.value:
                    self.dados['temp_motor'] = int(temp.value.magnitude)
                
                # Short Term Fuel Trim
                stft = self.connection.query(obd.commands.SHORT_FUEL_TRIM_1)
                if stft.value:
                    self.dados['stft'] = stft.value.magnitude
                
                # Long Term Fuel Trim
                ltft = self.connection.query(obd.commands.LONG_FUEL_TRIM_1)
                if ltft.value:
                    self.dados['ltft'] = ltft.value.magnitude
                
                # MAF
                maf = self.connection.query(obd.commands.MAF)
                if maf.value:
                    self.dados['maf'] = maf.value.magnitude
                
                # Tensão da bateria
                volt = self.connection.query(obd.commands.ELM_VOLTAGE)
                if volt.value:
                    self.dados['bateria'] = float(volt.value.magnitude)
                
                # Carga do motor
                load = self.connection.query(obd.commands.ENGINE_LOAD)
                if load.value:
                    self.dados['carga_motor'] = load.value.magnitude
                
                # Avanço de ignição
                timing = self.connection.query(obd.commands.TIMING_ADVANCE)
                if timing.value:
                    self.dados['avanco'] = timing.value.magnitude
                
                # Timestamp
                self.dados['timestamps'].append(time.time())
                if len(self.dados['timestamps']) > 100:
                    self.dados['timestamps'] = self.dados['timestamps'][-100:]
                
            except Exception as e:
                print(f"Erro na leitura: {e}")
            
            time.sleep(0.1)  # 10 Hz
    
    def ler_dtcs(self) -> List[Dict]:
        """Lê códigos de falha do veículo"""
        dtcs = []
        try:
            response = self.connection.query(obd.commands.GET_DTC)
            if response.value:
                for code in response.value:
                    dtcs.append({
                        'code': str(code),
                        'desc': 'Código de falha'
                    })
        except Exception as e:
            print(f"Erro ao ler DTCs: {e}")
        return dtcs
    
    def limpar_dtcs(self) -> bool:
        """Limpa códigos de falha"""
        try:
            self.connection.query(obd.commands.CLEAR_DTC)
            return True
        except:
            return False
    
    def get_dados(self) -> Dict:
        """Retorna últimos dados lidos"""
        return self.dados.copy()
    
    def desconectar(self):
        """Desconecta do veículo"""
        self.rodando = False
        self.connected = False
        if self.thread_leitura:
            self.thread_leitura.join(timeout=2)
        if self.connection:
            self.connection.close()
        st.success("✅ Desconectado do veículo")
