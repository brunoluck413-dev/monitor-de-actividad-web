# 🔍 URL Monitor

> Script Python que verifica el estado de URLs periódicamente y envía alertas por consola.  
> Usa las bibliotecas **`requests`** y **`schedule`**.

---

## ¿Qué hace?

- Lee una lista de URLs desde un archivo `.txt`
- Realiza peticiones HTTP GET a cada URL
- Detecta y alerta sobre:
  - URLs **caídas** (sin conexión, timeout, DNS)
  - Respuestas **5xx** (errores de servidor)
  - Respuestas **4xx** (errores de cliente)
  - Respuestas **lentas** (supera un umbral configurable)
- Muestra resultados con **colores en consola** (ANSI)
- Repite la verificación cada N segundos usando `schedule`

## Estructura del proyecto

```
url-monitor/
├── url_monitor.py   # Punto de entrada principal
├── checker.py       # Lógica de peticiones HTTP
├── config.py        # Carga de URLs y configuración
├── display.py       # Formateo de salida en consola
├── logger.py        # Configuración de logging
├── urls.txt         # Lista de URLs a monitorear
├── requirements.txt
└── README.md
```

## Instalación

**Requisitos:** Python 3.10+

```bash
# 1. Clona o descarga el proyecto
cd url-monitor

# 2. (Opcional) Crea un entorno virtual
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

# 3. Instala dependencias
pip install -r requirements.txt
```

## Uso

### Verificación continua (modo monitor)

```bash
python url_monitor.py
```

Usa `urls.txt` por defecto y repite cada 30 segundos.

### Una sola verificación

```bash
python url_monitor.py --once
```

### Opciones avanzadas

```bash
python url_monitor.py \
  --urls mis_urls.txt \
  --interval 60 \
  --timeout 5 \
  --slow-threshold 1500
```

## Formato de `urls.txt`

```
# Líneas con # son comentarios y se ignoran
https://www.google.com
https://mi-api.com/health
https://www.github.com
```

## Argumentos disponibles

| Argumento          | Default     | Descripción                                          |
|--------------------|-------------|------------------------------------------------------|
| `--urls`           | `urls.txt`  | Archivo con lista de URLs                            |
| `--interval`       | `30`        | Segundos entre verificaciones                        |
| `--timeout`        | `10`        | Timeout por petición HTTP (segundos)                 |
| `--slow-threshold` | `2000`      | Ms para considerar una respuesta lenta               |
| `--once`           | `False`     | Ejecutar solo una vez y salir                        |

## Salida de ejemplo

```
╔══════════════════════════════════════╗
║      🔍  URL Monitor v1.0            ║
╚══════════════════════════════════════╝

────────────────────────────────────────────────────────────────────────
  Verificación: 2025-01-15 10:45:02
────────────────────────────────────────────────────────────────────────
  ✓ OK (200)              45ms         https://www.google.com
  ✓ OK (200)              312ms        https://www.github.com
  ⚠ 404                   89ms         https://httpstat.us/404
  ✗ ERROR 500             102ms        https://httpstat.us/500
────────────────────────────────────────────────────────────────────────
  4 URLs verificadas · 2 OK · 2 alertas

  🚨 ALERTA: 1 URL(s) con fallos críticos:
     • https://httpstat.us/500
```

## Detener el monitor

Presiona `Ctrl+C` en cualquier momento.
