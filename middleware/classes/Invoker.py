from Marshaller import Marshaller
import Miop
from ServerRequestHandler import ServerRequestHandler

class Invoker:
    def __init__(self, host, port, broker_engine):
        self.srh = ServerRequestHandler(host, port)
        self.marshaller = Marshaller()
        self.broker_engine = broker_engine

    def invoke(self):
        print(f"[Invoker] Pronto em {self.srh.server_socket.getsockname()}")

        while True:
            try:
                req_bytes = self.srh.receive()
                if not req_bytes: continue

                # 1. Unmarshal (Bytes -> Dict)
                req_dict = self.marshaller.unmarshall(req_bytes)

                # 2. Extract (Dict Sujo -> Dict Limpo {'OP':.., 'params':..})
                req_clean = Miop.extractRequest(req_dict)
                
                op = req_clean['OP']
                params = req_clean['params']

                if not op: continue

                print(f"[Invoker] {op} -> {params}")

                # 3. Chama Engine
                method = getattr(self.broker_engine, op, None)
                if not method:
                    raise ValueError(f"Metodo {op} nao existe.")

                result = method(*params)

                # 4. Responde
                rep_dict = Miop.createReplyMIOP(result)
                self.srh.send(self.marshaller.marshall(rep_dict))

            except Exception as e:
                print(f"[Invoker Error] {e}")
                err_dict = Miop.createReplyMIOP({'status': 'Error', 'msg': str(e)})
                try: self.srh.send(self.marshaller.marshall(err_dict))
                except: pass
            finally:
                self.srh.close()