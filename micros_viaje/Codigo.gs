/**
 * Micros gratis para socios: formulario de inscripción + reporte en vivo.
 *
 * Se pega en la planilla de respuestas (Extensiones > Apps Script).
 * - crearFormulario(): crea el Google Form y lo vincula a esta planilla.
 * - doGet(): publica el reporte HTML (Implementar > Nueva implementación > App web).
 *
 * Ver micros_viaje/README.md para el paso a paso.
 */

// --- 1. CONFIGURACIÓN ---
var CONFIG = {
  TITULO_VIAJE: 'Micros gratis para socios',
  HOJA_PADRON: 'Padron',          // hoja con el padrón de socios activos
  CUPO: 0,                        // lugares disponibles en los micros (0 = no mostrar cupo)
  CLAVE_ACCESO: '',               // si se completa, el reporte solo abre con ?k=CLAVE en el link
  MOSTRAR_LISTADO: true,          // muestra el listado de inscriptos en el reporte
  ZONA_HORARIA: 'America/Argentina/Buenos_Aires'
};

var PREGUNTAS = {
  NOMBRE: 'Nombre y apellido',
  DNI: 'DNI',
  TELEFONO: 'Teléfono de contacto',
  MAIL: 'Mail de contacto'
};

var ESTADOS = { AL_DIA: 'al_dia', SIN_CUOTA: 'sin_cuota', NO_SOCIO: 'no_socio' };

// --- 2. MENÚ EN LA PLANILLA ---
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('Micros')
    .addItem('Crear formulario de inscripción', 'crearFormulario')
    .addItem('Ver links (formulario y reporte)', 'mostrarLinks')
    .addToUi();
}

// --- 3. CREACIÓN DEL FORMULARIO (se corre una sola vez) ---
function crearFormulario() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var props = PropertiesService.getScriptProperties();

  if (props.getProperty('FORM_ID')) {
    avisar_('El formulario ya fue creado. Usá "Micros > Ver links" para obtener el link.');
    return;
  }

  // Si la planilla ya es la de respuestas de un formulario existente, se usa ese.
  var existente = hojaRespuestas_(ss);
  if (existente) {
    props.setProperty('FORM_ID', FormApp.openByUrl(existente.getFormUrl()).getId());
    crearHojaPadron_(ss);
    mostrarLinks('Esta planilla ya tiene un formulario vinculado: se usa ese y no se crea uno nuevo.');
    return;
  }

  var form = FormApp.create(CONFIG.TITULO_VIAJE);
  form.setDescription('Inscripción exclusiva para socios del club. ' +
      'Completá tus datos y te vamos a contactar para confirmar tu lugar.')
    .setConfirmationMessage('¡Listo! Recibimos tu inscripción. ' +
      'Te vamos a contactar al teléfono o mail que dejaste para confirmar tu lugar.')
    .setAllowResponseEdits(false)
    .setShowLinkToRespondAgain(false);

  form.addTextItem()
    .setTitle(PREGUNTAS.NOMBRE)
    .setRequired(true);

  form.addTextItem()
    .setTitle(PREGUNTAS.DNI)
    .setHelpText('Solo números, sin puntos ni espacios.')
    .setRequired(true)
    .setValidation(FormApp.createTextValidation()
      .setHelpText('Ingresá solo números (7 u 8 dígitos), sin puntos ni espacios.')
      .requireTextMatchesPattern('^[0-9]{7,8}$')
      .build());

  form.addTextItem()
    .setTitle(PREGUNTAS.TELEFONO)
    .setHelpText('Con código de área. Ej: 221 555-1234')
    .setRequired(true)
    .setValidation(FormApp.createTextValidation()
      .setHelpText('Ingresá un teléfono válido (solo números, espacios, guiones o +).')
      .requireTextMatchesPattern('^[0-9 +()\\-]{8,20}$')
      .build());

  form.addTextItem()
    .setTitle(PREGUNTAS.MAIL)
    .setRequired(true)
    .setValidation(FormApp.createTextValidation()
      .setHelpText('Ingresá un mail válido.')
      .requireTextIsEmail()
      .build());

  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());
  props.setProperty('FORM_ID', form.getId());

  crearHojaPadron_(ss);
  mostrarLinks();
}

function crearHojaPadron_(ss) {
  if (ss.getSheetByName(CONFIG.HOJA_PADRON)) return;
  var padron = ss.insertSheet(CONFIG.HOJA_PADRON);
  padron.appendRow(['DNI', 'Nombre y apellido', 'Nro de socio', 'Cuota al día']);
  padron.setFrozenRows(1);
}

/** Muestra los links en un solo cartel (cada cartel frena el script hasta que se acepta). */
function mostrarLinks(encabezado) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var formId = PropertiesService.getScriptProperties().getProperty('FORM_ID');
  var hojaResp = hojaRespuestas_(ss);
  var lineas = typeof encabezado === 'string' ? [encabezado] : [];
  if (formId || hojaResp) {
    var form = formId ? FormApp.openById(formId) : FormApp.openByUrl(hojaResp.getFormUrl());
    lineas.push('Formulario para socios: ' + form.getPublishedUrl());
    lineas.push('Editar formulario: ' + form.getEditUrl());
  } else {
    lineas.push('Todavía no se creó el formulario (Micros > Crear formulario de inscripción).');
  }
  var urlReporte = ScriptApp.getService().getUrl();
  lineas.push(urlReporte
    ? 'Reporte: ' + urlReporte + (CONFIG.CLAVE_ACCESO ? '?k=' + CONFIG.CLAVE_ACCESO : '')
    : 'Reporte: todavía no está publicado (Implementar > Nueva implementación > App web).');
  avisar_(lineas.join('\n\n'));
}

function avisar_(mensaje) {
  Logger.log(mensaje);
  try {
    SpreadsheetApp.getUi().alert(mensaje);
  } catch (e) {
    // Corrido desde el editor de Apps Script: el mensaje queda en el registro de ejecución.
  }
}

// --- 4. REPORTE WEB ---
function doGet(e) {
  var clave = (e && e.parameter && e.parameter.k) || '';
  if (!claveValida_(clave)) {
    return HtmlService.createHtmlOutput(
      '<p style="font-family:sans-serif;padding:24px">Acceso no autorizado.</p>')
      .setTitle('Acceso restringido');
  }
  var t = HtmlService.createTemplateFromFile('Reporte');
  // "<" escapado para que el JSON no pueda cerrar el <script> donde se inserta.
  t.claveJson = JSON.stringify(clave).replace(/</g, '\\u003c');
  t.datosIniciales = JSON.stringify(obtenerResumen(clave)).replace(/</g, '\\u003c');
  return t.evaluate()
    .setTitle('Inscriptos · ' + CONFIG.TITULO_VIAJE)
    .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

function claveValida_(clave) {
  return !CONFIG.CLAVE_ACCESO || clave === CONFIG.CLAVE_ACCESO;
}

/** Llamado desde el reporte (google.script.run) para refrescar los datos. */
function obtenerResumen(clave) {
  if (!claveValida_(clave)) throw new Error('Acceso no autorizado.');

  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var avisos = [];

  var hojaResp = hojaRespuestas_(ss);
  var respuestas = hojaResp ? hojaResp.getDataRange().getValues() : [];
  if (!hojaResp) avisos.push('No se encontró la hoja de respuestas del formulario.');

  var hojaPadron = ss.getSheetByName(CONFIG.HOJA_PADRON);
  var padron = hojaPadron ? hojaPadron.getDataRange().getValues() : [];
  if (!hojaPadron) avisos.push('No se encontró la hoja "' + CONFIG.HOJA_PADRON + '" con el padrón.');

  var formatear = function (fecha, patron) {
    return Utilities.formatDate(fecha, CONFIG.ZONA_HORARIA, patron);
  };
  var resumen = calcularResumen_(respuestas, padron, formatear);

  resumen.avisos = avisos.concat(resumen.avisos);
  resumen.titulo = CONFIG.TITULO_VIAJE;
  resumen.cupo = CONFIG.CUPO;
  resumen.actualizado = formatear(new Date(), 'dd/MM/yyyy HH:mm');
  if (!CONFIG.MOSTRAR_LISTADO) resumen.listado = [];
  return resumen;
}

/** La hoja de respuestas es la vinculada a nuestro formulario (o, si no, la primera con formulario). */
function hojaRespuestas_(ss) {
  var formId = PropertiesService.getScriptProperties().getProperty('FORM_ID');
  var candidata = null;
  var hojas = ss.getSheets();
  for (var i = 0; i < hojas.length; i++) {
    var url = hojas[i].getFormUrl();
    if (!url) continue;
    if (formId && url.indexOf(formId) !== -1) return hojas[i];
    if (!candidata) candidata = hojas[i];
  }
  return candidata;
}

// --- 5. CRUCE INSCRIPTOS x PADRÓN ---
/**
 * respuestas y padron: matrices con la fila de encabezados primero (getValues()).
 * formatear(fecha, patron): formatea fechas en la zona horaria del club.
 */
function calcularResumen_(respuestas, padron, formatear) {
  var avisos = [];

  // Padrón indexado por DNI
  var socios = {};
  if (padron.length) {
    var encP = padron[0].map(normalizarTexto_);
    var pDni = buscarColumna_(encP, ['dni', 'documento']);
    var pCuota = buscarColumna_(encP, ['cuota', 'al dia', 'estado']);
    var pNombre = buscarColumna_(encP, ['nombre', 'apellido']);
    var pNro = buscarColumna_(encP, ['nro', 'numero', 'socio']);
    if (pDni === -1) avisos.push('En el padrón no hay una columna "DNI".');
    if (pCuota === -1) avisos.push('En el padrón no hay una columna "Cuota al día": todos los socios se cuentan sin cuota al día.');
    if (pDni !== -1) {
      for (var i = 1; i < padron.length; i++) {
        var dniP = normalizarDni_(padron[i][pDni]);
        if (!dniP) continue;
        socios[dniP] = {
          alDia: pCuota !== -1 && esCuotaAlDia_(padron[i][pCuota]),
          nombre: pNombre !== -1 ? String(padron[i][pNombre]).trim() : '',
          nroSocio: pNro !== -1 ? String(padron[i][pNro]).trim() : ''
        };
      }
    }
  }

  var totales = { inscriptos: 0, alDia: 0, sinCuota: 0, noSocio: 0, duplicados: 0 };
  var porDia = {};
  var listado = [];

  if (respuestas.length) {
    var encR = respuestas[0].map(normalizarTexto_);
    var rDni = buscarColumna_(encR, ['dni']);
    var rNombre = buscarColumna_(encR, ['nombre']);
    if (rDni === -1) avisos.push('En las respuestas no hay una columna "DNI".');

    var vistos = {};
    for (var j = 1; rDni !== -1 && j < respuestas.length; j++) {
      var fila = respuestas[j];
      var dni = normalizarDni_(fila[rDni]);
      if (!dni) continue;
      if (vistos[dni]) { totales.duplicados++; continue; }
      vistos[dni] = true;

      var socio = socios[dni];
      var estado = !socio ? ESTADOS.NO_SOCIO : (socio.alDia ? ESTADOS.AL_DIA : ESTADOS.SIN_CUOTA);
      totales.inscriptos++;
      if (estado === ESTADOS.AL_DIA) totales.alDia++;
      else if (estado === ESTADOS.SIN_CUOTA) totales.sinCuota++;
      else totales.noSocio++;

      // Columna 0 = "Marca temporal" del formulario
      var marca = fila[0];
      var esFecha = marca instanceof Date && !isNaN(marca.getTime());
      if (esFecha) {
        var dia = formatear(marca, 'yyyy-MM-dd');
        if (!porDia[dia]) porDia[dia] = { fecha: dia, total: 0, alDia: 0, sinCuota: 0, noSocio: 0 };
        porDia[dia].total++;
        porDia[dia][estado === ESTADOS.AL_DIA ? 'alDia' : estado === ESTADOS.SIN_CUOTA ? 'sinCuota' : 'noSocio']++;
      }

      listado.push({
        n: totales.inscriptos,
        fecha: esFecha ? formatear(marca, 'dd/MM HH:mm') : String(marca),
        nombre: rNombre !== -1 ? String(fila[rNombre]).trim() : (socio ? socio.nombre : ''),
        dni: dni,
        nroSocio: socio ? socio.nroSocio : '',
        estado: estado
      });
    }
  }

  return {
    totales: totales,
    porDia: completarDias_(porDia),
    listado: listado,
    sociosEnPadron: Object.keys(socios).length,
    avisos: avisos
  };
}

/** Ordena los días y agrega los que no tuvieron inscripciones (en 0) para no cortar la línea de tiempo. */
function completarDias_(porDia) {
  var claves = Object.keys(porDia).sort();
  if (!claves.length) return [];
  var salida = [];
  var actual = new Date(claves[0] + 'T00:00:00Z');
  var fin = new Date(claves[claves.length - 1] + 'T00:00:00Z');
  while (actual <= fin) {
    var clave = actual.toISOString().slice(0, 10);
    salida.push(porDia[clave] || { fecha: clave, total: 0, alDia: 0, sinCuota: 0, noSocio: 0 });
    actual.setUTCDate(actual.getUTCDate() + 1);
  }
  return salida;
}

function normalizarTexto_(v) {
  return String(v).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').trim();
}

/** "30.123.456", " 30123456 " y 30123456 terminan todos como "30123456". */
function normalizarDni_(v) {
  return String(v === null || v === undefined ? '' : v).replace(/\D/g, '').replace(/^0+/, '');
}

function buscarColumna_(encabezados, claves) {
  for (var k = 0; k < claves.length; k++) {
    for (var c = 0; c < encabezados.length; c++) {
      if (encabezados[c].indexOf(claves[k]) !== -1) return c;
    }
  }
  return -1;
}

/** Acepta casillas de verificación (TRUE/FALSE) y textos como "Sí", "Al día", "OK", "X". */
function esCuotaAlDia_(v) {
  if (v === true) return true;
  if (v === false || v === null || v === undefined) return false;
  var t = normalizarTexto_(v);
  return ['si', 's', 'true', 'verdadero', 'al dia', 'x', 'ok', '1', 'paga', 'pagada', 'pago'].indexOf(t) !== -1;
}
