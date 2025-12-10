import socket
import struct

class ServerRequestHandler:
    def __init__(self, host, port):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host, port))
        self.server_socket.listen(1)
        self.connection = None
        # Não chamamos accept aqui. O accept acontece A CADA receive.

    def receive(self):
        """
        Funcionamento igual ao Go:
        1. Aceita uma NOVA conexão.
        2. Lê o tamanho.
        3. Lê a mensagem.
        4. Retorna a mensagem (mantendo a conexão aberta no self.connection caso queira responder).
        """
        try:
            # BLOQUEIA AQUI até um cliente (CRH) conectar
            self.connection, _ = self.server_socket.accept()
            
            # 1. Lê tamanho (4 bytes)
            size_bytes = self._recv_exactly(4)
            if not size_bytes:
                return None

            size_int = struct.unpack('<I', size_bytes)[0]

            # 2. Lê mensagem
            msg = self._recv_exactly(size_int)
            if not msg:
                return None

            return msg

        except Exception as e:
            print(f"SRH Error: {e}")
            self.close()
            return None

    def send(self, msg_to_client: bytes):
        """
        Envia dados pela conexão que foi aberta no último receive().
        """
        if self.connection is None:
            return

        try:
            msg_len = len(msg_to_client)
            header = struct.pack('<I', msg_len)
            
            self.connection.sendall(header)
            self.connection.sendall(msg_to_client)

        except Exception as e:
            print(f"SRH Send Error: {e}")
            self.close()

    def _recv_exactly(self, n):
        data = b''
        try:
            while len(data) < n:
                packet = self.connection.recv(n - len(data))
                if not packet: return None
                data += packet
            return data
        except:
            return None

    def close(self):
        if self.connection:
            try:
                self.connection.close()
            except:
                pass
            self.connection = None