import time
import paho.mqtt.client as mqtt

BROKER_HOST = "localhost"
BROKER_PORT = 1883
TOPICO = "Transito/Velocidade"


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"[Subscriber] Conectado ao Mosquitto! Assinando tópico '{TOPICO}'...")
        client.subscribe(TOPICO)
    else:
        print(f"[Subscriber] Falha na conexão. Código: {rc}")


def on_message(client, userdata, msg):
    # Essa função é chamada automaticamente (Callback) quando chega mensagem
    conteudo = msg.payload.decode()
    print(f"📥 [RECEBIDO via Mosquitto] Tópico: {msg.topic} | Msg: {conteudo}")


# Configuração do Cliente
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

print("--- [Subscriber] Iniciando Monitoramento (Mosquitto) ---")
try:
    client.connect(BROKER_HOST, BROKER_PORT, 60)

    # Loop de bloqueio (esculta eterna)
    client.loop_forever()

except KeyboardInterrupt:
    print("\n[Subscriber] Encerrando.")
except Exception as e:
    print(f"Erro: {e}")