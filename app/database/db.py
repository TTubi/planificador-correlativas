"""Acceso a la base SQLite del plan de estudios.

Este es el único módulo que escribe SQL. El resto de la aplicación trabaja
con objetos Materia y no necesita saber cómo se guardan.
"""

import os
import sqlite3
from pathlib import Path

from app.services.plan import Materia

RAIZ_PROYECTO = Path(__file__).resolve().parents[2]
RUTA_BASE_POR_DEFECTO = RAIZ_PROYECTO / "planificador.db"
RUTA_ESQUEMA = Path(__file__).with_name("schema.sql")


def ruta_base_configurada() -> Path:
    """Devuelve dónde va la base: la variable PLANIFICADOR_DB o la ruta por defecto.

    Sirve para los hostings donde la carpeta del proyecto es de solo
    lectura, como Vercel, que solo deja escribir en /tmp.
    """
    return Path(os.environ.get("PLANIFICADOR_DB") or RUTA_BASE_POR_DEFECTO)


# Se lee una sola vez, al importar el módulo: la variable de entorno se
# define antes de arrancar el servidor y no cambia mientras corre.
RUTA_BASE = ruta_base_configurada()


def conectar(ruta: Path | str = RUTA_BASE) -> sqlite3.Connection:
    """Abre una conexión con las claves foráneas activadas.

    SQLite no controla las FOREIGN KEY salvo que se lo pidamos en cada
    conexión. Sin esta línea, la base aceptaría una correlativa que apunta
    a una materia inexistente.
    """
    conexion = sqlite3.connect(ruta)
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion


def crear_esquema(conexion: sqlite3.Connection) -> None:
    conexion.executescript(RUTA_ESQUEMA.read_text(encoding="utf-8"))


def guardar_materias(conexion: sqlite3.Connection, materias: list[Materia]) -> None:
    """Inserta las materias y sus correlativas en una sola transacción.

    `with conexion:` hace que, si falla cualquier INSERT, se deshaga todo.
    Así nunca queda una base cargada a medias.
    """
    with conexion:
        conexion.executemany(
            "INSERT INTO materias (numero, nombre, nivel) VALUES (?, ?, ?)",
            [(m.numero, m.nombre, m.nivel) for m in materias],
        )
        filas = []
        for m in materias:
            filas += [(m.numero, requerida, "regular") for requerida in m.regulares]
            filas += [(m.numero, requerida, "aprobada") for requerida in m.aprobadas]
        conexion.executemany(
            "INSERT INTO correlativas (materia, requiere, tipo) VALUES (?, ?, ?)",
            filas,
        )


def obtener_materias(conexion: sqlite3.Connection) -> list[Materia]:
    """Lee el plan completo y lo devuelve como lista de Materia."""
    requisitos: dict[int, dict[str, list[int]]] = {}
    for materia, requiere, tipo in conexion.execute(
        "SELECT materia, requiere, tipo FROM correlativas ORDER BY materia, requiere"
    ):
        requisitos.setdefault(materia, {"regular": [], "aprobada": []})[tipo].append(requiere)

    materias = []
    for numero, nombre, nivel in conexion.execute(
        "SELECT numero, nombre, nivel FROM materias ORDER BY numero"
    ):
        de_esta = requisitos.get(numero, {"regular": [], "aprobada": []})
        materias.append(
            Materia(
                numero=numero,
                nombre=nombre,
                nivel=nivel,
                regulares=tuple(de_esta["regular"]),
                aprobadas=tuple(de_esta["aprobada"]),
            )
        )
    return materias
