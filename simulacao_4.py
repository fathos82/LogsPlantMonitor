"""Ciclo completo de execução do PlantMonitor: boot -> MQTT -> descoberta de sensores -> leitura -> publish."""
import time

from main import print_banner, get_logger, setup_logging, conectar_device_existente

setup_logging()
logger_api = get_logger("API_CLIENT")
logger_mqtt = get_logger("MQTT")
logger_pool = get_logger("SENSOR_POOL")
logger_worker = get_logger("SENSOR_WORKER")
logger_publisher = get_logger("PUBLISHER")

DEVICE_UUID = "f656cca5-20eb-47f7-9126-281d0bc6b35f"
MQTT_HOST = "173.249.6.202"
MQTT_PORT = 1883

BATCH_SIZE = 5

_SENSORES_API = [
    {"id": 1, "tipo": "umidade_solo", "modelo": "YL-69"},
    {"id": 3, "tipo": "temperatura", "modelo": "LM35DZ"},
]

_LEITURAS_TEMPERATURA = [22.4, 23.1, 24.6, 25.0, 24.8]
_LEITURA_SOLO = 38.5  # % de umidade


def conectar_mqtt() -> None:
    logger_mqtt.info("Inicializando conexão com broker MQTT")
    logger_mqtt.debug("Conectando ao MQTT broker (%s:%d)...", MQTT_HOST, MQTT_PORT)
    time.sleep(0.5)


def descobrir_sensores() -> list[dict]:
    logger_pool.info("Iniciando varredura de sensores cadastrados")
    time.sleep(0.4)

    for sensor in _SENSORES_API:
        logger_pool.debug(
            "Sensor detectado: tipo=%s modelo=%s id=%s",
            sensor["tipo"], sensor["modelo"], sensor["id"],
        )
        time.sleep(0.15)

    logger_pool.info("Varredura concluída: %d sensor(es) encontrado(s)", len(_SENSORES_API))
    return _SENSORES_API


def adicionar_runner(sensor: dict) -> None:
    logger_pool.info("Adicionando runner para sensor %d", sensor["id"])
    time.sleep(0.1)
    logger_worker.debug("Worker criado")
    time.sleep(0.05)
    logger_worker.info("Worker iniciado")


def _payload_bytes(topic: str) -> int:
    return 90 + len(topic)


def _publicar(topic: str) -> None:
    payload_bytes = _payload_bytes(topic)
    # logger_publisher.debug("Publishing topic %s", topic)
    logger_mqtt.debug("Publicando em %s (%d bytes)", topic, payload_bytes)
    # logger_publisher.debug("Publicado em %s (%d bytes)", topic, payload_bytes)


def operar_sensores(sensores: list[dict]) -> None:
    sensor_solo = next(s for s in sensores if s["tipo"] == "umidade_solo")
    sensor_temp = next(s for s in sensores if s["tipo"] == "temperatura")

    for indice, temperatura in enumerate(_LEITURAS_TEMPERATURA, start=1):
        time.sleep(0.05)
        logger_worker.debug(
            "Leitura #%d: sensor_id=%d temperatura=%.1f", indice, sensor_temp["id"], temperatura
        )
        if indice == 3:
            time.sleep(0.05)
            logger_worker.debug(
                "Leitura #1: sensor_id=%d umidade=%.1f", sensor_solo["id"], _LEITURA_SOLO
            )

    # _publicar(f"plant_monitor/{sensor_solo['id']}/{sensor_solo['tipo'].upper()}")
    logger_worker.debug(f"5 Leituras do sensor_id=%d acumuladas, iniciando o envio para nuvem...",sensor_temp["id"])
    _publicar(f"plant_monitor/{sensor_temp['id']}/{sensor_temp['tipo'].upper()}")


def executar_ciclo_completo() -> None:
    print_banner()
    print()

    conectar_device_existente(DEVICE_UUID)
    conectar_mqtt()

    logger_api.info("Enviando Status de online para Api.")

    sensores = descobrir_sensores()
    for sensor in sensores:
        adicionar_runner(sensor)

    operar_sensores(sensores)


if __name__ == "__main__":
    executar_ciclo_completo()