from fastapi import APIRouter, Depends

from app.routes.dependencias import obtener_plan
from app.schemas.llaves import ResultadoLlaves
from app.services.llaves import calcular_llaves
from app.services.plan import Materia

router = APIRouter(prefix="/api", tags=["Plan"])


@router.get("/llaves", response_model=ResultadoLlaves)
def ver_llaves(plan: list[Materia] = Depends(obtener_plan)):
    """Devuelve qué materias desbloquea cada una, de la más llave a la menos."""
    return {"materias": calcular_llaves(plan)}
