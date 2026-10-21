"""Punto de extensión del CLI de inferencia sobre un bundle."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from pydantic import ValidationError

from model_packaging.artifact import (
    DEFAULT_BUNDLE_PATH,
    infer_wine_quality,
    load_model_bundle,
)
from model_packaging.contracts import WineQualityRequest
from model_packaging.preprocess import FEATURE_NAMES


def predict_file(
    input_path: Path,
    output_path: Path,
    bundle_path: Path,
) -> int:
    """Valida todas las filas y escribe el CSV solo al final."""

    input_fields = ("sample_id", *FEATURE_NAMES)
    output_fields = (
        "sample_id",
        "quality_band",
        "confidence",
        "model_version",
        "preprocessing_version",
    )

    bundle = load_model_bundle(bundle_path)
    predictions: list[dict[str, str | float]] = []

    with input_path.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        fieldnames = reader.fieldnames

        if not fieldnames:
            raise ValueError("El CSV de entrada debe incluir una cabecera.")

        if len(fieldnames) != len(set(fieldnames)):
            raise ValueError("El CSV de entrada contiene columnas duplicadas.")

        missing = [name for name in input_fields if name not in fieldnames]
        unknown = [name for name in fieldnames if name not in input_fields]

        if missing:
            raise ValueError(
                f"Faltan columnas obligatorias: {', '.join(missing)}."
            )
        if unknown:
            raise ValueError(
                f"Columnas no permitidas: {', '.join(unknown)}."
            )

        for row_number, row in enumerate(reader, start=2):
            sample_id = (row.get("sample_id") or "").strip()
            if not sample_id:
                raise ValueError(
                    f"Fila {row_number} tiene un sample_id vacío."
                )

            model_row = {
                key: value
                for key, value in row.items()
                if key != "sample_id"
            }

            try:
                request = WineQualityRequest.model_validate(model_row)
            except ValidationError as error:
                raise ValueError(
                    f"Fila {row_number} inválida para "
                    f"sample_id={sample_id}: {error}"
                ) from error

            prediction = infer_wine_quality(bundle, request)
            predictions.append(
                {"sample_id": sample_id, **prediction.model_dump()}
            )

    # Se crea el CSV cuando todas las filas se han validado y predicho.
    with output_path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(predictions)

    return len(predictions)


def parse_args() -> argparse.Namespace:
    """Declara la interfaz del comando público."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--bundle", default=DEFAULT_BUNDLE_PATH, type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    raise SystemExit(
        predict_file(
            input_path=arguments.input,
            output_path=arguments.output,
            bundle_path=arguments.bundle,
        )
    )

