"""Materias llave: cuántas materias desbloquea cada una.

Una materia "desbloquea" a otra cuando figura entre sus correlativas.
- Directamente: la otra materia la pide en `regulares` o `aprobadas`.
- En total: también cuenta las que se desbloquean después, en cadena.
  Por ejemplo, Programación I desbloquea Programación II, que a su vez
  desbloquea Programación III: Programación I desbloquea las dos.

Saber esto ayuda a priorizar: atrasarse en una materia con muchas
dependientes frena buena parte de la carrera.

Igual que el resto de `services/`, son funciones puras.
"""

from dataclasses import dataclass

from app.services.plan import Materia


@dataclass(frozen=True)
class Llave:
    numero: int
    nombre: str
    desbloquea_directamente: tuple[int, ...]
    desbloquea_en_total: tuple[int, ...]


def calcular_llaves(materias: list[Materia]) -> list[Llave]:
    """Calcula qué materias desbloquea cada una, directa e indirectamente.

    Devuelve las materias ordenadas de la que más desbloquea en total a la
    que menos (y por número, si empatan). Supone un plan válido, sin ciclos:
    eso ya lo controla `validar_materias` al cargar el plan.
    """
    # Grafo "al revés": para cada materia, quiénes la piden como correlativa.
    dependientes: dict[int, set[int]] = {m.numero: set() for m in materias}
    for materia in materias:
        for requerida in materia.regulares + materia.aprobadas:
            dependientes[requerida].add(materia.numero)

    def alcanzables(numero: int) -> set[int]:
        """Recorre el grafo desde `numero` y junta todo lo que encuentra."""
        encontradas: set[int] = set()
        pendientes = list(dependientes[numero])
        while pendientes:
            actual = pendientes.pop()
            if actual not in encontradas:
                encontradas.add(actual)
                pendientes.extend(dependientes[actual])
        return encontradas

    llaves = [
        Llave(
            numero=m.numero,
            nombre=m.nombre,
            desbloquea_directamente=tuple(sorted(dependientes[m.numero])),
            desbloquea_en_total=tuple(sorted(alcanzables(m.numero))),
        )
        for m in materias
    ]
    return sorted(llaves, key=lambda llave: (-len(llave.desbloquea_en_total), llave.numero))
