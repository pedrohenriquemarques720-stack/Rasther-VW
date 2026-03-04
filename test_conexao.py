# test_conexao.py - Teste rápido da conexão OBD-II

import time
from obd_conexao import ConexaoOBDReal

def testar_conexao():
    """Testa a conexão com o veículo"""
    
    print("=" * 50)
    print("🔧 TESTE DE CONEXÃO OBD-II")
    print("=" * 50)
    
    # 1. Escanear portas
    print("\n📡 Escaneando portas...")
    con = ConexaoOBDReal()
    ports = con.scan_ports()
    
    if not ports:
        print("❌ Nenhuma porta serial encontrada")
        return
    
    print(f"✅ {len(ports)} porta(s) encontrada(s):")
    for p in ports:
        print(f"   • {p['device']} - {p['description']}")
    
    # 2. Tentar conectar
    print("\n🔌 Tentando conectar...")
    if con.conectar():
        print(f"\n✅ Conectado com sucesso!")
        print(f"   Protocolo: {con.vehicle_info['protocolo']}")
        print(f"   VIN: {con.vehicle_info['vin']}")
        
        # 3. Ler dados por 5 segundos
        print("\n📊 Lendo dados em tempo real (5s)...")
        for i in range(10):
            dados = con.get_dados()
            print(f"\r   RPM: {dados['rpm']} | Temp: {dados['temp_motor']}°C | Bateria: {dados['bateria']}V", end="")
            time.sleep(0.5)
        
        # 4. Desconectar
        print("\n\n🔌 Desconectando...")
        con.desconectar()
    else:
        print("❌ Falha na conexão")

if __name__ == "__main__":
    testar_conexao()
