"""Falha de leitura do sensor de temperatura com retry, recuperação e report de erro à API."""
import time

from main import print_banner, get_logger, setup_logging, conectar_device_existente

setup_logging()
logger_api = get_logger("API_CLIENT")
logger_mqtt = get_logger("MQTT")
logger_pool = get_logger("SENSOR_POOL")
logger_sensor = get_logger("SENSOR_WORKER")

DEVICE_UUID = "f656cca5-20eb-47f7-9126-281d0bc6b35f"
MQTT_HOST = "173.249.6.202"
MQTT_PORT = 1883

_SENSORES_API = [
    {"id": 1, "tipo": "umidade_solo", "modelo": "YL-69"},
    {"id": 3, "tipo": "temperatura", "modelo": "LM35DZ"},
]

_SANIDADE_MIN = -40.0
_SANIDADE_MAX = 80.0

_MAX_TENTATIVAS = 5
_BACKOFF_BASE_SEGUNDOS = 0.5

_RESULTADOS_TENTATIVAS = [None, None, -127.0, None, 24.3]


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
    logger_sensor.debug("Worker criado")
    time.sleep(0.05)
    logger_sensor.info("Worker iniciado")


def _ler_sensor_bruto(tentativa_idx: int) -> float | None:
    return _RESULTADOS_TENTATIVAS[tentativa_idx]


def _reportar_erro_sensor(sensor_id: int) -> None:
    logger_api.debug("Enviando erro do sensor (sensor_id=%d)", sensor_id)
    time.sleep(0.2)
    logger_api.warning("Erro do sensor reportado (sensor_id=%d)", sensor_id)


def ler_temperatura_com_retry(sensor: dict) -> float:
    for tentativa in range(1, _MAX_TENTATIVAS + 1):
        valor = _ler_sensor_bruto(tentativa - 1)
        time.sleep(0.3)

        if valor is None:
            logger_sensor.warning(
                "Sensor não respondeu: sensor_id=%d tentativa=%d/%d",
                sensor["id"], tentativa, _MAX_TENTATIVAS,
            )

        elif not (_SANIDADE_MIN <= valor <= _SANIDADE_MAX):
            logger_sensor.error("Erro na leitura do sensor: sensor_id=%d", sensor["id"])
            _reportar_erro_sensor(sensor["id"])

        else:
            logger_sensor.debug(
                "Leitura obtida: sensor_id=%d temperatura=%.1f tentativa=%d/%d",
                sensor["id"], valor, tentativa, _MAX_TENTATIVAS,
            )
            return valor

        if tentativa < _MAX_TENTATIVAS:
            time.sleep(_BACKOFF_BASE_SEGUNDOS * (2 ** (tentativa - 1)))

    logger_sensor.error(
        "Falha na leitura do sensor de temperatura após %d tentativas: sensor_id=%d",
        _MAX_TENTATIVAS, sensor["id"],
    )
    _reportar_erro_sensor(sensor["id"])
    raise RuntimeError("Sensor de temperatura indisponível")


def executar_simulacao_falha_sensor() -> None:
    print_banner()
    print()

    conectar_device_existente(DEVICE_UUID)
    conectar_mqtt()

    logger_api.info("Enviando Status de online para Api.")

    sensores = descobrir_sensores()
    for sensor in sensores:
        adicionar_runner(sensor)

    sensor_temp = next(s for s in sensores if s["tipo"] == "temperatura")
    temperatura = ler_temperatura_com_retry(sensor_temp)
    logger_sensor.debug(
        "Leitura obtida: sensor_id=%d temperatura=%.1f", sensor_temp["id"], temperatura
    )


if __name__ == "__main__":
    executar_simulacao_falha_sensor()