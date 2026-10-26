// Muestra el plan de estudios agrupado por año.
// Por ahora solo lee GET /api/plan. Marcar estados y evaluar viene después.

const NOMBRES_NIVEL = { 1: "Primer año", 2: "Segundo año" };

async function cargarPlan() {
    const respuesta = await fetch("/api/plan");
    if (!respuesta.ok) {
        throw new Error(`El servidor respondió ${respuesta.status}`);
    }
    const datos = await respuesta.json();
    return datos.materias;
}

// Arma el texto de requisitos, por ejemplo:
// "Regulares: Programación I, Matemática · Aprobadas: Programación I"
function textoRequisitos(materia, nombrePorNumero) {
    const partes = [];
    if (materia.regulares.length > 0) {
        partes.push("Regulares: " + materia.regulares.map((n) => nombrePorNumero[n]).join(", "));
    }
    if (materia.aprobadas.length > 0) {
        partes.push("Aprobadas: " + materia.aprobadas.map((n) => nombrePorNumero[n]).join(", "));
    }
    return partes.length > 0 ? partes.join(" · ") : "Sin correlativas";
}

function crearTarjeta(materia, nombrePorNumero) {
    const tarjeta = document.createElement("li");
    tarjeta.className = "materia";

    const titulo = document.createElement("h3");
    const numero = document.createElement("span");
    numero.className = "numero";
    numero.textContent = materia.numero + ".";
    titulo.append(numero, materia.nombre);

    const requisitos = document.createElement("p");
    requisitos.className = "requisitos";
    requisitos.textContent = textoRequisitos(materia, nombrePorNumero);

    tarjeta.append(titulo, requisitos);
    return tarjeta;
}

function mostrarPlan(materias) {
    const contenedor = document.getElementById("plan");
    contenedor.replaceChildren();

    const nombrePorNumero = {};
    for (const materia of materias) {
        nombrePorNumero[materia.numero] = materia.nombre;
    }

    const niveles = [...new Set(materias.map((m) => m.nivel))].sort();
    for (const nivel of niveles) {
        const seccion = document.createElement("section");
        seccion.className = "nivel";

        const titulo = document.createElement("h2");
        titulo.textContent = NOMBRES_NIVEL[nivel] ?? `Año ${nivel}`;

        const lista = document.createElement("ul");
        lista.className = "materias";
        for (const materia of materias.filter((m) => m.nivel === nivel)) {
            lista.append(crearTarjeta(materia, nombrePorNumero));
        }

        seccion.append(titulo, lista);
        contenedor.append(seccion);
    }
}

function mostrarError(error) {
    const contenedor = document.getElementById("plan");
    const mensaje = document.createElement("p");
    mensaje.className = "mensaje error";
    mensaje.textContent = `No se pudo cargar el plan (${error.message}).`;
    contenedor.replaceChildren(mensaje);
}

cargarPlan().then(mostrarPlan).catch(mostrarError);
