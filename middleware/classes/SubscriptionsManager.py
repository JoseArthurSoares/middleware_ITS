from SubscriptionStorage import SubscriptionStorage

class SubscriptionsManager:
    def __init__(self):
        self.subscription_storage = SubscriptionStorage()

    def insert_subscription(self, queue_id, sensor_id):
        # Adiciona a assinatura
        self.subscription_storage.add_subscription(sensor_id, queue_id)

    # --- NOVO MÉTODO ---
    def remove_subscription(self, queue_id, sensor_id):
        """
        Remove a assinatura usando o storage.
        Retorna True se sucesso, False caso contrário.
        """
        return self.subscription_storage.remove_subscription(sensor_id, queue_id)

    def get_subscriptions(self):
        return self.subscription_storage.get_subscriptions()
    
    # Dentro de SubscriptionsManager.py
    def get_specific_queue(self, sensor_id, queue_id):
        if sensor_id in self.subscription_storage.subscriptions:
            user_subs = self.subscription_storage.subscriptions[sensor_id]
            if queue_id in user_subs:
                return user_subs[queue_id] # Retorna o objeto deque/MessageQueue
        return None