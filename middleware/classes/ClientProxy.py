from ClientRequestHandler import ClientRequestHandler
from Marshaller import Marshaller

class ClientProxy:
    def __init__(self, host='localhost', port=8080):
        self.crh = ClientRequestHandler(host, port)
        self.marshaller = Marshaller()

    def publish(self, topic, message):
        inv_args = {
            'OP': 'Publish',
            'queue_id': topic,
            'MSG': message
        }
        return self._send_request(inv_args)

    def subscribe(self, topic, sensor_id):
        inv_args = {
            'OP': 'Subscribe',
            'queue_id': topic,
            'sensor_id': sensor_id
        }
        return self._send_request(inv_args)

    def check_msg(self, topic, sensor_id):
        inv_args = {
            'OP': 'CheckMsg',
            'queue_id': topic,
            'sensor_id': sensor_id
        }
        return self._send_request(inv_args)

    def _send_request(self, inv_args):
        """Método auxiliar para evitar repetição de código"""
        msg_bytes = self.marshaller.marshall(inv_args)
        reply_bytes = self.crh.send_receive(msg_bytes)
        return self.marshaller.unmarshall(reply_bytes)