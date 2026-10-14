"""CLI: CSV de entrada -> validación -> vector -> predicción -> CSV de salida."""

import argparse
import csv
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile

from model_inference.contracts import WineQualityPrediction, WineQualityRequest
from model_inference.inference import (
    DEFAULT_MODEL_PATH,
    infer_wine_quality,
    load_wine_quality_model,
)
from model_inference.preprocess import FEATURE_NAMES, preprocess_wine_request


def predict_file(
    input_path: Path,
    output_path: Path,
    model_path: Path = DEFAULT_MODEL_PATH,
) -> int:
    """Procesa el lote completo y devuelve el número de predicciones escritas."""

    input_path, output_path, model_path = map(
        Path, (input_path, output_path, model_path)
    )
    if output_path.resolve() in (input_path.resolve(), model_path.resolve()):
        raise ValueError("La salida debe ser distinta del CSV de entrada y del modelo.")

    model = load_wine_quality_model(model_path)
    predictions = []
    with input_path.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        header = reader.fieldnames or []
        expected = {"sample_id", *FEATURE_NAMES}
        missing = expected - set(header)
        extra = set(header) - expected
        if missing or extra:
            raise ValueError(
                f"Columnas inválidas: faltan {sorted(missing)}; sobran {sorted(extra)}."
            )
        if len(header) != len(set(header)):
            raise ValueError("El CSV contiene nombres de columna duplicados.")

        for row in reader:
            sample_id = (row.pop("sample_id", None) or "").strip()
            try:
                if not sample_id:
                    raise ValueError("sample_id no puede estar vacío.")
                if None in row:
                    raise ValueError("La fila contiene más valores que la cabecera.")
                request = WineQualityRequest.model_validate(row)
                features = preprocess_wine_request(request)
                prediction = infer_wine_quality(features, model, sample_id=sample_id)
                predictions.append(prediction)
            except (ValueError, TypeError) as error:
                raise ValueError(
                    f"Línea {reader.line_num}, muestra {sample_id!r}: {error}"
                ) from error

    if not predictions:
        raise ValueError("El CSV no contiene muestras.")

    # Solo escribimos después de validar y predecir todas las filas.
    # Un temporal en el mismo directorio permite sustituir la salida de una vez.
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with NamedTemporaryFile(
            mode="w",
            newline="",
            encoding="utf-8",
            dir=output_path.parent,
            prefix=f".{output_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as target:
            temporary_path = Path(target.name)
            writer = csv.DictWriter(
                target, fieldnames=list(WineQualityPrediction.model_fields)
            )
            writer.writeheader()
            writer.writerows(prediction.model_dump() for prediction in predictions)
        temporary_path.replace(output_path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

    return len(predictions)


def main() -> int:
    parser = argparse.ArgumentParser(description="Inferencia local de calidad de vino.")
    parser.add_argument("--input", type=Path, required=True, help="CSV de muestras.")
    parser.add_argument(
        "--output", type=Path, required=True, help="CSV de predicciones."
    )
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL_PATH)
    args = parser.parse_args()

    try:
        count = predict_file(args.input, args.output, args.model)
    except (OSError, ValueError, TypeError, csv.Error) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2

    print(f"{count} predicciones guardadas en {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
