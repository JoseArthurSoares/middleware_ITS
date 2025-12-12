import pickle

class Marshaller:
    def marshall(self, data):
        """
        Serializa um objeto (dict, list, str) para bytes.
        """
        try:
            return pickle.dumps(data)
        except Exception as e:
            print(f"[Marshaller ERROR] Falha ao serializar: {e}")
            return b''

    def unmarshall(self, data_bytes):
        """
        Converte bytes de volta para o objeto original.
        """
        try:
            return pickle.loads(data_bytes)
        except Exception as e:
            print(f"[Marshaller ERROR] Falha ao deserializar: {e}")
            return None