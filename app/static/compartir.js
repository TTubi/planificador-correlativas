// Convierte el progreso del alumno en un link para compartir, y al revés.
//
// El progreso va en el "fragmento" del link, lo que está después del #:
//     https://.../#progreso=1a8,2a,3r
// Se lee como: la 1 aprobada con nota 8, la 2 aprobada sin nota, la 3 regular.
//
// El navegador nunca le manda el fragmento al servidor, así que el backend
// sigue sin ver datos del alumno.
//
// Son funciones puras: no tocan la página ni localStorage, y se pueden
// probar con `node --test "tests/js/*.test.mjs"`.

export const PARAMETRO = "progreso";
const LETRA_POR_ESTADO = { regular: "r", aprobada: "a" };
const ESTADO_POR_LETRA = { r: "regular", a: "aprobada" };
const NOTAS_POSIBLES = [6, 7, 8, 9, 10];

// { 1: "aprobada", 3: "regular" } y { 1: 8 } → "1a8,3r"
export function codificarProgreso(estados, notas) {
    return Object.keys(estados)
        .map(Number)
        .sort((a, b) => a - b)
        .map((numero) => {
            const letra = LETRA_POR_ESTADO[estados[numero]];
            const nota = estados[numero] === "aprobada" ? (notas[numero] ?? "") : "";
            return `${numero}${letra}${nota}`;
        })
        .join(",");
}

// "1a8,3r" → { estados: { 1: "aprobada", 3: "regular" }, notas: { 1: 8 } }
//
// El texto viene de un link, o sea de afuera: puede estar cortado, editado
// a mano o ser de una versión vieja del plan. Las partes que no tienen
// sentido se descartan una por una, igual que al leer localStorage.
export function decodificarProgreso(texto, numerosValidos) {
    const estados = {};
    const notas = {};
    for (const parte of texto.split(",")) {
        const coincidencia = /^(\d+)([ra])(\d+)?$/.exec(parte.trim());
        if (!coincidencia) {
            continue;
        }
        const numero = Number(coincidencia[1]);
        const estado = ESTADO_POR_LETRA[coincidencia[2]];
        if (!numerosValidos.has(numero)) {
            continue;
        }
        estados[numero] = estado;
        const nota = Number(coincidencia[3]);
        if (estado === "aprobada" && NOTAS_POSIBLES.includes(nota)) {
            notas[numero] = nota;
        }
    }
    return { estados, notas };
}

// Arma el link completo a partir de la dirección actual de la página.
export function linkDeProgreso(ubicacion, estados, notas) {
    return `${ubicacion.origin}${ubicacion.pathname}#${PARAMETRO}=${codificarProgreso(estados, notas)}`;
}

// Si el fragmento ("#progreso=...") trae un progreso, lo devuelve.
// Si no hay ningún progreso en el link, devuelve null.
export function leerProgresoDeLink(fragmento, numerosValidos) {
    const parametros = new URLSearchParams(fragmento.replace(/^#/, ""));
    if (!parametros.has(PARAMETRO)) {
        return null;
    }
    return decodificarProgreso(parametros.get(PARAMETRO), numerosValidos);
}
