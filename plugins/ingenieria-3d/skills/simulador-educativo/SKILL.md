---
name: simulador-educativo
description: "Simuladores interactivos en una sola página HTML que funciona sin internet (doble clic) y se puede publicar online, para corroborar un ensayo, un cálculo o un fenómeno de un trabajo práctico: parámetros con deslizadores, escenarios de la consigna, resultados con fórmula y reemplazo, gráfico con curvas y mediciones, animación del fenómeno, modo laboratorio que compara mediciones con la teoría (error %), exportación a CSV y PNG y vista para imprimir. Ejemplos: curva cupla-velocidad de un motor asincrónico (Kloss), ensayo de doblado y plegado, campo magnético giratorio, secado de un producto, rendimiento de un transformador, ensayo de tracción. Usar cuando se pida un simulador, una simulación interactiva, una app o calculadora para el TP, algo para corroborar el ensayo o los cálculos, ver cómo cambia una curva al mover un valor o comparar mediciones con la teoría."
---

# Simulador educativo (una página HTML sin internet)

Una sola página HTML, sin librerías ni CDN, que se abre con doble clic y también se publica online. El alumno mueve los parámetros y ve cambiar los resultados (con la fórmula y el reemplazo), el gráfico y una animación del fenómeno; en el modo laboratorio carga sus mediciones y las compara con la teoría.

Partir siempre de `plantilla/simulador.html` (en la carpeta de esta skill). Ya trae, funcionando y probado:
- parámetros con deslizador y campo numérico sincronizados (coma decimal, flechas, rango y aviso si el valor no sirve), listas desplegables y escenarios precargados;
- resultados destacados y cálculo paso a paso: fórmula = reemplazo = resultado;
- gráfico en canvas hecho a mano: ejes con marcas y rótulos, varias series, leyenda, puntos destacados con rótulo, tooltip con mouse, dedo o teclado, y las mediciones;
- animación en canvas con reproducir y pausar, velocidad, reinicio y escala de tiempo (cámara lenta o acelerada), que además puede mover un cursor sobre el gráfico;
- modo laboratorio: tabla editable, pegado desde Excel, error % por punto con colores, error medio y máximo, datos guardados en el navegador;
- exportar CSV (punto y coma y coma decimal: abre bien en Excel) y PNG del gráfico, vista para imprimir en A4 y PDF;
- paneles Teoría, Qué observar y Supuestos y límites;
- formato numérico argentino, tema claro y oscuro, diseño para celular y controles que se usan con teclado y lector de pantalla.

Como ejemplo trae la curva cupla-velocidad de un motor asincrónico con la fórmula de Kloss: reemplazarlo por el modelo del trabajo.

## Método (en este orden)

1. **Modelo físico primero.** Antes de tocar el HTML, escribir el fenómeno, las variables de entrada y de salida con unidades SI, las ecuaciones y de dónde salen (consigna, apunte, libro, norma, catálogo). Separar lo exacto, lo aproximado y lo empírico: los coeficientes de tabla o de catálogo van como parámetros con su fuente y nunca se inventan. Si el trabajo tiene memoria de cálculo (skill **calculos-ingenieria**), usar las mismas fórmulas, símbolos y datos.
2. **Validar con Python contra un caso resuelto a mano.** Escribir el mismo modelo en Python y comprobar:
   - que reproduce un caso resuelto a mano (diferencias solo de redondeo, menores que 0,5 %);
   - que da lo mismo por otro método independiente (bisección o integración numérica, otra fórmula, un límite conocido, un balance);
   - que es coherente (pasa por el punto nominal, signos y unidades correctos).

   El script guarda `casos.json` con los valores exactos y la página tiene que dar lo mismo (tolerancia relativa de 10⁻⁶): si no coincide, el error está en la página. Modelo para copiar: `scripts/validar_modelo_kloss.py`.
3. **Pocos parámetros con sentido**: de 3 a 6, los que el alumno cambiaría en el TP o en el ensayo. Lo demás queda constante en el modelo y se dice en los supuestos. Rangos físicos reales, paso con la resolución de la medición o del catálogo y valor por defecto igual al de la consigna. Si el rango depende de otro parámetro, usar porcentajes (carga en % de la nominal). Opciones discretas (material, conexión, pares de polos) en lista desplegable.
4. **Escenarios de la consigna**: el primero es el caso de la consigna (se carga al abrir y con Restablecer); después, uno por cada situación que la consigna pida analizar, uno de "qué pasa si" y uno que lleve al límite del modelo y muestre su aviso. Nombres que se entiendan solos: "Sobrecarga del 150 %", "Mandril de dos espesores".
5. **Supuestos y límites a la vista**: en su panel y, además, como avisos dentro del simulador cuando los valores salen de la zona válida (`error` si no tienen sentido físico, `atencion` si el modelo deja de valer o hay riesgo, `info` para aclarar). En "Qué observar", de 5 a 8 preguntas que se contesten moviendo el simulador, en el orden de la consigna, con al menos una sobre un límite del modelo y otra sobre el modo laboratorio.
6. **Armar la página** adaptando la plantilla (sección siguiente).
7. **Probar en Chrome sin ventana** y mirar las capturas (sección Verificación).
8. **Entregar** el `.html` que anda sin internet y, si el entorno tiene la herramienta de artefactos de Claude, la versión online publicada (sección Entrega).

## Cómo adaptar la plantilla

El script tiene dos partes: **1. Configuración**, el objeto `SIM`, que es lo único que se edita, y **2. Motor**, que no se toca (si falta algo, agregarlo sin romper lo que revisa el script de prueba). Cambiar también el `<title>` (de 2 a 4 palabras).

| Campo de `SIM` | Qué va |
|---|---|
| `titulo`, `tituloCorto`, `subtitulo` | Encabezado; `tituloCorto` también nombra los archivos exportados |
| `parametros` | `{ id, nombre, simbolo, unidad, min, max, paso, valor, ayuda }`, o `opciones: [[valor, 'texto'], ...]` para una lista |
| `escenarios` | `{ nombre, valores: { id: valor }, descripcion }`; lo que no se nombra toma el valor por defecto |
| `modelo(p)` | Función pura: recibe `p.id` y devuelve resultados, series, marcas, avisos y lo que necesiten los ejes, la animación y el laboratorio |
| `grafico` | `titulo` y ejes `x` e `y` con `titulo`, `simbolo`, `unidad`, `min` y `max` (número, función de `r` o nada para automático) |
| `animacion` | `titulo`, `leyenda`, `escalaTiempo` (segundos del fenómeno por segundo en pantalla) y `dibujar(ctx, a)`; `null` si no hay animación |
| `laboratorio` | Columnas `x` e `y`, `teorico(x, r, p)`, `tolerancia` (%), `ejemplo` y `notaEjemplo`; `null` si no hace falta |
| `teoria`, `observar`, `supuestos`, `limites` | HTML corto y listas de textos |

Lo que devuelve `modelo(p)`:
- `resultados`: `{ id, nombre, simbolo, valor, unidad, decimales, formula, reemplazo, nota, destacado }`. Se muestran como `formula = reemplazo = valor unidad`; con `destacado: true` aparecen arriba, en grande. El `id` es el que compara `casos.json`.
- `series`: `{ nombre, puntos: [[x, y], ...], color, ancho, guiones }`. Entre 200 y 400 puntos para una curva; dos puntos para una recta.
- `marcas`: puntos destacados con rótulo, `{ nombre, x, y, color, grande, hueco }` (punto de trabajo, máximo, valor de la consigna).
- `avisos`: `{ nivel: 'error' | 'atencion' | 'info', texto }`. Si los datos no tienen sentido físico, devolver solo el aviso de error: la página lo muestra y no dibuja curvas.

Reglas:
- En nombres, fórmulas y textos, `_x` se ve como subíndice (`T_máx`, `n_s`, `T_{carga 1}`), y `fmt(valor, decimales)` escribe 1.450,5. Armar el reemplazo con `fmt`, para que muestre los números con los que se calculó.
- Colores por nombre: `serie1` a `serie5`, `tinta`, `sub`, `acento`, `peligro`, `ok`, `metal`, `metalClaro`, `cobre`. Así funcionan el tema oscuro, la impresión y el PNG.
- En `dibujar(ctx, a)` las medidas son píxeles CSS (`a.ancho`, `a.alto`); lo que avanza con el tiempo (ángulos, posiciones) se suma con `a.dt` (segundos del fenómeno) y se guarda en `a.estado`; los textos van con `a.texto(t, x, y, { tam, color, alinear })`. Si `dibujar` devuelve un número, la página marca esa x en el gráfico: sirve para ensayos que avanzan en el tiempo (secado, calentamiento, doblado).
- Escala de tiempo: lo rápido, en cámara lenta (un rotor a 1.500 rpm con `escalaTiempo: 0.01`); lo lento, acelerado (un secado de horas con `3600`: 1 s en pantalla = 1 h). Un giro real de 25 vueltas por segundo se ve quieto, al revés o a los saltos.
- Nada de librerías, CDN, fuentes ni imágenes de internet: la página tiene que andar sin conexión. Las imágenes propias van como `data:` o dibujadas en el canvas.
- No cambiar los `id` que usa el script de prueba (`grafico`, `resultados`, `exportar-csv`, `exportar-png`, `vista-impresion`, `volver`, `restablecer`, `p-<id>` y `r-<id>`) ni `window.simulador`.

## Ejemplo mínimo

Otro fenómeno con el mismo motor: reemplazando el objeto `SIM` de la plantilla por este, la página pasa el script de prueba. La animación devuelve el tiempo y el gráfico muestra el cursor.

```js
const SIM = {
  titulo: 'Calentamiento de un motor',
  tituloCorto: 'Calentamiento de un motor',
  parametros: [
    { id: 'tau', nombre: 'Constante de tiempo', simbolo: 'τ', unidad: 'min', min: 5, max: 120, paso: 1, valor: 40 },
    { id: 'dTn', nombre: 'Calentamiento final', simbolo: 'Δθ_n', unidad: 'K', min: 20, max: 140, paso: 1, valor: 80 },
    { id: 'Ta', nombre: 'Temperatura ambiente', simbolo: 'θ_a', unidad: '°C', min: 0, max: 50, paso: 1, valor: 40 },
  ],
  escenarios: [{ nombre: 'Motor de la consigna', valores: {} }],
  modelo(p) {
    const theta = (t) => p.Ta + p.dTn * (1 - Math.exp(-t / p.tau));    // °C, t en min
    const puntos = [];
    for (let i = 0; i <= 300; i++) { const t = 5 * p.tau * i / 300; puntos.push([t, theta(t)]); }
    return {
      resultados: [{ id: 'tf', nombre: 'Temperatura final', simbolo: 'θ_f', valor: p.Ta + p.dTn, unidad: '°C',
        decimales: 1, destacado: true, formula: 'θ_f = θ_a + Δθ_n', reemplazo: `${fmt(p.Ta, 0)} °C + ${fmt(p.dTn, 0)} K` }],
      series: [{ nombre: 'Temperatura del motor', puntos, color: 'serie1' }],
      marcas: [{ nombre: '3τ: 95 %', x: 3 * p.tau, y: theta(3 * p.tau), color: 'serie2' }],
      avisos: p.Ta + p.dTn > 155 ? [{ nivel: 'atencion', texto: 'Supera los 155 °C de la clase térmica F.' }] : [],
      theta,                                                              // para la animación
    };
  },
  grafico: { titulo: 'Temperatura en el tiempo', x: { titulo: 'Tiempo', simbolo: 't', unidad: 'min', min: 0 },
             y: { titulo: 'Temperatura', simbolo: 'θ', unidad: '°C' } },
  animacion: {
    titulo: 'Termómetro', escalaTiempo: 600,                              // 1 s en pantalla = 10 min
    dibujar(ctx, a) {
      const t = (a.t / 60) % (5 * a.p.tau), th = a.r.theta(t);           // min y °C
      const h = (a.alto - 50) * (th - a.p.Ta) / a.p.dTn;
      ctx.fillStyle = a.c.peligro; ctx.fillRect(a.ancho / 2 - 15, a.alto - 20 - h, 30, h);
      a.texto(`θ = ${a.fmt(th, 1)} °C a los ${a.fmt(t, 0)} min`, a.ancho / 2, 18, { alinear: 'center' });
      return t;                                                           // cursor sobre el gráfico
    },
  },
  laboratorio: null,
};
```

Sin `teoria`, `observar`, `supuestos` ni `limites`, esos paneles no aparecen; en un trabajo real tienen que estar.

## Verificación

1. `python scripts/validar_modelo_<tema>.py casos.json`: el modelo en Python coincide con el caso a mano y con el otro método.
2. `python scripts/probar_simulador.py simulador.html --salida prueba --casos casos.json`. Necesita `pip install playwright` y Chrome, Edge o Chromium (`--chrome RUTA` elige el ejecutable). Abre la página con internet bloqueado y revisa:
   - cero errores de consola y ningún pedido a internet;
   - que el gráfico dibuje y que mover el primer deslizador cambie los resultados o las curvas, y su campo;
   - que salgan el CSV y el PNG;
   - que todos los controles tengan nombre accesible y que en el celular (390 px) nada se salga de costado;
   - que `window.simulador.calcular()` dé lo mismo que Python en cada caso de `casos.json`.

   Sale con código 1 si algo falla.
3. Mirar las capturas que deja, con la herramienta de lectura de imágenes: `escritorio.png`, `celular-pantalla.png`, `celular.png`, `impresion.png` e `impresion.pdf`. Buscar rótulos encimados o cortados, curvas que se salen del área, marcas fuera de lugar, textos de la animación sobre el dibujo, tablas que se salen y avisos que no corresponden. Corregir y volver a probar.
4. Recorrer los escenarios: cada uno tiene que mostrar lo que dice su nombre, y los de límite, su aviso.

## Entrega

- **Sin internet**: el `.html` solo, con un nombre claro (`simulador-curva-cupla-velocidad.html`); se abre con doble clic en Chrome, Edge o Firefox. En el celular conviene el link publicado: un `.html` abierto desde una app de mensajes o desde el administrador de archivos puede mostrarse sin ejecutar el JavaScript.
- **Online**, si el entorno tiene la herramienta de artefactos de Claude: leer su guía, publicar el mismo archivo y, después de publicar, declarar la capacidad `downloads` para que Exportar CSV y Gráfico en PNG bajen archivos (la plantilla ya la usa cuando está). Sin esa capacidad, la página muestra el CSV para copiar y la imagen para guardar con clic derecho. En el visor no se puede imprimir (se imprime desde el `.html`) y las mediciones pueden no quedar guardadas: avisarlo al entregar.
- **Con el informe** (skill **informe-tecnico**): el PNG del gráfico va como figura con epígrafe y la tabla del modo laboratorio, en un anexo; los números del simulador tienen que ser los de la memoria de cálculo.
- **Para una exposición** (skill **exposicion-oral**): elegir antes el escenario que se va a mostrar, llevar el `.html` en el pendrive y un video corto de la demo como plan B.
- Al entregar, decir en dos o tres líneas qué modelo usa, qué validación pasó (caso a mano y otro método) y sus límites principales.

## Errores frecuentes

- Números del simulador distintos de los del informe: mismo modelo, mismos datos y redondeo solo al mostrar.
- Unidades mezcladas: rpm y rad/s, kW y W, % y fracción, grados y radianes, mm y m. Anotar la unidad al lado de cada variable del modelo.
- Demasiados parámetros, o rangos que permiten valores sin sentido sin ningún aviso.
- Animaciones a velocidad real, o que no leen los valores del modelo (`a.r`): tienen que mostrar el mismo punto de trabajo que el gráfico.
- Mediciones de ejemplo presentadas como reales: marcarlas como ficticias y reemplazarlas por las del ensayo.
- Fórmulas empíricas usadas fuera de su rango (por ejemplo, Kloss cerca del arranque): decirlo en los límites y con un aviso.
- Tocar el motor y romper la impresión, el tema oscuro o el celular: volver a correr el script de prueba después de cada cambio.

## Material de referencia

- `references/recetas-modelos.md`: leerlo cuando el simulador sea de alguno de estos temas o de uno parecido: variantes de la curva cupla-velocidad (carga de ventilador, estrella-triángulo, rotor bobinado, variador de frecuencia), ensayo de doblado y plegado, campo magnético giratorio, secado de un producto, rendimiento y regulación de un transformador, ensayo de tracción y calentamiento de un motor. Para cada uno: ecuaciones, parámetros, escenarios, gráfico, animación, supuestos y límites, y un caso para validar.
- Para recorrer en 3D una máquina o una planta con el mouse, usar la skill **visor-3d-interactivo**; esta es para fenómenos con curvas, cálculos y animaciones en 2D.
