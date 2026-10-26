"""Modelos Pydantic para exponer las materias llave."""

from pydantic import BaseModel


class LlaveSchema(BaseModel):
    numero: int
    nombre: str
    desbloquea_directamente: list[int]
    desbloquea_en_total: list[int]


class ResultadoLlaves(BaseModel):
    materias: list[LlaveSchema]
