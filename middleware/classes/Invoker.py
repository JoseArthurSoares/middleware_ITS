from Marshaller import Marshaller
from Miop import Miop
from ServerRequestHandler import ServerRequestHandler

class Invoker:
    def __init__(self, host, port, engine_impl):
        # Inicializa infraestrutura de rede, serialização e a lógica de negócio
        self.srh = ServerRequestHandler(host, port)
        self.marshaller = Marshaller()
        self.engine_impl = engine_impl

    def invoke(self):
        print(f"Invoker rodando em {self.srh.server_socket.getsockname()}...")

        while True:
            try:
                # Recebe os bytes crus da rede via SRH
                req_bytes = self.srh.receive()
                if not req_bytes: continue

                # Converte os bytes recebidos de volta para um objeto de pacote
                miop_packet_req = self.marshaller.unmarshal(req_bytes)

                # Extrai o nome da operação alvo e seus argumentos
                request_data = Miop.extractRequest(miop_packet_req)
                operation_name = request_data.op
                params = request_data.params

                # Busca dinamicamente o método na Engine usando o nome da string
                method_to_call = getattr(self.engine_impl, operation_name, None)

                result = None
                if method_to_call:
                    print(f"--> Executando: {operation_name}{params}")
                    try:
                        # Executa o método real desempacotando a lista de parâmetros
                        result = method_to_call(*params)
                    except Exception as e:
                        result = f"Error: {e}"
                else:
                    result = "Error: Method not found"

                # Cria o pacote de resposta, serializa para bytes e envia ao cliente
                miop_packet_rep = Miop.createReplyMIOP(result)
                rep_bytes = self.marshaller.marshal(miop_packet_rep)
                self.srh.send(rep_bytes)

            except Exception as e:
                print(f"Erro crítico no Invoker: {e}")
                continue