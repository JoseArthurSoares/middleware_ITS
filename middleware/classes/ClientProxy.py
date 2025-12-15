from Requestor import Requestor
from Shared import Invocation, Request, IOR

class ClientProxy:
    def __init__(self, host='localhost', port=8080):
        # O Proxy NÃO conhece CRH nem Marshaller.
        # Ele só conhece o Requestor e o Endereço do Servidor (IOR).
        self.requestor = Requestor()
        self.ior = IOR(host=host, port=port)

    def publish(self, topic, message):
        # 1. Monta o objeto Request (O Que fazer)
        req = Request(op='Publish', params=[topic, message])
        
        # 2. Monta a Invocation (Quem + O Que)
        inv = Invocation(ior=self.ior, request=req)
        
        # 3. Delega para o Requestor (Como fazer)
        # O invoke retorna um objeto Termination
        termination = self.requestor.invoke(inv)
        
        return termination.rep.result

    def subscribe(self, topic, sensor_id):
        # A lógica é sempre a mesma: criar Request -> Invocation -> Invoke
        req = Request(op='Subscribe', params=[topic, sensor_id])
        inv = Invocation(ior=self.ior, request=req)
        
        termination = self.requestor.invoke(inv)
        return termination.rep.result

    def check_msg(self, topic, sensor_id):
        req = Request(op='CheckMsg', params=[topic, sensor_id])
        inv = Invocation(ior=self.ior, request=req)
        
        termination = self.requestor.invoke(inv)
        return termination.rep.result