import json

import pytest

from app.services.llaves import calcular_llaves
from app.services.plan import Materia, materias_desde_dict
from scripts.cargar_plan import RUTA_PLAN


@pytest.fixture(scope="module")
def llaves():
    plan = materias_desde_dict(json.loads(RUTA_PLAN.read_text(encoding="utf-8")))
    return {llave.numero: llave for llave in calcular_llaves(plan)}


def test_programacion_i_desbloquea_directamente_las_que_la_piden(llaves):
    # La piden regular Programación II y Base de Datos I, y aprobada
    # Programación III, Base de Datos II y Metodología de Sistemas I.
    assert llaves[1].desbloquea_directamente == (5, 7, 9, 10, 11)


def test_cuenta_tambien_las_que_se_desbloquean_en_cadena(llaves):
    # Las 5 directas, más 13, 14, 15, 16 y 17 a través de ellas.
    assert llaves[1].desbloquea_en_total == (5, 7, 9, 10, 11, 13, 14, 15, 16, 17)


def test_una_cadena_simple(llaves):
    assert llaves[8].desbloquea_directamente == (12,)
    assert llaves[8].desbloquea_en_total == (12,)


def test_las_materias_finales_no_desbloquean_nada(llaves):
    for numero in (12, 13, 14, 15, 16, 17):
        assert llaves[numero].desbloquea_en_total == ()


def test_ordena_de_la_mas_llave_a_la_menos():
    plan = [
        Materia(1, "A", 1),
        Materia(2, "B", 1),
        Materia(3, "C", 1, regulares=(2,)),
        Materia(4, "D", 2, regulares=(3,)),
    ]
    assert [llave.numero for llave in calcular_llaves(plan)] == [2, 3, 1, 4]


def test_una_materia_alcanzable_por_dos_caminos_se_cuenta_una_vez():
    # 1 → 2 → 4 y 1 → 3 → 4: la 4 tiene que aparecer una sola vez.
    plan = [
        Materia(1, "A", 1),
        Materia(2, "B", 1, regulares=(1,)),
        Materia(3, "C", 1, aprobadas=(1,)),
        Materia(4, "D", 2, regulares=(2, 3)),
    ]
    llave = next(llave for llave in calcular_llaves(plan) if llave.numero == 1)
    assert llave.desbloquea_en_total == (2, 3, 4)
