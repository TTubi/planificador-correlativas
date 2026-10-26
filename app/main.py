from fastapi import FastAPI

app = FastAPI(title="Planificador de Correlativas")


@app.get("/health")
def health():
    return {"status": "ok"}