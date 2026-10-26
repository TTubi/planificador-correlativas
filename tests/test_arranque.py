"""Tests de lo que pasa al arrancar el servidor.

`with TestClient(app)` ejecuta el ciclo de vida de la app (lo que en
producción hace Uvicorn al arrancar). Sin el `with`, no se ejecuta.
"""

import json

import pytest
from fastapi.testclient import TestClient

import app.main
from app.database import db


@pytest.fixture
def rutas_temporales(tmp_path, monkeypatch):
    """Hace que el arranque use una base temporal y no la del proyecto."""
    ruta_base = tmp_path / "planificador.db"
    monkeypatch.setattr(app.main, "RUTA_BASE", ruta_base)
    return ruta_base


def contar_materias(ruta_base) -> int:
    conexion = db.conectar(ruta_base)
    try:
        return conexion.execute("SELECT COUNT(*) FROM materias").fetchone()[0]
    finally:
        conexion.close()


def test_al_arrancar_genera_la_base(rutas_temporales):
    with TestClient(app.main.app):
        assert contar_materias(rutas_temporales) == 17


def test_regenera_una_base_vacia(rutas_temporales):
    # Es lo que deja sqlite3 si se pide la base antes de generarla.
    rutas_temporales.touch()
    with TestClient(app.main.app):
        assert contar_materias(rutas_temporales) == 17


def test_no_arranca_si_el_plan_tiene_errores(rutas_temporales, tmp_path, monkeypatch):
    plan_roto = tmp_path / "plan.json"
    plan_roto.write_text(
        json.dumps({"materias": [{"numero": 1, "nombre": "A", "nivel": 1, "regulares": [99]}]}),
        encoding="utf-8",
    )
    monkeypatch.setattr(app.main, "RUTA_PLAN", plan_roto)
    with pytest.raises(RuntimeError, match="El plan tiene errores"):
        with TestClient(app.main.app):
            pass
