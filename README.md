# Planificador de Correlativas

[![Tests](https://github.com/TTubi/planificador-correlativas/actions/workflows/tests.yml/badge.svg)](https://github.com/TTubi/planificador-correlativas/actions/workflows/tests.yml)

App web para estudiantes de la **Tecnicatura Universitaria en Programación (UTN, plan 2024)**. Marcás qué materias tenés regulares o aprobadas y te muestra qué podés cursar, qué podés rendir, qué está bloqueado y qué te falta para desbloquearlo.

**Demo online:** <https://planificador-correlativas.vercel.app/>

![Captura del planificador](docs/captura.png)

## Qué hace

- **Plan por año** con las correlativas de cada materia.
- **Marcás tu estado** en cada materia: pendiente, regular o aprobada.
- **Te dice qué podés hacer:**
  - 🟩 Podés cursarla.
  - 🟦 Podés rendirla.
  - 🟧 Bloqueada, con la lista exacta de lo que falta. Por ejemplo: "Para cursar falta: Programación II (regular)".
- **Tu avance en la carrera:** el porcentaje completado (por cantidad de materias aprobadas) y tu promedio. La nota de cada materia aprobada es opcional, y el promedio es sin aplazos: solo cuenta las notas con las que aprobaste.
- **Feedback motivador:** un mensaje según cuánto te falta y tu promedio. Por ejemplo: "¡Te faltan solo 2 materias! Metele un último esfuerzo 💪 Y con un promedio de 8,67, ¡excelente!"
- **Compartí tu progreso:** un botón genera un link con tu avance (en el celular abre el menú para mandarlo por WhatsApp). Quien lo abre lo ve en modo solo lectura, sin que se modifique su propio progreso.
- **Materias llave:** cuántas materias desbloquea cada una, directamente y en cadena. Por ejemplo, Programación I y Matemática desbloquean 10 de las 17.
- **Sin cuentas ni login:** tu progreso se guarda en tu navegador (`localStorage`). El servidor no guarda datos personales.

## Reglas de correlatividad

Según la Ordenanza N.º 2019/2023 del Consejo Superior de la UTN, cada materia tiene dos listas de correlativas:

- **Para cursar** una materia, sus correlativas `regulares` tienen que estar al menos regularizadas y sus correlativas `aprobadas`, aprobadas.
- **Para rendir** una materia, tiene que estar regularizada y todas sus correlativas (las dos listas) tienen que estar aprobadas.

El plan completo está en [`data/tup_plan2024.json`](data/tup_plan2024.json).

## Stack

| Parte | Tecnología |
|---|---|
| Backend | Python 3.13, FastAPI, Pydantic, Uvicorn |
| Base de datos | SQLite con SQL escrito a mano (módulo `sqlite3`, sin ORM) |
| Frontend | HTML, CSS y JavaScript sin frameworks |
| Tests | pytest y `TestClient` de FastAPI |
| CI | GitHub Actions (Windows y Linux) |

## Cómo correrlo

Necesitás Python 3.13, la versión fijada en [`.python-version`](.python-version). También funciona desde 3.10.

**Windows (PowerShell):**

```powershell
git clone https://github.com/TTubi/planificador-correlativas.git
cd planificador-correlativas
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Linux o macOS:**

```bash
git clone https://github.com/TTubi/planificador-correlativas.git
cd planificador-correlativas
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Después abrí <http://127.0.0.1:8000/>.

Al arrancar, la app valida el JSON del plan y genera la base `planificador.db`. Si el plan tiene errores, no arranca y los muestra. `python -m scripts.cargar_plan` hace lo mismo a mano, y sirve para validar el JSON sin levantar el servidor.

### Tests

```bash
python -m pytest                      # backend (Python)
node --test "tests/js/*.test.mjs"     # lógica del frontend (JavaScript)
```

Los tests no necesitan la base generada: los de la API arman una base temporal propia. Los de JavaScript usan el runner que trae Node 22 y no necesitan instalar paquetes.

### Configuración

| Variable de entorno | Para qué sirve | Valor por defecto |
|---|---|---|
| `PLANIFICADOR_DB` | Ruta del archivo de la base SQLite que se genera al arrancar. | `planificador.db` en la raíz del proyecto |

Localmente no hace falta definirla. Existe para los hostings donde la carpeta del proyecto es de solo lectura.

## Deploy en Vercel

Vercel detecta la app FastAPI en `app/main.py` y la publica como una función serverless, así que no hace falta un `vercel.json`. Los archivos de `app/static/` se sirven desde su CDN.

1. En [vercel.com](https://vercel.com), entrá con tu cuenta de GitHub y elegí **Add New → Project**.
2. Importá el repo `planificador-correlativas`. Vercel reconoce el preset **FastAPI**: no cambies los comandos de build ni la carpeta raíz.
3. En **Environment Variables**, agregá:

   | Nombre | Valor |
   |---|---|
   | `PLANIFICADOR_DB` | `/tmp/planificador.db` |

4. Tocá **Deploy**. En uno o dos minutos te da la URL pública. La demo de este repo está en <https://planificador-correlativas.vercel.app/>.

Desde ahí, cada push a `main` publica una versión nueva, y cada PR recibe su propia URL de vista previa.

Por qué hace falta `PLANIFICADOR_DB`: en Vercel el código queda en una carpeta de **solo lectura**, y el único lugar donde se puede escribir es `/tmp`. Sin la variable, la app intenta crear la base junto al código, falla al arrancar y el deploy queda caído.

Detalles a tener en cuenta:

- **Versión de Python:** Vercel la toma de `.python-version` (3.13). GitHub Actions usa el mismo archivo, así que el deploy y los tests corren con la misma versión.
- **La base vive en `/tmp`, que es temporal:** cada instancia de la función la regenera al arrancar (el `lifespan` de `main.py`). No es un problema, porque la base solo contiene el plan, que sale del JSON. El progreso de cada alumno nunca pasa por el servidor.
- **Arranque en frío:** si la app no recibió visitas por un rato, el primer pedido tarda un poco más, porque Vercel crea una instancia nueva y regenera la base. Son milisegundos para la base, más el arranque de Python.

## API

La documentación interactiva está en <http://127.0.0.1:8000/docs>.

| Método | Ruta | Qué hace |
|---|---|---|
| `GET` | `/api/plan` | Materias del plan con su año y sus correlativas. |
| `GET` | `/api/llaves` | Qué materias desbloquea cada una, de la más llave a la menos. |
| `POST` | `/api/evaluacion` | Recibe el estado del alumno (y opcionalmente sus notas) y devuelve qué puede cursar y rendir, qué le falta, el porcentaje de la carrera y el promedio. |
| `GET` | `/health` | Verifica que el servidor esté funcionando. |

Ejemplo:

```http
POST /api/evaluacion
Content-Type: application/json

{
  "estados": { "1": "aprobada", "2": "aprobada", "3": "regular" },
  "notas": { "1": 8, "2": 7 }
}
```

Las materias que no aparecen se consideran pendientes. `notas` es opcional: solo admite materias aprobadas y notas enteras del 6 al 10. Una materia inexistente, un estado inválido o una nota que no cumple esas reglas devuelven `422`.

La respuesta incluye, además de cada materia, el progreso y un mensaje de feedback:

```json
"progreso": { "aprobadas": 2, "total": 17, "porcentaje": 11, "promedio": 7.5, "notas_cargadas": 2 },
"mensaje": "Vas sumando: ya tenés el 11% de la carrera. ¡Paso a paso! Tu promedio es 7,5, ¡muy bien!"
```

## Estructura

```
app/
├── main.py              # crea la app, registra los routers y sirve el frontend
├── routes/              # endpoints HTTP
├── schemas/             # modelos Pydantic: el contrato de la API
├── services/            # lógica pura: correlativas, materias llave, progreso, feedback y validación del plan
├── database/            # esquema SQLite y el único módulo con SQL
└── static/              # frontend: index.html, estilos.css, app.js y compartir.js
data/tup_plan2024.json   # fuente de verdad del plan de estudios
scripts/cargar_plan.py   # valida el plan y genera la base
tests/                   # tests de Python, y tests/js/ con los de JavaScript
.python-version          # versión de Python (la usan Vercel y GitHub Actions)
```

## Decisiones de diseño

- **La lógica es pura.** `services/` recibe datos y devuelve resultados, sin leer la base, archivos ni HTTP. Así se testea rápido, y la misma función sirve para la API o para un script.
- **El JSON es la fuente de verdad.** La base SQLite es un archivo generado y no se versiona. Al cargarla, el plan se valida: referencias a materias inexistentes, nombres repetidos y correlativas circulares (con búsqueda en profundidad sobre el grafo de correlativas).
- **SQL a mano, en un solo módulo.** Sin ORM, para entender qué pasa con la base. Las restricciones (`CHECK`, `FOREIGN KEY`) repiten algunas validaciones de Python, así la base tampoco acepta datos sin sentido.
- **Las reglas viven en un solo lugar.** El frontend no recalcula correlativas: le pregunta a la API. Así no hay dos implementaciones que puedan diferir.
- **Sin datos personales en el servidor.** El progreso queda en el navegador del alumno. Al compartirlo, viaja en el fragmento del link (lo que va después del `#`), que el navegador nunca le manda al servidor.

## Fuera del alcance

Por ahora no incluye: promedio con aplazos, login, cálculo de cuatrimestres restantes, equivalencias, Trabajo Final Integrador y otras carreras.

## Autor

Proyecto de portfolio de Agustín ([TTubi](https://github.com/TTubi)), estudiante de la Tecnicatura Universitaria en Programación en la UTN Facultad Regional Rosario.
