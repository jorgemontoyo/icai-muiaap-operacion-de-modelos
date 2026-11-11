"""Transformación de una petición validada en once números ordenados."""

from dataclasses import dataclass

from model_inference.contracts import WineQualityRequest

PREPROCESSING_VERSION = "wine-red-features-v1"

# Este contrato se entrega ya decidido: no cambies ni los nombres ni el orden.
FEATURE_NAMES = (
    "fixed_acidity",
    "volatile_acidity",
    "citric_acid",
    "residual_sugar",
    "chlorides",
    "free_sulfur_dioxide",
    "total_sulfur_dioxide",
    "density",
    "ph",
    "sulphates",
    "alcohol",
)


@dataclass(frozen=True, slots=True)
class WineFeatures:
    """Vector inmutable con la versión de la transformación aplicada."""

    values: tuple[float, ...]
    preprocessing_version: str = PREPROCESSING_VERSION

    def __post_init__(self) -> None:
        if len(self.values) != len(FEATURE_NAMES):
            raise ValueError("El vector debe contener exactamente 11 características.")

    def as_vector(self) -> list[float]:
        return list(self.values)


def preprocess_wine_request(request: WineQualityRequest) -> WineFeatures:
    """Ordena por el contrato, independientemente del orden de columnas del CSV."""

    # No se ajusta un escalador ni se entrena nada durante la inferencia.
    return WineFeatures(tuple(getattr(request, name) for name in FEATURE_NAMES))
