from Marshaller import Marshaller
from Miop import Miop
from ServerRequestHandler import ServerRequestHandler

class Invoker:
    def __init__(self, host, port, engine_impl):
        """
        :param engine_impl: A instância direta da NotificationEngine.
        """
        self.srh = ServerRequestHandler(host, port)
        self.marshaller = Marshaller()
        self.engine_impl = engine_impl  # Aqui guardamos a Engine direta

    def invoke(self):
        print(f"Invoker rodando em {self.srh.server_socket.getsockname()}...")

        while True:
            try:
                # 1. Recebe bytes da rede
                req_bytes = self.srh.receive()
                if not req_bytes: continue

                # 2. Deserializa (Bytes -> Packet)
                miop_packet_req = self.marshaller.unmarshal(req_bytes)

                # 3. Extrai dados da Requisição
                request_data = Miop.extractRequest(miop_packet_req)
                operation_name = request_data.op  # Ex: "notify", "consume"
                params = request_data.params      # Ex: ["sensor1", 25.0, "temp"]

                # 4. EXECUÇÃO DINÂMICA (A mágica sem Proxy)
                # Procura o método dentro da NotificationEngine com o nome exato
                method_to_call = getattr(self.engine_impl, operation_name, None)

                result = None
                if method_to_call:
                    print(f"--> Executando: {operation_name}{params}")
                    # O '*' desempacota a lista de parâmetros para a função
                    try:
                        result = method_to_call(*params)
                    except Exception as e:
                        print(f"Erro na execução da Engine: {e}")
                        result = f"Error: {e}"
                else:
                    print(f"Erro: Método '{operation_name}' não existe na Engine.")
                    result = "Error: Method not found"

                # 5. Cria pacote de resposta e envia
                miop_packet_rep = Miop.createReplyMIOP(result)
                rep_bytes = self.marshaller.marshal(miop_packet_rep)
                self.srh.send(rep_bytes)

            except Exception as e:
                print(f"Erro crítico no Invoker: {e}")
                continue