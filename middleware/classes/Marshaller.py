import pickle

class Marshaller:
    def marshal(self, msg_object) -> bytes:
        """
        Serializa um objeto Python para bytes.
        
        OBS: Não precisamos adicionar cabeçalho de tamanho aqui, 
        pois o CRH/SRH já fazem isso automaticamente no método send().
        """
        # Transforma: Dict, Lista, String, Int -> Bytes
        return pickle.dumps(msg_object)

    def unmarshal(self, msg_bytes) -> any:
        """
        Deserializa bytes de volta para um objeto Python.
        """
        if not msg_bytes:
            return None
            
        # Transforma: Bytes -> Dict, Lista, String, Int
        return pickle.loads(msg_bytes)