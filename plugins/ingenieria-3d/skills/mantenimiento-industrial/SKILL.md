---
name: mantenimiento-industrial
description: "Mantenimiento industrial para técnicos electromecánicos, con calculadora en Python: tipos de mantenimiento (correctivo, preventivo, predictivo, TPM y RCM) y cuándo conviene cada uno; indicadores MTBF, MTTR, disponibilidad inherente y operativa, confiabilidad R(t), OEE (disponibilidad, rendimiento y calidad) y costo del mantenimiento; análisis de fallas con Pareto, Ishikawa, 5 porqués y AMFE (NPR = S × O × D); plan de mantenimiento preventivo, orden de trabajo y planilla de inspección; lubricación de rodamientos por el método SKF, vibraciones según ISO 20816-3, termografía, alineación de ejes, balanceo y bloqueo y etiquetado (LOTO). Usar cuando se pida calcular la disponibilidad de una máquina, el MTBF y el MTTR, qué es el OEE y cómo se calcula, armar un plan de mantenimiento preventivo o una orden de trabajo, hacer un AMFE o un Pareto de fallas, cada cuánto engrasar un rodamiento y cuánta grasa ponerle, evaluar las vibraciones de un motor o resolver un TP de mantenimiento."
---

# Mantenimiento industrial

Cómo elegir la estrategia, medir con indicadores, analizar fallas y armar el plan. `scripts/mantenimiento.py` (Python 3.9+, solo biblioteca estándar) hace cada cuenta con fórmula, reemplazo y resultado en coma decimal; las tablas de Pareto y AMFE salen en Markdown. La presentación de la memoria de cálculo está en **calculos-ingenieria** y la del informe en **informe-tecnico**; la vida y la selección de rodamientos, en **elementos-de-maquinas**; la placa, el arranque y la protección de motores, en **maquinas-electricas**.

| Leer | Cuándo |
|---|---|
| [tipos-de-mantenimiento.md](references/tipos-de-mantenimiento.md) | Elegir y justificar la estrategia; TPM (pilares, 5S, seis grandes pérdidas); RCM (las 7 preguntas) |
| [indicadores.md](references/indicadores.md) | Definiciones con fuente, tiempos de un registro, R(t) en serie y paralelo, OEE en detalle, costo |
| [analisis-de-fallas.md](references/analisis-de-fallas.md) | Pareto, Ishikawa, 5 porqués y AMFE con las escalas de S, O y D; formato CSV del script |
| [tecnicas-predictivas.md](references/tecnicas-predictivas.md) | Relubricación SKF completa, vibraciones ISO 20816-3, termografía, alineación y balanceo |
| [plantillas.md](references/plantillas.md) | Plan preventivo, orden de trabajo, planilla de inspección, registro de fallas, hoja de AMFE |
| [seguridad-bloqueo.md](references/seguridad-bloqueo.md) | Bloqueo y etiquetado (LOTO) y consignación eléctrica |

## Método (siempre)

1. **Datos** del período con su fuente (órdenes de trabajo, parte de producción, catálogo, medición), separando los tiempos como en la tabla de abajo.
2. **Fórmula** con símbolos y unidades → **reemplazo** → **resultado**, con el script; nunca de cabeza.
3. **Verificación** por otro camino: Ao por tiempos, OEE por la fórmula simple, horas que suman el total, NPR que se recalcula.
4. **Interpretación**: cuál es la mayor pérdida, qué acción se propone y con qué indicador se va a medir la mejora.

| Tiempo | Qué incluye | Se usa en |
|---|---|---|
| Planificado (requerido) | Turnos menos pausas, limpiezas y paradas programadas fuera de producción | Disponibilidad del OEE |
| Funcionamiento Tf | Planificado menos todas las paradas | MTBF, Ao, rendimiento |
| Reparación activa TTR | Diagnóstico, reparación y prueba de cada falla | MTTR, Ai |
| Esperas | Repuestos, técnico, herramientas, permisos | MDT, Ao |
| Otras paradas | Cambios de formato y ajustes: no son mantenimiento | Disponibilidad del OEE |

## Qué estrategia conviene

| Estrategia | Qué es | Conviene cuando |
|---|---|---|
| Correctivo | Reparar cuando falla, inmediato o diferido | La falla no afecta la seguridad ni el ambiente, es barata o hay reserva |
| Preventivo por tiempo o uso | Tareas a intervalo fijo: lubricar, ajustar, cambiar | La falla depende de la edad o del uso (juntas, correas, grasa) y la tarea cuesta menos que la falla |
| Predictivo (por condición) | Medir una variable y actuar cuando cambia | La falla avisa (vibración, temperatura, aceite) con tiempo para planificar; equipos críticos |
| TPM | Gestión con operadores que limpian, lubrican e inspeccionan; 8 pilares sobre las 5S; se mide con el OEE | Bajar las seis grandes pérdidas con todo el personal |
| RCM | Decidir la tarea modo de falla por modo de falla según sus consecuencias (SAE JA1011) | Equipos críticos, con fallas de consecuencias graves |

Dato clave (Nowlan y Heap, 1978, estudio de United Airlines): solo el 6 % de los componentes estudiados mostró un desgaste marcado y el 89 % no tenía zona de desgaste. Cambiar por edad sirve para el desgaste; para lo demás conviene medir la condición o rediseñar. Detalle y fuentes en [tipos-de-mantenimiento.md](references/tipos-de-mantenimiento.md).

## Indicadores

Definiciones de la *DoD Guide for Achieving Reliability, Availability, and Maintainability* (2005, sección 3.2.4), OEE según oee.com, confiabilidad según el manual de estadística de NIST (fuentes completas en [indicadores.md](references/indicadores.md)):

- MTBF = Tf/Nf [h]; tasa de fallas λ = 1/MTBF [fallas/h]. MTTR = ΣTTR/Nf [h], solo reparación activa.
- MDT = (ΣTTR + Σesperas + Σpreventivo)/(Nf + Np) [h]; MTBM = Tf/(Nf + Np) [h], con Np las intervenciones preventivas dentro del tiempo requerido.
- Disponibilidad inherente Ai = MTBF/(MTBF + MTTR). Disponibilidad operativa Ao = MTBM/(MTBM + MDT) = Tf/(Tf + paradas por mantenimiento).
- Confiabilidad con tasa constante: R(t) = e^(−t/MTBF); tiempo para una R pedida, t = −MTBF·ln R. Serie: R = R1·R2·… (las λ se suman); paralelo: R = 1 − (1 − R1)·(1 − R2)·…
- OEE = A·P·Q, con A = T marcha/T planificado, P = t ciclo ideal·N total/T marcha y Q = N buenas/N total. Control: OEE = N buenas·t ciclo ideal/T planificado. Clase mundial (Nakajima): OEE 85 % con A 90 %, P 95 % y Q 99 %.
- Costo total = directo (horas-hombre·costo horario + repuestos y materiales + terceros) + indirecto (horas de parada no planificada·costo de la hora parada).

```
python mantenimiento.py indicadores --operacion 306 --registro ../plantilla/registro-fallas-ejemplo.csv
python mantenimiento.py confiabilidad --mtbf 34 --t 8 --objetivo 0,9
python mantenimiento.py oee --planificado 330 --paradas 24 --tasa 100 --total 1562000 --rechazos 31400
python mantenimiento.py costo --hh 67 --costo-hh 15000 --materiales 1600000 --terceros 400000 --parada 18 --costo-parada 180000 --unidades 1530600 --reposicion 1500000000
```

## Ejemplo resuelto: línea de envasado (datos inventados; lo reproduce el `demo`)

Un mes de 22 días con 2 turnos de 8 h: 352 h; pausas y limpieza 22 h → planificado 330 h. Registro: 9 fallas con 13,5 h de reparación activa y 4,5 h de espera (18 h de parada); 4 cambios de formato, 6 h → Tf = 330 − 18 − 6 = 306 h. Velocidad ideal 100 envases/min (ciclo de 0,6 s); 1 562 000 envases, 31 400 rechazados. El preventivo se hace los sábados, fuera del tiempo planificado.

| Indicador | Cálculo | Resultado |
|---|---|---|
| MTBF / MTTR / MDT | 306/9; 13,5/9; 18/9 | 34,0 h / 1,50 h / 2,00 h |
| Ai | 34/(34 + 1,5) | 95,8 % |
| Ao | 34/(34 + 2) = 306/(306 + 18) | 94,4 % |
| R(8 h), un turno sin fallas | e^(−8/34) | 79,0 % (R = 90 % solo hasta 3,58 h) |
| Disponibilidad del OEE | 306/330 | 92,7 % |
| Rendimiento | 0,6 s·1 562 000/(306 h·3600) | 85,1 % |
| Calidad | 1 530 600/1 562 000 | 98,0 % |
| OEE | 0,9273·0,8508·0,9799 = 1 530 600·0,6/(330·3600) | 77,3 % |
| Costo del mes | directo 3 005 000 + parada 18 h·180 000 $/h | $ 6 245 000 ($ 4,08 por envase bueno) |

Costo directo: 67 h-h a $ 15 000, $ 1 600 000 de repuestos y materiales y $ 400 000 de terceros. Lectura: la mayor pérdida del OEE es el rendimiento (45,7 h contra 24 h de disponibilidad y 5,2 h de calidad): microparadas y velocidad reducida, que no se ven en el MTBF. La diferencia entre Ai y Ao son las 4,5 h de espera: stock de repuestos críticos. El costo de la parada es el 52 % del total.

**Pareto de las horas de parada** (`pareto ../plantilla/registro-fallas-ejemplo.csv`):

| Equipo y causa | Horas | % | % acumulado |
|---|---|---|---|
| Llenadora: válvulas de llenado (goteo), 3 fallas | 6,0 | 33,3 % | 33,3 % |
| Tapadora: embrague del cabezal, 2 fallas | 5,0 | 27,8 % | 61,1 % |
| Transportador: cadena trabada, 1 falla | 4,0 | 22,2 % | 83,3 % |
| Etiquetadora: sensor de etiqueta, 2 fallas | 1,5 | 8,3 % | 91,7 % |
| Encajonadora: ventosas, 1 falla | 1,5 | 8,3 % | 100,0 % |

Las tres primeras causas son las «pocas vitales» (83 % de las horas).

**AMFE corto de la llenadora** (`amfe ../plantilla/amfe-ejemplo.csv`; escalas de máquinas: S por horas de parada, O por MTBF del modo de falla, D por probabilidad de detección; ver [analisis-de-fallas.md](references/analisis-de-fallas.md)):

| Componente: modo de falla | S | O | D | NPR | Acción | S'·O'·D' = NPR' |
|---|---|---|---|---|---|---|
| Motor principal: rodamiento dañado, parada de 4 a 8 h | 7 | 4 | 8 | 224 | Plan de relubricación SKF y vibraciones mensuales con alarma | 7·3·3 = 63 |
| Válvulas de llenado: junta gastada que gotea | 6 | 7 | 5 | 210 | Cambio preventivo de juntas cada 250 h | 6·4·4 = 96 |
| Sensor de nivel: lente sucia, pasan envases mal llenados | 6 | 5 | 6 | 180 | Limpieza y prueba con envase patrón en cada turno | 6·3·3 = 54 |
| Cadena de la estrella: estirada o sin lubricar | 6 | 5 | 4 | 120 | Lubricación diaria y medición mensual del estiramiento | 6·3·4 = 72 |

La suma de NPR baja de 734 a 285 (61,2 %). La severidad no cambia: para bajarla hay que cambiar el diseño o el proceso.

## Análisis de fallas

- **Pareto** (Juran): ordenar las causas por horas de parada o costo, no solo por cantidad, y atacar las que suman alrededor del 80 %.
- **Ishikawa**: efecto en la cabeza y causas en las 6 M (máquina, método, materiales, medición, mano de obra, medio ambiente).
- **5 porqués** (Ohno, Toyota): preguntar «¿por qué?» hasta llegar a una causa sobre la que se puede actuar; puede haber más de una causa raíz.
- **AMFE**: por componente, modo de falla, efecto, causa y control actual; S, O y D de 1 a 10 con una escala escrita en el informe; NPR = S·O·D. Primero las severidades de 9 y 10 aunque su NPR sea bajo; preferir acciones que bajen O a las que solo bajan D. No hay un umbral universal de NPR, y el manual AIAG-VDA (2019) lo reemplazó por la prioridad de acción (AP).

## Plan de mantenimiento preventivo

1. Inventario de equipos con código y criticidad (qué pasa si fallan: seguridad, producción, calidad, costo).
2. Tareas por modo de falla desde el manual del fabricante (manda), el AMFE y el registro de fallas.
3. Para cada tarea: tipo, frecuencia con su fuente, quién (operador o mantenimiento), si exige parar y bloquear, duración, materiales y criterio de aceptación medible.
4. Rutas y calendario agrupados por equipo y frecuencia; lo que pide máquina parada, en las paradas planificadas.
5. Repuestos críticos en stock, una orden de trabajo por tarea y revisión mensual de las frecuencias con los indicadores.

Plan, orden de trabajo y planilla de inspección listos para completar en [plantillas.md](references/plantillas.md).

## Técnicas predictivas y de precisión

**Cada cuánto engrasar un rodamiento** (catálogo SKF *Rolling bearings*, PUB BU/P1 17000/1; detalle en [tecnicas-predictivas.md](references/tecnicas-predictivas.md)):

1. Factor de velocidad A = n·dm [mm/min], dm = (d + D)/2; con el factor bf del tipo de rodamiento (1 para rígidos de bolas) se controla el límite de la tabla de SKF (rígidos de bolas: 500 000 mm/min con C/P ≥ 15).
2. Con A·bf y la curva de C/P se lee tf en el diagrama de SKF (70 °C, eje horizontal, ambiente limpio), en horas de funcionamiento.
3. Ajustes: la mitad por cada 15 °C sobre 70 °C; ×2, una sola vez, si está 15 °C o más por debajo (nunca en llenos ni axiales); la mitad en eje vertical, con d > 300 mm o con ciertas jaulas; n·D si gira el aro exterior; nunca más de 30 000 h.
4. Grasa a reponer: Gp = 0,005·D·B [g] por el costado y 0,002·D·B por el aro exterior.

Ejemplo del curso de SKF: 61868 MA a 500 rpm, dm = 380 mm → A = 190 000 mm/min; con carga liviana el diagrama da hasta 10 000 h y, como d = 340 mm > 300 mm, se toma la mitad: 5000 h; Gp = 0,005·420·38 = 79,8 g. Un 6309 de motor (45 × 100 × 25 mm) a 1480 rpm: A = 107 300 mm/min y Gp = 12,5 g; a 85 °C, la mitad del tf leído. Si la placa o el manual del motor da intervalo y gramos, manda eso; los rodamientos tapados de fábrica no se engrasan.

```
python mantenimiento.py relubricacion --d 340 --D 420 --B 38 --rpm 500 --tipo rigido-bolas --tf 10000
```

**Vibraciones de un motor** (ISO 20816-3:2022, máquinas de más de 15 kW): velocidad eficaz de banda ancha (10 Hz a 1000 Hz) en mm/s, en dos direcciones radiales de cada cojinete. Grupo 1: más de 300 kW o H ≥ 315 mm; grupo 2: más de 15 kW hasta 300 kW o 160 mm ≤ H < 315 mm.

| Grupo y soporte | A/B | B/C | C/D [mm/s] |
|---|---|---|---|
| 1 rígido / 1 flexible | 2,3 / 3,5 | 4,5 / 7,1 | 7,1 / 11,0 |
| 2 rígido / 2 flexible | 1,4 / 2,3 | 2,8 / 4,5 | 4,5 / 7,1 |

Zona A: máquina nueva; B: sin restricciones; C: tiempo limitado, planificar la corrección; D: puede dañarse. ALARMA = base + 25 % de B/C (hasta 1,25·B/C); DISPARO hasta 1,25·C/D. Ejemplo: motor de la llenadora, carcasa 160 (grupo 2, base rígida), base 1,1 mm/s, medido 3,2 mm/s → zona C; ALARMA 1,8 mm/s; DISPARO hasta 5,6 mm/s (`vibracion --v 3,2 --altura 160 --base 1,1`). Espectro: 1× desbalance; 2× radial o 1× axial, desalineación.

**Termografía** (ANSI/NETA MTS, tabla 100.18): ΔT entre componentes similares de 1 a 3 °C, investigar; de 4 a 15 °C, reparar cuando se pueda; más de 15 °C (o más de 40 °C sobre el ambiente), reparar de inmediato. Medir con carga y anotarla.

**Alineación** (guía de SKF, TKSA 20): a 1000 a 2000 rpm, paralelo ≤ 0,10 mm y angular ≤ 0,08 mm/100 mm; la pata coja (menos de 0,05 mm) se corrige antes. **Balanceo** (ISO 21940-11): Uper = 9549·G·m/n [g·mm]; ventilador de 25 kg a 1480 rpm con G 6,3: 1016 g·mm.

## Seguridad: bloqueo y etiquetado

Antes de intervenir (OSHA 29 CFR 1910.147; en Argentina, consignación del Decreto 351/79, Anexo VI): preparar, parar, aislar cada energía, colocar candado personal y tarjeta, liberar la energía acumulada y verificar que no arranca y que no hay tensión. Cada uno saca su propio candado, después de revisar la zona y avisar. Procedimiento modelo en [seguridad-bloqueo.md](references/seguridad-bloqueo.md); marco legal en **normas-tecnicas-ar**.

El marco legal de higiene y seguridad (riesgo eléctrico, máquinas, EPP) está en **higiene-y-seguridad**; el mantenimiento de equipos hidráulicos (aceite, filtros, mangueras), en **oleohidraulica**.

## Errores frecuentes

- Calcular el MTBF con el tiempo calendario o el planificado en vez del de funcionamiento.
- Poner la espera de repuestos en el MTTR: va al MDT y a la Ao.
- Confundir la disponibilidad del OEE (incluye cambios de formato) con la de mantenimiento.
- Tomar el MTBF como tiempo garantizado: con tasa constante, R(MTBF) = e^(−1) = 36,8 %.
- Usar la confiabilidad exponencial en piezas que se desgastan.
- Poner en el OEE la velocidad de un día bueno en vez de la ideal: da rendimientos de más de 100 % (el script lo rechaza).
- Pareto solo por cantidad de fallas; AMFE que ignora S de 9 o 10 por tener NPR bajo, o que compara NPR hechos con escalas distintas.
- Engrasar de más o «a ojo», o engrasar rodamientos tapados.
- Comparar vibración pico con eficaz (√2 en una senoidal) o mm/s con mm, o aplicar ISO 20816-3 a máquinas de 15 kW o menos.
- Intervenir sin candado propio o sin verificar la ausencia de energía.

## Verificación

`python mantenimiento.py demo` tiene que terminar en `DEMO OK` (si algo no coincide, sale con código 1). Reproduce el ejemplo de esta página y controla: Ao por MTBF y por tiempos, OEE por el producto y por la fórmula simple, horas que suman 330, Pareto y AMFE desde las plantillas CSV de `plantilla/`, el ejemplo publicado por oee.com (OEE 74,79 %), el ejemplo del curso de SKF (A = 190 000 mm/min), los bordes de las zonas de ISO 20816-3, el ejemplo de balanceo de IRD (21 oz·in) y la tabla de NETA. Para una entrega, una revisión independiente con **revision-tecnica** o **equipo-de-modelos**.
