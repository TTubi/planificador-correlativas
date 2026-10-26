"""Modelos Pydantic para armar la publicación de LinkedIn."""

from pydantic import BaseModel, Field

from app.schemas.evaluacion import EstadoAlumno, ProgresoSchema


class SolicitudPublicacion(EstadoAlumno):
    """El mismo estado que /api/evaluacion, más las opciones del posteo."""

    incluir_promedio: bool = False
    # Qué versión del texto usar. Cualquier número sirve: se toma el resto
    # de dividir por la cantidad de versiones.
    version: int = Field(default=0, ge=0)


class PublicacionSchema(BaseModel):
    texto: str
    # Frase corta para la imagen, por ejemplo "¡Pasé la mitad!".
    titular: str
    version: int
    versiones: int
    # Si el promedio es lo bastante bueno como para ofrecer publicarlo.
    puede_incluir_promedio: bool
    progreso: ProgresoSchema
