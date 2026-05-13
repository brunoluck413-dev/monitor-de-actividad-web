"""
display.py
----------
Módulo de presentación en consola. Formatea y muestra los resultados
de verificación con colores ANSI y alertas claras.
"""

from datetime import datetime

from checker import CheckResult


# ── Códigos de color ANSI ──────────────────────────────────────────────────
class Color:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    RED     = "\033[91m"
    CYAN    = "\033[96m"
    MAGENTA = "\033[95m"
    GRAY    = "\033[90m"
    WHITE   = "\033[97m"


def _colored(text: str, *codes: str) -> str:
    return "".join(codes) + text + Color.RESET


def _status_label(result: CheckResult, slow_ms: int) -> str:
    """Retorna el emoji e icono de estado según el resultado."""
    if result.is_unreachable:
        return _colored("✗ CAÍDO", Color.RED, Color.BOLD)
    if result.is_server_error:
        return _colored(f"✗ ERROR {result.status_code}", Color.RED, Color.BOLD)
    if result.is_client_error:
        return _colored(f"⚠ {result.status_code}", Color.YELLOW, Color.BOLD)
    if result.is_redirect:
        return _colored(f"→ {result.status_code}", Color.CYAN)
    if result.is_ok:
        if result.response_ms is not None and result.response_ms > slow_ms:
            return _colored(f"⚡ LENTO ({result.status_code})", Color.YELLOW, Color.BOLD)
        return _colored(f"✓ OK ({result.status_code})", Color.GREEN)
    return _colored(f"? {result.status_code}", Color.GRAY)


def _response_time_label(result: CheckResult, slow_ms: int) -> str:
    """Formatea el tiempo de respuesta con color según umbral."""
    if result.response_ms is None:
        return _colored("N/A", Color.GRAY)
    ms = result.response_ms
    color = Color.RED if ms > slow_ms else (Color.YELLOW if ms > slow_ms * 0.7 else Color.GREEN)
    return _colored(f"{ms:.0f}ms", color)


def print_banner() -> None:
    """Imprime el banner de inicio del monitor."""
    print(_colored("\n╔══════════════════════════════════════╗", Color.CYAN))
    print(_colored("║      🔍  URL Monitor v1.0            ║", Color.CYAN, Color.BOLD))
    print(_colored("╚══════════════════════════════════════╝\n", Color.CYAN))


def print_summary(results: list[CheckResult], slow_threshold_ms: int = 2000) -> None:
    """Imprime el resumen de una ronda de verificación en consola."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sep = _colored("─" * 72, Color.GRAY)

    print(f"\n{sep}")
    print(_colored(f"  Verificación: {now}", Color.GRAY))
    print(sep)

    ok_count = 0
    alert_count = 0

    for r in results:
        status = _status_label(r, slow_threshold_ms)
        time_label = _response_time_label(r, slow_threshold_ms)
        url_display = r.url[:50] + "…" if len(r.url) > 50 else r.url

        # Línea principal
        print(f"  {status:<35} {time_label:<12} {_colored(url_display, Color.WHITE)}")

        # Alerta de error detallada
        if r.is_unreachable:
            print(_colored(f"    ↳ {r.error}", Color.RED))
            alert_count += 1
        elif r.is_server_error or r.is_client_error:
            alert_count += 1
        elif r.is_ok and r.response_ms is not None and r.response_ms > slow_threshold_ms:
            print(_colored(f"    ↳ Respuesta lenta: {r.response_ms:.0f}ms (umbral: {slow_threshold_ms}ms)", Color.YELLOW))
            alert_count += 1
        else:
            ok_count += 1

    print(sep)

    # Resumen de la ronda
    total = len(results)
    ok_txt = _colored(f"{ok_count} OK", Color.GREEN)
    alert_txt = _colored(f"{alert_count} alertas", Color.RED if alert_count > 0 else Color.GRAY)
    print(f"  {total} URLs verificadas · {ok_txt} · {alert_txt}")
    print(sep)

    # Alerta de emergencia si hay fallos críticos
    critical = [r for r in results if r.is_unreachable or r.is_server_error]
    if critical:
        print(_colored(f"\n  🚨 ALERTA: {len(critical)} URL(s) con fallos críticos:", Color.RED, Color.BOLD))
        for r in critical:
            print(_colored(f"     • {r.url}", Color.RED))
        print()
