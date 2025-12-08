from collections import deque

class SubscriptionManager:
    def __init__(self):
        # Estrutura do init: {'user_1': { 'fila_A': deque(), 'fila_B': deque()} }
        self.subscribers = {} 

    # 1. Método para CRIAR a estrutura (não recebe speed)
    def insert_subscription(self, subscriber_id, queue_id):
        if subscriber_id not in self.subscribers:
            self.subscribers[subscriber_id] = {}

        if queue_id not in self.subscribers[subscriber_id]:
            # Cria um deque VAZIO inicialmente
            self.subscribers[subscriber_id][queue_id] = deque(maxlen=20)
            print(f"Assinatura criada: {subscriber_id} -> {queue_id}")
        else:
            print(f"Assinatura já existe: {subscriber_id} -> {queue_id}")
    
    def remove_subscription(self, subscriber_id, queue_id):
        # 1. Verifica se o usuário existe
        if subscriber_id in self.subscribers:
            # 2. Verifica se a fila existe para aquele usuário
            if queue_id in self.subscribers[subscriber_id]:
                del self.subscribers[subscriber_id][queue_id]
                print(f"[-] Inscrição removida: {subscriber_id} -> {queue_id}")
                
                # Limpeza (Opcional): Se o usuário não tem mais filas, remove o usuário
                if not self.subscribers[subscriber_id]:
                    del self.subscribers[subscriber_id]
                    print(f"    (Usuário {subscriber_id} removido por inatividade)")
            else:
                print(f"[Erro] Fila {queue_id} não encontrada para {subscriber_id}")
        else:
            print(f"[Erro] Usuário {subscriber_id} não encontrado")

    def get_subscriptions(self):
        print(self.subscribers)

        """ Mostra tudo que está na memória
        print("\n--- MEMÓRIA ATUAL ---")
        if not self.subscribers:
            print("Nenhum dado registrado.")
        else:
            for veiculo, filas in self.subscribers.items():
                # Tenta acessar a fila "velocidade" se ela existir para aquele veículo
                if "velocidade" in filas:
                    print(f"Veículo: {veiculo} | Fila 'velocidade': {list(filas['velocidade'])}")
                else:
                    print(f"Veículo: {veiculo} | (Sem dados de velocidade)")
"""