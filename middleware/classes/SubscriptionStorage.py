from collections import deque

class SubscriptionStorage:
    def __init__(self):
        self.subcriptions = {}
        self.topics = {}


    # Adiciona assinatura passando o id do dispositivo e o tópico
    def add_subscription(self, thing_id, topic):
        # Associa um ID de dispositivo a um tópico
        if thing_id in self.subcriptions.keys():
            if not self.subcriptions[thing_id].get(topic):
                self.subcriptions[thing_id][topic] = deque([], maxlen=20)
        else:
            self.topics[topic] = deque([], maxlen=20)
            self.subcriptions[thing_id] = self.topics

    def get_subscriptions(self):
        return self.subcriptions