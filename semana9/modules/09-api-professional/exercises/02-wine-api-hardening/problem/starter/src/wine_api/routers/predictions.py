from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Body

from wine_api.dependencies import PredictorDep, RequestIdDep
from wine_api.schemas import (
    VALID_FEATURES_EXAMPLE,
    ErrorResponse,
    Prediction,
    PredictionRequest,
    PredictionResponse,
)

router = APIRouter(
    prefix="/v1/predictions",
    tags=["predictions"],
    responses={
        400: {
            "model": ErrorResponse,
            "description": "El cuerpo no es JSON válido.",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "code": "invalid_json",
                            "message": "Request body must be valid JSON",
                        },
                        "request_id": "req_example",
                    }
                }
            },
        },
        422: {
            "model": ErrorResponse,
            "description": "Entrada fuera de contrato.",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "code": "validation_error",
                            "message": "Invalid input",
                            "fields": [
                                {
                                    "field": "features.alcohol",
                                    "message": (
                                        "Input should be less than or equal to 20"
                                    ),
                                }
                            ],
                        },
                        "request_id": "req_example",
                    }
                }
            },
        },
        503: {
            "model": ErrorResponse,
            "description": "Modelo no disponible.",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "code": "model_unavailable",
                            "message": "The prediction model is not ready",
                        },
                        "request_id": "req_example",
                    }
                }
            },
        },
    },
)


@router.post(
    "",
    summary="Predecir la calidad de un vino tinto",
    response_description="Banda de calidad, confianza, versiones y trazabilidad.",
)
def create_prediction(
    payload: Annotated[
        PredictionRequest,
        Body(
            openapi_examples={
                "valid": {
                    "summary": "Muestra válida",
                    "value": {"features": VALID_FEATURES_EXAMPLE},
                },
                "alcohol_out_of_range": {
                    "summary": "Alcohol fuera de rango: 422",
                    "value": {"features": {**VALID_FEATURES_EXAMPLE, "alcohol": 21}},
                },
                "missing_ph": {
                    "summary": "Falta pH: 422",
                    "value": {
                        "features": {
                            name: value
                            for name, value in VALID_FEATURES_EXAMPLE.items()
                            if name != "ph"
                        }
                    },
                },
            }
        ),
    ],
    predictor: PredictorDep,
    request_id: RequestIdDep,
) -> PredictionResponse:
    """Predice una banda de calidad a partir de once variables fisicoquímicas.

    Envía `features` con todos los campos de `WineFeatures`, sin campos extra.
    Los rangos son inclusivos; `alcohol` admite de 5 a 20 % vol. Se aceptan
    números enteros y decimales, pero se rechazan textos y booleanos.

    `confidence` se redondea a dos decimales. La respuesta incluye versiones
    del modelo y preprocesado, `request_id` y `served_at` en UTC con sufijo Z.
    La puntuación interna del modelo queda excluida del contrato público.
    """

    output = predictor.predict(payload.features)
    return PredictionResponse(
        prediction=Prediction.model_validate(output),
        request_id=request_id,
        served_at=datetime.now(UTC),
    )
