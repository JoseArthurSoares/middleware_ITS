from SubscriptionStorage import SubscriptionStorage

class SubscriptionsManager:
    def __init__(self):
        self.subscription_storage = SubscriptionStorage()

    def insert_subscription(self, topic, thing_id, address):
        # Adiciona a assinatura usando o storage
        self.subscription_storage.add_subscription(thing_id, topic)

    def get_subscriptions(self):
        return self.subscription_storage.get_subscriptions()