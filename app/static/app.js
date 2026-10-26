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
const CLAVE_NOTAS = "planificador-correlativas:notas";
// En la UTN se aprueba con 6 o más. El backend valida lo mismo.
const NOTAS_POSIBLES = [6, 7, 8, 9, 10];

// Estado del alumno: número de materia → "regular" o "aprobada".
// Las pendientes no se guardan, igual que espera la API.
let estados = {};
// Número de materia aprobada → nota. Es opcional: puede no estar.
let notas = {};
let nombrePorNumero = {};
// Número de materia → qué materias desbloquea (de GET /api/llaves).
let llavePorNumero = {};
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

// Igual que con los estados, se descarta lo que no tiene sentido: una nota
// de una materia que no está aprobada o fuera de la escala haría que la API
// responda 422.
function leerNotasGuardadas() {
    let guardado;
    try {
        guardado = JSON.parse(localStorage.getItem(CLAVE_NOTAS)) ?? {};
    } catch {
        return {};
    }
    const limpias = {};
    for (const [numero, nota] of Object.entries(guardado)) {
        if (estados[numero] === "aprobada" && NOTAS_POSIBLES.includes(nota)) {
            limpias[numero] = nota;
        }
    }
    return limpias;
}

function guardar(clave, valor) {
    try {
        localStorage.setItem(clave, JSON.stringify(valor));
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
            body: JSON.stringify({ estados, notas }),
        });
        if (pedido === ultimoPedido) {
            mostrarEvaluacion(datos.materias, datos.progreso);
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

// Arma el texto de materia llave, por ejemplo:
// "Desbloquea 5 directamente · 10 en total"
function textoLlave(numero) {
    const llave = llavePorNumero[numero];
    const total = llave.desbloquea_en_total.length;
    if (total === 0) {
        return "No desbloquea otras materias";
    }
    return `Desbloquea ${llave.desbloquea_directamente.length} directamente · ${total} en total`;
}

function crearSelectorEstado(materia, selectorNota) {
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
        // La nota solo tiene sentido si la materia está aprobada.
        if (selector.value !== "aprobada") {
            delete notas[materia.numero];
            selectorNota.value = "";
        }
        selectorNota.hidden = selector.value !== "aprobada";
        guardar(CLAVE_GUARDADO, estados);
        guardar(CLAVE_NOTAS, notas);
        evaluar();
    });
    return selector;
}

function crearSelectorNota(materia) {
    const selector = document.createElement("select");
    selector.className = "nota";
    selector.setAttribute("aria-label", `Nota de ${materia.nombre}`);
    selector.append(new Option("Sin nota", ""));
    for (const nota of NOTAS_POSIBLES) {
        selector.append(new Option(`Nota ${nota}`, nota));
    }
    selector.value = notas[materia.numero] ?? "";
    selector.hidden = estados[materia.numero] !== "aprobada";

    selector.addEventListener("change", () => {
        if (selector.value === "") {
            delete notas[materia.numero];
        } else {
            notas[materia.numero] = Number(selector.value);
        }
        guardar(CLAVE_NOTAS, notas);
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

    const llave = document.createElement("p");
    llave.className = llavePorNumero[materia.numero].desbloquea_en_total.length > 0 ? "llave" : "llave ninguna";
    llave.textContent = textoLlave(materia.numero);
    // Al pasar el mouse se ven los nombres de todas las que desbloquea.
    llave.title = llavePorNumero[materia.numero].desbloquea_en_total.map((n) => nombrePorNumero[n]).join(", ");

    // Se completa cuando llega la respuesta de /api/evaluacion.
    const resultado = document.createElement("p");
    resultado.className = "resultado";

    const controles = document.createElement("div");
    controles.className = "controles";
    const selectorNota = crearSelectorNota(materia);
    controles.append(crearSelectorEstado(materia, selectorNota), selectorNota);

    tarjeta.append(titulo, controles, requisitos, llave, resultado);
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

function mostrarEvaluacion(evaluaciones, progreso) {
    for (const evaluacion of evaluaciones) {
        const tarjeta = document.querySelector(`.materia[data-numero="${evaluacion.numero}"]`);
        const { clase, texto } = situacion(evaluacion);
        tarjeta.className = `materia ${clase}`;
        tarjeta.querySelector(".resultado").textContent = texto;
    }

    mostrarResumen(evaluaciones, progreso);
}

// Un número grande con su descripción, por ejemplo "4 / materias para cursar".
function crearDato(clase, valor, descripcion) {
    const dato = document.createElement("div");
    dato.className = `dato ${clase}`;
    const numero = document.createElement("strong");
    numero.textContent = valor;
    const texto = document.createElement("span");
    texto.textContent = descripcion;
    dato.append(numero, texto);
    return dato;
}

// 7.5 → "7,5" y 8 → "8": formato argentino, sin ceros de más.
function formatearPromedio(promedio) {
    return promedio.toLocaleString("es-AR", { maximumFractionDigits: 2 });
}

function mostrarResumen(evaluaciones, progreso) {
    const cuantas = (condicion) => evaluaciones.filter(condicion).length;
    const { aprobadas, total, porcentaje, promedio } = progreso;

    // Barra de progreso de la carrera. Los atributos role y aria-* le dicen
    // a los lectores de pantalla qué representa y cuánto vale.
    const barra = document.createElement("div");
    barra.className = "progreso";
    barra.setAttribute("role", "progressbar");
    barra.setAttribute("aria-label", "Materias aprobadas");
    barra.setAttribute("aria-valuemin", 0);
    barra.setAttribute("aria-valuemax", total);
    barra.setAttribute("aria-valuenow", aprobadas);
    const relleno = document.createElement("div");
    relleno.style.width = `${(aprobadas / total) * 100}%`;
    barra.append(relleno);

    document.getElementById("resumen").replaceChildren(
        crearDato("cursable", cuantas((e) => e.puede_cursar), "para cursar"),
        crearDato("rendible", cuantas((e) => e.puede_rendir), "para rendir"),
        crearDato("aprobada", `${porcentaje}%`, `de la carrera · ${aprobadas}/${total} aprobadas`),
        promedio === null
            ? crearDato("promedio", "—", "promedio: cargá tus notas")
            : crearDato("promedio", formatearPromedio(promedio), "promedio"),
        barra,
    );
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
        // Los dos pedidos son independientes: se lanzan juntos y se espera a ambos.
        const [plan, llaves] = await Promise.all([pedirJson("/api/plan"), pedirJson("/api/llaves")]);
        const materias = plan.materias;
        for (const materia of materias) {
            nombrePorNumero[materia.numero] = materia.nombre;
        }
        for (const llave of llaves.materias) {
            llavePorNumero[llave.numero] = llave;
        }
        estados = leerEstadosGuardados(new Set(materias.map((m) => m.numero)));
        notas = leerNotasGuardadas();
        mostrarPlan(materias);
        await evaluar();
    } catch (error) {
        mostrarMensaje(document.getElementById("plan"), `No se pudo cargar el plan (${error.message}).`);
    }
}

iniciar();
