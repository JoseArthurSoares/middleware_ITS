import time
from ClientProxy import ClientProxy

class TrafficDashboard:
    def __init__(self, sensor_id="Dash_GUI_01", topic="Transito/Velocidade", host='localhost', port=8080):
        # Conecta ao Proxy
        self.proxy = ClientProxy(host, port)
        self.sensor_id = sensor_id
        self.topic = topic

    def start(self):
        print(f"--- Iniciando Dashboard de Monitoramento [{self.sensor_id}] ---")
        
        # ---------------------------------------------------------------------
        # PASSO 1: Assinar o Tópico (Subscribe)
        # ---------------------------------------------------------------------
        print(f"[Sub] Solicitando assinatura no tópico: '{self.topic}'...")
        
        try:
            ack = self.proxy.subscribe(self.topic, self.sensor_id)
            print(f"[Sub] Broker confirmou: {ack}")
        except Exception as e:
            print(f"[Sub] Erro crítico ao assinar: {e}")
            return

        # ---------------------------------------------------------------------
        # PASSO 2: Loop de Consumo (Polling)
        # ---------------------------------------------------------------------
        print("[Sub] Aguardando atualizações... (Ctrl+C para sair)")
        
        try:
            while True:
                # Pergunta ao Broker: "Tem algo pra mim?"
                response = self.proxy.check_msg(self.topic, self.sensor_id)
                
                # O Broker retorna algo como: 
                # {'MSG': {'Transito/Velocidade': '80km/h', 'Outra/Fila': None}}
                
                if response and 'MSG' in response:
                    msgs_dict = response['MSG']
                    
                    # --- ALTERAÇÃO AQUI: Iteramos sobre as filas retornadas ---
                    found_any = False
                    
                    for queue_name, content in msgs_dict.items():
                        if content: # Se tiver conteúdo (não for None)
                            print(f"🚗 [Fila: {queue_name}] {content}")
                            found_any = True
                    
                    # Se quiser debug visual de espera (opcional)
                    # if not found_any: print(".", end="", flush=True)

                else:
                    # Caso receba um pacote de erro ou formato inesperado
                    if response and 'status' in response and response['status'] == 'Error':
                        print(f"[Erro no Broker] {response.get('msg')}")

                # Espera 1 segundo antes de perguntar de novo
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n[Sub] Encerrando Dashboard.")
        except Exception as e:
            print(f"\n[Sub] Erro durante o consumo: {e}")

if __name__ == "__main__":
    # Instancia e roda o Dashboard
    dashboard = TrafficDashboard()
    dashboard.start()