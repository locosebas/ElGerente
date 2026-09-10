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

function celdaDoc(url) {
  if (!url) return "<td>—</td>";
  const seguro = String(url).replace(/"/g, "%22");
  return `<td><a class="doc" href="${seguro}" target="_blank" rel="noopener" title="${seguro}">📎</a></td>`;
}

// --- Navegación por pestañas ----------------------------------------------

const TABS = ["movimiento", "facturas", "contratos", "terceros", "balance", "libro"];
const TAB_INICIAL = "movimiento";

function mostrarTab(nombre) {
  const tab = TABS.includes(nombre) ? nombre : TAB_INICIAL;
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

// --- Controles de análisis (compartidos por Balance y Libro diario) ------

const ANIO_ACTUAL = new Date().getFullYear();
const MESES = [
  "enero", "febrero", "marzo", "abril", "mayo", "junio",
  "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
];
const LIBRO_NOTA = {
  oficial: "Oficial: la contabilidad real / externa (asientos con documento de soporte).",
  interna: "Interno: para-contabilidad — movimientos sin soporte formal (retiros, préstamos...).",
  todos: 'Total: oficial + interno junto — la caja "real".',
};

// Estado compartido de los dos controles.
const analisis = { libro: "oficial", anio: "", mes: "" };

function rangoFechas() {
  if (!analisis.anio) return {};
  const y = analisis.anio;
  if (!analisis.mes) return { desde: `${y}-01-01`, hasta: `${y}-12-31` };
  const m = Number(analisis.mes);
  const ultimo = new Date(y, m, 0).getDate();
  const mm = String(m).padStart(2, "0");
  return { desde: `${y}-${mm}-01`, hasta: `${y}-${mm}-${String(ultimo).padStart(2, "0")}` };
}

function paramsAnalisis(paraAsientos = false) {
  const p = new URLSearchParams();
  if (!(paraAsientos && analisis.libro === "todos")) p.set("libro", analisis.libro);
  const { desde, hasta } = rangoFechas();
  if (desde) p.set("desde", desde);
  if (hasta) p.set("hasta", hasta);
  return p.toString();
}

function montarControles(contenedor, alCambiar) {
  const anios = [];
  for (let y = ANIO_ACTUAL; y >= 2024; y--) anios.push(y);
  contenedor.innerHTML = `
    <div class="campo">Libro
      <div class="segmento" data-grupo="libro">
        <button type="button" data-v="oficial">Oficial</button>
        <button type="button" data-v="interna">Interno</button>
        <button type="button" data-v="todos">Total</button>
      </div>
    </div>
    <div class="campo">Periodo
      <div>
        <select data-c="anio">
          <option value="">histórico completo</option>
          ${anios.map((y) => `<option value="${y}">${y}</option>`).join("")}
        </select>
        <select data-c="mes">
          <option value="">todo el año</option>
          ${MESES.map((m, i) => `<option value="${i + 1}">${m}</option>`).join("")}
        </select>
      </div>
    </div>
    <p class="ctrl-nota"></p>`;

  contenedor._sync = () => {
    $$('.segmento[data-grupo="libro"] button', contenedor).forEach((b) =>
      b.classList.toggle("activo", b.dataset.v === analisis.libro)
    );
    $('[data-c="anio"]', contenedor).value = analisis.anio;
    $('[data-c="mes"]', contenedor).value = analisis.mes;
    $('[data-c="mes"]', contenedor).disabled = !analisis.anio;
    $(".ctrl-nota", contenedor).textContent = LIBRO_NOTA[analisis.libro];
  };
  contenedor._sync();

  const propagar = () => {
    $$(".analisis-ctrl").forEach((c) => c._sync && c._sync());
    alCambiar().catch((e) => mostrarError(e.message));
  };

  contenedor.addEventListener("click", (e) => {
    const b = e.target.closest('.segmento[data-grupo="libro"] button');
    if (!b) return;
    analisis.libro = b.dataset.v;
    propagar();
  });
  contenedor.addEventListener("change", (e) => {
    const c = e.target.closest("[data-c]");
    if (!c) return;
    analisis[c.dataset.c] = c.dataset.c === "anio" ? (c.value ? Number(c.value) : "") : c.value;
    if (!analisis.anio) analisis.mes = "";
    propagar();
  });
}

// --- Balance (árbol tipo -> cuenta -> extracto) --------------------------

const TIPO_ORDEN = ["activo", "pasivo", "patrimonio", "ingreso", "gasto"];
const TIPO_LABEL = {
  activo: "Activos", pasivo: "Pasivos", patrimonio: "Patrimonio",
  ingreso: "Ingresos", gasto: "Gastos",
};

const nn = (v) => (Number(v) < 0 ? " neg" : "");

async function cargarBalance() {
  const filas = await api("GET", `/balance?${paramsAnalisis()}`);
  const porTipo = {};
  filas.forEach((c) => (porTipo[c.tipo] ||= []).push(c));

  const html = TIPO_ORDEN.filter((t) => porTipo[t])
    .map((t) => {
      const cuentas = porTipo[t];
      const subtotal = cuentas.reduce((s, c) => s + Number(c.saldo), 0);
      const filasCuenta = cuentas
        .map(
          (c) => `
        <div class="fila-cuenta" data-cod="${c.cuenta_codigo}">
          <span><span class="cta-cod">${c.cuenta_codigo}</span>${c.cuenta_nombre}</span>
          <span class="num${nn(c.saldo)}">${money(c.saldo)}</span>
        </div>
        <div class="extracto" data-ext="${c.cuenta_codigo}"></div>`
        )
        .join("");
      return `<div class="grupo">
        <div class="fila-tipo">
          <span><span class="flecha">▶</span> ${TIPO_LABEL[t]}</span>
          <span class="num${subtotal < 0 ? " neg" : ""}">${money(subtotal)}</span>
        </div>
        <div class="cuentas">${filasCuenta}</div>
      </div>`;
    })
    .join("");
  $("#balance-arbol").innerHTML = html || '<p class="vacio">Sin datos para este filtro.</p>';
}

$("#balance-arbol").addEventListener("click", async (e) => {
  const tipo = e.target.closest(".fila-tipo");
  if (tipo) {
    const abierto = tipo.parentElement.classList.toggle("abierto");
    tipo.querySelector(".flecha").textContent = abierto ? "▼" : "▶";
    return;
  }
  const cuenta = e.target.closest(".fila-cuenta");
  if (!cuenta) return;
  const cod = cuenta.dataset.cod;
  const ext = cuenta.nextElementSibling;
  if (!cuenta.classList.toggle("abierto") || ext.dataset.cargado) return;
  ext.innerHTML = '<p class="vacio">cargando…</p>';
  try {
    const d = await api("GET", `/cuentas/${cod}/movimientos?${paramsAnalisis()}`);
    ext.dataset.cargado = "1";
    ext.innerHTML = d.movimientos.length
      ? `<table><thead><tr>
           <th>Fecha</th><th>Descripción</th><th class="num">Débito</th>
           <th class="num">Crédito</th><th class="num">Saldo</th>
         </tr></thead><tbody>${d.movimientos
           .map(
             (m) => `<tr>
             <td>${m.fecha}</td><td>${m.descripcion}</td>
             <td class="num">${Number(m.debito) ? money(m.debito) : ""}</td>
             <td class="num">${Number(m.credito) ? money(m.credito) : ""}</td>
             <td class="num${nn(m.saldo_acumulado)}">${money(m.saldo_acumulado)}</td>
           </tr>`
           )
           .join("")}</tbody></table>`
      : '<p class="vacio">Sin movimientos en este periodo.</p>';
  } catch (err) {
    ext.innerHTML = `<p class="vacio">${err.message}</p>`;
  }
});

// --- Libro diario --------------------------------------------------------

async function cargarLibro() {
  const asientos = await api("GET", `/asientos?${paramsAnalisis(true)}`);
  $("#libro-body").innerHTML = asientos.length
    ? asientos.map(renderAsiento).join("")
    : '<p class="hint">No hay asientos para este filtro.</p>';
}

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
        `<tr><td>${t.id}</td><td>${t.nombre}</td><td>${t.nit_cedula}</td><td>${t.tipo}</td>${celdaDoc(
          t.enlace_rut
        )}</tr>`
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
      enlace_rut: f.enlace_rut.value || null,
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
        ${celdaDoc(f.enlace_documento)}
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
      enlace_documento: f.enlace_documento.value || null,
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
         <td>${c.estado}</td>${celdaDoc(c.enlace_documento)}</tr>`
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
      enlace_documento: f.enlace_documento.value || null,
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
  const oficial = e.target.value === "oficial";
  $("#mov-soporte").required = oficial;
  $("#mov-soporte-req").hidden = !oficial;
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

montarControles($("#ctrl-balance"), cargarBalance);
montarControles($("#ctrl-libro"), cargarLibro);

mostrarTab(location.hash.replace("#/", "") || TAB_INICIAL);
