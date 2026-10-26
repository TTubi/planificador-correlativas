// Tests del módulo que arma y lee los links para compartir el progreso.
// Usan el runner que trae Node (sin instalar nada): node --test "tests/js/*.test.mjs"

import assert from "node:assert/strict";
import { test } from "node:test";

import {
    codificarProgreso,
    decodificarProgreso,
    leerProgresoDeLink,
    linkDeProgreso,
} from "../../app/static/compartir.js";

const PLAN = new Set(Array.from({ length: 17 }, (_, i) => i + 1));

test("codifica estados y notas ordenados por número", () => {
    const estados = { 3: "regular", 1: "aprobada", 2: "aprobada" };
    assert.equal(codificarProgreso(estados, { 1: 8 }), "1a8,2a,3r");
});

test("un alumno sin progreso da un texto vacío", () => {
    assert.equal(codificarProgreso({}, {}), "");
});

test("ordena los números como números y no como texto", () => {
    // Como texto, "10" iría antes que "2".
    assert.equal(codificarProgreso({ 10: "regular", 2: "regular" }, {}), "2r,10r");
});

test("decodificar deshace lo que hizo codificar", () => {
    const estados = { 1: "aprobada", 2: "aprobada", 3: "regular", 17: "aprobada" };
    const notas = { 1: 8, 17: 10 };
    assert.deepEqual(decodificarProgreso(codificarProgreso(estados, notas), PLAN), { estados, notas });
});

test("descarta las partes que no tienen sentido y conserva el resto", () => {
    const resultado = decodificarProgreso("1a8,99a7,2x,3r9,4a5,basura,,5a", PLAN);
    assert.deepEqual(resultado, {
        // 99 no existe; "2x" no es un estado; la nota de una regular y
        // una nota 5 se ignoran, pero la materia se conserva.
        estados: { 1: "aprobada", 3: "regular", 4: "aprobada", 5: "aprobada" },
        notas: { 1: 8 },
    });
});

test("un texto vacío es un progreso vacío", () => {
    assert.deepEqual(decodificarProgreso("", PLAN), { estados: {}, notas: {} });
});

test("arma el link con el progreso después del #", () => {
    const ubicacion = { origin: "https://planificador-correlativas.vercel.app", pathname: "/" };
    assert.equal(
        linkDeProgreso(ubicacion, { 1: "aprobada" }, { 1: 9 }),
        "https://planificador-correlativas.vercel.app/#progreso=1a9",
    );
});

test("lee el progreso desde el fragmento del link", () => {
    assert.deepEqual(leerProgresoDeLink("#progreso=1a9,2r", PLAN), {
        estados: { 1: "aprobada", 2: "regular" },
        notas: { 1: 9 },
    });
});

test("si el link no trae progreso devuelve null", () => {
    assert.equal(leerProgresoDeLink("", PLAN), null);
    assert.equal(leerProgresoDeLink("#otra-cosa", PLAN), null);
});

test("un link con progreso vacío se distingue de un link sin progreso", () => {
    assert.deepEqual(leerProgresoDeLink("#progreso=", PLAN), { estados: {}, notas: {} });
});
