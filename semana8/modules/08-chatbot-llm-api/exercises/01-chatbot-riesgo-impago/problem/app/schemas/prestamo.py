from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PrestamoEntrada(BaseModel):
    model_config = ConfigDict(extra="forbid")

    edad: int = Field(ge=18, le=75)
    ingresos_mensuales: float = Field(gt=0)
    importe_prestamo: float = Field(gt=0)
    plazo_meses: int = Field(ge=6, le=84)
    antiguedad_laboral_anios: int = Field(ge=0, le=50)
    impagos_previos: int = Field(ge=0, le=20)

    @field_validator("antiguedad_laboral_anios")
    @classmethod
    def validar_antiguedad(cls, valor: int, info) -> int:
        edad = info.data.get("edad")
        if edad is not None and valor > edad - 16:
            raise ValueError("La antiguedad laboral no puede superar edad - 16")
        return valor


class PrediccionSalida(BaseModel):
    probabilidad_impago: float = Field(ge=0, le=1)
    decision: Literal["aprobar", "revisar", "rechazar"]
