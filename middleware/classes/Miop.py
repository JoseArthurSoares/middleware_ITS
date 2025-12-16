"""
Miop.py Simplificado
Trabalha puramente com Dicionários. Elimina classes desnecessárias.
"""

def createRequestMIOP(op, params):
    """Cria um pacote de requisição simples."""
    return {
        'type': 'REQ',
        'OP': op,
        'params': params
    }

def createReplyMIOP(result):
    """Cria um pacote de resposta simples."""
    return {
        'type': 'REP',
        'result': result
    }

def extractRequest(packet):
    """
    Recebe um dicionário (ou objeto) e normaliza para:
    {'OP': 'NomeDaOperacao', 'params': [arg1, arg2]}
    """
    # 1. Garante que é um dicionário
    data = packet
    if not isinstance(packet, dict):
        # Se por acaso chegar um objeto antigo, tenta converter
        data = getattr(packet, 'bd', packet)
        if hasattr(data, '__dict__'): data = data.__dict__

    # 2. Extrai Operação (Case insensitive)
    op = data.get('OP') or data.get('op')
    params = data.get('params') or data.get('args') or []

    # 3. AUTO-CORREÇÃO (Compatibilidade com seu Cliente atual)
    # Se params estiver vazio, mas tivermos chaves soltas, montamos a lista.
    if op and not params:
        # Pega valores soltos e trata listas de um elemento ['T1'] -> 'T1'
        q_id = data.get('queue_id')
        if isinstance(q_id, list) and q_id: q_id = q_id[0]
        
        s_id = data.get('sensor_id')
        msg  = data.get('MSG')

        if op == 'Publish' and q_id and msg:
            params = [q_id, msg]
        
        elif op in ['Subscribe', 'CheckMsg'] and q_id and s_id:
            params = [q_id, s_id]

    return {'OP': op, 'params': params}