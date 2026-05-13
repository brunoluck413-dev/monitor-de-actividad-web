"""
url_monitor.py
--------------
Verifica el estado HTTP de una lista de URLs de forma periódica
y emite alertas por consola cuando detecta fallos o lentitud.

Usa las bibliotecas `requests` y `schedule`.

Uso:
    python url_monitor.py                        # usa urls.txt por defecto
    python url_monitor.py --urls urls.txt        # archivo personalizado
    python url_monitor.py --interval 60          # revisa cada 60 segundos
    python url_monitor.py --once                 # una sola verificación
"""

import argparse
import sys
import time

import schedule

from checker import check_all_urls
from config import load_urls, MonitorConfig
from display import print_banner, print_summary
from logger import get_logger

logger = get_logger(__name__)


def run_check(config: MonitorConfig) -> None:
    """Ejecuta una ronda completa de verificación y muestra resultados."""
    results = check_all_urls(config.urls, timeout=config.timeout)
    print_summary(results, config.slow_threshold_ms)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Monitor de URLs: verifica estado HTTP y emite alertas."
    )
    parser.add_argument(
        "--urls",
        default="urls.txt",
        help="Archivo de texto con una URL por línea (default: urls.txt).",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Segundos entre cada verificación (default: 30).",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Segundos de timeout por petición (default: 10).",
    )
    parser.add_argument(
        "--slow-threshold",
        type=int,
        default=2000,
        help="Tiempo en ms para considerar una respuesta lenta (default: 2000).",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Ejecutar solo una vez y salir (no programar repetición).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print_banner()

    try:
        urls = load_urls(args.urls)
    except FileNotFoundError as e:
        logger.error(f"No se encontró el archivo de URLs: {e}")
        sys.exit(1)

    if not urls:
        logger.warning("El archivo de URLs está vacío.")
        sys.exit(0)

    config = MonitorConfig(
        urls=urls,
        interval=args.interval,
        timeout=args.timeout,
        slow_threshold_ms=args.slow_threshold,
    )

    logger.info(f"URLs cargadas: {len(urls)}")
    logger.info(f"Intervalo de verificación: {config.interval}s")
    logger.info(f"Timeout por petición: {config.timeout}s")
    logger.info(f"Umbral de lentitud: {config.slow_threshold_ms}ms\n")

    # Primera verificación inmediata
    run_check(config)

    if args.once:
        return

    # Programar verificaciones periódicas con schedule
    schedule.every(config.interval).seconds.do(run_check, config=config)
    logger.info(f"\n⏱  Próxima verificación en {config.interval}s. Presiona Ctrl+C para detener.\n")

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\n🛑 Monitor detenido por el usuario.")


if __name__ == "__main__":
    main()
