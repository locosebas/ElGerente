"use strict";

// --- Utilidades -------------------------------------------------------------

const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

const avisoEl = $("#aviso");

function mostrarError(msg) {
  avisoEl.textContent = msg;
  avisoEl.hidden = false;
}
function limpiarError() {
  avisoEl.hidden = true;
}

async function api(metodo, ruta, cuerpo) {
  let resp;
  try {
    resp = await fetch(ruta, {
      method: metodo,
      headers: cuerpo ? { "Content-Type": "application/json" } : undefined,
      body: cuerpo ? JSON.stringify(cuerpo) : undefined,
    });
  } catch (e) {
    throw new Error("No se pudo conectar con el servidor.");
  }
  const texto = await resp.text();
  const data = texto ? JSON.parse(texto) : null;
  if (!resp.ok) {
    const detalle = data && data.detail ? data.detail : `Error ${resp.status}`;
    throw new Error(typeof detalle === "string" ? detalle : JSON.stringify(detalle));
  }
  return data;
}

const money = (v) =>
  Number(v).toLocaleString("es-CO", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

function celdaSaldo(v) {
  const n = Number(v);
  const cls = n < 0 ? ' class="num neg"' : ' class="num"';
  return `<td${cls}>${money(v)}</td>`;
}

// --- Navegación por pestañas ----------------------------------------------

const TABS = ["balance", "libro", "terceros", "facturas", "contratos", "movimiento"];

function mostrarTab(nombre) {
  const tab = TABS.includes(nombre) ? nombre : "balance";
  TABS.forEach((t) => {
    $(`#tab-${t}`).hidden = t !== tab;
  });
  $$(".sidebar nav a").forEach((a) =>
    a.classList.toggle("active", a.dataset.tab === tab)
  );
  limpiarError();
  (CARGADORES[tab] || (() => {}))().catch((e) => mostrarError(e.message));
}

window.addEventListener("hashchange", () => mostrarTab(location.hash.replace("#/", "")));

// --- Balance --------------------------------------------------------------

async function cargarBalance() {
  const incluir = $("#incluir-interna").checked;
  const filas = await api("GET", `/balance?incluir_interna=${incluir}`);
  $("#balance-body").innerHTML = filas
    .map(
      (c) =>
        `<tr><td>${c.cuenta_codigo}</td><td>${c.cuenta_nombre}</td><td>${c.tipo}</td>${celdaSaldo(
          c.saldo
        )}</tr>`
    )
    .join("");
}
$("#incluir-interna").addEventListener("change", () =>
  cargarBalance().catch((e) => mostrarError(e.message))
);

// --- Libro diario --------------------------------------------------------

async function cargarLibro() {
  const libro = $("#filtro-libro").value;
  const asientos = await api("GET", `/asientos${libro ? `?libro=${libro}` : ""}`);
  $("#libro-body").innerHTML = asientos.length
    ? asientos.map(renderAsiento).join("")
    : '<p class="hint">Todavía no hay asientos.</p>';
}
$("#filtro-libro").addEventListener("change", () =>
  cargarLibro().catch((e) => mostrarError(e.message))
);

function renderAsiento(a) {
  const lineas = a.lineas
    .map(
      (l) =>
        `<tr><td>${l.cuenta_codigo} ${l.cuenta_nombre}</td><td class="num">${
          Number(l.debito) ? money(l.debito) : ""
        }</td><td class="num">${Number(l.credito) ? money(l.credito) : ""}</td></tr>`
    )
    .join("");
  const soporte = a.documento_soporte
    ? `<span class="tag">${a.documento_soporte}</span>`
    : "";
  return `<div class="asiento">
    <div class="cab">
      <strong>#${a.id}</strong> <span>${a.fecha}</span> <span>${a.descripcion}</span>
      <span class="tag">${a.origen}</span> <span class="tag">${a.libro}</span> ${soporte}
    </div>
    <table><tbody>${lineas}</tbody></table>
  </div>`;
}

// --- Terceros ----------------------------------------------------------

async function cargarTerceros() {
  const ts = await api("GET", "/terceros");
  $("#terceros-body").innerHTML = ts
    .map(
      (t) =>
        `<tr><td>${t.id}</td><td>${t.nombre}</td><td>${t.nit_cedula}</td><td>${t.tipo}</td></tr>`
    )
    .join("");
}

$("#form-tercero").addEventListener("submit", async (e) => {
  e.preventDefault();
  limpiarError();
  const f = e.target;
  try {
    await api("POST", "/terceros", {
      nombre: f.nombre.value,
      nit_cedula: f.nit_cedula.value,
      tipo: f.tipo.value,
    });
    f.reset();
    await cargarTerceros();
  } catch (err) {
    mostrarError(err.message);
  }
});

// --- Facturas --------------------------------------------------------

async function opcionesTerceros(selectEl) {
  const ts = await api("GET", "/terceros");
  selectEl.innerHTML = ts
    .map((t) => `<option value="${t.id}">${t.nombre} (${t.tipo})</option>`)
    .join("");
}

async function cargarFacturas() {
  await opcionesTerceros($("#factura-tercero"));
  const fs = await api("GET", "/facturas");
  $("#facturas-body").innerHTML = fs
    .map((f) => {
      const accion =
        f.estado === "pendiente"
          ? `<button class="sec" data-pagar="${f.id}" data-tipo="${f.tipo}">${
              f.tipo === "recibida" ? "pagar" : "cobrar"
            }</button>`
          : "";
      return `<tr>
        <td>${f.numero}</td><td>${f.tipo}</td><td>${f.fecha}</td>
        <td class="num">${money(f.subtotal)}</td><td class="num">${money(f.iva)}</td>
        <td class="num">${money(f.total)}</td>
        <td><span class="badge ${f.estado}">${f.estado}</span></td>
        <td>${accion}</td>
      </tr>`;
    })
    .join("");
}

$("#facturas-body").addEventListener("click", async (e) => {
  const btn = e.target.closest("[data-pagar]");
  if (!btn) return;
  const medio = prompt("Medio de pago: caja o bancos", "bancos");
  if (!medio) return;
  const fecha = prompt("Fecha (AAAA-MM-DD)", new Date().toISOString().slice(0, 10));
  if (!fecha) return;
  try {
    await api("POST", `/facturas/${btn.dataset.pagar}/pagar`, {
      medio_pago: medio.trim(),
      fecha,
    });
    await cargarFacturas();
  } catch (err) {
    mostrarError(err.message);
  }
});

$("#form-factura").addEventListener("submit", async (e) => {
  e.preventDefault();
  limpiarError();
  const f = e.target;
  try {
    await api("POST", "/facturas", {
      tipo: f.tipo.value,
      numero: f.numero.value,
      fecha: f.fecha.value,
      tercero_id: Number(f.tercero_id.value),
      subtotal: f.subtotal.value,
      iva: f.iva.value || "0",
    });
    f.reset();
    f.iva.value = "0";
    await cargarFacturas();
  } catch (err) {
    mostrarError(err.message);
  }
});

// --- Contratos ------------------------------------------------------

async function cargarContratos() {
  await opcionesTerceros($("#contrato-tercero"));
  const cs = await api("GET", "/contratos");
  $("#contratos-body").innerHTML = cs
    .map(
      (c) =>
        `<tr><td>${c.id}</td><td>${c.tercero_id}</td><td>${c.objeto}</td>
         <td class="num">${money(c.valor)}</td>
         <td>${c.fecha_inicio}${c.fecha_fin ? " → " + c.fecha_fin : ""}</td>
         <td>${c.estado}</td></tr>`
    )
    .join("");
}

$("#form-contrato").addEventListener("submit", async (e) => {
  e.preventDefault();
  limpiarError();
  const f = e.target;
  try {
    await api("POST", "/contratos", {
      tercero_id: Number(f.tercero_id.value),
      objeto: f.objeto.value,
      valor: f.valor.value,
      fecha_inicio: f.fecha_inicio.value,
      fecha_fin: f.fecha_fin.value || null,
    });
    f.reset();
    await cargarContratos();
  } catch (err) {
    mostrarError(err.message);
  }
});

// --- Movimiento manual -------------------------------------------------

let cuentasCache = [];

async function cargarMovimiento() {
  if (!cuentasCache.length) cuentasCache = await api("GET", "/cuentas");
  if (!$("#lineas-body").children.length) {
    agregarLinea();
    agregarLinea();
  }
  recalcularCuadre();
}

function opcionesCuenta() {
  return (
    '<option value=""></option>' +
    cuentasCache
      .map((c) => `<option value="${c.codigo}">${c.codigo} ${c.nombre}</option>`)
      .join("")
  );
}

function agregarLinea() {
  const tr = document.createElement("tr");
  tr.innerHTML = `
    <td><select class="l-cuenta">${opcionesCuenta()}</select></td>
    <td class="num"><input class="l-debito" type="number" step="0.01" min="0" value="0"></td>
    <td class="num"><input class="l-credito" type="number" step="0.01" min="0" value="0"></td>
    <td><button type="button" class="sec l-quitar">×</button></td>`;
  $("#lineas-body").appendChild(tr);
}

$("#add-linea").addEventListener("click", agregarLinea);

$("#lineas-body").addEventListener("click", (e) => {
  if (e.target.classList.contains("l-quitar")) {
    e.target.closest("tr").remove();
    recalcularCuadre();
  }
});
$("#lineas-body").addEventListener("input", recalcularCuadre);

function recalcularCuadre() {
  let d = 0;
  let c = 0;
  $$("#lineas-body tr").forEach((tr) => {
    d += Number($(".l-debito", tr).value) || 0;
    c += Number($(".l-credito", tr).value) || 0;
  });
  $("#tot-debito").textContent = money(d);
  $("#tot-credito").textContent = money(c);
  const el = $("#cuadre");
  const cuadra = d === c && d > 0;
  el.textContent = cuadra ? "cuadra" : `descuadre ${money(d - c)}`;
  el.className = cuadra ? "ok" : "bad";
}

$("#mov-libro").addEventListener("change", (e) => {
  $("#mov-soporte").disabled = e.target.value === "interna";
});

$("#form-movimiento").addEventListener("submit", async (e) => {
  e.preventDefault();
  limpiarError();
  const f = e.target;
  const lineas = $$("#lineas-body tr").map((tr) => ({
    cuenta_codigo: $(".l-cuenta", tr).value,
    debito: $(".l-debito", tr).value || "0",
    credito: $(".l-credito", tr).value || "0",
  }));
  try {
    await api("POST", "/movimientos", {
      fecha: f.fecha.value,
      descripcion: f.descripcion.value,
      libro: f.libro.value,
      documento_soporte: f.documento_soporte.value || null,
      lineas,
    });
    f.reset();
    $("#lineas-body").innerHTML = "";
    mostrarError("");
    avisoEl.hidden = true;
    await cargarMovimiento();
    alert("Movimiento registrado.");
  } catch (err) {
    mostrarError(err.message);
  }
});

// --- Arranque -----------------------------------------------------------

const CARGADORES = {
  balance: cargarBalance,
  libro: cargarLibro,
  terceros: cargarTerceros,
  facturas: cargarFacturas,
  contratos: cargarContratos,
  movimiento: cargarMovimiento,
};

mostrarTab(location.hash.replace("#/", "") || "balance");
