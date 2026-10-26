from fastapi import APIRouter, Depends, HTTPException

from app.routes.dependencias import obtener_plan
from app.schemas.evaluacion import EstadoAlumno, ResultadoEvaluacion
from app.services.correlativas import evaluar_plan
from app.services.plan import Materia

router = APIRouter(prefix="/api", tags=["Evaluación"])


@router.post("/evaluacion", response_model=ResultadoEvaluacion)
def evaluar(alumno: EstadoAlumno, plan: list[Materia] = Depends(obtener_plan)):
    """Recibe el estado del alumno y devuelve qué puede cursar y rendir."""
    try:
        evaluaciones = evaluar_plan(plan, alumno.estados)
    except ValueError as error:
        # Es un error de quien hizo el pedido, no del servidor: 422 y no 500.
        raise HTTPException(status_code=422, detail=str(error)) from error
    # FastAPI convierte las dataclasses al formato de `response_model`.
    return {"materias": evaluaciones}
