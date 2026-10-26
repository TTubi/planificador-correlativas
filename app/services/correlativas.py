"""Lógica central: qué puede cursar y rendir un alumno según su avance.

Todas las funciones son "puras": reciben datos, devuelven un resultado y no
leen archivos, ni la base, ni la red. Por eso se pueden probar con tests
rápidos y la misma lógica sirve tanto para la API como para un script.

Reglas del régimen de correlatividades (Ordenanza 2019/2023):
- Para CURSAR una materia hay que tener sus correlativas "regulares" al
  menos regularizadas, y sus correlativas "aprobadas", aprobadas.
- Para RENDIR una materia hay que tenerla regularizada y todas sus
  correlativas aprobadas.
"""

from dataclasses import dataclass, field
from enum import Enum

from app.services.plan import Materia


class Estado(str, Enum):
    PENDIENTE = "pendiente"
    REGULAR = "regular"
    APROBADA = "aprobada"


@dataclass(frozen=True)
class Faltante:
    """Una correlativa que todavía no cumple la condición necesaria."""

    numero: int
    nombre: str
    se_necesita: Estado


@dataclass(frozen=True)
class Evaluacion:
    """El resultado de evaluar una materia para un alumno."""

    numero: int
    nombre: str
    estado: Estado
    puede_cursar: bool
    puede_rendir: bool
    faltan_para_cursar: list[Faltante] = field(default_factory=list)
    faltan_para_rendir: list[Faltante] = field(default_factory=list)


def evaluar_plan(materias: list[Materia], estados: dict[int, Estado]) -> list[Evaluacion]:
    """Evalúa cada materia del plan según el estado del alumno.

    `estados` solo necesita las materias regulares o aprobadas: las que no
    aparecen se consideran pendientes. Si aparece un número que no existe
    en el plan, se lanza ValueError, porque probablemente es un error de
    quien llamó a la función y conviene enterarse en lugar de ignorarlo.
    """
    por_numero = {m.numero: m for m in materias}
    desconocidas = sorted(set(estados) - set(por_numero))
    if desconocidas:
        raise ValueError(f"Materias que no existen en el plan: {desconocidas}")

    def estado_de(numero: int) -> Estado:
        return estados.get(numero, Estado.PENDIENTE)

    def faltante(numero: int, se_necesita: Estado) -> Faltante:
        return Faltante(numero, por_numero[numero].nombre, se_necesita)

    evaluaciones = []
    for materia in materias:
        estado = estado_de(materia.numero)

        faltan_para_cursar = [
            faltante(n, Estado.REGULAR) for n in materia.regulares if estado_de(n) == Estado.PENDIENTE
        ] + [faltante(n, Estado.APROBADA) for n in materia.aprobadas if estado_de(n) != Estado.APROBADA]

        faltan_para_rendir = [
            faltante(n, Estado.APROBADA)
            for n in materia.regulares + materia.aprobadas
            if estado_de(n) != Estado.APROBADA
        ]

        evaluaciones.append(
            Evaluacion(
                numero=materia.numero,
                nombre=materia.nombre,
                estado=estado,
                # Solo tiene sentido cursar lo que todavía está pendiente,
                # y rendir lo que ya está regularizado.
                puede_cursar=estado == Estado.PENDIENTE and not faltan_para_cursar,
                puede_rendir=estado == Estado.REGULAR and not faltan_para_rendir,
                faltan_para_cursar=faltan_para_cursar if estado == Estado.PENDIENTE else [],
                faltan_para_rendir=faltan_para_rendir if estado == Estado.REGULAR else [],
            )
        )
    return evaluaciones
