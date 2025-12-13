from ClientRequestHandler import ClientRequestHandler
from Marshaller import Marshaller

class ClientProxy:
    """
    Atua como um **Stub** (Ponte). 
    O objetivo desta classe é oferecer transparência de localização: fazer com que 
    uma chamada remota (via rede) pareça uma simples chamada de método local para a aplicação.
    """
    def __init__(self, host='localhost', port=8080):
        # Delega a parte "suja" de lidar com sockets para o CRH
        self.crh = ClientRequestHandler(host, port)
        
        # Delega a conversão de dados (Objeto <-> Bytes) para o Marshaller
        self.marshaller = Marshaller()

    def publish(self, topic, message):
        """
        Transforma a intenção de 'Publicar' em um comando compreensível pelo Broker.
        A aplicação só passa os dados úteis, o Proxy cuida da estrutura.
        """
        # Monta o "envelope" (Protocolo de Aplicação)
        inv_args = {
            'OP': 'Publish',      # O Código da Operação
            'queue_id': topic,    # O Destino
            'MSG': message        # O Conteúdo
        }
        # Inicia o processo de envio pela rede
        return self._send_request(inv_args)

    def subscribe(self, topic, sensor_id):
        """
        Envia um pedido de assinatura.
        Diz ao Broker: "Crie uma fila para mim (sensor_id) vinculada a este tópico".
        """
        inv_args = {
            'OP': 'Subscribe',
            'queue_id': topic,
            'sensor_id': sensor_id
        }
        return self._send_request(inv_args)

    def check_msg(self, topic, sensor_id):
        """
        Implementa o modelo **Pull** (Polling).
        O cliente vai perguntar: "Tem algo novo na minha fila?"
        """
        inv_args = {
            'OP': 'CheckMsg',
            'queue_id': topic,
            'sensor_id': sensor_id
        }
        return self._send_request(inv_args)

    def _send_request(self, inv_args):
        """
        Método auxiliar que padroniza o ciclo de vida de qualquer requisição (Pipeline).
        Centraliza a lógica de Serialização e Transporte em um só lugar.
        """
        # 1. Marshalling: Converte o dicionário Python em Bytes
        msg_bytes = self.marshaller.marshall(inv_args)
        
        # 2. Request-Reply: Envia os bytes e fica BLOQUEADO esperando a resposta do servidor
        reply_bytes = self.crh.send_receive(msg_bytes)
        
        # 3. Unmarshalling: Converte a resposta (Bytes) de volta para objeto Python
        return self.marshaller.unmarshall(reply_bytes)