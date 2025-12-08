from collections import deque

class NotificationEngine:
    def __init__(self):
        # Estrutura do init: {'user_1': { 'fila_A': deque(), 'fila_B': deque()} }
        self.subscribers = {} 
        self.publishers = {}

    #assinantes 
    #insere um assinante
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
        # 1. Verifica se o assinante já existe
        if subscriber_id in self.subscribers:
            # 2. Verifica se a fila existe para aquele assinante
            if queue_id in self.subscribers[subscriber_id]:
                del self.subscribers[subscriber_id][queue_id]
                print(f"[-] Inscrição removida: {subscriber_id} -> {queue_id}")
                
                # Limpeza (Opcional): Se o usuário não tem mais filas, remove o usuário
                #if not self.subscribers[subscriber_id]:
                 #   del self.subscribers[subscriber_id]
                  #  print(f"    (Usuário {subscriber_id} removido por inatividade)")
            else:
                print(f"[Erro] Fila {queue_id} não encontrada para {subscriber_id}")
        else:
            print(f"[Erro] Usuário {subscriber_id} não encontrado")

    def get_subscriptions(self):
        print(self.subscribers)

    #publish

    #insere um publisher
    def insert_publisher(self, publisher_id):
        if publisher_id not in self.subscribers:
            self.subscribers[publisher_id] = {}

        if publisher_id not in self.subscribers[publisher_id]:
            # Cria um deque VAZIO inicialmente
            self.subscribers[publisher_id] = deque(maxlen=20)
            print(f"Publicador criado: {publisher_id}")
        else:
            print(f"Publicador já existe: {publisher_id}")

    def remove_publisher(self, publisher_id):
        # 1. Verifica se o publicador já existe
        if publisher_id in self.subscribers:
            del self.subscribers[publisher_id]
            print(f"[-] Publicador removido: {publisher_id}")
        else:
            print(f"[Erro] Publicador {publisher_id} não encontrado")
    
    def get_publishers(self):
        print(self.publishers)

    def notify (self, publisher_id, message, queue_id):
        # Notifica todos os assinantes sobre uma nova mensagem do publicador
        if publisher_id in self.publishers:
            pass
            #if queue_id in self.subscribers[subscriber_id]:
            #     self.subscribers[subscriber_id][queue_id]
        else:
            print(f"[Erro] Publicador {publisher_id} não encontrado")