from SubscriptionsManager import SubscriptionsManager
from EventStorage import EventStorage
from NotificationConsumer import NotificationConsumer

class NotificationEngine:
    def __init__(self):
        # 1. Gestores de Dados
        self.sub_manager = SubscriptionsManager()
        self.event_manager = EventStorage()
        
        # 2. Gestor de Consumo (Injetamos o sub_manager nele)
        self.consumer = NotificationConsumer(self.sub_manager)
        
        # 3. Segurança (Lista de Publishers autorizados)
        self.authorized_publishers = set()

    # ======================================================
    # Métodos chamados pelo INVOKER (API Pública)
    # ======================================================

    # --- Gestão de Assinaturas ---
    def insert_subscription(self, sensor_id, queue_id):
        self.sub_manager.insert_subscription(queue_id, sensor_id)
        return f"ACK: {sensor_id} subscribed to {queue_id}"

    def remove_subscription(self, sensor_id, queue_id):
        res = self.sub_manager.remove_subscription(queue_id, sensor_id)
        return "ACK" if res else "ERR: Not found"

    # --- Gestão de Publishers ---
    def insert_publisher(self, publisher_id):
        self.authorized_publishers.add(publisher_id)
        return f"ACK: Publisher {publisher_id} registered"

    def remove_publisher(self, publisher_id):
        if publisher_id in self.authorized_publishers:
            self.authorized_publishers.remove(publisher_id)
            return "ACK"
        return "ERR: Not found"

    # --- Publicação (Notify) ---
    def notify(self, publisher_id, message, queue_id):
        """
        Recebe mensagem, guarda no histórico e distribui para as filas dos assinantes.
        """
        if publisher_id not in self.authorized_publishers:
            return "ERR: Unauthorized Publisher"

        # 1. Guarda no histórico global
        self.event_manager.publish_event(queue_id, message)

        # 2. Fan-out: Distribui para cada assinante interessado
        all_subs = self.sub_manager.get_subscriptions()
        count = 0
        
        for sensor_id, sensor_queues in all_subs.items():
            if queue_id in sensor_queues:
                # Acede à fila privada do utilizador
                user_queue = self.sub_manager.get_specific_queue(sensor_id, queue_id)
                if user_queue is not None:
                    user_queue.append(message)
                    count += 1
        
        return f"ACK: Delivered to {count} subscribers"

    # --- Consumo (Read) ---
    def consume(self, sensor_id, queue_id):
        """
        O Cliente chama este método para retirar dados da sua fila.
        """
        return self.consumer.consume(sensor_id, queue_id)