# obraia-ia

Servicio de inteligencia artificial de **ObraIA**. Recibe el plano de una obra (PDF o imagen), lo lee con un modelo de visión (Gemini) y devuelve las medidas de cada elemento: cimientos, columnas, vigas, losas, muros, pisos y cubierta.
Proyecto final de Patrones de Software: Kevin Basante y Arley Riascos.

Este servicio no tiene base de datos ni usuarios: solo lo llama el backend (`obraia-backend`), que guarda las medidas y las compara con las que se ingresan a mano.

```text
Frontend  →  Backend (Spring Boot)  →  obraia-ia (FastAPI)  →  Gemini
```

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
