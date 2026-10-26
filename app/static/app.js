// Muestra el plan por año, deja marcar el estado de cada materia y
// consulta a la API qué se puede cursar y rendir.
//
// El cálculo de correlativas NO se hace acá: lo hace el backend en
// POST /api/evaluacion, que ya tiene tests. El navegador solo guarda el
// estado del alumno y muestra el resultado.

const NOMBRES_NIVEL = { 1: "Primer año", 2: "Segundo año" };
const OPCIONES_ESTADO = [
    ["pendiente", "Pendiente"],
    ["regular", "Regular"],
    ["aprobada", "Aprobada"],
];
const CLAVE_GUARDADO = "planificador-correlativas:estados";

// Estado del alumno: número de materia → "regular" o "aprobada".
// Las pendientes no se guardan, igual que espera la API.
let estados = {};
let nombrePorNumero = {};
// Número del último pedido de evaluación. Sirve para descartar respuestas
// viejas si el alumno cambia varias materias rápido.
let ultimoPedido = 0;

// --- Guardado en el navegador -----------------------------------------------

// localStorage solo guarda texto, por eso se usa JSON.stringify / JSON.parse.
// Se filtra lo leído: si el plan cambió o alguien editó el dato a mano,
// no queremos mandarle a la API materias o estados que no existen.
function leerEstadosGuardados(numerosValidos) {
    let guardado;
    try {
        guardado = JSON.parse(localStorage.getItem(CLAVE_GUARDADO)) ?? {};
    } catch {
        return {};
    }
    const limpios = {};
    for (const [numero, estado] of Object.entries(guardado)) {
        if (numerosValidos.has(Number(numero)) && (estado === "regular" || estado === "aprobada")) {
            limpios[numero] = estado;
        }
    }
    return limpios;
}

function guardarEstados() {
    try {
        localStorage.setItem(CLAVE_GUARDADO, JSON.stringify(estados));
    } catch {
        // Puede fallar en modo privado o si el navegador bloquea el guardado.
        // La página sigue funcionando; solo no recuerda el progreso.
    }
}

// --- Pedidos a la API -------------------------------------------------------

async function pedirJson(url, opciones) {
    const respuesta = await fetch(url, opciones);
    if (!respuesta.ok) {
        throw new Error(`el servidor respondió ${respuesta.status}`);
    }
    return respuesta.json();
}

async function evaluar() {
    const pedido = ++ultimoPedido;
    try {
        const datos = await pedirJson("/api/evaluacion", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ estados }),
        });
        if (pedido === ultimoPedido) {
            mostrarEvaluacion(datos.materias);
        }
    } catch (error) {
        if (pedido === ultimoPedido) {
            mostrarMensaje(document.getElementById("resumen"), `No se pudo evaluar el plan (${error.message}).`);
        }
    }
}

// --- Dibujo del plan --------------------------------------------------------

// Arma el texto de requisitos, por ejemplo:
// "Regulares: Programación I, Matemática · Aprobadas: Programación I"
function textoRequisitos(materia) {
    const partes = [];
    if (materia.regulares.length > 0) {
        partes.push("Regulares: " + materia.regulares.map((n) => nombrePorNumero[n]).join(", "));
    }
    if (materia.aprobadas.length > 0) {
        partes.push("Aprobadas: " + materia.aprobadas.map((n) => nombrePorNumero[n]).join(", "));
    }
    return partes.length > 0 ? partes.join(" · ") : "Sin correlativas";
}

function crearSelectorEstado(materia) {
    const selector = document.createElement("select");
    selector.setAttribute("aria-label", `Estado de ${materia.nombre}`);
    for (const [valor, texto] of OPCIONES_ESTADO) {
        selector.append(new Option(texto, valor));
    }
    selector.value = estados[materia.numero] ?? "pendiente";

    selector.addEventListener("change", () => {
        if (selector.value === "pendiente") {
            delete estados[materia.numero];
        } else {
            estados[materia.numero] = selector.value;
        }
        guardarEstados();
        evaluar();
    });
    return selector;
}

function crearTarjeta(materia) {
    const tarjeta = document.createElement("li");
    tarjeta.className = "materia";
    tarjeta.dataset.numero = materia.numero;

    const titulo = document.createElement("h3");
    const numero = document.createElement("span");
    numero.className = "numero";
    numero.textContent = materia.numero + ".";
    titulo.append(numero, materia.nombre);

    const requisitos = document.createElement("p");
    requisitos.className = "requisitos";
    requisitos.textContent = textoRequisitos(materia);

    // Se completa cuando llega la respuesta de /api/evaluacion.
    const resultado = document.createElement("p");
    resultado.className = "resultado";

    tarjeta.append(titulo, crearSelectorEstado(materia), requisitos, resultado);
    return tarjeta;
}

function mostrarPlan(materias) {
    const contenedor = document.getElementById("plan");
    contenedor.replaceChildren();

    const niveles = [...new Set(materias.map((m) => m.nivel))].sort();
    for (const nivel of niveles) {
        const seccion = document.createElement("section");
        seccion.className = "nivel";

        const titulo = document.createElement("h2");
        titulo.textContent = NOMBRES_NIVEL[nivel] ?? `Año ${nivel}`;

        const lista = document.createElement("ul");
        lista.className = "materias";
        for (const materia of materias.filter((m) => m.nivel === nivel)) {
            lista.append(crearTarjeta(materia));
        }

        seccion.append(titulo, lista);
        contenedor.append(seccion);
    }
}

// --- Dibujo de la evaluación ------------------------------------------------

function listarFaltantes(faltantes) {
    return faltantes.map((f) => `${f.nombre} (${f.se_necesita})`).join(", ");
}

// Traduce una evaluación de la API a una clase CSS y un texto para el alumno.
function situacion(evaluacion) {
    if (evaluacion.estado === "aprobada") {
        return { clase: "aprobada", texto: "Aprobada" };
    }
    if (evaluacion.estado === "regular") {
        return evaluacion.puede_rendir
            ? { clase: "rendible", texto: "Podés rendirla" }
            : { clase: "bloqueada", texto: "Para rendir falta: " + listarFaltantes(evaluacion.faltan_para_rendir) };
    }
    return evaluacion.puede_cursar
        ? { clase: "cursable", texto: "Podés cursarla" }
        : { clase: "bloqueada", texto: "Para cursar falta: " + listarFaltantes(evaluacion.faltan_para_cursar) };
}

function mostrarEvaluacion(evaluaciones) {
    for (const evaluacion of evaluaciones) {
        const tarjeta = document.querySelector(`.materia[data-numero="${evaluacion.numero}"]`);
        const { clase, texto } = situacion(evaluacion);
        tarjeta.className = `materia ${clase}`;
        tarjeta.querySelector(".resultado").textContent = texto;
    }

    const cuantas = (condicion) => evaluaciones.filter(condicion).length;
    document.getElementById("resumen").textContent =
        `Podés cursar ${cuantas((e) => e.puede_cursar)} · ` +
        `Podés rendir ${cuantas((e) => e.puede_rendir)} · ` +
        `Aprobadas ${cuantas((e) => e.estado === "aprobada")} de ${evaluaciones.length}`;
}

function mostrarMensaje(contenedor, texto) {
    const mensaje = document.createElement("p");
    mensaje.className = "mensaje error";
    mensaje.textContent = texto;
    contenedor.replaceChildren(mensaje);
}

// --- Inicio -----------------------------------------------------------------

async function iniciar() {
    try {
        const { materias } = await pedirJson("/api/plan");
        for (const materia of materias) {
            nombrePorNumero[materia.numero] = materia.nombre;
        }
        estados = leerEstadosGuardados(new Set(materias.map((m) => m.numero)));
        mostrarPlan(materias);
        await evaluar();
    } catch (error) {
        mostrarMensaje(document.getElementById("plan"), `No se pudo cargar el plan (${error.message}).`);
    }
}

iniciar();
