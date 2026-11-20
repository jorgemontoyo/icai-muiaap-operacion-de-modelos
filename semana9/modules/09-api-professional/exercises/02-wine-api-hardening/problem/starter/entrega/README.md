# Assignment 9.2 Wine Quality API 1.1

La API valida y filtra sus respuestas, usa errores con un formato común y
documenta en Swagger los contratos de entrada, salida y error. La entrega
incluye los tests propios, el contrato OpenAPI y la nota de compatibilidad.

## S9.1 Contrato de salida

`schemas.py` define `Prediction` con los cuatro campos públicos:
`quality_band`, `confidence`, `model_version` y `preprocessing_version`.
`from_attributes=True` permite validar la salida interna del predictor como
modelo público sin exponer `raw_score`.

El serializador de `confidence` redondea el valor a dos decimales y mantiene
su tipo numérico en JSON. `PredictionResponse` añade `request_id` y
`served_at`; este último se escribe en UTC, en ISO 8601 y con sufijo `Z`.
Las rutas tienen tipos de retorno explícitos y construyen modelos Pydantic.

## S9.2 Errores consistentes

Los manejadores se registran en `errors.py`. La aplicación traduce los fallos
al contrato `ErrorResponse` y utiliza el mismo identificador en el cuerpo,
la cabecera `X-Request-Id` y el log del fallo inesperado.

| Fallo | Estado | `error.code` |
| --- | --- | --- |
| JSON mal formado | 400 | `invalid_json` |
| Tipo, rango, campo ausente o adicional | 422 | `validation_error` |
| Ruta inexistente | 404 | `not_found` |
| Método no permitido | 405 | `method_not_allowed` |
| Modelo no disponible | 503 | `model_unavailable` |
| Excepción inesperada | 500 | `internal_error` |

Los errores de validación incluyen rutas como `features.alcohol` en
`error.fields`, sin devolver el valor recibido. Los errores inesperados se
registran en el servidor y el consumidor recibe un mensaje genérico.
`/health` lanza `ModelUnavailableError` cuando el predictor no está listo.
La traducción a HTTP la realiza el manejador.

## S9.3 Documentación OpenAPI

La aplicación declara la versión `1.1.0`, resumen, descripción del servicio
y tags `health` y `predictions`. Las once variables de entrada tienen
descripciones con sus unidades y mantienen los rangos originales.

El router de predicción declara el prefijo y los errores `400`, `422` y
`503`, todos referenciados a `ErrorResponse`. Cada error tiene un ejemplo
de respuesta con su código correcto. `/health` documenta también el `503`.

La operación de predicción ofrece tres ejemplos de cuerpo:

- `valid`: las once variables válidas.
- `alcohol_out_of_range`: alcohol de 21, que devuelve `422`.
- `missing_ph`: falta `ph`, que devuelve `422`.

`swagger_ejemplos.png` muestra la versión, la operación desplegada, el ejemplo
de cuerpo y las respuestas documentadas `400`, `422` y `503`.

## S9.4 Tests propios

`tests/test_s9_4_student.py` completa los cuatro ejercicios:

1. Sustituye `get_predictor` con `dependency_overrides` para simular el modelo
   no disponible. Comprueba el `503` tanto en predicción como en `/health`,
   limpia el override en un `finally` y verifica que el servicio vuelve a `200`.
2. Usa `parametrize` con ocho entradas inválidas: alcohol por debajo y por
   encima del rango, `None`, texto y booleano, pH fuera de ambos límites y
   densidad demasiado alta. Comprueba `422`, el campo afectado y la trazabilidad.
3. Prueba por separado los extremos inclusivos de alcohol, 5 y 20: ambos `200`.
4. Compara el JSON generado por `render_openapi()` con
   `contracts/openapi.json`, resolviendo la ruta desde el archivo del test.

Las pruebas utilizan `TestClient` y predictores locales, sin llamadas de red
externas. Los archivos `predictor.py`, `request_id.py`, `dependencies.py` y
los tests de S9.1 a S9.3 conservan su contenido original.

## Resultados y reproducción

| Estado de la práctica | Resultado observado | Evidencia |
| --- | --- | --- |
| Starter inicial | 4 pasan y 23 fallan | `pytest_inicial.txt` |
| S9.1 completo | 8 pasan | `pytest_s9_1.txt` |
| S9.2 completo | 16 pasan | `pytest_s9_2.txt` |
| S9.3 completo | 23 pasan | `pytest_s9_3.txt` |
| S9.4 completo | 35 pasan, sin fallos | `pytest_final.txt` |
| Ruff | Sin errores | `ruff.txt` |
| Formato | 20 archivos con formato correcto | `ruff_format.txt` |

El número final aumenta porque los tests parametrizados se ejecutan una vez
por cada entrada. El entorno verificado usa Python 3.12.14. La versión del
paquete y la API es `1.1.0`; `uv.lock` conserva las dependencias fijadas.

Desde el directorio `problem/starter`:

```powershell
uv sync --locked
uv run --locked pytest -q
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked python -m wine_api.export_openapi
uv run fastapi dev
```

Abre `http://127.0.0.1:8000/docs`. Para simular el modelo no disponible,
detén el servidor con Ctrl+C y ejecuta:

```powershell
$env:WINE_API_MODE = "unavailable"
uv run fastapi dev
```

Para volver al modo normal, detén el servidor y elimina esa variable:

```powershell
Remove-Item Env:WINE_API_MODE
uv run fastapi dev
```

La nota de ocho líneas requerida está en `COMPATIBILIDAD.md`.
