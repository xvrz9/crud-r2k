// Envía los formularios a las rutas JSON de la aplicación y muestra el resultado.

function numero(texto) {
  // "$25.000" -> 25000. Si no es un número se manda tal cual y el servidor lo rechaza.
  const limpio = texto.replace(/[$.\s]/g, "");
  return /^-?\d+$/.test(limpio) ? Number(limpio) : texto;
}

function pesos(valor) {
  return "$" + valor.toLocaleString("es-CO");
}

function mostrar(texto, esError) {
  const caja = document.getElementById("mensaje");
  caja.textContent = texto;
  caja.className = esError ? "mensaje error" : "mensaje";
  caja.hidden = false;
  window.scrollTo(0, 0);
}

function leerFormulario(form) {
  const datos = {};
  for (const campo of form.elements) {
    if (!campo.name) continue;
    datos[campo.name] = campo.hasAttribute("data-numero") ? numero(campo.value) : campo.value;
  }
  if (form.dataset.tipo === "venta") {
    return { items: [{ id_producto: datos.id_producto, cantidad: datos.cantidad }] };
  }
  return datos;
}

async function enviar(form) {
  if (form.dataset.confirmar && !confirm(form.dataset.confirmar)) return;
  const metodo = form.dataset.metodo;
  let respuesta;
  let json;
  try {
    respuesta = await fetch(form.dataset.url, {
      method: metodo,
      headers: { "Content-Type": "application/json" },
      body: metodo === "DELETE" ? null : JSON.stringify(leerFormulario(form)),
    });
    json = await respuesta.json();
  } catch {
    mostrar("No se pudo guardar. Revise que la ventana negra de R2K siga abierta.", true);
    return;
  }
  if (!respuesta.ok) {
    mostrar(json.error, true);
    return;
  }
  let texto = form.dataset.ok || "Listo";
  if (json.total !== undefined) texto += ". Total: " + pesos(json.total);
  // El mensaje se muestra después de recargar la página con los datos nuevos
  sessionStorage.setItem("mensaje", texto);
  location.href = form.dataset.volver || location.pathname;
}

document.querySelectorAll("form[data-url]").forEach((form) => {
  form.addEventListener("submit", (evento) => {
    evento.preventDefault();
    enviar(form);
  });
});

const pendiente = sessionStorage.getItem("mensaje");
if (pendiente) {
  sessionStorage.removeItem("mensaje");
  mostrar(pendiente, false);
}
