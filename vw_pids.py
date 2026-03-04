# modules/vw_pids.py - PIDs exclusivos Volkswagen

class VW_PIDS:
    """Banco de dados de PIDs específicos Volkswagen"""
    
    MOTORES_EA211 = {
        '1.0 TSI': {
            'codigo': 'CHY/CJZ',
            'potencia': '105cv',
            'ano': '2016-2024'
        },
        '1.6 MSI': {
            'codigo': 'CJVD',
            'potencia': '110cv',
            'ano': '2016-2024'
        },
        '1.4 TSI': {
            'codigo': 'CJKA',
            'potencia': '150cv',
            'ano': '2018-2024'
        }
    }
    
    MOTORES_EA111 = {
        '1.0': {
            'codigo': 'CHY',
            'potencia': '76cv',
            'ano': '2008-2015'
        },
        '1.6': {
            'codigo': 'CJZ',
            'potencia': '101cv',
            'ano': '2008-2015'
        }
    }
    
    PIDS_ESPECIFICOS = {
        # Reset Flex Fuel
        0xF101: {
            'nome': 'Reset Adaptação Flex',
            'descricao': 'Reinicia parâmetros de adaptação etanol/gasolina',
            'motores': ['EA111', 'EA211'],
            'comando': 'UDS 0x2E',
            'seguranca': 'Nível 1'
        },
        
        # Adaptação Borboleta
        0xF102: {
            'nome': 'Reset Corpo Borboleta',
            'descricao': 'Reaprendizado da posição da borboleta',
            'motores': ['EA111', 'EA211'],
            'comando': 'UDS 0x2E',
            'seguranca': 'Nível 1'
        },
        
        # Correção Injetores
        0xF103: {
            'nome': 'Correção Injetores',
            'descricao': 'Ajuste fino por cilindro',
            'motores': ['EA211'],
            'comando': 'UDS 0x2E',
            'seguranca': 'Nível 2'
        },
        
        # Casamento de Chaves
        0xF104: {
            'nome': 'Programação Chaves',
            'descricao': 'Registro de novas chaves',
            'motores': ['TODOS'],
            'comando': 'UDS 0x31',
            'seguranca': 'Nível 3'
        }
    }