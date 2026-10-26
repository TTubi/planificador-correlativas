-- Esquema de la base del plan de estudios.
-- Las restricciones (CHECK, FOREIGN KEY) repiten a propósito algunas
-- validaciones de Python: si algún día alguien carga datos por otro camino,
-- la base igual rechaza lo que no tiene sentido.

CREATE TABLE materias (
    numero INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    nivel  INTEGER NOT NULL CHECK (nivel IN (1, 2))
);

-- Una fila por cada requisito. Por ejemplo, (9, 5, 'regular') significa:
-- "para cursar Programación III hay que tener Programación II regular".
CREATE TABLE correlativas (
    materia  INTEGER NOT NULL REFERENCES materias (numero),
    requiere INTEGER NOT NULL REFERENCES materias (numero),
    tipo     TEXT    NOT NULL CHECK (tipo IN ('regular', 'aprobada')),
    PRIMARY KEY (materia, requiere),
    CHECK (materia <> requiere)
);
