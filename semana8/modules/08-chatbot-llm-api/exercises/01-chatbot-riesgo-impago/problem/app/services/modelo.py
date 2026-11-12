import joblib

from app.config import MODEL_PATH
from app.schemas.prestamo import PrediccionSalida, PrestamoEntrada

# Orden en el que el modelo espera las variables
VARIABLES = [
    "edad",
    "ingresos_mensuales",
    "importe_prestamo",
    "plazo_meses",
    "antiguedad_laboral_anios",
    "impagos_previos",
]

modelo = joblib.load(MODEL_PATH)


def decidir(probabilidad: float) -> str:
    if probabilidad < 0.2:
        return "aprobar"
    if probabilidad < 0.5:
        return "revisar"
    return "rechazar"


def predecir(entrada: PrestamoEntrada) -> PrediccionSalida:
    valores = [getattr(entrada, nombre) for nombre in VARIABLES]
    probabilidad = float(modelo.predict_proba([valores])[0][1])
    return PrediccionSalida(
        probabilidad_impago=probabilidad,
        decision=decidir(probabilidad),
    )
