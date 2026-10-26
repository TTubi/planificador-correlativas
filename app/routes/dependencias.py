"""Dependencias compartidas por los endpoints.

Los endpoints las piden con `Depends(...)` en lugar de llamarlas
directamente. Así, en los tests se pueden reemplazar con
`app.dependency_overrides`, por ejemplo para usar una base temporal.
"""

from app.database import db
from app.services.plan import Materia


def obtener_plan() -> list[Materia]:
    """Lee el plan completo de la base."""
    conexion = db.conectar()
    try:
        return db.obtener_materias(conexion)
    finally:
        conexion.close()
