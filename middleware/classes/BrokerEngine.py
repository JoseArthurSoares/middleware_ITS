from EventStorage import EventStorage
from SubscriptionsManager import SubscriptionsManager
import time

class BrokerEngine:
    def __init__(self):
        print("[BrokerEngine] Engine Lógica Inicializada.")
        self.event_storage = EventStorage()
        self.subscription_manager = SubscriptionsManager()
        self.DEFAULT_TTL = 20.0 # Aumentei para dar tempo de testar

    def _sanitize(self, data):
        """
        Garante que o dado é uma String limpa, mesmo se vier dentro de uma lista.
        Ex: ['Transito'] -> 'Transito'
        """
        if isinstance(data, list):
            return str(data[0]) if len(data) > 0 else ""
        return str(data)

    def Publish(self, queue_id, message):
        # 1. Limpeza
        topic = self._sanitize(queue_id)
        
        envelope = {
            'payload': message,
            'timestamp': time.time()
        }
        
        print(f"[BrokerEngine] 📨 PUBLISH recebido no tópico '{topic}': {message}")

        # Persistência
        self.event_storage.add_message(topic, envelope)
        
        # Distribuição
        subs = self.subscription_manager.get_subscriptions()
        count = 0
        
        for subscriber_id, user_queues in subs.items():
            # user_queues é uma lista de tópicos que o usuário assina
            # Precisamos garantir que comparamos string com string
            if topic in [self._sanitize(q) for q in user_queues]:
                user_queue = self.subscription_manager.get_specific_queue(subscriber_id, topic)
                if user_queue is not None:
                    user_queue.append(envelope)
                    count += 1
        
        print(f"[BrokerEngine] -> Entregue para {count} filas de assinantes.")
        return f"ACK: Published to {count} subs"

    def Subscribe(self, queue_id, sensor_id):
        topic = self._sanitize(queue_id)
        sid = self._sanitize(sensor_id)
        
        print(f"[BrokerEngine] 📝 SUBSCRIBE: '{sid}' assinou '{topic}'")
        self.subscription_manager.insert_subscription(topic, sid)
        return "ACK: Subscribed"

    def CheckMsg(self, queue_id, sensor_id):
        topic = self._sanitize(queue_id)
        sid = self._sanitize(sensor_id)
        
        # Debug para ver quem está batendo na porta
        # print(f"[BrokerEngine Debug] CheckMsg de {sid} no tópico {topic}")

        user_queue = self.subscription_manager.get_specific_queue(sid, topic)
        
        found_payload = None
        current_time = time.time()

        if user_queue:
            while len(user_queue) > 0:
                envelope = user_queue[0]
                age = current_time - envelope['timestamp']
                
                if age > self.DEFAULT_TTL:
                    user_queue.popleft() # Remove vencida
                else:
                    found_payload = user_queue.popleft()['payload']
                    print(f"[BrokerEngine] 📤 Entregando mensagem para {sid}: {found_payload}")
                    break 
        
        # Se user_queue for None (usuário nunca assinou), found_payload continua None
        return {'MSG': {topic: found_payload}}