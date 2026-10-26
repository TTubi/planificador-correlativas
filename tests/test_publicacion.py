import pytest

from app.services.progreso import Progreso
from app.services.publicacion import (
    PERFIL_AUTOR,
    URL_APP,
    cantidad_de_versiones,
    etapa,
    promedio_suma,
    texto_publicacion,
)


def progreso(aprobadas: int, promedio: float | None = None, total: int = 17) -> Progreso:
    return Progreso(
        aprobadas=aprobadas,
        total=total,
        porcentaje=aprobadas * 100 // total,
        promedio=promedio,
        notas_cargadas=0 if promedio is None else aprobadas,
    )


@pytest.mark.parametrize(
    ("aprobadas", "esperada"),
    [(0, "inicio"), (3, "en_camino"), (8, "en_camino"), (9, "mitad"), (13, "mitad"), (14, "recta_final"), (16, "recta_final"), (17, "egreso")],
)
def test_la_etapa_usa_los_mismos_cortes_que_el_feedback(aprobadas, esperada):
    assert etapa(progreso(aprobadas)) == esperada


def test_el_texto_lleva_el_porcentaje_y_las_materias_del_alumno():
    texto = texto_publicacion(progreso(3))
    assert texto.startswith("Ya aprobé 3 de las 17 materias de la Tecnicatura Universitaria en Programación en la UTN: llevo el 17%")


def test_cada_etapa_tiene_mas_de_una_version_y_son_distintas():
    for aprobadas in (0, 3, 9, 15, 17):
        p = progreso(aprobadas)
        versiones = {texto_publicacion(p, version=v) for v in range(cantidad_de_versiones(p))}
        assert len(versiones) == cantidad_de_versiones(p) >= 2


def test_cualquier_numero_de_version_es_valido():
    p = progreso(3)
    assert texto_publicacion(p, version=2) == texto_publicacion(p, version=0)
    assert texto_publicacion(p, version=7) == texto_publicacion(p, version=1)


def test_en_la_recta_final_dice_cuantas_faltan_en_singular_o_plural():
    assert "Me faltan solo 2 materias" in texto_publicacion(progreso(15))
    assert "Me faltan solo 1 materia para" in texto_publicacion(progreso(16))
    assert "a 1 materia de terminar" in texto_publicacion(progreso(16), version=1)


def test_siempre_da_credito_a_la_app_y_a_su_creador():
    for aprobadas in (0, 9, 17):
        texto = texto_publicacion(progreso(aprobadas))
        assert URL_APP in texto
        assert PERFIL_AUTOR in texto
        assert "Agustín Singh" in texto
        assert texto.endswith("#UTN #Programación #DesarrolloDeSoftware #Estudiantes")


def test_el_promedio_solo_aparece_si_se_pide():
    assert "Promedio" not in texto_publicacion(progreso(3, 8.5))
    assert "Promedio actual: 8,5 ⭐" in texto_publicacion(progreso(3, 8.5), incluir_promedio=True)


def test_al_terminar_es_el_promedio_final():
    assert "Promedio final: 9 ⭐" in texto_publicacion(progreso(17, 9.0), incluir_promedio=True)


@pytest.mark.parametrize(("promedio", "suma"), [(None, False), (6.5, False), (6.99, False), (7, True), (9.25, True)])
def test_el_promedio_se_ofrece_solo_si_suma(promedio, suma):
    assert promedio_suma(progreso(3, promedio)) is suma


def test_un_promedio_que_no_suma_no_se_publica_aunque_se_pida():
    assert "Promedio" not in texto_publicacion(progreso(3, 6.5), incluir_promedio=True)


def test_los_textos_no_asumen_el_genero_de_quien_publica():
    # Lo publica cualquier alumno: nada de "desarrollador", "recibido", "técnico".
    for aprobadas in (0, 3, 9, 15, 17):
        p = progreso(aprobadas, 9)
        for version in range(cantidad_de_versiones(p)):
            texto = texto_publicacion(p, incluir_promedio=True, version=version).lower()
            for palabra in ("desarrollador", "recibido", "recibida", "técnico ", "egresado", "egresada"):
                assert palabra not in texto
