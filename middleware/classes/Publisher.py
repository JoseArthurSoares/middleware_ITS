
import time
import random
from ClientProxy import ClientProxy


class Publisher:
    def __init__(self, topic="Transito/Velocidade", host='localhost', port=8080):
        self.proxy = ClientProxy(host, port)
        self.topic = topic

    def start(self):
        print(f"--- [Publisher] Iniciando Sensor de Velocidade ---")

        try:
            while True:
                # 1. Gera dado simulado
                velocidade = random.randint(40, 120)
                msg = f"Velocidade aferida: {velocidade} km/h"

                # 2. Publica no Broker
                print(f"📤 [ENVIANDO] {msg}")
                self.proxy.publish(self.topic, msg)

        except KeyboardInterrupt:
            print("\n[Publisher] Encerrando sensor.")


if __name__ == "__main__":
    pub = Publisher()
    pub.start()