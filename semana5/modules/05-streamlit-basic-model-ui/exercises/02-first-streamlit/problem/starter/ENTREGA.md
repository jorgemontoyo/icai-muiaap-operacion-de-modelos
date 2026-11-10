# Entrega de la práctica 5.2

## Ejecución con el bundle de S4

Desde esta carpeta, en PowerShell:

```powershell
uv sync
$env:MODEL_UI_BUNDLE = 'C:\ruta\a\tu\bundle_wine'
Test-Path (Join-Path $env:MODEL_UI_BUNDLE 'manifest.json')
Test-Path (Join-Path $env:MODEL_UI_BUNDLE 'model.joblib')
uv run python -m pytest -q
uv run ruff check app.py src tests
uv run ruff format --check app.py src tests
uv run --with 'streamlit>=1.40,<2.0' streamlit run app.py
```

Los dos `Test-Path` deben devolver `True`. `MODEL_UI_BUNDLE` apunta a la
carpeta del artefacto, no al fichero `model.joblib`. El bundle no se incluye en
la entrega.

## Verificación automática

El 4 de noviembre de 2026, las 27 pruebas pasaron usando el intérprete ya
instalado en `semana4/.venv`. También pasaron `ruff check` y
`ruff format --check`. Queda pendiente repetir los comandos anteriores con
`uv` en el entorno de entrega.

## QA visual con bundle real

| Caso | Acción | Resultado esperado | Evidencia |
| --- | --- | --- | --- |
| Arranque | Abrir la app con `MODEL_UI_BUNDLE` válido. | Once campos, sin predicción inicial. | Pendiente de captura. |
| Edición | Cambiar valores sin pulsar el botón. | Ninguna inferencia; se mantienen los valores. | Pendiente de captura. |
| Envío | Pulsar **Ejecutar inferencia**. | Una predicción con categoría, confianza y dos versiones. | Pendiente de captura. |
| Bundle ausente | Quitar la variable y reiniciar la app. | Mensaje para configurar `MODEL_UI_BUNDLE`, sin ruta ni traceback. | Pendiente de captura. |

Para el último caso:

```powershell
Remove-Item Env:MODEL_UI_BUNDLE -ErrorAction SilentlyContinue
```

## Límites observables para la semana 6

- La predicción no se conserva al recargar la página.
- El bundle se carga de nuevo en cada ejecución de la aplicación.

El estado de sesión, la caché y la telemetría se trabajarán en la semana 6.
