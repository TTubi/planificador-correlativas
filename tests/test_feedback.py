import pytest

from app.services.feedback import formatear_numero, mensaje_de_avance
from app.services.progreso import Progreso


def progreso(aprobadas: int, promedio: float | None = None, total: int = 17) -> Progreso:
    """Arma un Progreso de prueba. El porcentaje se calcula igual que en progreso.py."""
    return Progreso(
        aprobadas=aprobadas,
        total=total,
        porcentaje=aprobadas * 100 // total,
        promedio=promedio,
        notas_cargadas=0 if promedio is None else aprobadas,
    )


def test_un_alumno_nuevo_recibe_la_bienvenida():
    assert mensaje_de_avance(progreso(0)) == "¡Arrancamos! Empezá por las materias que podés cursar ahora."


def test_antes_de_la_mitad_muestra_el_porcentaje():
    assert mensaje_de_avance(progreso(3)) == "Vas sumando: ya tenés el 17% de la carrera. ¡Paso a paso!"


def test_desde_la_mitad_lo_celebra():
    # 9 de 17 = 52 %.
    assert mensaje_de_avance(progreso(9)) == "Ya pasaste la mitad de la carrera: llevás el 52%. ¡Seguí así!"


def test_justo_antes_de_la_mitad_todavia_no():
    # 8 de 17 = 47 %.
    assert mensaje_de_avance(progreso(8)).startswith("Vas sumando")


@pytest.mark.parametrize(
    ("aprobadas", "esperado"),
    [
        (14, "¡Te faltan solo 3 materias! Metele un último esfuerzo 💪"),
        (15, "¡Te faltan solo 2 materias! Metele un último esfuerzo 💪"),
        (16, "¡Te falta solo 1 materia! Metele un último esfuerzo 💪"),
    ],
)
def test_cuando_falta_poco_pide_un_ultimo_esfuerzo(aprobadas, esperado):
    assert mensaje_de_avance(progreso(aprobadas)) == esperado


def test_con_4_pendientes_todavia_no_es_el_ultimo_esfuerzo():
    assert mensaje_de_avance(progreso(13)).startswith("Ya pasaste la mitad")


def test_al_terminar_felicita():
    assert mensaje_de_avance(progreso(17)) == "¡Terminaste la tecnicatura! 🎓 Felicitaciones, te lo ganaste."


@pytest.mark.parametrize(
    ("promedio", "frase"),
    [
        (9.25, "Y con un promedio de 9,25, ¡excelente!"),
        (8, "Y con un promedio de 8, ¡excelente!"),
        (7.5, "Tu promedio es 7,5, ¡muy bien!"),
        (6.67, "Tu promedio es 6,67: cada final que rendís suma para subirlo."),
    ],
)
def test_suma_una_frase_segun_el_promedio(promedio, frase):
    assert mensaje_de_avance(progreso(3, promedio)).endswith(" " + frase)


def test_sin_notas_no_habla_del_promedio():
    assert "promedio" not in mensaje_de_avance(progreso(3))


def test_terminar_con_buen_promedio():
    assert mensaje_de_avance(progreso(17, 8.5)) == (
        "¡Terminaste la tecnicatura! 🎓 Felicitaciones, te lo ganaste. Y con un promedio de 8,5, ¡excelente!"
    )


@pytest.mark.parametrize(("numero", "texto"), [(7.5, "7,5"), (8.0, "8"), (7.67, "7,67"), (10, "10"), (6.1, "6,1")])
def test_formatea_numeros_en_formato_argentino(numero, texto):
    assert formatear_numero(numero) == texto
