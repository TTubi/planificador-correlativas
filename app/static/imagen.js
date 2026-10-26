// Dibuja la imagen con el progreso del alumno para publicar en LinkedIn.
//
// Usa <canvas>, que viene en todos los navegadores: no hace falta ninguna
// librería ni que el servidor genere la imagen. El resultado es un PNG
// cuadrado de 1080×1080, el tamaño que mejor se ve en el feed de LinkedIn.

const LADO = 1080;
const CENTRO = LADO / 2;
const FUENTE = 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif';

// datos: { porcentaje, aprobadas, total, titular, promedio }
// `promedio` es un texto ya formateado ("8,5") o null para no mostrarlo.
// Devuelve una promesa con la imagen como Blob (un archivo en memoria).
export function crearImagenProgreso(datos) {
    const lienzo = document.createElement("canvas");
    lienzo.width = LADO;
    lienzo.height = LADO;
    const ctx = lienzo.getContext("2d");

    dibujarFondo(ctx);
    dibujarTextos(ctx, datos);
    dibujarAnillo(ctx, datos.porcentaje);

    return new Promise((resolver) => lienzo.toBlob(resolver, "image/png"));
}

function dibujarFondo(ctx) {
    const degradado = ctx.createLinearGradient(0, 0, LADO, LADO);
    degradado.addColorStop(0, "#4c5fd5");
    degradado.addColorStop(1, "#27307f");
    ctx.fillStyle = degradado;
    ctx.fillRect(0, 0, LADO, LADO);
}

function texto(ctx, contenido, y, { tamano, peso = 400, opacidad = 1 }) {
    ctx.font = `${peso} ${tamano}px ${FUENTE}`;
    ctx.fillStyle = `rgba(255, 255, 255, ${opacidad})`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(contenido, CENTRO, y);
}

function dibujarTextos(ctx, { porcentaje, aprobadas, total, titular, promedio }) {
    texto(ctx, "TECNICATURA UNIVERSITARIA EN PROGRAMACIÓN · UTN", 105, { tamano: 28, peso: 600, opacidad: 0.75 });
    texto(ctx, titular, 190, { tamano: 70, peso: 800 });

    // El porcentaje va en el centro del anillo.
    texto(ctx, `${porcentaje}%`, 505, { tamano: 150, peso: 800 });
    texto(ctx, "de la carrera", 600, { tamano: 36, opacidad: 0.85 });

    texto(ctx, `${aprobadas} de ${total} materias aprobadas`, 865, { tamano: 44, peso: 600 });
    if (promedio) {
        texto(ctx, `Promedio: ${promedio} ⭐`, 925, { tamano: 38, opacidad: 0.9 });
    }
    texto(ctx, "planificador-correlativas.vercel.app · creado por Agustín Singh", 1025, { tamano: 26, opacidad: 0.7 });
}

function dibujarAnillo(ctx, porcentaje) {
    const centroY = 535;
    const radio = 230;
    ctx.lineWidth = 42;
    ctx.lineCap = "round";

    // Anillo de fondo: el 100 %.
    ctx.strokeStyle = "rgba(255, 255, 255, 0.18)";
    ctx.beginPath();
    ctx.arc(CENTRO, centroY, radio, 0, 2 * Math.PI);
    ctx.stroke();

    // Arco del avance. Los ángulos van en radianes y 0 es "las 3 en punto",
    // por eso se arranca en -90° (las 12) y se avanza en sentido horario.
    if (porcentaje > 0) {
        const inicio = -Math.PI / 2;
        ctx.strokeStyle = "#ffffff";
        ctx.beginPath();
        ctx.arc(CENTRO, centroY, radio, inicio, inicio + (2 * Math.PI * porcentaje) / 100);
        ctx.stroke();
    }
}
