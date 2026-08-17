"""Setup de logging e banner do PlantMonitor — reutilizado pelas simulações."""

import logging
import time
import uuid
from logging.handlers import RotatingFileHandler
from pathlib import Path

import segno
from rich.console import Console
from rich.logging import RichHandler
from rich.text import Text

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

def conectar_device_existente(device_uuid: str) -> None:
    logger_api.debug("Verificando existência do device na API (uuid=%s)", device_uuid)
    time.sleep(0.3)
    logger_api.debug("Device encontrado na API")

    logger_api.info("Enviando Status de online para Api.")
    time.sleep(0.2)



def print_banner() -> None:
    console = Console()
    banner_ascii = r"""
  _____  _                   _   __  __             _ _                   
 |  __ \| |           | | |    \/  |           (_) |                  
 | |__) | | __ _ _ __ | |_  | \  / | ___  _ __  _| |_ ___  _ __       
 |  ___/| |/ _` | '_ \| __| | |\/| |/ _ \| '_ \| | __/ _ \| '__|      
 | |    | | (_| | | | | |_  | |  | | (_) | | | | | || (_) | |         
 |_|    |_|\__,_|_| |_|\__| |_|  |_|\___/|_| |_|_|\__\___/|_|         
"""
    console.print(Text(banner_ascii, style="bold spring_green1"))
    footer = Text.assemble(
        (" :: ", "bold black on green"),
        (" PlantMonitor ", "bold white on green"),
        (" :: ", "bold black on green"),
        ("                       (v1.0.0-sim)\n", "dim white"),
    )
    console.print(footer)


def setup_logging() -> None:
    file_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    rich_handler = RichHandler(
        show_time=False, show_level=True, show_path=False, rich_tracebacks=True
    )
    rich_handler.setLevel(logging.DEBUG)

    file_handler = RotatingFileHandler(
        LOG_DIR / "app.log", maxBytes=5_000_000, backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(rich_handler)
    root_logger.addHandler(file_handler)


def get_logger(context: str) -> logging.Logger:
    return logging.getLogger(context.upper())


setup_logging()
logger_device = get_logger("DEVICE")
logger_api = get_logger("API_CLIENT")

_DEVICE_UUID_FILE = Path("simulated_data/device_id")


def gerar_codigo_pareamento(device_uuid: str) -> None:
    data = f"plantmonitor://pair?token={device_uuid}"
    qr = segno.make(data)
    qr.terminal(border=2, compact=True)
    print(f"\nCódigo de pareamento: {device_uuid}\n")


def aguardar_confirmacao_pareamento(device_uuid: str, tentativas_ate_confirmar: int = 4) -> None:
    logger_device.info("Aguardando confirmação de pareamento (uuid=%s)", device_uuid)

    for tentativa in range(1, tentativas_ate_confirmar + 1):
        time.sleep(1)
        confirmado = tentativa >= tentativas_ate_confirmar
        if confirmado:
            logger_device.info("Pareamento confirmado (uuid=%s)", device_uuid)
            return
        logger_device.debug(
            "Pareamento pendente (tentativa %d/%d)", tentativa, tentativas_ate_confirmar
        )


def load_or_create_simulado() -> None:
    print_banner()
    print()
    device_uuid = str(uuid.uuid4())

    logger_device.warning("Dispositivo não encontrado. Criando novo registro.")

    gerar_codigo_pareamento(device_uuid)
    aguardar_confirmacao_pareamento(device_uuid)

    logger_api.debug("Enviando dados do dispositivo para a API")
    time.sleep(0.3)
    logger_api.debug("Dispositivo registrado com sucesso na API")

    _DEVICE_UUID_FILE.parent.mkdir(parents=True, exist_ok=True)
    _DEVICE_UUID_FILE.write_text(device_uuid)

    logger_device.info("UUID persistido localmente")


if __name__ == "__main__":
    load_or_create_simulado()