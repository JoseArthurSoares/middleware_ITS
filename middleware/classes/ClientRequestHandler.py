import socket
import struct
import time

# Defina aqui o número máximo de tentativas de conexão
MAX_CONNECTION_ATTEMPTS = 5

class ClientRequestHandler:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.connection = None

    def _connect_with_retry(self):
        """
        Tenta conectar ao servidor repetidas vezes.
        Retorna True se conseguir, lança Exception se falhar após todas as tentativas.
        """
        for i in range(MAX_CONNECTION_ATTEMPTS):
            try:
                self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.connection.connect((self.host, self.port))
                return True # Conectado com sucesso
            except socket.error:
                # Se falhar, espera 10ms (igual ao Go)
                time.sleep(0.01)
                
        # Se saiu do loop, é porque falhou todas as vezes
        print("CRH 0:: Number Max of attempts achieved...")
        raise ConnectionError("Falha ao conectar após várias tentativas")

    def send_receive(self, msg_to_server: bytes) -> bytes:
        """
        Padrão Request-Reply: Envia dados e espera uma resposta.
        """
        try:
            # Tenta conectar (Retry Logic)
            self._connect_with_retry()

            # -----------------------------------------------------
            # ENVIO
            # -----------------------------------------------------
            # Envia tamanho (4 bytes Little Endian)
            msg_len = len(msg_to_server)
            header = struct.pack('<I', msg_len)
            self.connection.sendall(header)

            # Envia mensagem
            self.connection.sendall(msg_to_server)

            # RECEBIMENTO
            # Recebe tamanho da resposta
            size_bytes_server = self._recv_exactly(4)
            if not size_bytes_server:
                raise Exception("CRH 3:: Falha ao receber tamanho da resposta")
            
            size_server_int = struct.unpack('<I', size_bytes_server)[0]

            # Recebe a resposta (Reply)
            msg_from_server = self._recv_exactly(size_server_int)
            if not msg_from_server:
                raise Exception("CRH 4:: Falha ao receber corpo da resposta")

            return msg_from_server

        except Exception as e:
            # Emula o log.Fatal imprimindo e repassando o erro (ou retornando None)
            print(f"CRH Error: {e}")
            raise e # Ou return None, dependendo de como você quer tratar
        finally:
            # Garante o fechamento da conexão (Defer connection.Close())
            if self.connection:
                self.connection.close()

    def send(self, msg_to_server: bytes):
        """
        Padrão Fire-and-Forget (MOM): Envia e desconecta sem esperar resposta.
        """
        try:
            # 1. Tenta conectar
            self._connect_with_retry()

            # 2. Envia tamanho
            msg_len = len(msg_to_server)
            header = struct.pack('<I', msg_len)
            self.connection.sendall(header)

            # 3. Envia mensagem
            self.connection.sendall(msg_to_server)

            # Não espera resposta, apenas termina.

        except Exception as e:
            print(f"CRH Error: {e}")
            # Em Go era log.Fatal, aqui apenas printamos o erro crítico
        finally:
            if self.connection:
                self.connection.close()

    def _recv_exactly(self, n):
        """Helper para ler exatamente N bytes (Vital para TCP)"""
        data = b''
        while len(data) < n:
            try:
                packet = self.connection.recv(n - len(data))
                if not packet:
                    return None
                data += packet
            except:
                return None
        return data