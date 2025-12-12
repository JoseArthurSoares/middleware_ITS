from EventStorage import EventStorage
from SubscriptionsManager import SubscriptionsManager
from ServerRequestHandler import ServerRequestHandler
from Marshaller import Marshaller
import sys

class BrokerEngine:
    def __init__(self, host='localhost', port=8080):
        print("[DEBUG] Inicializando Managers...")
        self.event_storage = EventStorage()
        self.subscription_manager = SubscriptionsManager()
        
        print("[DEBUG] Inicializando Rede...")
        self.srh = ServerRequestHandler(host, port)
        self.marshaller = Marshaller()

    def start(self):
        print(f"[BrokerEngine] Serviço rodando em {self.srh.server_socket.getsockname()}")
        
        while True:
            # 1. RECEIVE
            bytes_received = self.srh.receive()
            if bytes_received is None:
                continue

            print(f"\n[DEBUG] 1. Bytes recebidos: {len(bytes_received)}")

            try:
                # 2. UNMARSHALL
                inv_arg = self.marshaller.unmarshall(bytes_received)
                if inv_arg is None:
                    raise ValueError("Falha no Unmarshall (Dados inválidos ou corrompidos)")
                
                print(f"[DEBUG] 2. Objeto recebido: {inv_arg}")

                # 3. DISPATCH (Lógica)
                print("[DEBUG] 3. Entrando na lógica de negócio (run)...")
                result_data = self.run(inv_arg)
                print(f"[DEBUG] 4. Retorno da lógica: {result_data}")

                # 4. MARSHALL RESPOSTA
                bytes_response = self.marshaller.marshall(result_data)
                print(f"[DEBUG] 5. Tamanho da resposta serializada: {len(bytes_response)}")

                # 5. SEND
                self.srh.send(bytes_response)
                print("[DEBUG] 6. Resposta enviada com sucesso.")

            except Exception as e:
                # AQUI É ONDE VAMOS DESCOBRIR O ERRO
                print("="*40)
                print(f"[CRITICAL ERROR] O Servidor falhou durante o processamento!")
                print(f"Tipo do Erro: {type(e)}")
                print(f"Mensagem: {e}")
                import traceback
                traceback.print_exc() # Imprime a linha exata do erro
                print("="*40)
                
                # Tenta avisar o cliente que deu erro para ele não travar
                try:
                    err_bytes = self.marshaller.marshall({'status': 'Error', 'msg': str(e)})
                    self.srh.send(err_bytes)
                except:
                    pass
            
            finally:
                self.srh.close()
                print("[DEBUG] Conexão fechada.\n")

    def run(self, invArg):
        operation = invArg.get('OP')
        if operation == 'Publish':
            return self._handle_publish(invArg)
        elif operation == 'Subscribe':
            return self._handle_subscribe(invArg)
        elif operation == 'CheckMsg':
            return self._handle_check_msg(invArg)
        else:
            return {'status': 'Error', 'msg': 'Operation not supported'}

    def _handle_publish(self, args):
        # Validação extra para debug
        if 'queue_id' not in args:
            raise KeyError("O dicionário não contem a chave 'queue_id'")
        
        queue_ids = args['queue_id']
        message_content = args['MSG']

        if not isinstance(queue_ids, list):
            queue_ids = [queue_ids]

        for q_id in queue_ids:
            self.event_storage.add_message(q_id, message_content)
            all_subs = self.subscription_manager.get_subscriptions()
            for subscriber_id, user_queues in all_subs.items():
                if q_id in user_queues:
                    user_queue = self.subscription_manager.get_specific_queue(subscriber_id, q_id)
                    if user_queue is not None:
                        user_queue.append(message_content)
        return "ACK: Published"

    def _handle_subscribe(self, args):
        sensor_id = args['sensor_id']
        queue_ids = args['queue_id']
        if not isinstance(queue_ids, list):
            queue_ids = [queue_ids]
        for q_id in queue_ids:
            self.subscription_manager.insert_subscription(q_id, sensor_id)
        return "ACK: Subscribed"

    def _handle_check_msg(self, args):
        sensor_id = args['sensor_id']
        queue_ids = args['queue_id']
        if not isinstance(queue_ids, list):
            queue_ids = [queue_ids]
        messages_found = {}
        for q_id in queue_ids:
            user_queue = self.subscription_manager.get_specific_queue(sensor_id, q_id)
            if user_queue and len(user_queue) > 0:
                msg = user_queue.popleft()
                messages_found[q_id] = msg
            else:
                messages_found[q_id] = None
        return {'OP': 'CheckMsgReply', 'sensor_id': sensor_id, 'MSG': messages_found}

if __name__ == "__main__":
    broker = BrokerEngine()
    broker.start()