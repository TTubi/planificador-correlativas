"""Mensajes de feedback para el alumno según su avance y su promedio.

El tono es cercano y motivador, con voseo. Nunca reta: a un promedio bajo
le corresponde un "cada final suma", no un reproche.

Igual que el resto de `services/`, son funciones puras.
"""

from app.services.progreso import Progreso

# Cuántas materias pendientes cuentan como "te falta poco".
POCAS_MATERIAS = 3
PROMEDIO_EXCELENTE = 8
PROMEDIO_MUY_BUENO = 7


def formatear_numero(numero: float) -> str:
    """7.5 → "7,5" y 8.0 → "8": formato argentino, sin ceros de más."""
    return f"{numero:.2f}".rstrip("0").rstrip(".").replace(".", ",")


def mensaje_de_avance(progreso: Progreso) -> str:
    """Arma un mensaje según cuánto falta y, si hay notas, según el promedio."""
    faltan = progreso.total - progreso.aprobadas

    if faltan == 0:
        avance = "¡Terminaste la tecnicatura! 🎓 Felicitaciones, te lo ganaste."
    elif faltan <= POCAS_MATERIAS:
        cuantas = "1 materia" if faltan == 1 else f"{faltan} materias"
        falta = "falta" if faltan == 1 else "faltan"
        avance = f"¡Te {falta} solo {cuantas}! Metele un último esfuerzo 💪"
    elif progreso.porcentaje >= 50:
        avance = f"Ya pasaste la mitad de la carrera: llevás el {progreso.porcentaje}%. ¡Seguí así!"
    elif progreso.aprobadas == 0:
        avance = "¡Arrancamos! Empezá por las materias que podés cursar ahora."
    else:
        avance = f"Vas sumando: ya tenés el {progreso.porcentaje}% de la carrera. ¡Paso a paso!"

    if progreso.promedio is None:
        return avance
    return f"{avance} {frase_de_promedio(progreso.promedio)}"


def frase_de_promedio(promedio: float) -> str:
    valor = formatear_numero(promedio)
    if promedio >= PROMEDIO_EXCELENTE:
        return f"Y con un promedio de {valor}, ¡excelente!"
    if promedio >= PROMEDIO_MUY_BUENO:
        return f"Tu promedio es {valor}, ¡muy bien!"
    return f"Tu promedio es {valor}: cada final que rendís suma para subirlo."
