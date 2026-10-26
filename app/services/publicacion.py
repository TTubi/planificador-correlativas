"""Texto de la publicación de LinkedIn con el progreso del alumno.

El texto está escrito en primera persona, porque lo publica el alumno en su
perfil, y pensado para que le sume: destaca su avance y su constancia, nunca
lo que le falta como algo negativo. El promedio solo se ofrece si suma
(7 o más) y si el alumno elige incluirlo.

Hay varias versiones por etapa, así no todas las publicaciones son iguales.
Al final se da crédito a la app y a su creador.

Igual que el resto de `services/`, son funciones puras.
"""

from app.services.feedback import POCAS_MATERIAS, formatear_numero
from app.services.progreso import Progreso

URL_APP = "https://planificador-correlativas.vercel.app/"
AUTOR = "Agustín Singh"
PERFIL_AUTOR = "https://www.linkedin.com/in/agustin-ezequiel-singh-576059267"
CARRERA = "Tecnicatura Universitaria en Programación"
HASHTAGS = "#UTN #Programación #DesarrolloDeSoftware #Estudiantes"

# El promedio se ofrece para publicar solo desde este valor.
PROMEDIO_QUE_SUMA = 7

TITULARES = {
    "inicio": "¡Arranqué la carrera!",
    "en_camino": "Sumando materias",
    "mitad": "¡Pasé la mitad!",
    "recta_final": "Recta final",
    "egreso": "¡Terminé la carrera!",
}

# Variables disponibles: {porcentaje}, {aprobadas}, {total}, {carrera} y {faltan}
# (este último ya armado en singular o plural: "1 materia", "2 materias").
PLANTILLAS = {
    "inicio": [
        "Arranqué la {carrera} en la UTN 🚀\n\n"
        "Tengo por delante {total} materias y un objetivo claro: formarme en desarrollo de software. "
        "Voy a ir compartiendo mi avance.",
        "Primer paso dado: empecé la {carrera} en la UTN 💻\n\n"
        "{total} materias para aprender a programar, diseñar bases de datos y trabajar en equipo. ¡Vamos!",
    ],
    "en_camino": [
        "Ya aprobé {aprobadas} de las {total} materias de la {carrera} en la UTN: llevo el {porcentaje}% de la carrera 📚\n\n"
        "Cada materia suma herramientas que ya estoy aplicando en proyectos propios.",
        "{porcentaje}% de la {carrera} (UTN) completado ✅\n\n"
        "{aprobadas} materias aprobadas y muchas ganas de seguir aprendiendo.",
    ],
    "mitad": [
        "¡Pasé la mitad de la carrera! 🎯 Ya completé el {porcentaje}% de la {carrera} en la UTN "
        "({aprobadas} de {total} materias).\n\n"
        "Constancia y práctica, materia a materia.",
        "Más de la mitad del camino recorrido 💪 {aprobadas} de {total} materias aprobadas en la {carrera} (UTN).\n\n"
        "Cada cuatrimestre, más cerca del objetivo.",
    ],
    "recta_final": [
        "Recta final 🏁 Me faltan solo {faltan} para terminar la {carrera} en la UTN.\n\n"
        "Ya completé el {porcentaje}% de la carrera. ¡A dar el último empujón!",
        "{porcentaje}% completado y a {faltan} de terminar la {carrera} (UTN) 🔥\n\n"
        "El final está cerca.",
    ],
    "egreso": [
        "¡Terminé la {carrera} en la UTN! 🎓\n\n"
        "{total} materias aprobadas. Gracias a docentes y compañeros por el camino recorrido. "
        "Ahora, a seguir creciendo en el desarrollo de software.",
        "100% completado 🎓 Aprobé las {total} materias de la {carrera} (UTN).\n\n"
        "Una etapa que se cierra y muchas ganas de lo que viene.",
    ],
}


def etapa(progreso: Progreso) -> str:
    """En qué momento de la carrera está el alumno.

    Usa los mismos cortes que los mensajes de feedback, para que la app y la
    publicación digan lo mismo.
    """
    faltan = progreso.total - progreso.aprobadas
    if faltan == 0:
        return "egreso"
    if faltan <= POCAS_MATERIAS:
        return "recta_final"
    if progreso.porcentaje >= 50:
        return "mitad"
    if progreso.aprobadas == 0:
        return "inicio"
    return "en_camino"


def promedio_suma(progreso: Progreso) -> bool:
    """Si el promedio está cargado y es lo bastante bueno para mostrarlo."""
    return progreso.promedio is not None and progreso.promedio >= PROMEDIO_QUE_SUMA


def cantidad_de_versiones(progreso: Progreso) -> int:
    return len(PLANTILLAS[etapa(progreso)])


def texto_publicacion(progreso: Progreso, incluir_promedio: bool = False, version: int = 0) -> str:
    """Arma el texto completo para publicar en LinkedIn.

    `version` elige entre las plantillas de la etapa. Se usa el resto de la
    división (%), así cualquier número da una versión válida y el botón
    "Otra versión" puede sumar de a uno sin preocuparse por el límite.
    """
    plantillas = PLANTILLAS[etapa(progreso)]
    faltan = progreso.total - progreso.aprobadas
    cuerpo = plantillas[version % len(plantillas)].format(
        porcentaje=progreso.porcentaje,
        aprobadas=progreso.aprobadas,
        total=progreso.total,
        carrera=CARRERA,
        faltan="1 materia" if faltan == 1 else f"{faltan} materias",
    )

    partes = [cuerpo]
    if incluir_promedio and promedio_suma(progreso):
        nombre = "Promedio final" if faltan == 0 else "Promedio actual"
        partes.append(f"{nombre}: {formatear_numero(progreso.promedio)} ⭐")
    partes.append(
        f"Sigo mi avance con el Planificador de Correlativas, una app creada por {AUTOR} "
        f"({PERFIL_AUTOR}): {URL_APP}"
    )
    partes.append(HASHTAGS)
    return "\n\n".join(partes)
