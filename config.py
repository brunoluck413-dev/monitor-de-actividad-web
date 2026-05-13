"""
config.py
---------
Carga la configuración del monitor: lista de URLs y parámetros de ejecución.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class MonitorConfig:
    """Parámetros de configuración del monitor."""
    urls: list[str]
    interval: int = 30          # Segundos entre verificaciones
    timeout: int = 10           # Timeout por petición (segundos)
    slow_threshold_ms: int = 2000  # Ms a partir de los cuales se considera lento


def load_urls(filepath: str) -> list[str]:
    """
    Lee un archivo de texto y retorna una lista de URLs válidas.

    El archivo debe tener una URL por línea.
    Las líneas en blanco y comentarios (#) son ignorados.

    Args:
        filepath: Ruta al archivo de URLs.

    Returns:
        Lista de URLs limpias.

    Raises:
        FileNotFoundError: Si el archivo no existe.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(filepath)

    urls = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            url = line.strip()
            # Ignorar líneas vacías y comentarios
            if url and not url.startswith("#"):
                urls.append(url)

    return urls
