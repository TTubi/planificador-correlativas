import json

import pytest

from app.services.correlativas import Estado
from app.services.plan import Materia, materias_desde_dict
from app.services.progreso import calcular_progreso
from scripts.cargar_plan import RUTA_PLAN

R, A = Estado.REGULAR, Estado.APROBADA


@pytest.fixture(scope="module")
def plan() -> list[Materia]:
    return materias_desde_dict(json.loads(RUTA_PLAN.read_text(encoding="utf-8")))


def test_un_alumno_nuevo_tiene_cero_por_ciento_y_sin_promedio(plan):
    progreso = calcular_progreso(plan, {}, {})
    assert (progreso.aprobadas, progreso.total, progreso.porcentaje) == (0, 17, 0)
    assert progreso.promedio is None


def test_el_porcentaje_cuenta_solo_las_aprobadas(plan):
    # 3 de 17 = 17,6 %: las regulares no suman.
    progreso = calcular_progreso(plan, {1: A, 2: A, 3: A, 4: R}, {})
    assert progreso.aprobadas == 3
    assert progreso.porcentaje == 17


def test_el_porcentaje_nunca_redondea_a_100_si_falta_una(plan):
    # 16 de 17 = 94,1 %. Con 2000 materias y una pendiente sería 99,95 %:
    # redondeando hacia abajo nunca se muestra 100 % antes de tiempo.
    estados = {m.numero: A for m in plan if m.numero != 17}
    assert calcular_progreso(plan, estados, {}).porcentaje == 94


def test_toda_la_carrera_es_100_por_ciento(plan):
    estados = {m.numero: A for m in plan}
    assert calcular_progreso(plan, estados, {}).porcentaje == 100


def test_el_promedio_es_sobre_las_notas_cargadas(plan):
    # La 3 está aprobada pero sin nota: no cuenta para el promedio.
    progreso = calcular_progreso(plan, {1: A, 2: A, 3: A}, {1: 8, 2: 7})
    assert progreso.promedio == 7.5
    assert progreso.notas_cargadas == 2


def test_el_promedio_se_redondea_a_dos_decimales(plan):
    progreso = calcular_progreso(plan, {1: A, 2: A, 3: A}, {1: 7, 2: 8, 3: 8})
    assert progreso.promedio == 7.67


@pytest.mark.parametrize(
    ("estados", "notas", "mensaje"),
    [
        ({}, {99: 8}, "la materia 99 no existe"),
        ({1: R}, {1: 8}, "Programación I tiene nota pero no está aprobada"),
        ({}, {1: 8}, "Programación I tiene nota pero no está aprobada"),
        ({1: A}, {1: 4}, "la nota 4 no está entre 6 y 10"),
        ({1: A}, {1: 11}, "la nota 11 no está entre 6 y 10"),
    ],
)
def test_rechaza_notas_que_no_tienen_sentido(plan, estados, notas, mensaje):
    with pytest.raises(ValueError, match=mensaje):
        calcular_progreso(plan, estados, notas)
