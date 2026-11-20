from fastapi import APIRouter

from wine_api.dependencies import PredictorDep, RequestIdDep
from wine_api.errors import ModelUnavailableError
from wine_api.schemas import ErrorResponse, HealthResponse

SERVICE_NAME = "wine-quality-prediction"

router = APIRouter(
    tags=["health"],
    responses={
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
        }
    },
)


@router.get(
    "/health",
    summary="Consultar disponibilidad del modelo",
    response_description="Servicio listo, versión del modelo y request_id.",
)
def read_health(predictor: PredictorDep, request_id: RequestIdDep) -> HealthResponse:
    """Comprueba si el servicio puede atender predicciones.

    Devuelve 200 cuando el modelo está listo y 503 con `model_unavailable`
    cuando no está disponible. Usa esta ruta antes de enviar trabajo al modelo.
    """

    if not predictor.is_ready():
        raise ModelUnavailableError()
    return HealthResponse(
        status="ok",
        service=SERVICE_NAME,
        model_status="ready",
        model_version=predictor.model_version,
        request_id=request_id,
    )
