from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes import evaluacion, health, llaves, plan

CARPETA_FRONTEND = Path(__file__).with_name("static")

app = FastAPI(title="Planificador de Correlativas")

app.include_router(health.router)
app.include_router(plan.router)
app.include_router(llaves.router)
app.include_router(evaluacion.router)

# El frontend se monta al final: "/" atrapa cualquier ruta, así que tiene que
# ir después de la API. `html=True` hace que "/" devuelva index.html.
app.mount("/", StaticFiles(directory=CARPETA_FRONTEND, html=True), name="frontend")
