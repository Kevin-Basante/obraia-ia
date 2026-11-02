# obraia-ia

Servicio de inteligencia artificial de **ObraIA**. Recibe el plano de una obra (PDF o imagen), lo lee con un modelo de visión (Gemini) y devuelve las medidas de cada elemento: cimientos, columnas, vigas, losas, muros, pisos y cubierta.
Proyecto final de Patrones de Software: Kevin Basante y Arley Riascos.

Este servicio no tiene base de datos ni usuarios: solo lo llama el backend (`obraia-backend`), que guarda las medidas y las compara con las que se ingresan a mano.

```text
Frontend  →  Backend (Spring Boot)  →  obraia-ia (FastAPI)  →  Gemini
```

## Tecnologías

- Python 3.11 + FastAPI
- Uvicorn como servidor
- Google Gen AI SDK (`google-genai`) para llamar a Gemini
- Pydantic para validar los datos
- Pytest para las pruebas
- Render para el despliegue

## Requisitos

- Python 3.11 o superior
- Git
- Una clave de Gemini de [Google AI Studio](https://aistudio.google.com/apikey) (opcional: sin clave se puede usar el analizador `fake`)

## Instalación

```bash
git clone https://github.com/Kevin-Basante/obraia-ia.git
cd obraia-ia
python -m venv venv
```

Activar el entorno virtual:

| Windows (PowerShell)        | Mac / Linux               |
| --------------------------- | ------------------------- |
| `.\venv\Scripts\Activate.ps1` | `source venv/bin/activate` |

Instalar las dependencias (incluye las de pruebas):

```bash
pip install -r requirements-dev.txt
```

## Variables de entorno

1. Copia `.env.example` y renómbralo a `.env`.
2. Completa los valores.

El archivo `.env` está en `.gitignore` y **nunca** se sube a GitHub. La clave de Gemini tampoco se pega en el chat ni en capturas.

| Variable         | Descripción                                                                  |
| ---------------- | ---------------------------------------------------------------------------- |
| `ANALYZER`       | `gemini` lee el plano con Gemini (por defecto); `fake` devuelve medidas de ejemplo sin IA |
| `GEMINI_API_KEY` | Clave de Google AI Studio (solo con `ANALYZER=gemini`)                       |
| `GEMINI_MODEL`   | Modelo de Gemini que lee los planos (por defecto `gemini-3.5-flash`)         |
| `GEMINI_FALLBACK_MODEL` | Modelo de respaldo cuando el principal está saturado (por defecto `gemini-3.5-flash-lite`; vacío lo desactiva) |
| `GEMINI_RETRIES` | Reintentos de cada modelo cuando Gemini responde que está saturado (por defecto 2) |
| `SERVICE_TOKEN`  | Clave compartida con el backend; llega en el encabezado `X-Service-Token`    |
| `MAX_FILE_MB`    | Tamaño máximo del plano en MB (por defecto 10)                               |
| `MAX_PDF_PAGES`  | Páginas máximas de un PDF (por defecto 10)                                    |
| `MAX_CONCURRENT_ANALYSES` | Análisis al mismo tiempo; los demás reciben `503 ANALYZER_BUSY` (por defecto 2) |
| `PORT`           | Puerto del servidor (Render lo asigna solo)                                   |

## Comandos

| Comando                                  | Qué hace                                         |
| ---------------------------------------- | ------------------------------------------------ |
| `uvicorn app.main:app --reload`          | Inicia el servidor en `http://localhost:8000`    |
| `pytest`                                 | Ejecuta las pruebas (no llaman a Gemini)         |
| `pytest --cov`                           | Pruebas con el reporte de cobertura              |
| `ruff check .`                           | Revisa errores y el orden de los imports         |
| `ruff format .`                          | Da formato al código                             |

La documentación interactiva (Swagger) queda en `http://localhost:8000/docs`.

## Endpoints

| Método | Ruta                          | Token | Qué hace                                             |
| ------ | ----------------------------- | ----- | ---------------------------------------------------- |
| GET    | `/health`                     | No    | Estado del servicio; `ready` dice si puede analizar   |
| POST   | `/api/v1/blueprints/analyze`  | Sí    | Lee un plano y devuelve las medidas de sus elementos  |
| GET    | `/api/v1/elements`            | Sí    | Tipos de elemento, medidas que necesita cada uno y su unidad |
| GET    | `/docs`                       | No    | Documentación Swagger                                |

`POST /api/v1/blueprints/analyze` recibe un formulario `multipart/form-data`:

| Campo    | Tipo    | Descripción                                   |
| -------- | ------- | --------------------------------------------- |
| `file`   | archivo | Plano en PDF, PNG, JPG o WEBP                 |
| `floors` | número  | Pisos de la obra: 1 o 2 (por defecto 1)       |

Respuesta (200):

```json
{
  "measurements": [
    {
      "element_type": "wall",
      "floor_number": 1,
      "length_m": 36.0,
      "width_m": null,
      "height_m": 2.4,
      "quantity": 1,
      "notes": "Muros de fachada"
    }
  ],
  "warnings": ["La escala del plano no es visible"],
  "discarded": 0,
  "merged": 0,
  "summary": [
    { "element_type": "wall", "rows": 1, "pieces": 1, "total": 86.4, "unit": "m2" }
  ],
  "model": "gemini-3.5-flash",
  "elapsed_ms": 8421
}
```

- `merged`: filas repetidas que se unieron en una sola (se suman sus cantidades).
- `summary`: totales por tipo de elemento. `total` es volumen (m3) para cimientos, columnas, vigas y losas, y superficie (m2) para muros, pisos y cubierta.

Errores, con la misma forma que el backend (`{ "error": { "code", "message" } }`):

| Código HTTP | `code`                  | Cuándo                                          |
| ----------- | ----------------------- | ----------------------------------------------- |
| 400         | `EMPTY_FILE`            | El archivo está vacío                           |
| 400         | `UNSUPPORTED_FILE`      | No es PDF, PNG, JPG ni WEBP                     |
| 400         | `VALIDATION_ERROR`      | Falta el archivo o `floors` no es 1 o 2         |
| 401         | `INVALID_SERVICE_TOKEN` | Falta `X-Service-Token` o no coincide           |
| 413         | `FILE_TOO_LARGE`        | El plano pasa de `MAX_FILE_MB`                  |
| 502         | `ANALYZER_FAILED`       | Gemini rechazó la petición o su respuesta no se pudo leer |
| 503         | `ANALYZER_NOT_READY`    | Falta `GEMINI_API_KEY`                          |
| 503         | `SERVICE_NOT_CONFIGURED`| Falta `SERVICE_TOKEN` en el servidor            |
| 503         | `ANALYZER_BUSY`         | Gemini sigue saturado después de los reintentos y del modelo de respaldo; se puede intentar más tarde |

## Cómo se lee un plano

1. **Tipo de archivo:** se reconoce por sus primeros bytes, no por el nombre, así que un `.pdf` falso se rechaza.
2. **Modelo:** el plano y unas instrucciones (`app/prompt.py`) se envían a Gemini, que responde en JSON con la forma de `RawAnalysis`. La temperatura es 0 para que el mismo plano dé el mismo resultado.
   - Si Gemini responde que está saturado (429, 500, 503 o 504), se reintenta hasta `GEMINI_RETRIES` veces, esperando 2 s, luego 4 s.
   - Si el modelo principal sigue saturado, se prueba `GEMINI_FALLBACK_MODEL`, y la respuesta trae una advertencia que lo dice.
   - Si los dos siguen saturados, se responde `503 ANALYZER_BUSY`. Cada intento queda en los logs de Render.
3. **Limpieza** (`app/cleaning.py`): cada elemento se revisa antes de devolverlo.
   - Solo se aceptan los 7 tipos del backend (también en plural, como `walls`).
   - Cada tipo guarda solo las medidas que necesita: volumen (largo, ancho y alto) para cimientos, columnas, vigas y losas; largo y alto para muros; largo y ancho para pisos y cubierta.
   - Las medidas se redondean a centímetros. Un elemento sin una medida obligatoria, con valores fuera de rango o en un piso que la obra no tiene se descarta y se cuenta en `discarded`.
4. **Respuesta:** las medidas válidas, las advertencias del modelo (en español), el modelo usado y el tiempo que tardó.

## Patrones de diseño

| Patrón             | Dónde                                   | Para qué                                                         |
| ------------------ | --------------------------------------- | ---------------------------------------------------------------- |
| Strategy           | `app/analyzers/` (`BlueprintAnalyzer`)  | Cambiar entre Gemini y el analizador de ejemplo sin tocar la ruta |
| Factory            | `app/analyzers/factory.py`              | Crear el analizador que dice `ANALYZER`                          |
| Inyección de dependencias | `Depends` de FastAPI             | Las pruebas reemplazan el analizador y la configuración          |
| DTO                | `app/schemas.py`                        | Formas de los datos que entran y salen del servicio              |

En el backend, el **Adapter** (`AiServiceAdapter`) traduce las respuestas de este servicio al dominio de Java y el **Proxy** (`AiServiceProxy`) controla el acceso, guarda en caché los análisis y limita cuántos se hacen por obra.

## Estructura

```text
app/
├── main.py              # Crea la aplicación y registra las rutas
├── config.py            # Variables de entorno
├── errors.py            # Errores con la forma { error: { code, message } }
├── security.py          # Revisa el encabezado X-Service-Token
├── elements.py          # Tipos de elemento y medidas que necesita cada uno
├── file_types.py        # Reconoce PDF, PNG, JPG y WEBP
├── schemas.py           # Modelos de entrada y salida (Pydantic)
├── prompt.py            # Instrucciones para el modelo
├── cleaning.py          # Revisa y limpia las medidas del modelo
├── analyzers/
│   ├── base.py          # Interfaz BlueprintAnalyzer (Strategy)
│   ├── gemini.py        # Lee el plano con Gemini
│   ├── fake.py          # Medidas de ejemplo, sin IA
│   └── factory.py       # Elige el analizador
└── routers/
    ├── health.py        # GET /health
    └── analysis.py      # POST /api/v1/blueprints/analyze
tests/                   # Pruebas con pytest (Gemini simulado)
```

## Despliegue en Render

1. En Render: **New → Web Service** y conecta el repositorio `obraia-ia`.
2. Configuración:
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** Free
   - **Health Check Path:** `/health`
3. En **Environment** agrega `ANALYZER=gemini`, `GEMINI_API_KEY` y `SERVICE_TOKEN` (un texto aleatorio largo). El mismo `SERVICE_TOKEN` va en el backend como `AI_SERVICE_TOKEN`.
4. La versión de Python sale del archivo `.python-version`.

El plan gratuito de Render apaga el servicio tras 15 minutos sin uso; la primera llamada después puede tardar cerca de un minuto mientras arranca.

## Equipo y responsabilidades

| Integrante    | Responsabilidad                                                    |
| ------------- | ------------------------------------------------------------------ |
| Kevin Basante | Servicio de IA (este repositorio), backend y base de datos         |
| Arley Riascos | Frontend (`obraia-frontend`)                                       |

Los dos trabajan juntos en el diseño y revisan el avance de los tres repositorios.

## Convenciones

- Código, comentarios, rutas y claves JSON en inglés; documentación en español.
- Commits con prefijo según el tipo de cambio: `feat:`, `fix:`, `docs:`, `chore:`, `test:`.
- Las claves (`GEMINI_API_KEY`, `SERVICE_TOKEN`) solo van en `.env` o en Render, nunca en GitHub.
