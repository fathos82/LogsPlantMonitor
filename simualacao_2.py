"""Conexão com o broker MQTT e publicação em lote das leituras do sensor de temperatura."""
import time

from main import print_banner, get_logger, setup_logging, conectar_device_existente
DEVICE_UUID = "f656cca5-20eb-47f7-9126-281d0bc6b35f"

setup_logging()
logger_mqtt = get_logger("MQTT")
logger_sensor = get_logger("SENSOR_WORKER")
logger_publisher = get_logger("PUBLISHER")

_MQTT_HOST = "173.249.6.202"
_MQTT_PORT = 1883

_SENSOR_TEMPERATURA = {"id": 3, "tipo": "temperatura", "modelo": "DHT22", "porta": "GPIO4"}

_TEMP_MIN_NORMAL = 18.0
_TEMP_MAX_NORMAL = 29.0
_BATCH_SIZE = 10

_LEITURAS_TEMPERATURA = [
    22.4, 23.1, 24.6, 25.0, 24.8,
    23.9, 24.1, 25.3, 24.6, 23.8,
]


def conectar_mqtt() -> None:
    logger_mqtt.info("Inicializando conexão com broker MQTT")
    logger_mqtt.debug("Conectando ao MQTT broker (%s:%d)...", _MQTT_HOST, _MQTT_PORT)
    time.sleep(0.5)


def realizar_leituras_e_publicar(sensor: dict) -> None:
    buffer: list[float] = []
    topic = f"plant_monitor/{sensor['id']}/{sensor['tipo'].upper()}"

    for indice, temperatura in enumerate(_LEITURAS_TEMPERATURA, start=1):
        time.sleep(0.4)

        if _TEMP_MIN_NORMAL <= temperatura <= _TEMP_MAX_NORMAL:
            logger_sensor.debug(
                "Leitura: sensor_id=%d temperatura=%.1f",  sensor["id"], temperatura
            )
        else:
            logger_sensor.warning(
                "Leitura fora da faixa esperada: sensor_id=%d temperatura=%.1f (limite=%.1f-%.1f)",
                sensor["id"], temperatura, _TEMP_MIN_NORMAL, _TEMP_MAX_NORMAL,
            )

        buffer.append(temperatura)

        if len(buffer) >= _BATCH_SIZE:
            payload_bytes = 14 * len(buffer)  # simula tamanho serializado do payload

            logger_publisher.debug("Publishing topic %s", topic)
            logger_mqtt.debug("Publicando em %s (%d bytes)", topic, payload_bytes)
            logger_publisher.debug("Publicado em %s (%d bytes)", topic, payload_bytes)

            buffer.clear()


def executar_simulacao_publicacao() -> None:
    print_banner()
    conectar_device_existente(DEVICE_UUID)
    print()

    conectar_mqtt()
    realizar_leituras_e_publicar(_SENSOR_TEMPERATURA)


if __name__ == "__main__":
    executar_simulacao_publicacao()