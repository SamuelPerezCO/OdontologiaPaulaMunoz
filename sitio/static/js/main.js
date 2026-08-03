/* ============================================================
   Arcada dental interactiva.

   Los dientes se dibujan con sus medidas reales de corona en
   milímetros (ancho mesiodistal × altura), colocados sobre una
   elipse por longitud de arco. El viewBox está en milímetros.

   La arcada es un realce: el contenido real son los <li> de la
   lista de tratamientos, que funcionan sin JavaScript.
   ============================================================ */

(function () {
  'use strict';

  var SVG_NS = 'http://www.w3.org/2000/svg';

  /* Medidas de corona en mm — odontometría de referencia.
     tipo: incisivo | canino | premolar | molar
     grupo: enlaza con [data-tx] en la lista de tratamientos. */
  var ANATOMIA = {
    1: { w: 8.5, h: 10.5, tipo: 'incisivo', grupo: 'incisivos' },
    2: { w: 6.5, h: 9.0,  tipo: 'incisivo', grupo: 'incisivos' },
    3: { w: 7.5, h: 10.0, tipo: 'canino',   grupo: 'caninos'   },
    4: { w: 7.0, h: 8.5,  tipo: 'premolar', grupo: 'premolares'},
    5: { w: 6.5, h: 8.5,  tipo: 'premolar', grupo: 'premolares'},
    6: { w: 10.0, h: 7.5, tipo: 'molar',    grupo: 'molares'   },
    7: { w: 9.0, h: 7.0,  tipo: 'molar',    grupo: 'molares'   },
    8: { w: 8.5, h: 6.5,  tipo: 'molar',    grupo: 'cordales'  }
  };

  /* Numeración FDI de la arcada superior, de derecha a izquierda
     del paciente (que es de izquierda a derecha en pantalla). */
  var FDI = [18, 17, 16, 15, 14, 13, 12, 11, 21, 22, 23, 24, 25, 26, 27, 28];

  var ELIPSE_A = 26;   /* semieje transversal (mm) */
  var ELIPSE_B = 36;   /* semieje anteroposterior (mm) */

  var svg = document.querySelector('[data-arch]');
  var lista = document.querySelector('[data-tx-list]');
  if (!svg || !lista) return;

  /* ── Geometría de la elipse por longitud de arco ─────────── */

  function puntoElipse(t) {
    return { x: ELIPSE_A * Math.sin(t), y: -ELIPSE_B * Math.cos(t) };
  }

  /* Tabla acumulada de longitud de arco desde t = 0 (línea media). */
  var PASOS = 2000;
  var tabla = [{ t: 0, s: 0 }];
  (function construirTabla() {
    var dt = Math.PI / PASOS;
    var s = 0;
    var prev = puntoElipse(0);
    for (var i = 1; i <= PASOS; i++) {
      var t = i * dt;
      var p = puntoElipse(t);
      s += Math.hypot(p.x - prev.x, p.y - prev.y);
      tabla.push({ t: t, s: s });
      prev = p;
    }
  })();

  /* Devuelve el parámetro t para una longitud de arco dada.
     El signo de s decide el lado de la arcada. */
  function tParaArco(s) {
    var signo = s < 0 ? -1 : 1;
    var objetivo = Math.abs(s);
    for (var i = 1; i < tabla.length; i++) {
      if (tabla[i].s >= objetivo) {
        var a = tabla[i - 1], b = tabla[i];
        var f = (objetivo - a.s) / (b.s - a.s || 1);
        return signo * (a.t + f * (b.t - a.t));
      }
    }
    return signo * Math.PI;
  }

  /* Normal exterior a la elipse en t (hacia afuera de la boca). */
  function anguloNormal(t) {
    var nx = ELIPSE_B * Math.sin(t);
    var ny = -ELIPSE_A * Math.cos(t);
    return Math.atan2(ny, nx) * 180 / Math.PI + 90;
  }

  /* ── Forma de la corona (coords locales, borde incisal en -y) ──

     La corona recibe dos anchos, no uno. Sobre una curva, el borde
     incisal recorre más arco que el cuello, así que un diente de ancho
     constante deja huecos en cuña entre vecinos. Con el ancho exterior
     e interior calculados sobre la misma elipse, los dientes contiguos
     comparten esquina y los puntos de contacto cierran. */

  function trazoCorona(wIn, wOut, h, tipo) {
    var hi = wIn / 2, ho = wOut / 2, hh = h / 2;
    var cuello = hi * 0.94;
    var d;

    if (tipo === 'molar' || tipo === 'premolar') {
      /* Cara oclusal casi plana, esquinas redondeadas. */
      var borde = ho * 0.92;
      d = 'M ' + (-cuello) + ' ' + hh +
          ' C ' + (-ho * 1.02) + ' ' + (hh * 0.3) + ' ' + (-ho * 1.03) + ' ' + (-hh * 0.35) + ' ' + (-borde) + ' ' + (-hh * 0.76) +
          ' Q ' + (-borde) + ' ' + (-hh) + ' ' + (-borde * 0.55) + ' ' + (-hh) +
          ' L ' + (borde * 0.55) + ' ' + (-hh) +
          ' Q ' + borde + ' ' + (-hh) + ' ' + borde + ' ' + (-hh * 0.76) +
          ' C ' + (ho * 1.03) + ' ' + (-hh * 0.35) + ' ' + (ho * 1.02) + ' ' + (hh * 0.3) + ' ' + cuello + ' ' + hh +
          ' Z';
    } else if (tipo === 'canino') {
      /* Cúspide única, apenas insinuada: el canino termina en punta,
         pero marcarla de más lo convierte en un pincho. */
      var hombro = ho * 0.86;
      d = 'M ' + (-cuello) + ' ' + hh +
          ' C ' + (-ho * 1.02) + ' ' + (hh * 0.25) + ' ' + (-ho * 1.02) + ' ' + (-hh * 0.35) + ' ' + (-hombro) + ' ' + (-hh * 0.72) +
          ' Q ' + (-hombro * 0.46) + ' ' + (-hh * 0.95) + ' 0 ' + (-hh) +
          ' Q ' + (hombro * 0.46) + ' ' + (-hh * 0.95) + ' ' + hombro + ' ' + (-hh * 0.72) +
          ' C ' + (ho * 1.02) + ' ' + (-hh * 0.35) + ' ' + (ho * 1.02) + ' ' + (hh * 0.25) + ' ' + cuello + ' ' + hh +
          ' Z';
    } else {
      /* Incisivo: borde recto con los ángulos suavizados. */
      var ancho = ho * 0.95;
      d = 'M ' + (-cuello) + ' ' + hh +
          ' C ' + (-ho * 1.02) + ' ' + (hh * 0.3) + ' ' + (-ho * 1.02) + ' ' + (-hh * 0.4) + ' ' + (-ancho) + ' ' + (-hh * 0.8) +
          ' Q ' + (-ancho) + ' ' + (-hh) + ' ' + (-ancho * 0.5) + ' ' + (-hh) +
          ' L ' + (ancho * 0.5) + ' ' + (-hh) +
          ' Q ' + ancho + ' ' + (-hh) + ' ' + ancho + ' ' + (-hh * 0.8) +
          ' C ' + (ho * 1.02) + ' ' + (-hh * 0.4) + ' ' + (ho * 1.02) + ' ' + (hh * 0.3) + ' ' + cuello + ' ' + hh +
          ' Z';
    }
    return d;
  }

  /* Anchos interior y exterior de la corona, medidos entre las esquinas
     que este diente comparte con sus vecinos. */
  function anchos(s, w, h) {
    var hh = h / 2;
    var tL = tParaArco(s - w / 2), tR = tParaArco(s + w / 2);
    var pL = puntoElipse(tL), pR = puntoElipse(tR);
    var nL = normalUnidad(tL), nR = normalUnidad(tR);
    return {
      fuera: Math.hypot((pR.x + nR.x * hh) - (pL.x + nL.x * hh),
                        (pR.y + nR.y * hh) - (pL.y + nL.y * hh)),
      dentro: Math.hypot((pR.x - nR.x * hh) - (pL.x - nL.x * hh),
                         (pR.y - nR.y * hh) - (pL.y - nL.y * hh))
    };
  }

  /* ── Construcción del SVG ────────────────────────────────── */

  function el(nombre, attrs) {
    var nodo = document.createElementNS(SVG_NS, nombre);
    for (var k in attrs) nodo.setAttribute(k, attrs[k]);
    return nodo;
  }

  function defs() {
    var d = el('defs');

    /* Dentina cálida en el cuello, esmalte translúcido en el borde. */
    var g1 = el('linearGradient', { id: 'grad-diente', x1: '0', y1: '1', x2: '0', y2: '0' });
    g1.appendChild(el('stop', { offset: '0',    'stop-color': '#E3D3BC' }));
    g1.appendChild(el('stop', { offset: '0.45', 'stop-color': '#F6F1E7' }));
    g1.appendChild(el('stop', { offset: '0.86', 'stop-color': '#FCFBF8' }));
    g1.appendChild(el('stop', { offset: '1',    'stop-color': '#DDE4F3' })); /* opalescencia incisal */
    d.appendChild(g1);

    var g2 = el('linearGradient', { id: 'grad-activo', x1: '0', y1: '1', x2: '0', y2: '0' });
    g2.appendChild(el('stop', { offset: '0',    'stop-color': '#EBC9CD' }));
    g2.appendChild(el('stop', { offset: '0.5',  'stop-color': '#FAF0F1' }));
    g2.appendChild(el('stop', { offset: '1',    'stop-color': '#FCFBF8' }));
    d.appendChild(g2);

    return d;
  }

  var porGrupo = {};   /* grupo → [elementos] */

  /* Vector normal unitario hacia afuera de la arcada en t. */
  function normalUnidad(t) {
    var nx = ELIPSE_B * Math.sin(t);
    var ny = -ELIPSE_A * Math.cos(t);
    var m = Math.hypot(nx, ny) || 1;
    return { x: nx / m, y: ny / m };
  }

  function bandaGingival() {
    var pts = [];
    /* ±60 mm: la banda acompaña a los dientes sin sobresalir por detrás
       de los cordales (la hemiarcada mide 63,5 mm). */
    for (var s = -60; s <= 60; s += 2) {
      var t = tParaArco(s);
      var p = puntoElipse(t);
      var n = normalUnidad(t);
      pts.push((p.x - n.x * 5).toFixed(2) + ' ' + (p.y - n.y * 5).toFixed(2));
    }
    return el('path', { d: 'M ' + pts.join(' L '), class: 'gum', 'data-grupo': 'encia' });
  }

  function construir() {
    svg.appendChild(defs());

    var encia = bandaGingival();
    svg.appendChild(encia);
    porGrupo.encia = [encia];

    /* Cada lado se reparte desde la línea media hacia atrás, y cada
       diente ocupa exactamente su ancho mesiodistal sobre el arco. */
    var mitad = FDI.length / 2;
    var lados = [
      { dientes: FDI.slice(0, mitad).reverse(), signo: -1 },  /* 11→18, a la izquierda en pantalla */
      { dientes: FDI.slice(mitad),              signo:  1 }   /* 21→28, a la derecha en pantalla */
    ];

    lados.forEach(function (lado) {
      var acumulado = 0;
      lado.dientes.forEach(function (num, i) {
        var info = ANATOMIA[Number(String(num)[1])];
        acumulado += info.w / 2;
        colocar(num, info, lado.signo * acumulado, i);
        acumulado += info.w / 2;
      });
    });
  }

  function colocar(num, info, s, rango) {
    var t = tParaArco(s);
    var p = puntoElipse(t);
    var giro = anguloNormal(t);

    /* Dos grupos a propósito: la colocación va en el atributo transform
       del exterior, la animación en el interior. Si compartieran nodo, la
       transformación de CSS pisaría la del atributo y los dientes se
       amontonarían en el origen. */
    var lugar = el('g', {
      class: 'tooth-place',
      transform: 'translate(' + p.x.toFixed(3) + ' ' + p.y.toFixed(3) + ') rotate(' + giro.toFixed(2) + ')'
    });

    var g = el('g', {
      class: 'tooth-group',
      style: 'animation-delay:' + (rango * 55 + 120) + 'ms'
    });

    var diente = el('g', { class: 'tooth', 'data-grupo': info.grupo, 'data-num': num });
    var an = anchos(s, info.w, info.h);
    diente.appendChild(el('path', {
      class: 'tooth__shape',
      d: trazoCorona(an.dentro, an.fuera, info.h, info.tipo)
    }));

    /* El número se contrarrota para leerse siempre derecho. */
    var etiqueta = el('text', {
      class: 'tooth__num',
      x: 0,
      y: info.h / 2 + 3.2,
      transform: 'rotate(' + (-giro).toFixed(2) + ' 0 ' + (info.h / 2 + 3.2) + ')'
    });
    etiqueta.textContent = num;
    diente.appendChild(etiqueta);

    g.appendChild(diente);
    lugar.appendChild(g);
    svg.appendChild(lugar);

    (porGrupo[info.grupo] = porGrupo[info.grupo] || []).push(diente);
  }

  /* ── Interacción ─────────────────────────────────────────── */

  var items = {};
  Array.prototype.forEach.call(lista.querySelectorAll('[data-tx]'), function (li) {
    items[li.getAttribute('data-tx')] = li;
  });

  var activo = null;

  function activar(grupo) {
    if (activo === grupo) return;
    limpiar();
    activo = grupo;
    (porGrupo[grupo] || []).forEach(function (n) { n.classList.add('is-active'); });
    if (items[grupo]) items[grupo].classList.add('is-active');
  }

  function limpiar() {
    if (!activo) return;
    (porGrupo[activo] || []).forEach(function (n) { n.classList.remove('is-active'); });
    if (items[activo]) items[activo].classList.remove('is-active');
    activo = null;
  }

  construir();

  /* Hover sobre la arcada. */
  svg.addEventListener('pointerover', function (e) {
    var zona = e.target.closest('[data-grupo]');
    if (zona) activar(zona.getAttribute('data-grupo'));
  });
  svg.addEventListener('pointerleave', limpiar);

  /* Clic: lleva al tratamiento correspondiente. */
  svg.addEventListener('click', function (e) {
    var zona = e.target.closest('[data-grupo]');
    if (!zona) return;
    var grupo = zona.getAttribute('data-grupo');
    var li = items[grupo];
    if (!li) return;
    activar(grupo);
    li.scrollIntoView({ behavior: 'smooth', block: 'center' });
    li.focus({ preventScroll: true });
  });

  /* La relación funciona en los dos sentidos: recorrer la lista
     resalta los dientes, para quien no usa el ratón. */
  Object.keys(items).forEach(function (grupo) {
    var li = items[grupo];
    li.addEventListener('pointerenter', function () { activar(grupo); });
    li.addEventListener('focus', function () { activar(grupo); });
  });
  lista.addEventListener('pointerleave', limpiar);

})();
