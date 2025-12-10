from SubscriptionsManager import SubscriptionsManager
from collections import deque
            
# Instancia a classe ANTES do loop para não perder os dados
manager = SubscriptionsManager()

while True: 
    print("\n--- MENU DE COMANDOS ---")
    print("1. Registrar a fila que o veículo vai publicar")
    print("2. Ver dados salvos (Debug)")
    print("3. remover")
    print("4. Sair")

    choice = input("Escolha uma opção: ")

    if choice == '1':
        # Coleta os dados do usuário
        vehicle_id = input("Digite o ID do veículo: ")
        #speed_input = input("Digite a velocidade do veículo (km/h): ")        
        queue_id = "velocidade" 
        manager.insert_subscription(vehicle_id, queue_id)
    
    elif choice == '2':
        manager.get_subscriptions()        

    elif choice == '3':
        vehicle_id = input("Digite o ID do veículo para remover a assinatura: ")
        queue_id = "velocidade"  # Usando a mesma fila padrão

        manager.remove_subscription(vehicle_id, queue_id)

    elif choice == '4':
        print("Saindo do programa.")
        break

    else:
        print("Opção inválida. Tente novamente.")