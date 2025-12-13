from EventStorage import EventStorage
from SubscriptionsManager import SubscriptionsManager
from ServerRequestHandler import ServerRequestHandler
from Marshaller import Marshaller
import time

class BrokerEngine:
    def __init__(self, host='localhost', port=8080):
        print("[DEBUG] Inicializando Managers (Camada de Negócio)...")
        self.event_storage = EventStorage()
        self.subscription_manager = SubscriptionsManager()
        
        print("[DEBUG] Inicializando Infraestrutura (Rede e Serialização)...")
        self.srh = ServerRequestHandler(host, port)
        self.marshaller = Marshaller()
        
        # [CONFIGURAÇÃO] Tempo de Vida da Mensagem (TTL)
        # 0.001 segundos = 1 milésimo. 
        # Mensagens mais velhas que isso serão descartadas na leitura.
        self.DEFAULT_TTL = 1.0  # segundos 

    def start(self):
        """
        Loop Principal (Main Loop).
        Gerencia o ciclo de vida da requisição: Escutar -> Traduzir -> Processar -> Responder.
        """
        print(f"[BrokerEngine] Serviço rodando em {self.srh.server_socket.getsockname()} com TTL de {self.DEFAULT_TTL}s")
        
        while True:
            # 1. Wait: Bloqueia até chegar dados na porta
            bytes_received = self.srh.receive()
            if bytes_received is None:
                continue

            try:
                # 2. Unmarshall: Traduz bytes para Dicionário Python
                inv_arg = self.marshaller.unmarshall(bytes_received)
                if inv_arg is None:
                    raise ValueError("Falha no Unmarshall (Pacote corrompido)")
                
                print(f"[DEBUG] Processando Operação: {inv_arg.get('OP')}")
                
                # 3. Dispatch: Executa a lógica de negócio
                result_data = self.run(inv_arg)
                
                # 4. Marshall: Traduz a resposta do Dicionário para Bytes
                bytes_response = self.marshaller.marshall(result_data)
                
                # 5. Reply: Envia de volta ao cliente
                self.srh.send(bytes_response)

            except Exception as e:
                print(f"[ERROR] Falha no processamento: {e}")
                # Tenta enviar o erro para o cliente não ficar travado (Timeout)
                try:
                    err = self.marshaller.marshall({'status': 'Error', 'msg': str(e)})
                    self.srh.send(err)
                except: pass
            
            finally:
                # Encerra a conexão com o cliente atual para liberar o socket
                self.srh.close()

    def run(self, invArg):
        """Roteador de comandos."""
        op = invArg.get('OP')
        if op == 'Publish':
            return self._handle_publish(invArg)
        elif op == 'Subscribe':
            return self._handle_subscribe(invArg)
        elif op == 'CheckMsg':
            return self._handle_check_msg(invArg)
        else:
            return {'status': 'Error', 'msg': 'Operation not supported'}

    # =========================================================================
    # Lógica de Negócio
    # =========================================================================

    def _handle_publish(self, args):
        """
        Ao receber uma publicação, agora "envelopamos" o dado com o horário de chegada.
        Isso permite calcular a idade da mensagem depois.
        """
        if 'queue_id' not in args: raise KeyError("Missing queue_id")
        
        queue_ids = args['queue_id']
        message_content = args['MSG']
        
        # Carimbo de tempo (Timestamp) da chegada
        arrival_time = time.time()

        # O Envelope contém o Dado Real + Metadados
        envelope = {
            'payload': message_content,
            'timestamp': arrival_time
        }

        if not isinstance(queue_ids, list): queue_ids = [queue_ids]

        for q_id in queue_ids:
            # Persistência Global
            self.event_storage.add_message(q_id, envelope)
            
            # Fan-out: Distribui cópias para as filas de quem assinou
            all_subs = self.subscription_manager.get_subscriptions()
            for subscriber_id, user_queues in all_subs.items():
                if q_id in user_queues:
                    user_queue = self.subscription_manager.get_specific_queue(subscriber_id, q_id)
                    if user_queue is not None:
                        user_queue.append(envelope)
                        
        return "ACK: Published"

    def _handle_subscribe(self, args):
        sensor_id = args['sensor_id']
        queue_ids = args['queue_id']
        if not isinstance(queue_ids, list): queue_ids = [queue_ids]
        
        for q_id in queue_ids:
            self.subscription_manager.insert_subscription(q_id, sensor_id)
        return "ACK: Subscribed"

    def _handle_check_msg(self, args):
        """
        Regra de Expiração (Lazy Expiration):
        Quando o cliente vem buscar, verificamos se o dado "venceu".
        Se (Agora - Chegada) > 0.001s, jogamos fora.
        """
        sensor_id = args['sensor_id']
        queue_ids = args['queue_id']
        if not isinstance(queue_ids, list): queue_ids = [queue_ids]
            
        messages_found = {}
        current_time = time.time()

        for q_id in queue_ids:
            user_queue = self.subscription_manager.get_specific_queue(sensor_id, q_id)
            
            valid_msg = None
            
            if user_queue:
                # Enquanto tiver mensagem na fila, checa a validade da primeira
                while len(user_queue) > 0:
                    envelope = user_queue[0] # Olha a primeira sem remover (Peek)
                    
                    msg_time = envelope['timestamp']
                    age = current_time - msg_time # Calcula a idade
                    
                    if age > self.DEFAULT_TTL:
                        # DESCARTAR: Está velha demais
                        print(f"[TTL] Mensagem descartada do tópico '{q_id}'. Idade: {age:.4f}s > {self.DEFAULT_TTL}s")
                        user_queue.popleft() # Remove definitivamente
                        # O loop roda de novo para testar a próxima da fila
                    else:
                        # MANTER: Está fresca
                        valid_msg = user_queue.popleft()['payload']
                        break # Encontrou uma válida, para de procurar
            
            messages_found[q_id] = valid_msg
                
        return {'OP': 'CheckMsgReply', 'sensor_id': sensor_id, 'MSG': messages_found}

if __name__ == "__main__":
    broker = BrokerEngine()
    broker.start()