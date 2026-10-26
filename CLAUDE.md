# Planificador de Correlativas

Proyecto de portfolio de Agustín, estudiante de la Tecnicatura Universitaria en Programación (UTN Rosario). App web que, a partir de las materias que un alumno tiene regulares o aprobadas, muestra qué puede cursar, qué puede rendir, qué está bloqueado y por qué. Se va a publicar en GitHub, con una demo online y un post en LinkedIn.

## Cómo trabajar en este proyecto

El objetivo es que Agustín **aprenda** mientras se desarrolla, y que pueda explicar cada decisión en una entrevista. Por eso:

- Avanzar en tareas chicas y coherentes. Nunca generar la aplicación entera de una vez.
- Antes de implementar, explicar qué se va a hacer y por qué. Después, explicar los conceptos nuevos sin asumir conocimientos avanzados.
- Si hay varias opciones, recomendar una y explicar brevemente ventajas y desventajas.
- Cada tarea va en su propia rama y termina en un commit que funciona. No encadenar PRs.
- Correr `python -m pytest` antes de cada commit. No afirmar que algo funciona sin haberlo ejecutado.
- No agregar dependencias, capas ni patrones que el MVP no necesite. Si algo parece necesario, explicar por qué y esperar su aprobación.
- No borrar archivos ni hacer operaciones destructivas sin preguntar.
- Responder en español. El código (nombres, comentarios, docstrings) también va en español.

## Stack

- Backend: Python, FastAPI, Pydantic, Uvicorn.
- Base de datos: SQLite con SQL escrito a mano (sin ORM), usando el módulo `sqlite3`.
- Frontend: HTML, CSS y JavaScript sin frameworks, servido por FastAPI como archivos estáticos.
- Tests: pytest (y `TestClient` de FastAPI para la API, que necesita `httpx`).
- Entorno: Windows, PowerShell, VS Code, entorno virtual en `.venv`.

## Arquitectura

```
app/
├── main.py                 # app FastAPI
├── routes/                 # endpoints (todavía no existe)
├── schemas/                # modelos Pydantic de la API (todavía no existe)
├── services/
│   ├── plan.py             # Materia y validación del plan (ciclos, referencias)
│   └── correlativas.py     # lógica pura: evaluar_plan()
└── database/
    ├── schema.sql          # tablas materias y correlativas
    └── db.py               # único módulo con SQL
data/tup_plan2024.json      # fuente de verdad del plan (Ordenanza 2019/2023 CS UTN)
scripts/cargar_plan.py      # genera planificador.db desde el JSON
tests/
```

Principios:

- `services/` contiene funciones puras: no leen la base, archivos ni HTTP.
- La base `planificador.db` es un archivo generado y está en `.gitignore`. La fuente de verdad es el JSON.
- El progreso del alumno se guarda en su navegador (`localStorage`). El backend no guarda datos personales ni tiene login.

## Reglas del dominio

- Cada materia tiene dos listas: `regulares` y `aprobadas`.
- **Cursar:** la materia está pendiente, sus `regulares` están al menos regularizadas y sus `aprobadas` están aprobadas.
- **Rendir:** la materia está regularizada y todas sus correlativas (las dos listas) están aprobadas.
- No se valida que el estado del alumno sea "posible" (puede haber equivalencias).

## Comandos

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m scripts.cargar_plan
python -m pytest
uvicorn app.main:app --reload
```

## Estado y próximos pasos

Hecho:

1. Estructura inicial y `GET /health`.
2. Plan en JSON, esquema SQLite, script de carga y validaciones.
3. Lógica de cursar, rendir y faltantes, con tests.

Siguiente:

4. API: endpoint que recibe el estado del alumno y devuelve `evaluar_plan()`, con esquemas Pydantic y tests con `TestClient`. Mover `/health` a `routes/` y explicar `APIRouter`.
5. Frontend: vista del plan por año, marcar estados, `localStorage` y resultados.
6. Materias llave: cuántas materias desbloquea cada una, directa e indirectamente.
7. Diseño, README y GitHub Actions.
8. Deploy y lanzamiento.

Queda fuera del MVP: login, cálculo de cuatrimestres restantes, equivalencias, Trabajo Final Integrador (se agrega como caso especial más adelante), tabla `carreras` (se agrega cuando haya una segunda carrera) e IA.
