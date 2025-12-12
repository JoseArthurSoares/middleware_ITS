import socket
import struct
import time

MAX_CONNECTION_ATTEMPTS = 5

class ClientRequestHandler:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.connection = None

    def _connect_with_retry(self):
        """Tenta conectar com lógica de re-tentativa."""
        for i in range(MAX_CONNECTION_ATTEMPTS):
            try:
                self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.connection.connect((self.host, self.port))
                return True
            except socket.error:
                time.sleep(0.01) # Espera curta
        raise ConnectionError("Falha ao conectar após várias tentativas")

    def send_receive(self, msg_to_server: bytes) -> bytes:
        """
        Padrão Síncrono (Request-Reply).
        """
        try:
            self._connect_with_retry()

            # 1. Envia Tamanho + Mensagem
            msg_len = len(msg_to_server)
            self.connection.sendall(struct.pack('<I', msg_len))
            self.connection.sendall(msg_to_server)

            # 2. Recebe Tamanho da Resposta
            size_bytes = self._recv_exactly(4)
            if not size_bytes:
                raise Exception("CRH: Servidor fechou conexão sem resposta (Header).")
            
            size_int = struct.unpack('<I', size_bytes)[0]

            # 3. Recebe Corpo da Resposta
            response_data = self._recv_exactly(size_int)
            if not response_data:
                raise Exception("CRH: Servidor fechou conexão sem resposta (Body).")

            return response_data

        except Exception as e:
            raise e
        finally:
            if self.connection:
                self.connection.close()

    def send(self, msg_to_server: bytes):
        """
        Padrão Assíncrono (Fire-and-Forget).
        Uso opcional, caso queira implementar envio sem espera.
        """
        try:
            self._connect_with_retry()
            msg_len = len(msg_to_server)
            self.connection.sendall(struct.pack('<I', msg_len))
            self.connection.sendall(msg_to_server)
        except Exception as e:
            print(f"CRH Send Error: {e}")
        finally:
            if self.connection:
                self.connection.close()

    def _recv_exactly(self, n):
        data = b''
        while len(data) < n:
            packet = self.connection.recv(n - len(data))
            if not packet: return None
            data += packet
        return data