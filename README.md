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
| `SERVICE_TOKEN`  | Clave compartida con el backend; llega en el encabezado `X-Service-Token`    |
| `MAX_FILE_MB`    | Tamaño máximo del plano en MB (por defecto 10)                               |
| `PORT`           | Puerto del servidor (Render lo asigna solo)                                   |

## Comandos

| Comando                                  | Qué hace                                         |
| ---------------------------------------- | ------------------------------------------------ |
| `uvicorn app.main:app --reload`          | Inicia el servidor en `http://localhost:8000`    |
| `pytest`                                 | Ejecuta las pruebas (no llaman a Gemini)         |

La documentación interactiva (Swagger) queda en `http://localhost:8000/docs`.

## Endpoints

| Método | Ruta                          | Token | Qué hace                                             |
| ------ | ----------------------------- | ----- | ---------------------------------------------------- |
| GET    | `/health`                     | No    | Estado del servicio; `ready` dice si puede analizar   |
| POST   | `/api/v1/blueprints/analyze`  | Sí    | Lee un plano y devuelve las medidas de sus elementos  |
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
  "model": "gemini-3.5-flash",
  "elapsed_ms": 8421
}
```

Errores, con la misma forma que el backend (`{ "error": { "code", "message" } }`):

| Código HTTP | `code`                  | Cuándo                                          |
| ----------- | ----------------------- | ----------------------------------------------- |
| 400         | `EMPTY_FILE`            | El archivo está vacío                           |
| 400         | `UNSUPPORTED_FILE`      | No es PDF, PNG, JPG ni WEBP                     |
| 400         | `VALIDATION_ERROR`      | Falta el archivo o `floors` no es 1 o 2         |
| 401         | `INVALID_SERVICE_TOKEN` | Falta `X-Service-Token` o no coincide           |
| 413         | `FILE_TOO_LARGE`        | El plano pasa de `MAX_FILE_MB`                  |
| 502         | `ANALYZER_FAILED`       | Gemini falló o su respuesta no se pudo leer     |
| 503         | `ANALYZER_NOT_READY`    | Falta `GEMINI_API_KEY`                          |
| 503         | `SERVICE_NOT_CONFIGURED`| Falta `SERVICE_TOKEN` en el servidor            |

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
