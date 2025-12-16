# Arquivo: Subscriber.py
# Responsabilidade: Assinar tópicos e ficar ESCUTANDO a fila (Loop de Consumo)
import time
from ClientProxy import ClientProxy


class Subscriber:
    def __init__(self, sub_id="Assinante_Transito", topic="Transito/Velocidade", host='localhost', port=8080):
        self.proxy = ClientProxy(host, port)
        self.sub_id = sub_id
        self.topic = topic

    def start(self):
        print(f"--- [Subscriber] Iniciando Monitoramento ({self.sub_id}) ---")

        # 1. Avisa ao Broker que quer receber mensagens desse tópico
        print(f"[Subscriber] Assinando tópico: '{self.topic}'...")
        ack = self.proxy.subscribe(self.topic, self.sub_id)
        print(f"[Subscriber] Status da assinatura: {ack}")

        # 2. Loop Infinito (Bloqueante)
        print(f"[Subscriber] Modo de Escuta ATIVO. Aguardando publicações...")

        try:
            while True:
                # Pergunta ao Broker se tem novidade
                data = self.proxy.check_msg(self.topic, self.sub_id)

                # Se houver mensagem no tópico, exibe
                if data and 'MSG' in data and data['MSG'].get(self.topic):
                    conteudo = data['MSG'][self.topic]
                    print(f"📥 [RECEBIDO] {conteudo}")

                time.sleep(1)  # Aguarda um pouco antes de checar novamente

        except KeyboardInterrupt:
            print("\n[Subscriber] Encerrando.")


if __name__ == "__main__":
    sub = Subscriber()
    sub.start()