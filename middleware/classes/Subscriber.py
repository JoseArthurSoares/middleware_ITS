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

                # --- MUDANÇA AQUI: Debug para ver o que chega ---
                # Se data não for None, imprime para entendermos a estrutura
                if data: 
                    # print(f"[DEBUG RAW] Recebido do Proxy: {data}") # Descomente se quiser ver tudo
                    pass
                
                # Validação da mensagem
                if data and 'MSG' in data:
                    # Verifica se é deste tópico específico ou se veio genérico
                    if self.topic in data['MSG']:
                        conteudo = data['MSG'][self.topic]
                        print(f"📥 [RECEBIDO] {conteudo}")
                    else:
                        print(f"⚠️ [AVISO] Recebi estrutura 'MSG', mas tópico incorreto: {data['MSG'].keys()}")
                
                # Caso o servidor retorne algo que não seja a estrutura esperada
                elif data and 'result' in data and data['result'] == 'No msg':
                     # É normal receber 'No msg', então geralmente não printamos nada para não poluir
                     pass
                elif data:
                     print(f"⚠️ [ESTRUTURA DESCONHECIDA] {data}")

                time.sleep(1)

        except KeyboardInterrupt:
            print("\n[Subscriber] Encerrando.")

if __name__ == "__main__":
    sub = Subscriber()
    sub.start()