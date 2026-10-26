"""Modelos Pydantic para exponer el plan de estudios."""

from pydantic import BaseModel


class MateriaSchema(BaseModel):
    numero: int
    nombre: str
    nivel: int
    regulares: list[int]
    aprobadas: list[int]


class PlanSchema(BaseModel):
    materias: list[MateriaSchema]
