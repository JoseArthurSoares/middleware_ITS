from Marshaller import Marshaller
import Miop
from ClientRequestHandler import ClientRequestHandler
from Shared import Termination

class Requestor:
    """
    O Requestor encapsula a lógica de:
    1. Empacotamento (MIOP)
    2. Serialização (Marshaller)
    3. Transporte (CRH)
    """

    def invoke(self, invocation) -> Termination:
        """
        Realiza a invocação remota seguindo o fluxo padrão do middleware.
        Recebe uma 'Invocation' (contendo IOR e Request) e retorna uma 'Termination'.
        """
        
        
        #Criação do Pacote MIOP (Protocolo)
        
        # Extrai dados da invocação
        op = invocation.request.op
        params = invocation.request.params
        
        # Usa a função do módulo miop (camelCase) para criar o pacote
        miopReqPacket = Miop.createRequestMIOP(op, params)

        
        #Serialização (Marshaller)
        
        #Transforma o objeto Packet em bytes usando pickle
        marshaller = Marshaller()
        msg_bytes = marshaller.marshal(miopReqPacket)

        
        #Envio via CRH (Rede)
        
        # Instancia o CRH com host/porta do IOR da invocação
        # O CRH cuida de conectar, enviar o tamanho (framing) e receber a resposta
        crh = ClientRequestHandler(invocation.ior.host, invocation.ior.port)
        
        response_bytes = crh.send_receive(msg_bytes)

        # Validação de segurança
        if not response_bytes:
            raise Exception("Requestor: Recebeu resposta vazia do CRH (Falha de Rede ou Servidor caiu?)")

        
        #Extração da Resposta
        
        # A. Unmarshalling: Bytes -> Objeto Packet
        miopRepPacket = marshaller.unmarshal(response_bytes)
        
        # B. MIOP Extraction: Packet -> Objeto shared.Reply
        # Nota: extractReply devolve um objeto Reply (que contém o .result dentro)
        reply = Miop.extractReply(miopRepPacket)

        # C. Termination: Encapsula o Reply para devolver ao Proxy
        t = Termination(reply)

        return t