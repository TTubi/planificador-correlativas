"""Progreso del alumno en la carrera: porcentaje completado y promedio.

- El porcentaje se calcula por cantidad de materias aprobadas.
- El promedio es "sin aplazos": solo cuenta las notas con las que el alumno
  aprobó. La nota es opcional (por ejemplo, una materia por equivalencia
  de la que no recuerda la nota), así que puede haber aprobadas sin nota.

Igual que el resto de `services/`, son funciones puras.
"""

import math
from dataclasses import dataclass

from app.services.correlativas import Estado
from app.services.plan import Materia

# En la UTN una materia se aprueba con 6 o más, en una escala hasta 10.
NOTA_MINIMA = 6
NOTA_MAXIMA = 10


@dataclass(frozen=True)
class Progreso:
    aprobadas: int
    total: int
    porcentaje: int
    promedio: float | None
    notas_cargadas: int


def calcular_progreso(
    materias: list[Materia], estados: dict[int, Estado], notas: dict[int, int]
) -> Progreso:
    """Calcula cuánto de la carrera tiene aprobado el alumno y su promedio.

    Lanza ValueError si una nota es de una materia que no existe, que no está
    aprobada o que está fuera de la escala: una nota así no tiene sentido y
    conviene avisarle a quien llamó en lugar de ignorarla en silencio.
    """
    por_numero = {m.numero: m for m in materias}
    errores = []
    for numero, nota in sorted(notas.items()):
        if numero not in por_numero:
            errores.append(f"la materia {numero} no existe en el plan")
        elif estados.get(numero) != Estado.APROBADA:
            errores.append(f"{por_numero[numero].nombre} tiene nota pero no está aprobada")
        elif not NOTA_MINIMA <= nota <= NOTA_MAXIMA:
            errores.append(f"{por_numero[numero].nombre}: la nota {nota} no está entre {NOTA_MINIMA} y {NOTA_MAXIMA}")
    if errores:
        raise ValueError("Notas inválidas: " + "; ".join(errores))

    total = len(materias)
    aprobadas = sum(1 for m in materias if estados.get(m.numero) == Estado.APROBADA)
    return Progreso(
        aprobadas=aprobadas,
        total=total,
        # Se redondea para abajo: así nunca dice 100% si falta una materia.
        porcentaje=math.floor(aprobadas * 100 / total) if total else 0,
        promedio=round(sum(notas.values()) / len(notas), 2) if notas else None,
        notas_cargadas=len(notas),
    )
