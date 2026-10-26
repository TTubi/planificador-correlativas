from fastapi import APIRouter, Depends

from app.routes.dependencias import obtener_plan
from app.schemas.plan import PlanSchema
from app.services.plan import Materia

router = APIRouter(prefix="/api", tags=["Plan"])


@router.get("/plan", response_model=PlanSchema)
def ver_plan(plan: list[Materia] = Depends(obtener_plan)):
    """Devuelve las materias del plan con su nivel y sus correlativas.

    No depende del alumno: el frontend lo pide una vez para dibujar la
    estructura, y después usa /api/evaluacion para el estado de cada materia.
    """
    return {"materias": plan}
