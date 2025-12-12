from collections import deque

class SubscriptionStorage:
    def __init__(self):
        # Mapeia: sensor_id -> { queue_id : deque }
        self.subscriptions = {}

    def add_subscription(self, sensor_id, queue_id):
        # 1. Se o sensor não existe, cria um dicionário para ele
        if sensor_id not in self.subscriptions:
            self.subscriptions[sensor_id] = {}

        # 2. Se a fila não existe, cria o deque
        if queue_id not in self.subscriptions[sensor_id]:
            self.subscriptions[sensor_id][queue_id] = deque([], maxlen=20)

    # --- NOVO MÉTODO ---
    def remove_subscription(self, sensor_id, queue_id):
        """
        Remove a assinatura de uma fila específica para um sensor.
        Retorna True se removeu, False se não encontrou.
        """
        if sensor_id in self.subscriptions:
            if queue_id in self.subscriptions[sensor_id]:
                del self.subscriptions[sensor_id][queue_id]
                return True
        return False

    def get_subscriptions(self):
        return self.subscriptions