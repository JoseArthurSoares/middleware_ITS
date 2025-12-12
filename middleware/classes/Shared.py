from dataclasses import dataclass, field
from typing import Any, List

# ==========================================
# Identificação do Objeto Remoto
# ==========================================
@dataclass
class IOR:
    """
    Interoperable Object Reference.
    Guarda onde o objeto está (Host/Port) e qual objeto é (ObjectKey).
    """
    host: str = "localhost"
    port: int = 0
    objectKey: int = 0  # Identificador único do objeto no servidor

# ==========================================
# Estruturas de Mensagem Interna
# ==========================================
@dataclass
class Request:
    """
    Representa O QUE deve ser executado.
    """
    op: str = ""                # Nome do método (ex: "add")
    params: List[Any] = field(default_factory=list) # Parâmetros (ex: [10, 20])

@dataclass
class Reply:
    """
    Representa O QUE foi retornado.
    """
    result: Any = None          # O retorno (ex: 30)

# ==========================================
# Estruturas de Fluxo (Proxy <-> Requestor)
# ==========================================
@dataclass
class Invocation:
    """
    Pacote completo que o Proxy entrega para o Requestor.
    Diz: "Mande esse Request para esse IOR".
    """
    ior: IOR = field(default_factory=IOR)
    request: Request = field(default_factory=Request)

@dataclass
class Termination:
    """
    Pacote completo que o Requestor devolve para o Proxy.
    Diz: "Aqui está a resposta (Reply) que chegou".
    """
    rep: Reply = field(default_factory=Reply)