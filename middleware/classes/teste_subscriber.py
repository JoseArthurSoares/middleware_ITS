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
        # Isso cria a fila para este usuário lá no BrokerEngine/SubscriptionsManager
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
        print("[Sub] Aguardando atualizações de velocidade (Ctrl+C para sair)...")
        
        try:
            while True:
                # Pergunta ao Broker: "Tem algo pra mim?"
                response = self.proxy.check_msg(self.topic, self.sensor_id)
                
                # O formato esperado da resposta é:
                # {'OP': 'CheckMsgReply', 'sensor_id': '...', 'MSG': {'Transito/Velocidade': 'VALOR' ou None}}
                
                if response and 'MSG' in response:
                    msgs_dict = response['MSG']
                    content = msgs_dict.get(self.topic)

                    if content:
                        # Se tiver conteúdo (não for None), imprime formatado
                        print(f"🚗 [RECEBIDO] {content}")
                    else:
                        # Fila vazia no momento.
                        # Dica: Descomente a linha abaixo se quiser ver "pontinhos" enquanto espera
                        # print(".", end="", flush=True)
                        pass
                else:
                    print("[Sub] Resposta estranha do broker:", response)

                # Espera 1 segundo antes de perguntar de novo (evita floodar o servidor)
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n[Sub] Encerrando Dashboard.")
        except Exception as e:
            print(f"\n[Sub] Erro durante o consumo: {e}")

if __name__ == "__main__":
    # Instancia e roda o Dashboard
    dashboard = TrafficDashboard()
    dashboard.start()