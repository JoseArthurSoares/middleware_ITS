import time
from ClientProxy import ClientProxy

class Subscriber:
    def __init__(self, sub_id="Assinante_Transito", topic="Transito/Velocidade", host='localhost', port=8080):
        self.proxy = ClientProxy(host, port)
        self.sub_id = sub_id
        self.topic = topic

    def start(self):
        print(f"--- [Subscriber] Iniciando Monitoramento ({self.sub_id}) ---")

        # 1. Assinatura
        print(f"[Subscriber] Assinando tópico: '{self.topic}'...")
        ack = self.proxy.subscribe(self.topic, self.sub_id)
        print(f"[Subscriber] Status da assinatura: {ack}")

        # 2. Loop de Consumo
        print(f"[Subscriber] Modo de Escuta ATIVO. Aguardando publicações...")

        try:
            while True:
                # Pergunta ao Broker
                data = self.proxy.check_msg(self.topic, self.sub_id)
                
                # Validação da mensagem
                if data and 'MSG' in data:
                    # Verifica se é deste tópico específico ou se veio genérico
                    if self.topic in data['MSG']:
                        conteudo = data['MSG'][self.topic]
                        print(f"📥 [RECEBIDO] {conteudo}")
                    else:
                        print(f"⚠️ [AVISO] Recebi estrutura 'MSG', mas tópico incorreto: {data['MSG'].keys()}")

                time.sleep(1)

        except KeyboardInterrupt:
            print("\n[Subscriber] Encerrando.")

if __name__ == "__main__":
    sub = Subscriber()
    sub.start()