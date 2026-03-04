# gerar_tutoriais.py - Gera arquivos markdown com tutoriais

import os
from datetime import datetime

class GeradorTutoriais:
    """Gera tutoriais em formato markdown para os procedimentos"""
    
    def __init__(self):
        self.output_dir = "tutoriais"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def gerar_tutorial_reset_flex(self):
        """Tutorial passo a passo do Reset Flex Fuel"""
        
        tutorial = f"""# 🔄 RESET FLEX FUEL - VOLKSWAGEN
**Data:** {datetime.now().strftime('%d/%m/%Y')}
**Modelos:** Gol, Polo, Virtus (EA111/EA211)

---

## 📋 **Descrição**
O Reset Flex Fuel reinicia as adaptações de combustível da central eletrônica, permitindo que o motor reaprenda a trabalhar com etanol ou gasolina.

## ⚠️ **Quando realizar**
- ✅ Após troca de combustível (etanol ↔ gasolina)
- ✅ Quando aparecer falha P0171 (mistura pobre)
- ✅ A cada 10.000km preventivamente
- ✅ Após limpeza de bicos injetores

---

## 🔧 **Materiais necessários**
- ✅ Scanner RASTHER VW (ou qualquer scanner com função OBD-II)
- ✅ Chave de ignição do veículo
- ✅ Paciência (processo leva cerca de 2 minutos)

---

## 📝 **Passo a Passo Detalhado**

### **Passo 1: Preparação**
1. Estacione o veículo em local plano e seguro
2. Motor deve estar **frio** (temperatura abaixo de 30°C)
3. Todos os equipamentos elétricos desligados (faróis, ar condicionado, som)

### **Passo 2: Conexão**
1. Conecte o scanner RASTHER VW à porta OBD-II
2. Aguarde a inicialização do sistema
3. Verifique se a conexão foi estabelecida (luz verde)

### **Passo 3: Execução**
1. Ligue a ignição **sem dar partida** (apenas uma luz no painel)
2. Aguarde **30 segundos** exatos
3. Pressione o pedal do acelerador **totalmente** (até o fim do curso)
4. Mantenha pressionado por **10 segundos** exatos
5. Solte o acelerador
6. Desligue a ignição e aguarde **10 segundos**
7. Dê partida normal no motor

### **Passo 4: Verificação**
1. Deixe o motor funcionando em marcha lenta por 2 minutos
2. Verifique se a marcha lenta está estável (entre 750-850 RPM)
3. Teste o veículo em baixas rotações

---

## 🎥 **Vídeo Tutorial**
[Assista ao vídeo completo](https://youtube.com/rasther-vw/reset-flex)
