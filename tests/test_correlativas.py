import json

import pytest

from app.services.correlativas import Estado, Evaluacion, Faltante, evaluar_plan
from app.services.plan import Materia, materias_desde_dict
from scripts.cargar_plan import RUTA_PLAN

R, A = Estado.REGULAR, Estado.APROBADA


@pytest.fixture(scope="module")
def plan() -> list[Materia]:
    return materias_desde_dict(json.loads(RUTA_PLAN.read_text(encoding="utf-8")))


def evaluar(plan, estados) -> dict[int, Evaluacion]:
    """Atajo para buscar el resultado de una materia por su número."""
    return {e.numero: e for e in evaluar_plan(plan, estados)}


def cursables(plan, estados) -> list[int]:
    return [e.numero for e in evaluar_plan(plan, estados) if e.puede_cursar]


def rendibles(plan, estados) -> list[int]:
    return [e.numero for e in evaluar_plan(plan, estados) if e.puede_rendir]


# --- Cursar ------------------------------------------------------------------


def test_un_alumno_nuevo_solo_puede_cursar_materias_sin_correlativas(plan):
    assert cursables(plan, {}) == [1, 2, 3, 4, 8]


def test_explica_que_falta_para_cursar(plan):
    prog_ii = evaluar(plan, {})[5]
    assert not prog_ii.puede_cursar
    assert prog_ii.faltan_para_cursar == [
        Faltante(1, "Programación I", R),
        Faltante(2, "Arquitectura y Sistemas Operativos", R),
    ]


def test_alcanza_con_regularizar_las_correlativas_regulares(plan):
    assert evaluar(plan, {1: R, 2: R})[5].puede_cursar


def test_una_correlativa_aprobada_tambien_cuenta_como_regular(plan):
    assert evaluar(plan, {1: A, 2: A})[5].puede_cursar


def test_las_correlativas_aprobadas_no_alcanzan_con_regularizarlas(plan):
    # Programación III: II y BD I regulares, pero Programación I aprobada.
    prog_iii = evaluar(plan, {1: R, 5: R, 7: R})[9]
    assert not prog_iii.puede_cursar
    assert prog_iii.faltan_para_cursar == [Faltante(1, "Programación I", A)]

    assert evaluar(plan, {1: A, 5: R, 7: R})[9].puede_cursar


def test_no_se_puede_cursar_una_materia_ya_cursada(plan):
    resultado = evaluar(plan, {1: R, 3: A})
    assert not resultado[1].puede_cursar
    assert not resultado[3].puede_cursar
    assert resultado[1].faltan_para_cursar == []


# --- Rendir ------------------------------------------------------------------


def test_solo_se_rinde_lo_que_esta_regularizado(plan):
    assert rendibles(plan, {}) == []
    assert rendibles(plan, {1: R, 3: A}) == [1]


def test_para_rendir_las_correlativas_tienen_que_estar_aprobadas(plan):
    # Programación II regular, pero Programación I todavía sin el final.
    prog_ii = evaluar(plan, {1: R, 2: A, 5: R})[5]
    assert not prog_ii.puede_rendir
    assert prog_ii.faltan_para_rendir == [Faltante(1, "Programación I", A)]

    assert evaluar(plan, {1: A, 2: A, 5: R})[5].puede_rendir


def test_para_rendir_cuentan_las_dos_listas_de_correlativas(plan):
    # Metodología de Sistemas I: regulares 5 y 7, aprobadas 1 y 4.
    estados = {1: A, 4: A, 5: A, 7: R, 11: R}
    metodologia_i = evaluar(plan, estados)[11]
    assert metodologia_i.faltan_para_rendir == [Faltante(7, "Base de Datos I", A)]


def test_una_materia_aprobada_no_se_cursa_ni_se_rinde(plan):
    prog_i = evaluar(plan, {1: A})[1]
    assert not prog_i.puede_cursar
    assert not prog_i.puede_rendir


# --- Casos completos ---------------------------------------------------------


def test_alumno_con_primer_anio_casi_terminado(plan):
    estados = {1: A, 2: A, 3: A, 4: A, 5: R, 6: A, 7: R, 8: A}
    # Puede cursar las de segundo año que dependen solo de primero, pero no
    # las que piden materias de segundo año (13, 14, 15 y 17).
    assert cursables(plan, estados) == [9, 10, 11, 12, 16]
    assert rendibles(plan, estados) == [5, 7]


def test_alumno_que_termino_la_carrera(plan):
    todas_aprobadas = {m.numero: A for m in plan}
    resultado = evaluar_plan(plan, todas_aprobadas)
    assert not any(e.puede_cursar or e.puede_rendir for e in resultado)


# --- Errores -----------------------------------------------------------------


def test_rechaza_materias_que_no_estan_en_el_plan(plan):
    with pytest.raises(ValueError, match=r"\[99\]"):
        evaluar_plan(plan, {99: A})
