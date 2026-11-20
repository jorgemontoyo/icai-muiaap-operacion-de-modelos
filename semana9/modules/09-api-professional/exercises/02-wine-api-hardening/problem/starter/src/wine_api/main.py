"""Punto de entrada de la API: `fastapi dev` usa `wine_api.main:app`."""

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from wine_api.errors import install_error_handlers
from wine_api.predictor import Predictor, build_predictor
from wine_api.request_id import request_id_middleware
from wine_api.routers import health, predictions

API_VERSION = "1.1.0"


def create_app(predictor: Predictor | None = None) -> FastAPI:
    """Crea la aplicación; los tests inyectan su propio predictor."""

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
        app.state.predictor = predictor or build_predictor(
            os.environ.get("WINE_API_MODE", "ready")
        )
        yield

    app = FastAPI(
        title="Wine Quality API",
        version=API_VERSION,
        summary="Predicción de calidad de vino tinto con un contrato verificable.",
        description=(
            "Envía once variables fisicoquímicas a `POST /v1/predictions`. "
            "El predictor es una demo determinista para uso docente.\n\n"
            "Cada respuesta incluye `request_id`, también en la cabecera "
            "`X-Request-Id`, para relacionar peticiones, respuestas y logs. "
            "`served_at` indica cuándo se atendió la predicción, en UTC.\n\n"
            "Los errores usan `ErrorResponse`: `error.code` es estable, "
            "`error.message` explica el fallo y `error.fields` identifica los "
            "campos inválidos cuando procede; `request_id` está en la raíz. "
            "El cuerpo no devuelve entradas ni detalles internos del servidor."
        ),
        openapi_tags=[
            {
                "name": "health",
                "description": "Disponibilidad del servicio y del modelo.",
            },
            {
                "name": "predictions",
                "description": "Inferencia de calidad de vino tinto.",
            },
        ],
        lifespan=lifespan,
    )
    app.middleware("http")(request_id_middleware)
    install_error_handlers(app)
    app.include_router(health.router)
    app.include_router(predictions.router)
    return app


app = create_app()
