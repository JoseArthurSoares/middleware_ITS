import time
import random
from ClientProxy import ClientProxy  # Certifique-se que o arquivo ClientProxy.py existe na mesma pasta

class SpeedPublisher:
    def __init__(self, topic="Transito/Velocidade", host='localhost', port=8080):
        # O Cliente usa o ClientProxy, não o ServerRequestHandler
        self.proxy = ClientProxy(host, port)
        self.topic = topic

    def start(self):
        # Esta é a mensagem correta para o Publisher
        print(f"[Publisher] Iniciando sensor de velocidade no tópico '{self.topic}'...")
        
        try:
            while True:
                # 1. Simula dados
                current_speed = random.randint(60, 100)
                timestamp = time.strftime("%H:%M:%S")
                msg_content = f"{timestamp} - {current_speed} km/h"

                print(f"[Publisher] Enviando: {msg_content}")

                # 2. Envia via Proxy
                # O método publish() está dentro da classe ClientProxy
                ack = self.proxy.publish(self.topic, msg_content)

                print(f"[Publisher] Confirmação recebida: {ack}")

                # 3. Espera um pouco
                time.sleep(2)

        except KeyboardInterrupt:
            print("\n[Publisher] Encerrando sensor.")
        except Exception as e:
            print(f"[Publisher] Erro crítico: {e}")

if __name__ == "__main__":
    # Cria e inicia o sensor
    sensor = SpeedPublisher()
    sensor.start()