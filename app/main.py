from fastapi import FastAPI

from app.routes import evaluacion, health

app = FastAPI(title="Planificador de Correlativas")

app.include_router(health.router)
app.include_router(evaluacion.router)
