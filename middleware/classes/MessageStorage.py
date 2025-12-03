from collections import deque

class MessageStorage:
    def __init__(self):
        self.topics = {}

    # Adiciona mensagem à fila
    def add_message(self, topic, message):
        # Se o tópico já existe, adiciona a mensagem à fila
        if topic in self.topics.keys():
            self.topics[topic].append(message)
        else:
            # Cria uma nova fila circular
            self.topics[topic] = deque([message], maxlen=20)

    # Recupera mensagem passando o tópico
    def get_message_by_topic(self, topic):
        if topic in self.topics.keys():
            return self.topics[topic]