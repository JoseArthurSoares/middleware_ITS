import time
import random
import paho.mqtt.client as mqtt

BROKER_HOST = "localhost"
BROKER_PORT = 1883
TOPICO = "Transito/Velocidade"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

print("--- [Publisher] Iniciando Sensor (Mosquitto) ---")
try:
    client.connect(BROKER_HOST, BROKER_PORT, 60)
    client.loop_start()  # Inicia loop em background

    while True:
        # 1. Gera dado
        velocidade = random.randint(40, 120)
        mensagem = f"Velocidade aferida: {velocidade} km/h"

        # 2. Publica no Mosquitto
        print(f"📤 [ENVIANDO] {mensagem}")
        info = client.publish(TOPICO, mensagem)

        # Espera confirmação de envio
        info.wait_for_publish()

        time.sleep(2)

except KeyboardInterrupt:
    print("\n[Publisher] Encerrando.")
    client.loop_stop()