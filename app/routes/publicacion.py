from fastapi import APIRouter, Depends, HTTPException

from app.routes.dependencias import obtener_plan
from app.schemas.publicacion import PublicacionSchema, SolicitudPublicacion
from app.services.correlativas import evaluar_plan
from app.services.plan import Materia
from app.services.progreso import calcular_progreso
from app.services.publicacion import TITULARES, cantidad_de_versiones, etapa, promedio_suma, texto_publicacion

router = APIRouter(prefix="/api", tags=["Publicación"])


@router.post("/publicacion", response_model=PublicacionSchema)
def armar_publicacion(solicitud: SolicitudPublicacion, plan: list[Materia] = Depends(obtener_plan)):
    """Arma el texto (y el titular de la imagen) para publicar el progreso en LinkedIn."""
    try:
        # evaluar_plan() se llama para validar los estados igual que en
        # /api/evaluacion: una materia inexistente tiene que dar 422 acá también.
        evaluar_plan(plan, solicitud.estados)
        progreso = calcular_progreso(plan, solicitud.estados, solicitud.notas)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    versiones = cantidad_de_versiones(progreso)
    return {
        "texto": texto_publicacion(progreso, solicitud.incluir_promedio, solicitud.version),
        "titular": TITULARES[etapa(progreso)],
        "version": solicitud.version % versiones,
        "versiones": versiones,
        "puede_incluir_promedio": promedio_suma(progreso),
        "progreso": progreso,
    }
