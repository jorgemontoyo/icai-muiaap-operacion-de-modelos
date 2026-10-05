from pathlib import Path

import joblib

MODEL_PATH = Path(__file__).resolve().parent / "wine_quality_classifier.joblib"

modelo = joblib.load(MODEL_PATH).get("estimator")

print(modelo)

resultado = modelo.predict([[7.4, 0.7, 0, 1.9, 0.076, 11, 34, 0.9978, 3.51, 0.56, 9.4]])


print(resultado)
