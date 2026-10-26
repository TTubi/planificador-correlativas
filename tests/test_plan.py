import json

import pytest

from app.database.db import conectar, crear_esquema, guardar_materias, obtener_materias
from app.services.plan import Materia, buscar_ciclo, materias_desde_dict, validar_materias
from scripts.cargar_plan import RUTA_PLAN, cargar


@pytest.fixture
def plan_real() -> list[Materia]:
    datos = json.loads(RUTA_PLAN.read_text(encoding="utf-8"))
    return materias_desde_dict(datos)


# --- El plan oficial ---------------------------------------------------------


def test_el_plan_oficial_es_valido(plan_real):
    assert validar_materias(plan_real) == []


def test_el_plan_oficial_tiene_17_materias(plan_real):
    assert len(plan_real) == 17
    assert [m.numero for m in plan_real] == list(range(1, 18))


def test_programacion_iii_tiene_las_correlativas_del_documento(plan_real):
    prog_iii = next(m for m in plan_real if m.nombre == "Programación III")
    assert prog_iii.regulares == (5, 7)
    assert prog_iii.aprobadas == (1,)


# --- Validaciones ------------------------------------------------------------


def test_detecta_una_correlativa_inexistente():
    materias = [Materia(1, "A", 1, regulares=(99,))]
    errores = validar_materias(materias)
    assert errores == ["A: requiere la materia 99, que no existe"]


def test_detecta_una_materia_correlativa_de_si_misma():
    materias = [Materia(1, "A", 1, aprobadas=(1,))]
    assert "A: no puede ser correlativa de sí misma" in validar_materias(materias)


def test_detecta_numeros_repetidos():
    materias = [Materia(1, "A", 1), Materia(1, "B", 1)]
    assert "Números de materia repetidos: [1]" in validar_materias(materias)


def test_detecta_nivel_invalido():
    materias = [Materia(1, "A", 3)]
    assert "A: nivel 3 inválido (debe ser 1 o 2)" in validar_materias(materias)


def test_detecta_materia_en_las_dos_listas():
    materias = [Materia(1, "A", 1), Materia(2, "B", 1, regulares=(1,), aprobadas=(1,))]
    errores = validar_materias(materias)
    assert errores == ["B: las materias [1] figuran como regulares y aprobadas a la vez"]


def test_detecta_un_ciclo_indirecto():
    # A requiere B, B requiere C y C requiere A: ninguna se podría cursar.
    materias = [
        Materia(1, "A", 1, regulares=(2,)),
        Materia(2, "B", 1, regulares=(3,)),
        Materia(3, "C", 1, aprobadas=(1,)),
    ]
    assert buscar_ciclo(materias) == [1, 2, 3, 1]
    assert validar_materias(materias) == ["Hay correlativas circulares: A → B → C → A"]


def test_sin_ciclo_cuando_dos_materias_comparten_requisito():
    # B y C requieren A: es un "diamante", no un ciclo.
    materias = [
        Materia(1, "A", 1),
        Materia(2, "B", 1, regulares=(1,)),
        Materia(3, "C", 1, regulares=(1,)),
        Materia(4, "D", 2, regulares=(2, 3)),
    ]
    assert buscar_ciclo(materias) is None


def test_formato_invalido_da_un_error_claro():
    with pytest.raises(ValueError, match="formato inválido"):
        materias_desde_dict({"materias": [{"numero": 1}]})


# --- Base de datos -----------------------------------------------------------


def test_guardar_y_leer_devuelve_las_mismas_materias(plan_real):
    conexion = conectar(":memory:")
    crear_esquema(conexion)
    guardar_materias(conexion, plan_real)
    assert obtener_materias(conexion) == plan_real


def test_la_base_rechaza_una_correlativa_a_materia_inexistente():
    conexion = conectar(":memory:")
    crear_esquema(conexion)
    with pytest.raises(Exception):
        guardar_materias(conexion, [Materia(1, "A", 1, regulares=(99,))])
    # Por la transacción, tampoco quedó guardada la materia.
    assert obtener_materias(conexion) == []


def test_el_script_genera_la_base(tmp_path, capsys):
    ruta_base = tmp_path / "prueba.db"
    assert cargar(ruta_base=ruta_base) == 0
    # 19 requisitos de "regular" + 12 de "aprobada", contados en el documento.
    assert "17 materias y 31 correlativas" in capsys.readouterr().out

    conexion = conectar(ruta_base)
    assert len(obtener_materias(conexion)) == 17
    conexion.close()


def test_el_script_no_carga_un_plan_invalido(tmp_path, capsys):
    ruta_plan = tmp_path / "plan.json"
    ruta_plan.write_text(
        json.dumps({"carrera": "X", "plan": "1", "materias": [
            {"numero": 1, "nombre": "A", "nivel": 1, "regulares": [2]},
        ]}),
        encoding="utf-8",
    )
    ruta_base = tmp_path / "prueba.db"
    assert cargar(ruta_plan, ruta_base) == 1
    assert "no se cargó" in capsys.readouterr().out
    assert not ruta_base.exists()
