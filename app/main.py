from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database.db import RUTA_BASE
from app.routes import evaluacion, health, llaves, plan
from scripts.cargar_plan import RUTA_PLAN, cargar

CARPETA_FRONTEND = Path(__file__).with_name("static")


def generar_base() -> None:
    """Regenera la base desde el JSON del plan.

    Se hace siempre al arrancar, y no solo cuando falta el archivo, porque
    si alguien pidió la base antes de generarla, sqlite3 deja creado un
    archivo vacío. Además, así la base nunca queda desactualizada respecto
    del JSON. Con 17 materias tarda milisegundos.
    """
    if cargar(ruta_plan=RUTA_PLAN, ruta_base=RUTA_BASE) != 0:
        raise RuntimeError(f"El plan tiene errores y la app no puede arrancar: revisá {RUTA_PLAN.name}")


@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    # Lo que va antes del `yield` corre una vez, al arrancar el servidor y
    # antes de atender cualquier pedido. Lo de después correría al apagarlo.
    generar_base()
    yield


app = FastAPI(title="Planificador de Correlativas", lifespan=ciclo_de_vida)

app.include_router(health.router)
app.include_router(plan.router)
app.include_router(llaves.router)
app.include_router(evaluacion.router)

# El frontend se monta al final: "/" atrapa cualquier ruta, así que tiene que
# ir después de la API. `html=True` hace que "/" devuelva index.html.
app.mount("/", StaticFiles(directory=CARPETA_FRONTEND, html=True), name="frontend")
