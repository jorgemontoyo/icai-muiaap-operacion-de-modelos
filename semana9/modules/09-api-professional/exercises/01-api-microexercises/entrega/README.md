# Assignment 9.1 Serialización errores OpenAPI y tests

Las demos permiten comprobar cómo FastAPI limita la salida pública, valida las
entradas, documenta el contrato y detecta regresiones con tests. Las respuestas
observadas se guardan en `evidencias.json`; las comprobaciones finales dejan
10 tests pasando, frente a los 9 iniciales.

## M1 Serialización y campos públicos

`GET /v1/scores/leaky` devuelve:

```json
{
  "band": "acceptable",
  "confidence": 0.8312377,
  "raw_score": 6.137,
  "threshold_config": "/srv/models/thresholds.yaml"
}
```

`GET /v1/scores/public` devuelve `band`, `confidence`, `served_at`, `note`
e `is_reliable`. Los campos que aparecen en `/leaky` y desaparecen en `/public`
son **`raw_score` y `threshold_config`**: son detalles internos del modelo.

En `/filtered`, `response_model=PublicScore` hace que FastAPI valide y serialice
la respuesta según el modelo público y filtre los campos que este no declara,
aunque la función devuelva un diccionario que los contenga.

En la respuesta pública, `confidence` se redondea a `0.83` y `served_at` se
serializa como fecha ISO 8601 en UTC con sufijo `Z`. Su valor cambia en cada
petición. `note` vale `null`; en `/compact` se omite gracias a
`response_model_exclude_none=True`.

**Sí aparece `is_reliable` en el esquema `PublicScore` de respuesta**: es una
propiedad calculada mediante `computed_field`, de solo lectura. En este ejemplo
vale `true`, porque la confianza interna es mayor o igual a `0.8`.

## M2 Respuestas y manejo de errores

Los tres POST se envían a `/v1/scores` de `errors_demo.py`.

| Petición | Estado HTTP | `error.code` | `error.fields` |
| --- | --- | --- | --- |
| POST `{"age":30,"income":1000}` | 200 | No existe: respuesta correcta `{"score":0.01}` | No existe |
| POST `{"age":"treinta","income":1000}` | 422 | `validation_error` | `age`: se esperaba un entero válido |
| POST `{"age":30}` | 422 | `validation_error` | `income`: campo requerido |
| GET `/v1/nada` | 404 | `not_found` | No existe |
| GET `/v1/boom` | 500 | `internal_error` | No existe |
| POST válido con el modelo no disponible, usando un override adicional | 503 | `model_unavailable` | No existe |

La primera de las cinco peticiones del enunciado es válida; por eso devuelve
`200` y no tiene una clave `error`. El caso adicional `503` permite comprobar
también el fallo de disponibilidad del modelo. Todas las respuestas de error
de esta demo tienen `error` en la raíz y ninguna contiene `TU_SECRETO`.
Los cuerpos completos, incluidos los mensajes de `fields`, están en
`evidencias.json`.

Al desactivar el registro de `handle_validation`, FastAPI mantiene el estado
`422`, pero usa su formato por defecto:

```json
{
  "detail": [
    {
      "type": "int_parsing",
      "loc": ["body", "age"],
      "msg": "Input should be a valid integer, unable to parse string as an integer",
      "input": "treinta"
    }
  ]
}
```

Esta comparación se ejecutó sobre una copia aislada en memoria con el decorador
desactivado. El archivo original conserva el manejador registrado y las
peticiones normales siguen recibiendo el sobre `error`.

## M3 OpenAPI y ejemplos de Swagger

En `/openapi.json`, la operación está en:

```text
paths["/v1/scores"]["post"]
```

Dentro de esa operación:

| Declaración en Python | Ubicación en OpenAPI |
| --- | --- |
| `summary` del decorador | `summary` |
| Docstring de `create_score` | `description` |
| `responses` del router | `responses["422"]` y `responses["503"]` |
| `openapi_examples` de `Body` | `requestBody.content["application/json"].examples` |

Al ejecutar `minor` desde Swagger con **Try it out** y **Execute**, se envía
`{"age":16,"income":1}` y se recibe **422**, porque `age` debe ser al menos
18. La captura `swagger_minor_422.png` muestra esa respuesta.

Se añadió `no_income` con `{"age":30}`. Swagger ofrece tres ejemplos:
`valid` (Cliente válido), `minor` (Menor de edad: 422) y `no_income`
(Falta income: 422). La captura `swagger_tres_ejemplos.png` muestra el nuevo
ejemplo seleccionado; el contrato guardado y el test comprueban las tres
opciones. El test que enumeraba dos ejemplos se actualizó para esperar tres.

Esta demo de OpenAPI conserva los manejadores predeterminados de FastAPI:
el error real de `minor` usa `detail`. Declarar un esquema en `responses`
documenta la operación, pero no instala un manejador de errores. El sobre
unificado de M2 pertenece a `errors_demo.py`.

## M4 Tests y simulación de fallos

El test `test_dependency_override_simulates_unavailable_model` sustituye
`get_model` mediante `app.dependency_overrides`. Devuelve un modelo con
`ready=False` y verifica `503` y `model_unavailable`. El fixture limpia los
overrides al terminar para evitar que afecten a otros tests.

Si se elimina `raise_server_exceptions=False` del fixture `errors_client`,
`TestClient` vuelve a propagar las excepciones inesperadas del servidor al
test. Al pedir `/v1/boom` se lanza `RuntimeError`: el test deja de recibir
normalmente la respuesta `500` que pretendía examinar. Se reprodujo este
comportamiento con un cliente de configuración predeterminada, conservando el
fixture original.

Se añadió `test_zero_income_is_rejected`, que envía `{"age":30,"income":0}`
y comprueba:

```python
assert response.status_code == 422
assert response.json()["error"]["code"] == "validation_error"
assert response.json()["error"]["fields"][0]["field"] == "income"
```

La razón es que `income` está declarado con `Field(gt=0)`: el límite es
estrictamente mayor que cero.

## Comprobación final y archivos de evidencia

Desde la raíz del módulo `semana9/modules/09-api-professional`:

```powershell
uv sync --locked
uv run --locked pytest -q
uv run --locked ruff check .
uv run --locked ruff format --check .
```

Resultados guardados:

- `pytest.txt`: **10 passed**.
- `ruff.txt`: **All checks passed!**.
- `ruff_format.txt`: **10 files already formatted**.
- `evidencias.json`: respuestas reales de M1 y M2, comparación sin manejador,
  operación OpenAPI, respuestas de sus ejemplos y excepción propagada en M4.
- `swagger_minor_422.png`: ejecución de `minor` en Swagger.
- `swagger_tres_ejemplos.png`: selección del nuevo ejemplo `no_income`.

Para abrir las demos, ejecuta una cada vez y visita
`http://127.0.0.1:8000/docs`; detén la anterior con Ctrl+C antes de cambiar:

```powershell
uv run fastapi dev examples/serialization_demo.py
uv run fastapi dev examples/errors_demo.py
uv run fastapi dev examples/openapi_demo.py
```
