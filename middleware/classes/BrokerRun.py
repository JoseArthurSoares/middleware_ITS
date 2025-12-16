from Invoker import Invoker
from BrokerEngine import BrokerEngine

if __name__ == "__main__":
    print("--- Inicializando Servidor Middleware ---")
    
    # 1. Instancia a Lógica (O Cérebro)
    my_engine = BrokerEngine()
    
    # 2. Instancia o Invoker (A Rede) passando a Lógica
    my_invoker = Invoker('localhost', 8080, my_engine)
    
    # 3. Roda
    my_invoker.invoke()