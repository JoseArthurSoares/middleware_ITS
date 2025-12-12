from dataclasses import dataclass, field
from typing import List, Any
#from Shared import IOR, Request, Reply, Invocation, Termination
import Shared as shared
# ==========================================
# Estruturas de Dados (Dataclasses)
# ==========================================

@dataclass
class Header:
    magic: str = "MIOP"
    version: str = "1.0"
    byteOrder: bool = False
    messageType: int = 0
    size: int = 0

@dataclass
class RequestHeader:
    context: str = ""
    requestId: int = 0
    responseExpected: bool = True
    objectKey: int = 0
    operation: str = ""

@dataclass
class RequestBody:
    body: List[Any] = field(default_factory=list)

@dataclass
class ReplyHeader:
    context: str = ""
    requestId: int = 0
    status: int = 0

@dataclass
class ReplyBody:
    operationResult: Any = None

@dataclass
class Body:
    reqHeader: RequestHeader = field(default_factory=RequestHeader)
    reqBody: RequestBody = field(default_factory=RequestBody)
    repHeader: ReplyHeader = field(default_factory=ReplyHeader)
    repBody: ReplyBody = field(default_factory=ReplyBody)

@dataclass
class Packet:
    hdr: Header = field(default_factory=Header)
    bd: Body = field(default_factory=Body)

# ==========================================
# Funções do Módulo (camelCase)
# ==========================================

def createRequestMIOP(op: str, params: List[Any]) -> Packet:
    """
    Cria um pacote MIOP configurado como Request.
    """
    reqHeader = RequestHeader(
        operation=op,
        responseExpected=True,
        requestId=100
    )
    reqBody = RequestBody(body=params)
    
    # Observe o uso das chaves em camelCase aqui também
    miopBody = Body(reqHeader=reqHeader, reqBody=reqBody)
    
    return Packet(bd=miopBody)

def createReplyMIOP(result: Any) -> Packet:
    """
    Cria um pacote MIOP configurado como Reply.
    """
    repHeader = ReplyHeader(requestId=1313, status=1)
    repBody = ReplyBody(operationResult=result)
    
    miopBody = Body(repHeader=repHeader, repBody=repBody)
    
    return Packet(bd=miopBody)

def extractRequest(packet: Packet) -> shared.Request:
    """
    Extrai a requisição do pacote.
    """
    req = shared.Request()
    # Acesso via camelCase
    req.op = packet.bd.reqHeader.operation
    req.params = packet.bd.reqBody.body
    
    return req

def extractReply(packet: Packet) -> shared.Reply:
    """
    Extrai a resposta do pacote.
    """
    rep = shared.Reply()
    # Acesso via camelCase
    rep.result = packet.bd.repBody.operationResult
    
    return rep