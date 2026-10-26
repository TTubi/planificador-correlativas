"""Modelo del plan de estudios y validación de sus datos.

Acá no hay base de datos ni HTTP: solo estructuras de Python y reglas.
Eso permite probar todo con tests rápidos y sin preparar nada.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Materia:
    """Una materia del plan con sus dos listas de correlativas.

    - regulares: materias que hay que tener regularizadas para cursarla
      (y aprobadas para rendirla).
    - aprobadas: materias que hay que tener aprobadas para cursarla.
    """

    numero: int
    nombre: str
    nivel: int
    regulares: tuple[int, ...] = ()
    aprobadas: tuple[int, ...] = ()


def materias_desde_dict(datos: dict) -> list[Materia]:
    """Convierte el contenido del JSON del plan en una lista de Materia."""
    try:
        return [
            Materia(
                numero=m["numero"],
                nombre=m["nombre"],
                nivel=m["nivel"],
                regulares=tuple(m.get("regulares", [])),
                aprobadas=tuple(m.get("aprobadas", [])),
            )
            for m in datos["materias"]
        ]
    except (KeyError, TypeError) as error:
        raise ValueError(f"El archivo del plan tiene un formato inválido: {error}") from error


def validar_materias(materias: list[Materia]) -> list[str]:
    """Revisa que el plan sea coherente y devuelve la lista de errores.

    Devuelve todos los errores juntos (y no solo el primero) para que,
    si el archivo tiene varios problemas, se puedan corregir de una vez.
    Una lista vacía significa que el plan es válido.
    """
    errores: list[str] = []

    numeros = [m.numero for m in materias]
    repetidos = sorted({n for n in numeros if numeros.count(n) > 1})
    if repetidos:
        errores.append(f"Números de materia repetidos: {repetidos}")

    nombres = [m.nombre for m in materias]
    nombres_repetidos = sorted({n for n in nombres if nombres.count(n) > 1})
    if nombres_repetidos:
        errores.append(f"Nombres de materia repetidos: {nombres_repetidos}")

    existentes = set(numeros)
    for materia in materias:
        if materia.nivel not in (1, 2):
            errores.append(f"{materia.nombre}: nivel {materia.nivel} inválido (debe ser 1 o 2)")

        for requerida in materia.regulares + materia.aprobadas:
            if requerida == materia.numero:
                errores.append(f"{materia.nombre}: no puede ser correlativa de sí misma")
            elif requerida not in existentes:
                errores.append(f"{materia.nombre}: requiere la materia {requerida}, que no existe")

        en_ambas = set(materia.regulares) & set(materia.aprobadas)
        if en_ambas:
            errores.append(
                f"{materia.nombre}: las materias {sorted(en_ambas)} figuran como regulares y aprobadas a la vez"
            )

    # La búsqueda de ciclos solo tiene sentido si las referencias son válidas.
    if not errores:
        ciclo = buscar_ciclo(materias)
        if ciclo:
            nombres_por_numero = {m.numero: m.nombre for m in materias}
            recorrido = " → ".join(nombres_por_numero[n] for n in ciclo)
            errores.append(f"Hay correlativas circulares: {recorrido}")

    return errores


def buscar_ciclo(materias: list[Materia]) -> list[int] | None:
    """Busca un ciclo en el grafo de correlativas.

    Cada materia es un nodo y cada correlativa, una flecha hacia la materia
    que se requiere. Si siguiendo las flechas se vuelve a una materia ya
    visitada en el mismo recorrido, hay un ciclo: A requiere B y B requiere A
    (directa o indirectamente), así que ninguna de las dos se podría cursar.

    Usa una búsqueda en profundidad (DFS) que marca cada nodo con un estado:
    sin visitar, en el recorrido actual, o terminado.
    Devuelve el ciclo como lista de números, o None si no hay ninguno.
    """
    requisitos = {m.numero: m.regulares + m.aprobadas for m in materias}
    SIN_VISITAR, EN_CAMINO, TERMINADO = 0, 1, 2
    estado = {numero: SIN_VISITAR for numero in requisitos}
    camino: list[int] = []

    def visitar(numero: int) -> list[int] | None:
        estado[numero] = EN_CAMINO
        camino.append(numero)
        for requerida in requisitos[numero]:
            if estado[requerida] == EN_CAMINO:
                inicio = camino.index(requerida)
                return camino[inicio:] + [requerida]
            if estado[requerida] == SIN_VISITAR:
                ciclo = visitar(requerida)
                if ciclo:
                    return ciclo
        camino.pop()
        estado[numero] = TERMINADO
        return None

    for numero in requisitos:
        if estado[numero] == SIN_VISITAR:
            ciclo = visitar(numero)
            if ciclo:
                return ciclo
    return None
