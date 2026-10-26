# Planificador de Correlativas

Proyecto de portfolio de Agustín, estudiante de la Tecnicatura Universitaria en Programación (UTN Rosario). App web que, a partir de las materias que un alumno tiene regulares o aprobadas, muestra qué puede cursar, qué puede rendir, qué está bloqueado y por qué. Se va a publicar en GitHub, con una demo online y un post en LinkedIn.

## Cómo trabajar en este proyecto

Trabajá de forma **autónoma**, como un desarrollador senior en un equipo profesional. No le preguntes a Agustín antes de cada paso ni esperes que apruebe los PRs: tomá las decisiones razonables, implementalas, documentalas en el PR, integralo vos y seguí con la próxima tarea. Agustín revisa los PRs después de integrados; si algo no le gusta, lo corrige con un PR nuevo.

Flujo para cada tarea:

1. Partir de `main` actualizado (`git checkout main` y `git pull`) y crear una rama con un nombre descriptivo.
2. Implementar en commits chicos y coherentes, con mensajes claros en español.
3. Correr `python -m pytest` antes de cada commit. Si algo falla, arreglarlo antes de seguir. No afirmar que algo funciona sin haberlo ejecutado.
4. Actualizar la sección "Estado y próximos pasos" de este archivo.
5. Subir la rama y abrir un PR contra `main`. No encadenar PRs ni commitear directo en `main`.
6. Si el repo tiene GitHub Actions, esperar a que el PR quede en verde. Si falla, arreglarlo en la misma rama.
7. **Integrar el PR vos mismo** con *squash merge* y borrar la rama: `gh pr merge <número> --squash --delete-branch` (si `gh pr merge` no está disponible, usar la API REST: `gh api -X PUT repos/TTubi/planificador-correlativas/pulls/<número>/merge -f merge_method=squash`).
8. Volver al paso 1 con la siguiente tarea de "Estado y próximos pasos", sin esperar indicaciones, hasta terminar la lista o encontrar uno de los casos de abajo en los que hay que frenar.

Al terminar una tanda de trabajo, dejale a Agustín un resumen corto con la lista de PRs integrados.

La descripción de cada PR es donde Agustín aprende, así que tiene que incluir:

- Qué se hizo y por qué.
- Los conceptos nuevos, explicados sin asumir conocimientos avanzados.
- Las decisiones tomadas, con las alternativas descartadas y el motivo.
- Cómo probarlo en su PC.

Criterios de calidad:

- Tareas chicas: una funcionalidad por PR. Nunca generar la aplicación entera de una vez.
- Sin dependencias, capas ni patrones que el MVP no necesite. Si una dependencia nueva hace falta, se puede agregar, pero justificándola en el PR.
- Código legible, con nombres descriptivos y tests para cada funcionalidad nueva.
- Todo en español: respuestas, nombres, comentarios, docstrings, commits y PRs.

Frená y preguntá **solo** en estos casos:

- Borrar archivos o datos que no sean generados, o cualquier operación que no se pueda deshacer (`git push --force`, `git reset --hard` sobre trabajo ajeno, etc.).
- Manejar claves, contraseñas o cualquier dato secreto.
- Cambiar el alcance del MVP o una regla del dominio.

## Stack

- Backend: Python, FastAPI, Pydantic, Uvicorn.
- Base de datos: SQLite con SQL escrito a mano (sin ORM), usando el módulo `sqlite3`.
- Frontend: HTML, CSS y JavaScript sin frameworks, servido por FastAPI como archivos estáticos.
- Tests: pytest (y `TestClient` de FastAPI para la API, que necesita `httpx`).
- Entorno: Windows, PowerShell, VS Code, entorno virtual en `.venv`.

## Arquitectura

```
app/
├── main.py                 # app FastAPI: registra los routers y monta el frontend
├── routes/                 # endpoints: health, plan (GET /api/plan), llaves (GET /api/llaves), evaluacion (POST /api/evaluacion)
│   └── dependencias.py     # obtener_plan(), reemplazable en los tests
├── schemas/                # modelos Pydantic de la API
├── static/                 # frontend: index.html, estilos.css, app.js
├── services/
│   ├── plan.py             # Materia y validación del plan (ciclos, referencias)
│   ├── correlativas.py     # lógica pura: evaluar_plan()
│   └── llaves.py           # lógica pura: calcular_llaves()
└── database/
    ├── schema.sql          # tablas materias y correlativas
    └── db.py               # único módulo con SQL
data/tup_plan2024.json      # fuente de verdad del plan (Ordenanza 2019/2023 CS UTN)
scripts/cargar_plan.py      # genera planificador.db desde el JSON
.github/workflows/tests.yml # corre pytest en GitHub Actions
.python-version             # versión de Python: la leen Vercel y GitHub Actions
tests/
```

Principios:

- `services/` contiene funciones puras: no leen la base, archivos ni HTTP.
- La base `planificador.db` es un archivo generado y está en `.gitignore`. La fuente de verdad es el JSON. La app la regenera al arrancar (`lifespan` en `main.py`); `scripts/cargar_plan.py` hace lo mismo a mano. Su ruta se puede cambiar con la variable de entorno `PLANIFICADOR_DB` (en Vercel: `/tmp/planificador.db`).
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
4. API: `POST /api/evaluacion` recibe `{"estados": {"1": "aprobada"}}` y devuelve `evaluar_plan()`. Esquemas Pydantic, `/health` en `routes/` y tests con `TestClient`.
5. Frontend: `GET /api/plan`, plan por año servido por FastAPI, selector de estado por materia guardado en `localStorage` y resultado de `/api/evaluacion` (cursable, rendible, bloqueada y qué falta).
6. Materias llave: `calcular_llaves()` y `GET /api/llaves` dicen cuántas materias desbloquea cada una, directamente y en total. Cada tarjeta lo muestra.
7. GitHub Actions (`.github/workflows/tests.yml`): `pytest` corre en cada PR y en cada push a `main`, en Windows y en Linux.
8. README con captura, cómo correrlo, API y decisiones de diseño.
9. Diseño visual: colores con variables CSS, modo oscuro, resumen con barra de progreso, leyenda y contraste WCAG AA.

Siguiente:

10. Deploy y lanzamiento en Vercel. Ya resuelto: la base se genera sola al arrancar, su ruta se configura con `PLANIFICADOR_DB`, la versión de Python está en `.python-version` y el README explica el deploy. Falta que Agustín cree el proyecto en Vercel y sumar el link de la demo al README.

Queda fuera del MVP: login, cálculo de cuatrimestres restantes, equivalencias, Trabajo Final Integrador (se agrega como caso especial más adelante), tabla `carreras` (se agrega cuando haya una segunda carrera) e IA.
