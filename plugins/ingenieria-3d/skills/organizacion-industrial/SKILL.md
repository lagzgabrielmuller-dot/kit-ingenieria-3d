---
name: organizacion-industrial
description: "Organización industrial y evaluación de proyectos para técnicos electromecánicos, con script de cálculo: costos fijos y variables, costo unitario, punto de equilibrio, amortización lineal, flujo de fondos, VAN, TIR, recupero y beneficio/costo en dólares o moneda constante; estudio de tiempos con suplementos de la OIT, tiempo estándar y muestreo; cursograma ASME; capacidad, cuello de botella y balanceo de línea; layout de la planta; diagrama de Gantt, CPM y PERT; Pareto, Ishikawa, gráfico de control X-R, Cp y Cpk; 5S y Lean. Usar cuando pregunten si es rentable el proyecto, pidan los costos del proyecto final, el punto de equilibrio, el flujo de fondos, el VAN o la TIR, un estudio de tiempos o el tiempo estándar, un diagrama de Gantt, un PERT o el camino crítico, el balanceo de línea, el layout de la planta, un gráfico de control o el Cpk, o un trabajo de organización industrial."
---

# Organización industrial y evaluación de proyectos

`scripts/organizacion.py` (Python 3.9+, solo biblioteca estándar) hace cada cuenta e imprime fórmula, reemplazo y resultado con coma decimal, listo para la memoria de cálculo (formato en **calculos-ingenieria**). El capítulo económico del informe se arma con **informe-tecnico** y se defiende con **exposicion-oral**. Los indicadores de mantenimiento (MTBF, MTTR, disponibilidad, OEE) están en **mantenimiento-industrial**, y la seguridad de la planta, en **higiene-y-seguridad**.

En la línea de comandos van punto decimal y listas con coma. Si la lista empieza con un negativo, se escribe con `=`: `--flujos=-70000,26800`.

Referencias, según el tema:
- [references/evaluacion-economica.md](references/evaluacion-economica.md): costos de un proyecto, estructura del flujo de fondos con impuestos, inflación, tasa de descuento y trampas de la TIR. Leer antes de armar el estudio económico.
- [references/metodos-y-tiempos.md](references/metodos-y-tiempos.md): símbolos y tipos de cursograma, pasos del estudio de tiempos, tabla de suplementos de la OIT y muestreo del trabajo. Leer antes de un estudio de tiempos.
- [references/produccion-y-planificacion.md](references/produccion-y-planificacion.md): capacidad, reglas de balanceo, tipos de layout y método SLP, CPM y PERT paso a paso y formato de los archivos. Leer para resolver a mano o cargar datos.
- [references/calidad-y-mejora.md](references/calidad-y-mejora.md): tabla completa de constantes, reglas de Western Electric, Cp y Cpk, Pareto, Ishikawa, 5S y Lean. Leer para un plan de calidad.

## Método (proyecto final o trabajo de la materia)

1. Fijar la **moneda** y escribirla: dólares constantes o pesos constantes de un año base, con tasa real. Nunca pesos corrientes con tasa real.
2. **Costos** fijos y variables, costo unitario y punto de equilibrio.
3. **Inversión** (equipos con cotización, fuente y fecha; obra; instalación; capital de trabajo) y **amortización**.
4. **Flujo de fondos** del horizonte (5 a 10 años): VAN, TIR, recupero y B/C, y sensibilidad del VAN al precio, a la cantidad y a la inversión (±10 y ±20 %).
5. **Producción**: tiempos, capacidad y cuello de botella, balanceo y layout.
6. **Plan de obra** (Gantt, CPM o PERT) y **plan de calidad** (gráficos de control y Cpk).

## Costos y punto de equilibrio

| Clase | Qué es | Ejemplos |
|---|---|---|
| Fijo (CF) | no cambia con la cantidad del período | alquiler, sueldos de supervisión, seguros, amortizaciones |
| Variable (cv·Q) | proporcional a la cantidad | materia prima, energía de proceso, embalaje |
| Directo | se asigna a un producto sin repartir | material y mano de obra del producto |
| Indirecto | se reparte con una base (horas máquina, m², unidades) | mantenimiento, iluminación, administración |

- Costo unitario: cu = cv + CF/Q [$/u], con Q la cantidad del período.
- Margen de contribución: mc = p − cv [$/u]; razón de contribución mc/p.
- Punto de equilibrio: Qe = CF/(p − cv) [u/período]; en ventas, Ve = CF/(1 − cv/p) = Qe·p [$/período].
- Utilidad U = Q·mc − CF; margen de seguridad (Q − Qe)/Q; para una utilidad objetivo, Q = (CF + U)/mc.

## Amortización

Lineal: A = (V0 − VR)/n [$/año], con V0 el valor de origen, VR el valor residual y n la vida útil en años. Otros métodos (solo nombrados): suma de los dígitos de los años, saldo decreciente y por unidades producidas u horas de uso. La amortización no es una salida de caja, pero baja el impuesto (ahorro t·A por año). Si se usa la vida útil impositiva, citar la norma (verificar en la norma vigente).

## Evaluación del proyecto

- Flujo de fondos de cada año: FF = (I − C − A)·(1 − t) + A − inversiones − aumento del capital de trabajo + valor residual, con I los ingresos, C los costos desembolsables, A la amortización y t la alícuota del impuesto a las ganancias.
- VAN = Σ FFt/(1 + i)^t, de t = 0 a n, con i la tasa de descuento por período.
- TIR: la tasa que anula el VAN (el script la busca por bisección y la confirma con Newton).
- Recupero simple: el año en que el acumulado de FF llega a cero, interpolando; el descontado, lo mismo con FFt/(1 + i)^t.
- B/C = VA de los flujos positivos / VA de los negativos.
- Decisión con un solo cambio de signo en el flujo: VAN > 0 ⇔ TIR > i ⇔ B/C > 1, y el proyecto es rentable a esa tasa. Con más cambios de signo puede haber varias TIR (el script las lista): se decide por el VAN.
- **Tasa de descuento**: el costo de oportunidad, es decir, lo que rendiría el dinero en otra inversión de riesgo parecido. En dólares se arma con la tasa de un bono del Tesoro de EE. UU., el riesgo país y una prima por el riesgo del proyecto. Va siempre como supuesto explícito, con sensibilidad.
- **Inflación (Fisher)**: (1 + i) = (1 + r)·(1 + π), con i nominal, r real y π la inflación del período. El formulario EGEL IINDU del CENEVAL la usa para la TMAR. Flujos constantes van con tasa real; corrientes, con nominal. Con inflación alta no sirve r ≈ i − π. A moneda constante: Ct = Ft·IPC0/IPCt, con el IPC del INDEC.

## Ejemplo resuelto (USD constantes de 2026, tasa real)

Una planta que fabrica soportes metálicos evalúa una línea nueva (datos inventados).

| Dato | Valor |
|---|---|
| Precio p y costo variable cv | 25 y 13 USD/u |
| Costos fijos | 48 000 USD/año (38 000 desembolsables + 10 000 de amortización) |
| Ventas previstas | 6 000 u/año |
| Máquina | V0 = 60 000 USD, VR = 10 000 USD, n = 5 años → A = 10 000 USD/año |
| Capital de trabajo | 10 000 USD en el año 0, recuperado en el año 5 |
| Impuesto a las ganancias | t = 30 % (supuesto del ejemplo; usar la alícuota vigente) |
| Tasa de descuento | i = 12 % anual, real en dólares (supuesto) |

1. Equilibrio (`equilibrio --cf 48000 --precio 25 --cv 13 --cantidad 6000`): mc = 12 USD/u (48 %); Qe = 48 000/12 = 4 000 u/año; Ve = 48 000/0,48 = 100 000 USD/año. Con 6 000 u: U = 24 000 USD/año, cu = 21 USD/u y margen de seguridad de 33,3 %.
2. Flujo de los años 1 a 5: (150 000 − 78 000 − 38 000 − 10 000)·(1 − 0,30) + 10 000 = 26 800 USD. El año 0 es −70 000 (máquina y capital de trabajo); el año 5 suma 20 000 (valor residual igual al de libro, sin impuesto, y capital de trabajo): 46 800.
3. `python organizacion.py van --flujos=-70000,26800,26800,26800,26800,46800 --tasa 12 --moneda "USD constantes de 2026"` → VAN = 37 956,54 USD; TIR = 30,46 %; recupero simple de 2,61 años y descontado de 3,33 años; B/C = 1,54. Es rentable al 12 %.
4. Control con otra fórmula: VAN = −70 000 + 26 800·FA + 20 000/1,12⁵, con FA = (1 − 1,12⁻⁵)/0,12 = 3,6048 → 37 956,54 USD.
5. En pesos corrientes, con 30 % de inflación anual, la tasa sería (1,12)·(1,30) − 1 = 45,6 % (`inflacion --real 12 --inflacion 30`). Si todos los flujos acompañan a la inflación, el VAN da lo mismo; con la amortización sin actualizar, no (ver la referencia).

## Estudio de métodos y tiempos

Cursograma analítico con los símbolos de la ASME (adoptados en 1947 a partir de los de Gilbreth). Al lado de cada paso van la distancia [m] y el tiempo [min]. Detalle y ejemplo en la referencia.

| ○ Operación | ⇨ Transporte | □ Inspección | D Espera | ▽ Almacenamiento |
|---|---|---|---|---|
| se modifica o prepara | se mueve de lugar | se controla calidad o cantidad | queda detenido | queda guardado bajo control |

- Tiempo observado TO: media de los ciclos cronometrados [min].
- Tiempo normal (básico, para la OIT): TN = TO·V/100, con V la valoración del ritmo en % (100 = ritmo normal).
- Tiempo estándar (tipo, para la OIT): TS = TN·(1 + S), con S los suplementos como fracción del tiempo normal. Si la empresa los da sobre la jornada, TS = TN/(1 − S) (Niebel y Freivalds, 12.ª ed., 2009).
- Producción por turno: T_turno/TS, redondeada hacia abajo.
- Observaciones necesarias: n = (t·s/(k·x̄))², con t de Student para N − 1 grados de libertad, s el desvío de la muestra, x̄ la media y k el error admitido (0,05) (Niebel y Freivalds, ejemplo 10.1).
- Muestreo del trabajo: p = k/N y N = z²·p·(1 − p)/e², con k las veces que se vio la actividad en N observaciones, e el error absoluto y z = 1,96 al 95 %.

| Suplementos de la OIT (extracto) | Hombres [%] | Mujeres [%] |
|---|---|---|
| Necesidades personales (constante) | 5 | 7 |
| Fatiga básica (constante) | 4 | 4 |
| Trabajo de pie | 2 | 4 |
| Postura ligeramente incómoda / incómoda / muy incómoda | 0 / 2 / 7 | 1 / 3 / 7 |
| Trabajo de cierta precisión / preciso / de gran precisión | 0 / 2 / 5 | 0 / 2 / 5 |
| Tensión mental: bastante complejo / complejo / muy complejo | 1 / 4 / 8 | 1 / 4 / 8 |
| Monotonía: algo / bastante / muy monótono | 0 / 1 / 4 | 0 / 1 / 4 |

Fuente: tabla de la OIT reproducida en Niebel y Freivalds (2009), tabla 11.9, y en CENEVAL, Formulario EGEL Plus IINDU (2021), tabla 3. La tabla completa (iluminación, ruido, aire, tedio) está en la referencia. Los valores por peso levantado difieren entre versiones (verificar en la tabla que use la cátedra).

Ejemplo: 10 ciclos de agujereado (TO = 1,230 min), V = 110 % y suplementos 5 + 4 + 2 (de pie) + 2 (trabajo preciso) = 13 %:
`python organizacion.py tiempos --obs 1.20,1.25,1.18,1.22,1.30,1.24,1.19,1.21,1.26,1.25 --valoracion 110 --suplementos 5,4,2,2 --turno 480` → TN = 1,353 min; TS = 1,529 min; 313 piezas por turno de 480 min. Alcanzan 2 observaciones y se tomaron 10.
Muestreo: 60 paradas en 400 recorridos dan p = 15 % ± 3,5 %; para ±3 % hacen falta 545 (`muestreo --ocurrencias 60 --total 400 --error 3`).

## Capacidad, cuello de botella y balanceo de línea

- Capacidad de una estación: C = m·T·η/t [u/período], con m las máquinas iguales, T el tiempo disponible, η la fracción productiva y t el tiempo por unidad. La línea produce lo que su estación más lenta, el cuello de botella. Eficiencia = producción real/capacidad efectiva (CENEVAL).
- Balanceo: tiempo de ciclo C = T/D, con T el tiempo productivo y D la demanda del período (en Lean, takt time). Estaciones mínimas: Nt = ⌈Σt/C⌉. Eficiencia: E = Σt/(N·C). Retraso del balance: 1 − E.
- Asignación: se abre una estación y se le carga, entre las tareas que tienen sus precedentes asignados y entran en el tiempo que queda, la de más tareas sucesoras (o la de mayor peso posicional, o la de mayor tiempo). Cuando no entra ninguna, se abre otra.

Ejemplo de capacidad, con 480 min por turno: `capacidad --tiempos 1.2,1.53,2.0,0.9 --disponible 480 --nombres corte,agujereado,plegado,pintura --demanda 260` → el cuello de botella es el plegado (240 u por turno) y faltan 20 u. Con una segunda plegadora, el cuello pasa al agujereado (313,7 u por turno).
Ejemplo de balanceo: 10 tareas que suman 300 s y 420 u en 7 h (25 200 s) dan C = 60 s y Nt = 5. `balanceo tareas.csv --disponible 25200 --demanda 420` (archivo de `balanceo --ejemplo`) → 6 estaciones y E = 83,3 %. Con 5 no se puede, porque después de A (40 s) no queda disponible ninguna tarea de 20 s.

## Distribución en planta (layout)

| Tipo | Cuándo conviene | Ejemplo |
|---|---|---|
| Por posición fija | producto grande o pesado que no se mueve | montaje de una secadora industrial |
| Por proceso (funcional) | mucha variedad y poco volumen; máquinas agrupadas por función | taller de mecanizado a pedido |
| Por producto (en línea) | poca variedad y mucho volumen; máquinas en el orden de las operaciones | línea de armado de soportes |
| Celular | familias de piezas parecidas y volumen medio | celda de torno CNC, fresadora y control para bujes |

El tipo se elige por volumen y variedad (análisis producto-cantidad), recorridos, relaciones entre sectores, espacio, ampliaciones y seguridad (**higiene-y-seguridad**). Las relaciones se califican con los códigos A, E, I, O, U y X del método SLP de Muther (tabla en la referencia). Para comparar alternativas se usa Σ carga·distancia entre sectores: gana la menor.

## Planificación: Gantt, CPM y PERT

- Ida: IT = máx(FT de las precedentes) y FT = IT + d. Vuelta: FR = mín(IR de las siguientes) e IR = FR − d. IT y FT son el inicio y el fin más tempranos; IR y FR, los más tardíos.
- Holgura total HT = IR − IT; holgura libre HL = mín(IT de las siguientes) − FT. Camino crítico: las actividades con HT = 0, que fijan la duración T del proyecto.
- PERT (Malcolm y otros, 1959): te = (a + 4·m + b)/6 y σ² = ((b − a)/6)², con a el tiempo optimista, m el más probable y b el pesimista. Con la varianza del camino crítico, P(T ≤ plazo) = Φ((plazo − T)/σ).
- Gantt: una barra por actividad desde su IT y la holgura a continuación (`cpm --gantt` lo dibuja en texto). Para el informe se pasa a una planilla o a un programa de proyectos.

Ejemplo (montaje de una máquina, en días): `cpm red.csv --plazo 24 --probabilidad 0.95 --gantt` (archivo de `cpm --ejemplo`) → T = 21 días y camino crítico A–B–E–F–G. Holguras: C 5, D 10 y H 1 día. σ = 2,186 días, P(T ≤ 24) = 91,5 % y plazo al 95 % de 24,6 días.

## Control de calidad

- Pareto: defectos ordenados de mayor a menor con el % acumulado; los pocos que suman cerca del 80 % se atacan primero. Ishikawa: causas agrupadas en mano de obra, máquina, método, material, medición y medio ambiente (6M).
- Gráfico X̄-R con k subgrupos de n piezas: X̿ = ΣX̄/k y R̄ = ΣR/k. Límites de X̄: X̿ ± A2·R̄. Límites de R: LCS = D4·R̄ y LCI = D3·R̄.
- Capacidad: σ̂ = R̄/d2; Cp = (LES − LEI)/(6·σ̂); Cpk = mín[(LES − X̿)/(3·σ̂); (X̿ − LEI)/(3·σ̂)]. Con Cpk < Cp el proceso está descentrado; con Cp < 1 la dispersión no entra en la tolerancia.

| n | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|
| A2 | 1,880 | 1,023 | 0,729 | 0,577 | 0,483 |
| D3 | 0 | 0 | 0 | 0 | 0 |
| D4 | 3,267 | 2,575 | 2,282 | 2,115 | 2,004 |
| d2 | 1,128 | 1,693 | 2,059 | 2,326 | 2,534 |

Fuente: A2, D3 y D4, NIST/SEMATECH e-Handbook of Statistical Methods, sección 6.3.2.1 (hasta n = 10 en la referencia). d2 se calculó por integración numérica y cumple A2 = 3/(d2·√n).

Ejemplo: 10 subgrupos de 5 diámetros con tolerancia 20,00 ± 0,05 mm. `calidad sub.csv --lei 19.95 --les 20.05` (archivo de `calidad --ejemplo`) → X̿ = 20,0088 mm y R̄ = 0,0314 mm; X̄ entre 19,9907 y 20,0269 mm; R hasta 0,0664 mm. El proceso está bajo control, pero con Cp = 1,23 y Cpk = 1,02 hay que centrarlo.

## Mejora continua

- 5S (Hirano, 1995): seiri (clasificar), seiton (ordenar), seisō (limpiar), seiketsu (estandarizar) y shitsuke (sostener con disciplina).
- Lean: eliminar los siete desperdicios de Ohno (1988), que son sobreproducción, esperas, transporte, procesos de más, inventario, movimientos y defectos, además de la sobrecarga (muri) y el desparejo (mura). Herramientas: kaizen, kanban, SMED, poka-yoke y flujo al ritmo de la demanda (takt time).

## Errores frecuentes

- No decir en qué moneda está el flujo, o descontar pesos corrientes con una tasa real.
- Restar la amortización como salida de caja, u olvidar sumarla de vuelta después del impuesto.
- Usar r ≈ i − π con inflación alta.
- Elegir entre proyectos excluyentes por la TIR en lugar del VAN, o usar la TIR con flujos que cambian varias veces de signo.
- Presentar el recupero simple como único criterio.
- Aplicar la valoración dos veces, o sumar los suplementos al tiempo observado en lugar del normal.
- Redondear hacia arriba la producción por turno, o hacia abajo las estaciones mínimas.
- Balancear sin respetar las precedencias, o con un ciclo menor que la tarea más larga.
- Calcular Cp y Cpk con el proceso fuera de control, o confundir la tolerancia con los límites de control.

## Verificación

`python organizacion.py --help` lista los comandos y `python organizacion.py demo` tiene que terminar en `DEMO OK`. El demo reproduce el ejemplo resuelto: VAN por suma y por anualidad, TIR por bisección y por Newton, la equivalencia real-nominal de Fisher, tiempos, muestreo, capacidad, balanceo con control de precedencias, CPM contra la lista de todos los caminos y PERT. Además recalcula A2, D3 y D4 por integración y los compara con la tabla del NIST, y reproduce el ejemplo de Cp y Cpk del NIST (6.1.6), el ejemplo 10.1 de Niebel y Freivalds y los valores de t de la tabla del NIST (1.3.6.7.2). Para una entrega, conviene una revisión independiente con **revision-tecnica** o **equipo-de-modelos**.
