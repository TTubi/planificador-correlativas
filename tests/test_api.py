"""Tests de la API con TestClient.

La lógica de correlativas ya está probada en test_correlativas.py.
Acá se prueba la "cañería" HTTP: que los datos entren, pasen por la base
y la lógica, y salgan con el formato esperado.
"""

import pytest
from fastapi.testclient import TestClient

from app.database import db
from app.main import app
from app.routes.dependencias import obtener_plan
from scripts.cargar_plan import cargar


@pytest.fixture
def cliente(tmp_path):
    """Cliente que usa una base temporal generada desde el JSON del plan."""
    ruta_base = tmp_path / "test.db"
    assert cargar(ruta_base=ruta_base) == 0

    def obtener_plan_de_prueba():
        conexion = db.conectar(ruta_base)
        try:
            return db.obtener_materias(conexion)
        finally:
            conexion.close()

    app.dependency_overrides[obtener_plan] = obtener_plan_de_prueba
    yield TestClient(app)
    app.dependency_overrides.clear()


def evaluar(cliente, estados: dict) -> dict[int, dict]:
    respuesta = cliente.post("/api/evaluacion", json={"estados": estados})
    assert respuesta.status_code == 200
    return {m["numero"]: m for m in respuesta.json()["materias"]}


def test_health(cliente):
    respuesta = cliente.get("/health")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"status": "ok"}


def test_un_alumno_nuevo_solo_puede_cursar_materias_sin_correlativas(cliente):
    materias = evaluar(cliente, {})
    assert len(materias) == 17
    assert [n for n, m in materias.items() if m["puede_cursar"]] == [1, 2, 3, 4, 8]


def test_el_cuerpo_vacio_equivale_a_un_alumno_nuevo(cliente):
    respuesta = cliente.post("/api/evaluacion", json={})
    assert respuesta.status_code == 200


def test_devuelve_el_formato_completo_de_una_materia(cliente):
    prog_ii = evaluar(cliente, {"1": "regular"})[5]
    assert prog_ii == {
        "numero": 5,
        "nombre": "Programación II",
        "estado": "pendiente",
        "puede_cursar": False,
        "puede_rendir": False,
        "faltan_para_cursar": [
            {"numero": 2, "nombre": "Arquitectura y Sistemas Operativos", "se_necesita": "regular"},
        ],
        "faltan_para_rendir": [],
    }


def test_usa_los_estados_recibidos(cliente):
    materias = evaluar(cliente, {"1": "aprobada", "2": "aprobada", "5": "regular"})
    assert materias[5]["estado"] == "regular"
    assert materias[5]["puede_rendir"] is True


def test_un_estado_invalido_da_422(cliente):
    respuesta = cliente.post("/api/evaluacion", json={"estados": {"1": "cursando"}})
    assert respuesta.status_code == 422


def test_una_materia_inexistente_da_422_con_mensaje(cliente):
    respuesta = cliente.post("/api/evaluacion", json={"estados": {"99": "aprobada"}})
    assert respuesta.status_code == 422
    assert respuesta.json() == {"detail": "Materias que no existen en el plan: [99]"}


def test_devuelve_el_progreso_con_porcentaje_y_promedio(cliente):
    respuesta = cliente.post(
        "/api/evaluacion",
        json={"estados": {"1": "aprobada", "2": "aprobada", "3": "regular"}, "notas": {"1": 8, "2": 7}},
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["progreso"] == {
        "aprobadas": 2,
        "total": 17,
        "porcentaje": 11,
        "promedio": 7.5,
        "notas_cargadas": 2,
    }


def test_devuelve_un_mensaje_de_feedback(cliente):
    respuesta = cliente.post(
        "/api/evaluacion",
        json={"estados": {"1": "aprobada", "2": "aprobada", "3": "regular"}, "notas": {"1": 8, "2": 7}},
    )
    assert respuesta.json()["mensaje"] == (
        "Vas sumando: ya tenés el 11% de la carrera. ¡Paso a paso! Tu promedio es 7,5, ¡muy bien!"
    )


def test_sin_notas_el_promedio_es_null(cliente):
    respuesta = cliente.post("/api/evaluacion", json={"estados": {"1": "aprobada"}})
    assert respuesta.json()["progreso"]["promedio"] is None


def test_una_nota_fuera_de_escala_da_422(cliente):
    respuesta = cliente.post("/api/evaluacion", json={"estados": {"1": "aprobada"}, "notas": {"1": 5}})
    assert respuesta.status_code == 422


def test_una_nota_de_una_materia_no_aprobada_da_422_con_mensaje(cliente):
    respuesta = cliente.post("/api/evaluacion", json={"estados": {"1": "regular"}, "notas": {"1": 8}})
    assert respuesta.status_code == 422
    assert respuesta.json() == {"detail": "Notas inválidas: Programación I tiene nota pero no está aprobada"}


# --- Plan --------------------------------------------------------------------


def test_devuelve_el_plan_con_nivel_y_correlativas(cliente):
    respuesta = cliente.get("/api/plan")
    assert respuesta.status_code == 200
    materias = {m["numero"]: m for m in respuesta.json()["materias"]}
    assert len(materias) == 17
    assert materias[13] == {
        "numero": 13,
        "nombre": "Programación IV",
        "nivel": 2,
        "regulares": [9, 10, 11],
        "aprobadas": [5, 7],
    }


# --- Materias llave ----------------------------------------------------------


def test_devuelve_las_materias_llave_ordenadas(cliente):
    respuesta = cliente.get("/api/llaves")
    assert respuesta.status_code == 200
    materias = respuesta.json()["materias"]
    assert len(materias) == 17
    assert materias[0] == {
        "numero": 1,
        "nombre": "Programación I",
        "desbloquea_directamente": [5, 7, 9, 10, 11],
        "desbloquea_en_total": [5, 7, 9, 10, 11, 13, 14, 15, 16, 17],
    }
    totales = [len(m["desbloquea_en_total"]) for m in materias]
    assert totales == sorted(totales, reverse=True)

# --- Frontend ----------------------------------------------------------------


def test_la_raiz_sirve_el_frontend(cliente):
    respuesta = cliente.get("/")
    assert respuesta.status_code == 200
    assert "text/html" in respuesta.headers["content-type"]
    assert '<script src="app.js"' in respuesta.text


def test_sirve_los_archivos_del_frontend(cliente):
    assert cliente.get("/app.js").status_code == 200
    assert cliente.get("/estilos.css").status_code == 200


def test_la_api_no_queda_tapada_por_el_frontend(cliente):
    # El frontend está montado en "/", que atrapa cualquier ruta.
    # Si se registrara antes que los routers, /health devolvería 404.
    assert cliente.get("/health").json() == {"status": "ok"}
