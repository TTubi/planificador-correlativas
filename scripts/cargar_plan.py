"""Genera la base SQLite a partir del JSON del plan de estudios.

Uso, desde la raíz del proyecto:

    python -m scripts.cargar_plan

La base es un archivo generado: se borra y se vuelve a crear en cada
ejecución. Lo que se versiona en Git es el JSON, que es la fuente de verdad.
"""

import json
import sys
from pathlib import Path

from app.database.db import RAIZ_PROYECTO, RUTA_BASE, conectar, crear_esquema, guardar_materias
from app.services.plan import materias_desde_dict, validar_materias

RUTA_PLAN = RAIZ_PROYECTO / "data" / "tup_plan2024.json"


def cargar(ruta_plan: Path = RUTA_PLAN, ruta_base: Path = RUTA_BASE) -> int:
    datos = json.loads(ruta_plan.read_text(encoding="utf-8"))
    materias = materias_desde_dict(datos)

    errores = validar_materias(materias)
    if errores:
        print("El plan tiene errores y no se cargó:")
        for error in errores:
            print(f"  - {error}")
        return 1

    ruta_base.unlink(missing_ok=True)
    conexion = conectar(ruta_base)
    try:
        crear_esquema(conexion)
        guardar_materias(conexion, materias)
        total_correlativas = conexion.execute("SELECT COUNT(*) FROM correlativas").fetchone()[0]
    finally:
        conexion.close()

    print(f"Plan cargado: {datos['carrera']} (plan {datos['plan']})")
    print(f"  {len(materias)} materias y {total_correlativas} correlativas en {ruta_base.name}")
    return 0


if __name__ == "__main__":
    sys.exit(cargar())
