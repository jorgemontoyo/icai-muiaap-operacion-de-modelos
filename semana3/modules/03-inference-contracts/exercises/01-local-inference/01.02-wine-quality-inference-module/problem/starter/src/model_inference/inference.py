"""Carga del artefacto del docente y predicción sobre un vector preparado."""

from pathlib import Path
from typing import Any

import joblib

from model_inference.contracts import WineQualityPrediction
from model_inference.preprocess import FEATURE_NAMES, WineFeatures

DEFAULT_MODEL_PATH = (
    Path(__file__).resolve().parents[2] / "models" / "wine_quality_classifier.joblib"
)


def load_wine_quality_model(model_path: Path = DEFAULT_MODEL_PATH) -> dict[str, Any]:
    """Carga solo artefactos de confianza y comprueba su contrato antes de usarlos."""

    model_path = Path(model_path)
    if not model_path.is_file():
        raise FileNotFoundError(f"No se encuentra el modelo preentrenado: {model_path}")
    try:
        artifact = joblib.load(model_path)
    except Exception as error:
        raise ValueError(
            f"No se pudo cargar el artefacto {model_path}: {error}"
        ) from error

    if not isinstance(artifact, dict):
        raise ValueError("El artefacto debe contener un diccionario.")

    names = artifact.get("feature_names")
    if not isinstance(names, (list, tuple)) or tuple(names) != FEATURE_NAMES:
        raise ValueError(
            "feature_names no coincide con los nombres y el orden esperados."
        )

    estimator = artifact.get("estimator")
    if (
        not callable(getattr(estimator, "predict", None))
        or not callable(getattr(estimator, "predict_proba", None))
        or getattr(estimator, "classes_", None) is None
    ):
        raise ValueError("El artefacto no contiene un clasificador compatible.")

    n_features = getattr(estimator, "n_features_in_", len(FEATURE_NAMES))
    if n_features != len(FEATURE_NAMES):
        raise ValueError(
            "El clasificador no espera las 11 características del contrato."
        )

    version = artifact.get("model_version")
    if not isinstance(version, str) or not version.strip():
        raise ValueError("El artefacto necesita un model_version no vacío.")
    return artifact


def infer_wine_quality(
    features: WineFeatures,
    model: dict[str, Any],
    *,
    sample_id: str,
) -> WineQualityPrediction:
    """Predice una muestra con un artefacto validado por el cargador."""

    estimator = model["estimator"]
    # sklearn espera una matriz: una fila y once columnas.
    matrix = [features.as_vector()]
    labels = estimator.predict(matrix)
    probabilities = estimator.predict_proba(matrix)
    classes = list(estimator.classes_)

    if len(labels) != 1 or len(probabilities) != 1:
        raise ValueError("El clasificador debe devolver un resultado por muestra.")
    label = labels[0]
    if label not in classes or len(probabilities[0]) != len(classes):
        raise ValueError("Las categorías y las probabilidades no son compatibles.")

    # Seleccionamos la probabilidad de la categoría que realmente se predijo.
    confidence = float(probabilities[0][classes.index(label)])
    return WineQualityPrediction(
        sample_id=sample_id,
        quality_band=label,
        confidence=confidence,
        model_version=model["model_version"],
        preprocessing_version=features.preprocessing_version,
    )
