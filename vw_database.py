# vw_database_expandido.py - Banco de dados Volkswagen expandido

# =============================================
# MODELOS VW COMPLETOS
# =============================================
MODELOS_VW_COMPLETO = {
    'Gol': {
        'anos': '2008-2024',
        'motores': ['1.0 8V', '1.6 8V', '1.0 TSI', '1.6 MSI'],
        'geracoes': ['G4', 'G5', 'G6', 'G7'],
        'imagem': '🚗',
        'codigos': ['G5', 'G6', 'G7'],
        'observacoes': 'Modelo mais vendido do Brasil'
    },
    'Polo': {
        'anos': '2017-2024',
        'motores': ['1.0 TSI', '1.6 MSI', '200 TSI'],
        'geracoes': ['G6', 'G7'],
        'imagem': '🚘',
        'codigos': ['AW', 'BZ'],
        'observacoes': 'Plataforma MQB'
    },
    'Virtus': {
        'anos': '2018-2024',
        'motores': ['1.0 TSI', '1.6 MSI'],
        'geracoes': ['G1', 'G2'],
        'imagem': '🚙',
        'codigos': ['A8'],
        'observacoes': 'Sedã do Polo'
    },
    'T-Cross': {
        'anos': '2019-2024',
        'motores': ['1.0 TSI', '1.4 TSI'],
        'geracoes': ['G1'],
        'imagem': '🚐',
        'codigos': ['A11'],
        'observacoes': 'SUV compacto'
    },
    'Nivus': {
        'anos': '2020-2024',
        'motores': ['1.0 TSI'],
        'geracoes': ['G1'],
        'imagem': '🚗',
        'codigos': ['A12'],
        'observacoes': 'SUV cupê'
    },
    'Taos': {
        'anos': '2021-2024',
        'motores': ['1.4 TSI'],
        'geracoes': ['G1'],
        'imagem': '🚙',
        'codigos': ['A13'],
        'observacoes': 'SUV médio'
    },
    'Saveiro': {
        'anos': '2010-2024',
        'motores': ['1.6', '1.6 MSI'],
        'geracoes': ['G5', 'G6'],
        'imagem': '🛻',
        'codigos': ['LS'],
        'observacoes': 'Picape compacta'
    },
    'Amarok': {
        'anos': '2010-2024',
        'motores': ['2.0 TDI', '3.0 V6'],
        'geracoes': ['G1'],
        'imagem': '🛻',
        'codigos': ['2H'],
        'observacoes': 'Picape média'
    },
    'Jetta': {
        'anos': '2011-2024',
        'motores': ['1.4 TSI', '2.0 TSI', 'GLI'],
        'geracoes': ['G6', 'G7'],
        'imagem': '🚘',
        'codigos': ['162'],
        'observacoes': 'Sedã médio'
    },
    'Passat': {
        'anos': '2010-2020',
        'motores': ['2.0 TSI'],
        'geracoes': ['G7'],
        'imagem': '🚘',
        'codigos': ['3C'],
        'observacoes': 'Sedã grande'
    },
    'Tiguan': {
        'anos': '2012-2024',
        'motores': ['2.0 TSI'],
        'geracoes': ['G1', 'G2'],
        'imagem': '🚙',
        'codigos': ['5N'],
        'observacoes': 'SUV médio'
    },
    'Fox': {
        'anos': '2008-2020',
        'motores': ['1.0', '1.6'],
        'geracoes': ['G1', 'G2'],
        'imagem': '🚗',
        'codigos': ['5Z'],
        'observacoes': 'Hatch compacto'
    },
    'SpaceFox': {
        'anos': '2008-2020',
        'motores': ['1.6'],
        'geracoes': ['G1'],
        'imagem': '🚙',
        'codigos': ['5Z'],
        'observacoes': 'Perua compacta'
    },
    'Up': {
        'anos': '2014-2020',
        'motores': ['1.0'],
        'geracoes': ['G1'],
        'imagem': '🚗',
        'codigos': ['AA'],
        'observacoes': 'Hatch urbano'
    }
}

# =============================================
# DTCs VW EXPANDIDOS (30+ códigos)
# =============================================
DTC_VW_EXPANDIDO = {
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
        'dificuldade': 'Fácil',
        'frequencia': 'Alta (40.000km+)',
        'motores': ['EA111', 'EA211']
    },
    'P0302': {
        'vw_code': '17918',
        'descricao': 'Falha de ignição - Cilindro 2',
        'causa': 'Bobina de ignição com defeito',
        'solucao': 'Substituir bobina Bosch 06K905110',
        'procedimento': [
            'Trocar bobina com cilindro 1 para teste',
            'Se falha acompanhar, substituir bobina'
        ],
        'valor': 450.00,
        'tempo': '1.5 horas',
        'dificuldade': 'Fácil',
        'motores': ['EA111', 'EA211']
    },
    'P0303': {
        'vw_code': '17919',
        'descricao': 'Falha de ignição - Cilindro 3',
        'causa': 'Bobina de ignição com defeito',
        'solucao': 'Substituir bobina',
        'valor': 450.00,
        'tempo': '1.5 horas',
        'dificuldade': 'Fácil',
        'motores': ['EA111', 'EA211']
    },
    'P0304': {
        'vw_code': '17920',
        'descricao': 'Falha de ignição - Cilindro 4',
        'causa': 'Bobina de ignição com defeito',
        'solucao': 'Substituir bobina',
        'valor': 450.00,
        'tempo': '1.5 horas',
        'dificuldade': 'Fácil',
        'motores': ['EA111', 'EA211']
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
        'dificuldade': 'Médio',
        'motores': ['EA111', 'EA211', 'EA888']
    },
    'P0430': {
        'vw_code': '16814',
        'descricao': 'Catalisador ineficiente - Banco 2',
        'causa': 'Catalisador ou sonda lambda com defeito',
        'solucao': 'Diagnóstico similar ao P0420',
        'valor': 1850.00,
        'tempo': '3.0 horas',
        'motores': ['EA888']
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
        'dificuldade': 'Médio',
        'motores': ['EA111', 'EA211']
    },
    'P0172': {
        'vw_code': '17536',
        'descricao': 'Mistura rica (Banco 1)',
        'causa': 'Injetores com defeito ou pressão de combustível alta',
        'solucao': 'Verificar injetores e pressão de combustível',
        'valor': 450.00,
        'tempo': '2.0 horas',
        'motores': ['EA111', 'EA211']
    },
    'P0130': {
        'vw_code': '16514',
        'descricao': 'Sonda Lambda - Circuito (Banco 1 Sensor 1)',
        'causa': 'Sonda lambda com defeito ou fiação danificada',
        'solucao': 'Verificar sonda e fiação',
        'valor': 380.00,
        'tempo': '1.0 hora',
        'motores': ['EA111', 'EA211', 'EA888']
    },
    'P0131': {
        'vw_code': '16515',
        'descricao': 'Sonda Lambda - Tensão baixa',
        'causa': 'Sonda lambda com defeito',
        'solucao': 'Substituir sonda lambda',
        'valor': 380.00,
        'tempo': '1.0 hora',
        'motores': ['EA111', 'EA211']
    },
    'P0132': {
        'vw_code': '16516',
        'descricao': 'Sonda Lambda - Tensão alta',
        'causa': 'Sonda lambda com defeito',
        'solucao': 'Substituir sonda lambda',
        'valor': 380.00,
        'tempo': '1.0 hora',
        'motores': ['EA111', 'EA211']
    },
    'P0133': {
        'vw_code': '16517',
        'descricao': 'Sonda Lambda - Resposta lenta',
        'causa': 'Sonda lambda envelhecida',
        'solucao': 'Substituir sonda lambda',
        'valor': 380.00,
        'tempo': '1.0 hora',
        'motores': ['EA111', 'EA211']
    },
    'P0134': {
        'vw_code': '16518',
        'descricao': 'Sonda Lambda - Circuito inativo',
        'causa': 'Sonda lambda desconectada',
        'solucao': 'Verificar conexão da sonda',
        'valor': 150.00,
        'tempo': '0.5 hora',
        'motores': ['EA111', 'EA211']
    },
    'P0135': {
        'vw_code': '16519',
        'descricao': 'Sonda Lambda - Aquecimento',
        'causa': 'Resistência de aquecimento queimada',
        'solucao': 'Substituir sonda lambda',
        'valor': 380.00,
        'tempo': '1.0 hora',
        'motores': ['EA111', 'EA211']
    },
    'P0140': {
        'vw_code': '16520',
        'descricao': 'Sonda Lambda - Circuito inativo (Banco 1 Sensor 2)',
        'causa': 'Sonda pós-catalisador com defeito',
        'solucao': 'Substituir sonda',
        'valor': 380.00,
        'tempo': '1.0 hora',
        'motores': ['EA111', 'EA211']
    },
    'P0141': {
        'vw_code': '16521',
        'descricao': 'Sonda Lambda - Aquecimento (Banco 1 Sensor 2)',
        'causa': 'Aquecedor da sonda com defeito',
        'solucao': 'Substituir sonda',
        'valor': 380.00,
        'tempo': '1.0 hora',
        'motores': ['EA111', 'EA211']
    },
    'P0321': {
        'vw_code': '16711',
        'descricao': 'Sensor de Rotação - Sinal',
        'causa': 'Sensor CKP com defeito',
        'solucao': 'Substituir sensor de rotação',
        'valor': 290.00,
        'tempo': '1.0 hora',
        'motores': ['EA111', 'EA211']
    },
    'P0322': {
        'vw_code': '16712',
        'descricao': 'Sensor de Rotação - Sem sinal',
        'causa': 'Sensor CKP com defeito ou fiação partida',
        'solucao': 'Verificar sensor e fiação',
        'valor': 290.00,
        'tempo': '1.5 horas',
        'motores': ['EA111', 'EA211']
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
        'dificuldade': 'Médio',
        'motores': ['EA111', 'EA211']
    },
    'P0336': {
        'vw_code': '16706',
        'descricao': 'Sensor de Rotação - Faixa/Performance',
        'causa': 'Sinal inconsistente do sensor',
        'solucao': 'Verificar anel fônico e sensor',
        'valor': 290.00,
        'tempo': '1.0 hora',
        'motores': ['EA111', 'EA211']
    },
    'P0340': {
        'vw_code': '16717',
        'descricao': 'Sensor de Fase - Circuito',
        'causa': 'Sensor CMP com defeito',
        'solucao': 'Substituir sensor de fase',
        'valor': 320.00,
        'tempo': '1.0 hora',
        'motores': ['EA211']
    },
    'P0341': {
        'vw_code': '16718',
        'descricao': 'Sensor de Fase - Fora de fase',
        'causa': 'Sincronismo do motor incorreto',
        'solucao': 'Verificar corrente de comando',
        'valor': 450.00,
        'tempo': '2.0 horas',
        'motores': ['EA211']
    },
    'P0400': {
        'vw_code': '16784',
        'descricao': 'EGR - Fluxo insuficiente',
        'causa': 'Válvula EGR entupida',
        'solucao': 'Limpar válvula EGR',
        'valor': 250.00,
        'tempo': '1.5 horas',
        'motores': ['EA111']
    },
    'P0401': {
        'vw_code': '16785',
        'descricao': 'EGR - Fluxo insuficiente detectado',
        'causa': 'Válvula EGR entupida',
        'solucao': 'Limpar válvula EGR',
        'valor': 250.00,
        'tempo': '1.5 horas',
        'motores': ['EA111']
    },
    'P0402': {
        'vw_code': '16786',
        'descricao': 'EGR - Fluxo excessivo',
        'causa': 'Válvula EGR aberta',
        'solucao': 'Substituir válvula EGR',
        'valor': 380.00,
        'tempo': '1.5 horas',
        'motores': ['EA111']
    },
    'P0411': {
        'vw_code': '16795',
        'descricao': 'Injeção de ar secundário - Fluxo incorreto',
        'causa': 'Bomba de ar secundário com defeito',
        'solucao': 'Verificar bomba e válvulas',
        'valor': 580.00,
        'tempo': '2.0 horas',
        'motores': ['EA111']
    },
    'P0441': {
        'vw_code': '16825',
        'descricao': 'Sistema EVAP - Fluxo incorreto',
        'causa': 'Válvula de purga com defeito',
        'solucao': 'Substituir válvula de purga',
        'valor': 280.00,
        'tempo': '1.0 hora',
        'motores': ['EA111', 'EA211']
    },
    'P0442': {
        'vw_code': '16826',
        'descricao': 'Sistema EVAP - Vazamento pequeno',
        'causa': 'Tampa do combustível mal fechada',
        'solucao': 'Verificar tampa do combustível',
        'valor': 50.00,
        'tempo': '0.2 hora',
        'motores': ['TODOS']
    },
    'P0455': {
        'vw_code': '16839',
        'descricao': 'Sistema EVAP - Vazamento grande',
        'causa': 'Mangueiras soltas ou danificadas',
        'solucao': 'Verificar mangueiras do sistema',
        'valor': 180.00,
        'tempo': '1.0 hora',
        'motores': ['TODOS']
    },
    'P0501': {
        'vw_code': '17069',
        'descricao': 'Sensor de Velocidade - Faixa/Performance',
        'causa': 'Sensor VSS com defeito',
        'solucao': 'Substituir sensor de velocidade',
        'valor': 220.00,
        'tempo': '1.0 hora',
        'motores': ['TODOS']
    },
    'P0505': {
        'vw_code': '17070',
        'descricao': 'Sistema de Marcha Lenta',
        'causa': 'Corpo de borboleta sujo',
        'solucao': 'Limpar corpo de borboleta e fazer adaptação',
        'procedimento': [
            'Remover duto de ar',
            'Limpar borboleta com cleaner',
            'Religar e fazer adaptação'
        ],
        'valor': 180.00,
        'tempo': '1.0 hora',
        'dificuldade': 'Fácil',
        'motores': ['EA111', 'EA211']
    },
    'P0506': {
        'vw_code': '17071',
        'descricao': 'Marcha Lenta baixa',
        'causa': 'Corpo de borboleta sujo',
        'solucao': 'Limpar corpo de borboleta',
        'valor': 180.00,
        'tempo': '1.0 hora',
        'motores': ['EA111', 'EA211']
    },
    'P0507': {
        'vw_code': '17072',
        'descricao': 'Marcha Lenta alta',
        'causa': 'Vazamento de vácuo',
        'solucao': 'Verificar mangueiras de vácuo',
        'valor': 150.00,
        'tempo': '1.0 hora',
        'motores': ['EA111', 'EA211']
    },
    'P0600': {
        'vw_code': '16890',
        'descricao': 'Falha de comunicação serial',
        'causa': 'Problema na rede CAN',
        'solucao': 'Verificar terminações CAN',
        'valor': 380.00,
        'tempo': '2.0 horas',
        'motores': ['TODOS']
    },
    'P0601': {
        'vw_code': '16891',
        'descricao': 'Falha de memória interna',
        'causa': 'Checksum da ECU inválido',
        'solucao': 'Reprogramar ECU',
        'valor': 580.00,
        'tempo': '2.0 horas',
        'motores': ['TODOS']
    }
}

# =============================================
# PROCEDIMENTOS VW EXPANDIDOS
# =============================================
PROCEDIMENTOS_VW_EXPANDIDO = {
    'reset_flex': {
        'nome': 'Reset Flex Fuel',
        'descricao': 'Reinicia as adaptações de combustível flex (etanol/gasolina)',
        'motores': ['EA111', 'EA211'],
        'passos': [
            'Motor frio (temperatura abaixo de 30°C)',
            'Ligar ignição sem dar partida',
            'Aguardar 30 segundos',
            'Pressionar acelerador totalmente por 10 segundos',
            'Desligar ignição e aguardar 10 segundos',
            'Dar partida normal'
        ],
        'quando': [
            'Após troca de combustível',
            'Quando aparecer falha P0171',
            'A cada 10.000km preventivamente'
        ],
        'dicas': 'Não acelerar durante o processo de reset'
    },
    'adaptacao_borboleta': {
        'nome': 'Adaptação de Corpo de Borboleta',
        'descricao': 'Reaprendizado da posição da borboleta após limpeza',
        'motores': ['EA111', 'EA211'],
        'passos': [
            'Ligar ignição (motor desligado)',
            'Aguardar 30 segundos (borboleta fará movimento)',
            'Desligar ignição por 10 segundos',
            'Ligar motor e deixar em marcha lenta por 5 minutos',
            'Não acelerar durante o processo'
        ],
        'quando': [
            'Após limpeza do corpo de borboleta',
            'Quando marcha lenta estiver irregular',
            'Após troca da bateria'
        ],
        'dicas': 'Pode ser necessário fazer 2-3 ciclos para aprendizado completo'
    },
    'casamento_chaves': {
        'nome': 'Casamento de Chaves CAN-BUS',
        'descricao': 'Registro de novas chaves no imobilizador',
        'motores': ['TODOS'],
        'passos': [
            'Ter todas as chaves que serão programadas',
            'Inserir chave válida e ligar ignição',
            'Aguardar luz do imobilizador apagar',
            'Inserir nova chave e ligar ignição',
            'Repetir para até 4 chaves'
        ],
        'quando': [
            'Perda de chaves',
            'Substituição do módulo imobilizador',
            'Adquirir chave reserva'
        ],
        'dicas': 'Processo deve ser feito com todas as chaves presentes'
    },
    'reset_imotion': {
        'nome': 'Reset de Adaptação I-Motion',
        'descricao': 'Reaprendizado do ponto de embreagem do câmbio automatizado',
        'motores': ['EA111', 'EA211'],
        'passos': [
            'Veículo em local plano',
            'Ligar motor e deixar em marcha lenta',
            'Pisar no freio e engatar primeira marcha',
            'Aguardar 30 segundos',
            'Repetir para as demais marchas'
        ],
        'quando': [
            'Após substituição da embreagem',
            'Trocas bruscas ou lentas',
            'Após reset da central'
        ],
        'dicas': 'Pode levar até 10 minutos para aprendizado completo'
    },
    'reset_abs': {
        'nome': 'Sangria e Reset ABS',
        'descricao': 'Procedimento para sangria do sistema ABS',
        'motores': ['TODOS'],
        'passos': [
            'Conectar scanner ao veículo',
            'Acessar módulo ABS',
            'Selecionar função "Sangria"',
            'Seguir instruções na tela',
            'Testar sistema após conclusão'
        ],
        'quando': [
            'Após troca de fluido de freio',
            'Entrada de ar no sistema',
            'Substituição de componentes do ABS'
        ],
        'dicas': 'Necessário scanner com função específica'
    },
    'reset_airbag': {
        'nome': 'Reset Airbag',
        'descricao': 'Limpeza de códigos e reset do sistema airbag',
        'motores': ['TODOS'],
        'passos': [
            'Verificar se todos os conectores estão firmes',
            'Ler códigos de falha',
            'Reparar problemas encontrados',
            'Limpar códigos de falha',
            'Verificar luz do airbag'
        ],
        'quando': [
            'Luz do airbag acesa',
            'Após reparo no sistema',
            'Troca de bancos'
        ],
        'dicas': 'Muito cuidado ao trabalhar com sistema airbag'
    }
}
