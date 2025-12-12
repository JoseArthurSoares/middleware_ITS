from collections import deque

class EventStorage:
    def __init__(self):
        # Mapeia: queue_id (tópico) -> deque (mensagens)
        self.queue_ids = {}

    def add_message(self, queue_id, message):
        """Adiciona mensagem na fila (Push)"""
        if queue_id in self.queue_ids:
            self.queue_ids[queue_id].append(message)
        else:
            self.queue_ids[queue_id] = deque([message], maxlen=20)

    def consume_message(self, queue_id):
        """
        NOVO MÉTODO: Retira a mensagem mais antiga da fila (Pull/Pop).
        Retorna a mensagem ou None se vazio.
        """
        # Verifica se a fila existe E se tem itens dentro
        if queue_id in self.queue_ids and self.queue_ids[queue_id]:
            # Encapsula o 'popleft' aqui dentro. O Consumer não precisa saber que é um deque.
            return self.queue_ids[queue_id].popleft()
            
        return None

    def get_message_by_queue_id(self, queue_id):
        """Retorna a lista completa (apenas para visualização/debug)"""
        if queue_id in self.queue_ids:
            return list(self.queue_ids[queue_id])
        return []