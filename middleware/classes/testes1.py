import threading
import time
import random

from ServerRequestHandler import ServerRequestHandler
from ClientRequestHandler import ClientRequestHandler
from Marshaller import Marshaller

# Configurações
HOST = 'localhost'
PORT = 8085
QTD_ENVIOS = 10  # Quantas vezes o cliente vai mandar dados

# ==============================================================================
# LÓGICA DO SERVIDOR (A CENTRAL)
# ==============================================================================
def rodar_servidor():
    print("[Central] Inicializando sistema de multas...")
    srh = ServerRequestHandler(HOST, PORT)
    marshaller = Marshaller()
    
    print("[Central] Aguardando infrações...")
    
    while True:
        # 1. BLOQUEIO: O servidor para aqui e espera um CRH conectar
        # Na Opção 1, cada mensagem é uma nova conexão aceita.
        bytes_recebidos = srh.receive()
        
        if bytes_recebidos is None:
            # Isso acontece se der erro grave no socket
            continue

        # 2. Desempacota (Bytes -> Objeto Python)
        dados = marshaller.unmarshal(bytes_recebidos)
        
        # 3. Processa a lógica de negócio
        if isinstance(dados, dict):
            placa = dados.get('placa')
            velocidade = dados.get('velocidade')
            
            # Simula processamento
            status = "MULTADO 🚨" if velocidade > 100 else "Dentro do limite 👍"
            
            print(f"\n--- [CENTRAL RECEBEU] ---")
            print(f"   Radar ID: {dados.get('id_radar')}")
            print(f"   Carro: {placa} a {velocidade} km/h")
            print(f"   Análise: {status}")
            print(f"-------------------------")
        else:
            print(f"[Central] Recebeu dados desconhecidos: {dados}")

# ==============================================================================
# LÓGICA DO CLIENTE (O RADAR)
# ==============================================================================
def rodar_sensor():
    # Espera um pouquinho para garantir que o servidor subiu
    time.sleep(1)
    
    crh = ClientRequestHandler(HOST, PORT)
    marshaller = Marshaller()
    
    print("[Sensor] Radar ligado e operando!")
    
    for i in range(QTD_ENVIOS):
        # 1. Gera dados dinâmicos aleatórios
        velocidade_leitura = random.randint(40, 140)
        placa_fake = f"ABC-{random.randint(1000, 9999)}"
        
        payload = {
            'id_radar': 'BR-101-KM50',
            'timestamp': time.time(),
            'placa': placa_fake,
            'velocidade': velocidade_leitura
        }
        
        print(f"[Sensor] Capturou {placa_fake} a {velocidade_leitura} km/h... Enviando.")
        
        # 2. Serializa (Objeto -> Bytes)
        msg_bytes = marshaller.marshal(payload)
        
        # 3. Envia via CRH
        # OBS: O CRH vai Conectar -> Enviar -> Desconectar
        try:
            crh.send(msg_bytes)
        except Exception as e:
            print(f"[Sensor] Falha ao enviar: {e}")
        
        # Simula o tempo entre um carro e outro passar no radar
        # Isso deixa o teste dinâmico e visual
        intervalo = random.uniform(0.5, 2.0)
        time.sleep(intervalo)
        
    print("[Sensor] Fim do expediente. Desligando radar.")
    # Hack para fechar o programa de teste pois o servidor está em loop infinito
    import os
    os._exit(0) 

# ==============================================================================
# EXECUÇÃO PARALELA (THREADS)
# ==============================================================================
if __name__ == "__main__":
    # Cria uma thread para o servidor e outra para o cliente
    # Assim eles rodam "ao mesmo tempo" no seu terminal
    t_server = threading.Thread(target=rodar_servidor)
    t_client = threading.Thread(target=rodar_sensor)
    
    # Daemon=True significa que se o programa principal fechar, a thread morre
    t_server.daemon = True 
    
    t_server.start()
    t_client.start()
    
    # Mantém o script principal rodando enquanto as threads trabalham
    try:
        while t_client.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        print("Encerrando teste.")