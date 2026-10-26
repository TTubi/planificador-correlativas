"""Modelos Pydantic que definen el formato de la API.

Son el "contrato" con el frontend: qué se recibe y qué se devuelve.
Se mantienen separados de las dataclasses de `services/` para que un cambio
interno en la lógica no cambie la API sin que nos demos cuenta.
"""

from typing import Annotated

from pydantic import BaseModel, Field

from app.services.correlativas import Estado
from app.services.progreso import NOTA_MAXIMA, NOTA_MINIMA

# Pydantic rechaza con 422 una nota fuera de la escala, y /docs la muestra.
Nota = Annotated[int, Field(ge=NOTA_MINIMA, le=NOTA_MAXIMA)]


class EstadoAlumno(BaseModel):
    """El avance del alumno: número de materia → estado.

    En JSON las claves son texto ("1"), pero Pydantic las convierte a int.
    Las materias que no aparecen se consideran pendientes.
    """

    estados: dict[int, Estado] = Field(default_factory=dict)
    # Opcional: número de materia aprobada → nota con la que se aprobó.
    notas: dict[int, Nota] = Field(default_factory=dict)


class FaltanteSchema(BaseModel):
    numero: int
    nombre: str
    se_necesita: Estado


class EvaluacionSchema(BaseModel):
    numero: int
    nombre: str
    estado: Estado
    puede_cursar: bool
    puede_rendir: bool
    faltan_para_cursar: list[FaltanteSchema]
    faltan_para_rendir: list[FaltanteSchema]


class ProgresoSchema(BaseModel):
    aprobadas: int
    total: int
    porcentaje: int
    promedio: float | None
    notas_cargadas: int


class ResultadoEvaluacion(BaseModel):
    """La respuesta va dentro de un objeto (y no como lista suelta) para
    poder agregar campos más adelante sin romper a quien ya la usa."""

    materias: list[EvaluacionSchema]
    progreso: ProgresoSchema
