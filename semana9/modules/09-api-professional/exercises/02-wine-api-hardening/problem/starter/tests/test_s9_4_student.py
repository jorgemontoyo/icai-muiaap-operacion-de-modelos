"""S9.4 — Pruebas de disponibilidad, rangos y estabilidad del contrato."""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from wine_api.dependencies import get_predictor
from wine_api.export_openapi import render_openapi
from wine_api.predictor import UnavailablePredictor
from wine_api.schemas import ErrorResponse


def test_prediction_returns_503_when_model_is_unavailable(
    client: TestClient, valid_payload: dict
) -> None:
    client.app.dependency_overrides[get_predictor] = UnavailablePredictor
    try:
        prediction = client.post("/v1/predictions", json=valid_payload)
        health = client.get("/health")
        for response in (prediction, health):
            assert response.status_code == 503
            body = ErrorResponse.model_validate(response.json())
            assert body.error.code == "model_unavailable"
            assert body.request_id == response.headers["X-Request-Id"]
            assert "detail" not in response.json()
    finally:
        client.app.dependency_overrides.pop(get_predictor, None)

    # El fallo simulado no debe contaminar las siguientes peticiones.
    assert client.post("/v1/predictions", json=valid_payload).status_code == 200
    assert client.get("/health").status_code == 200


@pytest.mark.parametrize(
    ("field", "value"),
    [
        pytest.param("alcohol", 4.99, id="alcohol-below-minimum"),
        pytest.param("alcohol", 20.01, id="alcohol-above-maximum"),
        pytest.param("alcohol", None, id="alcohol-null"),
        pytest.param("alcohol", "token-do-not-echo", id="alcohol-text"),
        pytest.param("alcohol", True, id="alcohol-boolean"),
        pytest.param("ph", 2.49, id="ph-below-minimum"),
        pytest.param("ph", 4.51, id="ph-above-maximum"),
        pytest.param("density", 1.02, id="density-above-maximum"),
    ],
)
def test_out_of_contract_values_are_rejected(
    client: TestClient, valid_payload: dict, field: str, value: object
) -> None:
    valid_payload["features"][field] = value

    response = client.post("/v1/predictions", json=valid_payload)

    assert response.status_code == 422
    body = ErrorResponse.model_validate(response.json())
    assert body.error.code == "validation_error"
    assert body.error.fields is not None
    assert [error.field for error in body.error.fields] == [f"features.{field}"]
    assert body.request_id == response.headers["X-Request-Id"]
    assert "token-do-not-echo" not in response.text


@pytest.mark.parametrize("alcohol", [5, 20])
def test_range_limits_are_inclusive(
    client: TestClient, valid_payload: dict, alcohol: int
) -> None:
    valid_payload["features"]["alcohol"] = alcohol

    response = client.post("/v1/predictions", json=valid_payload)

    assert response.status_code == 200
    assert set(response.json()["prediction"]) == {
        "quality_band",
        "confidence",
        "model_version",
        "preprocessing_version",
    }


def test_openapi_matches_versioned_contract() -> None:
    contract_path = Path(__file__).resolve().parents[1] / "contracts" / "openapi.json"

    expected = json.loads(contract_path.read_text(encoding="utf-8"))
    actual = json.loads(render_openapi())

    assert actual == expected
