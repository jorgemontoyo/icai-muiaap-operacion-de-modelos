#"""TODO: contratos de entrada y salida de la inferencia."""

# Implementa WineQualityRequest y WineQualityPrediction con Pydantic.
# Revisa los campos de assets/inference_samples.csv y prohíbe columnas extra.
from pydantic import BaseModel, ConfigDict, Field


class WineQualityRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sample_id: str

    fixed_acidity: float
    volatile_acidity: float
    citric_acid: float
    residual_sugar: float
    chlorides: float
    free_sulfur_dioxide: float
    total_sulfur_dioxide: float
    density: float
    ph: float
    sulphates: float
    alcohol: float


class WineQualityPrediction(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    sample_id: str
    quality_band: str
    confidence: float = Field(ge=0.0, le=1.0)
    model_version: str
    preprocessing_version: str
