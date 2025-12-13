import socket
import struct

class ServerRequestHandler:
    def __init__(self, host, port):
        # Configuração do Socket TCP (IPv4, Stream)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Permite reiniciar o servidor rapidamente sem esperar o timeout do OS na porta
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Vincula o socket ao endereço IP e porta especificados
        self.server_socket.bind((host, port))
        
        # Entra em modo de escuta. 
        # O parâmetro '1' define o tamanho da fila de conexões pendentes (Backlog).
        self.server_socket.listen(1)
        
        self.connection = None
        # Nota arquitetural: O 'accept' não ocorre aqui, mas sim sob demanda no loop do servidor.

    def receive(self):
        """
        Implementa o padrão de recepção "Connection-per-Request".
        Bloqueia a execução até que um Cliente (CRH) tente falar conosco.
        """
        try:
            # 1. Handshake TCP: Aceita uma NOVA conexão de cliente.
            # O código para aqui (Block) até alguém conectar.
            self.connection, _ = self.server_socket.accept()
            
            # 2. Framing (Cabeçalho): Lê os primeiros 4 bytes para saber o tamanho da mensagem.
            size_bytes = self._recv_exactly(4)
            if not size_bytes:
                return None

            # Desempacota os 4 bytes em um inteiro (Little Endian)
            size_int = struct.unpack('<I', size_bytes)[0]

            # 3. Payload (Corpo): Lê exatamente a quantidade de bytes que o cabeçalho prometeu.
            msg = self._recv_exactly(size_int)
            if not msg:
                return None

            # Retorna os bytes puros para o Marshaller/Invoker processar.
            return msg

        except Exception as e:
            print(f"SRH Error: {e}")
            self.close()
            return None

    def send(self, msg_to_client: bytes):
        """
        Envia a resposta usando o mesmo socket que foi aceito no receive().
        """
        if self.connection is None:
            return

        try:
            # Adiciona o cabeçalho de tamanho antes dos dados (Framing)
            msg_len = len(msg_to_client)
            header = struct.pack('<I', msg_len)
            
            # Envia tudo pela rede (Header + Body)
            self.connection.sendall(header)
            self.connection.sendall(msg_to_client)

        except Exception as e:
            print(f"SRH Send Error: {e}")
            self.close()

    def _recv_exactly(self, n):
        #Este loop acumula pedaços até ter exatamente 'n' bytes.

        data = b''
        try:
            while len(data) < n:
                packet = self.connection.recv(n - len(data))
                if not packet: return None # Conexão caiu
                data += packet
            return data
        except:
            return None

    def close(self):
        #Encerra a conexão com o cliente atual.
        if self.connection:
            try:
                self.connection.close()
            except:
                pass
            self.connection = None