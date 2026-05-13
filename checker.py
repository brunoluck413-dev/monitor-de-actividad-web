"""
checker.py
----------
Módulo de verificación HTTP. Realiza peticiones GET a cada URL
y captura el código de estado, tiempo de respuesta y errores.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import requests


@dataclass
class CheckResult:
    """Resultado de la verificación de una URL."""
    url: str
    status_code: Optional[int]      # None si hubo error de conexión
    response_ms: Optional[float]    # Tiempo de respuesta en milisegundos
    error: Optional[str]            # Mensaje de error (si aplica)
    checked_at: datetime

    @property
    def is_ok(self) -> bool:
        """True si la respuesta fue 2xx."""
        return self.status_code is not None and 200 <= self.status_code < 300

    @property
    def is_redirect(self) -> bool:
        """True si la respuesta fue 3xx."""
        return self.status_code is not None and 300 <= self.status_code < 400

    @property
    def is_client_error(self) -> bool:
        """True si la respuesta fue 4xx."""
        return self.status_code is not None and 400 <= self.status_code < 500

    @property
    def is_server_error(self) -> bool:
        """True si la respuesta fue 5xx."""
        return self.status_code is not None and self.status_code >= 500

    @property
    def is_unreachable(self) -> bool:
        """True si no se pudo conectar (timeout, DNS, etc.)."""
        return self.status_code is None


def check_url(url: str, timeout: int = 10) -> CheckResult:
    """
    Realiza una petición GET a la URL y retorna el resultado.

    Args:
        url: URL a verificar (debe incluir esquema http/https).
        timeout: Segundos antes de abortar la petición.

    Returns:
        CheckResult con el estado de la verificación.
    """
    checked_at = datetime.now()

    try:
        response = requests.get(
            url,
            timeout=timeout,
            allow_redirects=True,
            headers={"User-Agent": "url-monitor/1.0"},
        )
        response_ms = response.elapsed.total_seconds() * 1000
        return CheckResult(
            url=url,
            status_code=response.status_code,
            response_ms=round(response_ms, 1),
            error=None,
            checked_at=checked_at,
        )

    except requests.exceptions.ConnectionError:
        error_msg = "Error de conexión (DNS o red)"
    except requests.exceptions.Timeout:
        error_msg = f"Timeout después de {timeout}s"
    except requests.exceptions.TooManyRedirects:
        error_msg = "Demasiadas redirecciones"
    except requests.exceptions.RequestException as e:
        error_msg = str(e)

    return CheckResult(
        url=url,
        status_code=None,
        response_ms=None,
        error=error_msg,
        checked_at=checked_at,
    )


def check_all_urls(urls: list[str], timeout: int = 10) -> list[CheckResult]:
    """
    Verifica una lista de URLs de forma secuencial.

    Args:
        urls: Lista de URLs a verificar.
        timeout: Timeout por petición en segundos.

    Returns:
        Lista de CheckResult en el mismo orden que las URLs de entrada.
    """
    return [check_url(url, timeout=timeout) for url in urls]
