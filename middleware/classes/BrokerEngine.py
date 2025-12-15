from EventStorage import EventStorage
from SubscriptionsManager import SubscriptionsManager
from ServerRequestHandler import ServerRequestHandler
from Marshaller import Marshaller
import Miop
import time

class BrokerEngine:
    def __init__(self, host='localhost', port=8080):
        print("[DEBUG] Inicializando Managers (Camada de Negócio)...")
        self.event_storage = EventStorage()
        self.subscription_manager = SubscriptionsManager()
        
        print("[DEBUG] Inicializando Infraestrutura (Rede e Serialização)...")
        self.srh = ServerRequestHandler(host, port)
        self.marshaller = Marshaller()
        
        self.DEFAULT_TTL = 10.0 

    def start(self):
        print(f"[BrokerEngine] Serviço rodando em {self.srh.server_socket.getsockname()} com TTL de {self.DEFAULT_TTL}s")
        
        while True:
            bytes_received = self.srh.receive()
            if bytes_received is None:
                continue

            try:
                # 1. Unmarshall: Bytes -> Objeto Complexo
                req_packet = self.marshaller.unmarshal(bytes_received)
                if req_packet is None: continue

                # Tenta pegar .bd ou usa o próprio objeto
                raw_body = getattr(req_packet, 'bd', req_packet)
                
                # Debug para confirmar o sucesso
                # print(f"[DEBUG RAW] Chegou: {raw_body}")

                # =========================================================
                # BLOCO DE ADAPTAÇÃO (ATUALIZADO PARA SUA ESTRUTURA)
                # =========================================================
                
                inv_arg = {}
                op_name = None
                params = []

                # --- CASO 1: Estrutura Complexa (Body -> reqHeader -> operation) ---
                # É este caso que apareceu no seu LOG de erro
                if hasattr(raw_body, 'reqHeader'):
                    # Pega a operação dentro do Header
                    op_name = getattr(raw_body.reqHeader, 'operation', None)
                    
                    # Pega os parâmetros dentro do Body -> body
                    if hasattr(raw_body, 'reqBody'):
                        params = getattr(raw_body.reqBody, 'body', [])

                # --- CASO 2: Estrutura Simples (Request -> op) ---
                elif hasattr(raw_body, 'op'): 
                    op_name = raw_body.op
                    params = raw_body.params

                # --- CASO 3: Dicionário (Legado) ---
                elif isinstance(raw_body, dict):
                    op_name = raw_body.get('OP') or raw_body.get('op')
                    params = raw_body.get('params') or raw_body.get('args') or []
                
                # Validação Final
                if op_name is None:
                    raise ValueError(f"Estrutura de pacote não reconhecida: {raw_body}")

                # ---------------------------------------------------------
                # Normalização para o Broker (Mapeamento)
                # ---------------------------------------------------------
                inv_arg['OP'] = op_name
                
                if op_name == 'Publish':
                    if len(params) >= 2:
                        inv_arg['queue_id'] = params[0]
                        inv_arg['MSG'] = params[1]
                elif op_name == 'Subscribe':
                    if len(params) >= 2:
                        inv_arg['queue_id'] = params[0]
                        inv_arg['sensor_id'] = params[1]
                elif op_name == 'CheckMsg':
                    if len(params) >= 2:
                        inv_arg['queue_id'] = params[0]
                        inv_arg['sensor_id'] = params[1]
                # =========================================================

                print(f"[DEBUG] Interpretado: OP={inv_arg.get('OP')} | Params: {params}")
                
                # 3. Executa a lógica
                result_data = self.run(inv_arg)
                
                # 4. Encapsula resposta e Envia
                reply_packet = Miop.createReplyMIOP(result_data)
                bytes_response = self.marshaller.marshal(reply_packet)
                self.srh.send(bytes_response)

            except Exception as e:
                print(f"[ERROR] Falha no processamento: {e}")
                try:
                    err_packet = Miop.createReplyMIOP({'status': 'Error', 'msg': str(e)})
                    self.srh.send(self.marshaller.marshal(err_packet))
                except: pass
            finally:
                self.srh.close()

    def run(self, invArg):
        op = invArg.get('OP')
        if op == 'Publish':
            return self._handle_publish(invArg)
        elif op == 'Subscribe':
            return self._handle_subscribe(invArg)
        elif op == 'CheckMsg':
            return self._handle_check_msg(invArg)
        else:
            return {'status': 'Error', 'msg': f'Operacao {op} desconhecida'}

    def _handle_publish(self, args):
        q_ids = args.get('queue_id')
        msg = args.get('MSG')
        if not q_ids or not msg: raise ValueError("Dados incompletos para Publish")
        
        envelope = {'payload': msg, 'timestamp': time.time()}
        if not isinstance(q_ids, list): q_ids = [q_ids]

        for q in q_ids:
            self.event_storage.add_message(q, envelope)
            subs = self.subscription_manager.get_subscriptions()
            for sub_id, queues in subs.items():
                if q in queues:
                    uq = self.subscription_manager.get_specific_queue(sub_id, q)
                    if uq is not None: uq.append(envelope)
        return "ACK: Published"

    def _handle_subscribe(self, args):
        sid = args.get('sensor_id')
        q_ids = args.get('queue_id')
        if not sid or not q_ids: raise ValueError("Dados incompletos para Subscribe")
        
        if not isinstance(q_ids, list): q_ids = [q_ids]
        for q in q_ids:
            self.subscription_manager.insert_subscription(q, sid)
        return "ACK: Subscribed"

    def _handle_check_msg(self, args):
        sid = args.get('sensor_id')
        q_ids = args.get('queue_id')
        if not isinstance(q_ids, list): q_ids = [q_ids]
        
        found = {}
        now = time.time()
        for q in q_ids:
            uq = self.subscription_manager.get_specific_queue(sid, q)
            if uq:
                while uq:
                    env = uq[0]
                    if (now - env['timestamp']) > self.DEFAULT_TTL:
                        uq.popleft() 
                    else:
                        found[q] = uq.popleft()['payload']
                        break
        return {'OP': 'CheckMsgReply', 'MSG': found}

if __name__ == "__main__":
    BrokerEngine().start()