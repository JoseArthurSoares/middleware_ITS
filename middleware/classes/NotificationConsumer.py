class NotificationConsumer:
    def __init__(self, subscriptions_manager):
        self.sub_manager = subscriptions_manager

    def consume(self, sensor_id, queue_id):
        """
        Delega a lógica de retirada para a classe MessageStorage.
        """
        # 1. O Manager deve retornar a instância de MessageStorage deste sensor
        # (Em vez de retornar o deque bruto como fazia antes)
        user_storage = self.sub_manager.get_user_storage(sensor_id)
        
        if user_storage:
            # 2. Usa a classe MessageStorage para consumir
            # Não acessamos mais dicionários ou deques aqui!
            msg = user_storage.consume_message(queue_id)
            
            if msg:
                print(f"[Consumer] {sensor_id} consumiu mensagem de '{queue_id}'")
                return msg
                
        return None