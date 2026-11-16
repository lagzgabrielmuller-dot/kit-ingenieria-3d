# Indicadores de mantenimiento: definiciones, fuentes y detalle

Leer cuando haya que citar la definición de un indicador, separar bien los tiempos de un registro, calcular el OEE con datos de producción o el costo del mantenimiento. Las cuentas las hace `scripts/mantenimiento.py` (subcomandos `indicadores`, `confiabilidad`, `oee` y `costo`).

## 1. Tiempos del período

| Tiempo | Qué incluye | Dónde se usa |
|---|---|---|
| Calendario o de turnos | Todas las horas del período (o de los turnos habilitados) | Referencia |
| Planificado de producción (requerido) | Turnos menos pausas, limpiezas y paradas programadas fuera de producción | Base de la disponibilidad del OEE |
| Funcionamiento (en marcha) | Planificado menos todas las paradas | MTBF, MTBM, Ao, rendimiento del OEE |
| Reparación activa (TTR) | Diagnóstico, reparación y prueba de cada falla | MTTR, Ai |
| Esperas | Repuestos, personal, herramientas, permisos y trámites | MDT, Ao |
| Preventivo dentro del tiempo requerido | Intervenciones programadas que paran la producción | MTBM, MDT, Ao |
| Otras paradas | Cambios de formato, ajustes, falta de material | Disponibilidad del OEE (no son mantenimiento) |

El dato sale de las órdenes de trabajo (hora de parada, de comienzo y de fin de la reparación, de puesta en marcha) y del parte de producción. Modelos en [plantillas.md](plantillas.md).

## 2. MTBF, MTTR, MDT y disponibilidad

Definiciones de la *DoD Guide for Achieving Reliability, Availability, and Maintainability* (Departamento de Defensa de EE. UU., 3/8/2005, sección 3.2.4, págs. 3-10 a 3-12 y tabla 3-4; [copia archivada](https://webarchive.library.unt.edu/web/20130305103248/http://www.acq.osd.mil/se/docs/RAM_Guide_080305.pdf)) y del *DoD RAM-C Rationale Report Manual* (1/6/2009, tabla 3-1; [copia archivada](https://webarchive.library.unt.edu/web/20161117071716/http://www.acq.osd.mil/se/docs/DoD-RAM-C-Manual.pdf)):

| Símbolo | Definición | Fórmula con datos de un período |
|---|---|---|
| MTBF [h] | Tiempo medio entre fallas | MTBF = Tf/Nf (Tf: horas de funcionamiento; Nf: fallas) |
| λ [fallas/h] | Tasa de fallas | λ = Nf/Tf = 1/MTBF |
| MTTR [h] | Tiempo medio de reparación, **solo reparación activa** | MTTR = ΣTTR/Nf |
| MTBM [h] | Tiempo medio entre intervenciones de mantenimiento (correctivas y preventivas) | MTBM = Tf/(Nf + Np) |
| MDT [h] | Tiempo medio de parada por mantenimiento: incluye el MTTR, las demoras logísticas y las administrativas | MDT = (ΣTTR + Σesperas + Σpreventivo)/(Nf + Np) |
| Ai | Disponibilidad inherente: solo efectos de diseño y mantenibilidad | Ai = MTBF/(MTBF + MTTR) |
| Ao | Disponibilidad operativa: suma mantenimiento preventivo, logística y organización | Ao = MTBM/(MTBM + MDT) = Tf/(Tf + paradas por mantenimiento) |

Para equipos que no se reparan se usa el MTTF (tiempo medio hasta la falla). Con distribución exponencial de los tiempos hasta la falla, el MTTF es la inversa de la tasa de fallas, y vale lo mismo para equipos que quedan «como nuevos» después de cada reparación (IEC 60050-192, término 192-05-11, [Electropedia](https://electropedia.org/iev/iev.nsf/IEVref_xref/en:192-05-11)).

**Ejemplo con preventivo** (verificado en el `demo`): si en la línea de SKILL.md hubiera además 2 preventivos de 1,5 h dentro del tiempo requerido, MTBM = 306/11 = 27,82 h, MDT = (13,5 + 4,5 + 3)/11 = 1,909 h y Ao = 27,82/(27,82 + 1,909) = 93,58 % = 306/(306 + 21).

## 3. Confiabilidad con tasa de fallas constante

Distribución exponencial (NIST/SEMATECH, *e-Handbook of Statistical Methods*, sección 8.1.6.1, [Exponential](https://www.itl.nist.gov/div898/handbook/apr/section1/apr161.htm)): R(t) = e^(−λ·t), F(t) = 1 − R(t), tasa de fallas h(t) = λ constante y media 1/λ. Modela el tramo plano de la curva de la bañera, donde los equipos pasan la mayor parte de su vida.

| t/MTBF | 0,05 | 0,1 | 0,25 | 0,5 | 1 | 2 |
|---|---|---|---|---|---|---|
| R(t) | 95,1 % | 90,5 % | 77,9 % | 60,7 % | 36,8 % | 13,5 % |

(valores de e^(−t/MTBF), calculados). Con tasa constante, solo el 36,8 % de los equipos llega a funcionar un MTBF sin fallar: el MTBF es un promedio, no una garantía.

- Tiempo para una confiabilidad pedida: t = −MTBF·ln R.
- **Serie** (si falla uno, para el sistema): R = R1·R2·…·Rn y las tasas de fallas se suman (NIST, sección 8.1.8.2, [Series model](https://www.itl.nist.gov/div898/handbook/apr/section1/apr182.htm)).
- **Paralelo** (redundancia: alcanza con que funcione uno): la probabilidad de falla del sistema es el producto de las de los componentes, F = F1·F2·…, así que R = 1 − (1 − R1)·(1 − R2)·… (NIST, sección 8.1.8.3, [Parallel or redundant model](https://www.itl.nist.gov/div898/handbook/apr/section1/apr183.htm)).
- Si hay desgaste (la tasa de fallas crece con la edad) el modelo exponencial ya no sirve: se usa, por ejemplo, la distribución de Weibull, que está en la misma sección del manual de NIST.

## 4. OEE (eficiencia general de los equipos)

Definiciones de [oee.com, Calculating OEE](https://www.oee.com/calculating-oee/):

- Tiempo planificado de producción = duración del turno − pausas.
- Tiempo en marcha = planificado − paradas; las paradas son todo el tiempo en que se pensaba producir y no se produjo, sean no planificadas (fallas) o planificadas (cambios de formato).
- Disponibilidad A = tiempo en marcha/tiempo planificado.
- Rendimiento P = (tiempo de ciclo ideal·cantidad total)/tiempo en marcha.
- Calidad Q = cantidad buena/cantidad total.
- OEE = A·P·Q, que es igual a (cantidad buena·tiempo de ciclo ideal)/tiempo planificado.

Ejemplo publicado en esa página (lo reproduce el `demo`): turno de 480 min con 60 min de pausas → 420 min planificados; 47 min de paradas → 373 min en marcha; ciclo ideal 1,0 s; 19 271 piezas, 423 malas → A 88,81 %, P 86,11 %, Q 97,80 %, **OEE 74,79 %**.

La norma internacional de indicadores de producción es **ISO 22400-2** (verificar la edición vigente): disponibilidad = APT/PBT (tiempo real de producción sobre tiempo ocupado planificado), eficacia = PRI·PQ/APT (tiempo de ciclo planificado por pieza por cantidad producida, sobre el tiempo real de producción), tasa de calidad = GQ/PQ, y el OEE es el producto de las tres, según la especificación OPC 40501-1 que la toma como base ([OPC Foundation, KPI Calculation](https://reference.opcfoundation.org/specs/OPC-40501-1/19)).

**Clase mundial**: OEE 85 % con disponibilidad 90 %, rendimiento 95 % y calidad 99 %, números que Nakajima incluyó en *Introduction to TPM*; la misma fuente aclara que nacieron en la industria automotriz japonesa de los años setenta, que valen para manufactura discreta, que la mayoría de las empresas está cerca de 60 % y que lo importante es mejorar el propio valor, no compararlo ([oee.com, World-Class OEE](https://oee.com/world-class-oee)).

**Pérdidas en horas** (ejemplo de SKILL.md, ciclo ideal 0,6 s):

| Concepto | Cálculo | Horas |
|---|---|---|
| Tiempo planificado | 352 − 22 | 330,0 |
| Pérdida por disponibilidad | fallas 18 h + cambios de formato 6 h | 24,0 |
| Pérdida por rendimiento | 306 − 1 562 000·0,6/3600 | 45,7 |
| Pérdida por calidad | 31 400·0,6/3600 | 5,2 |
| Tiempo plenamente productivo | 1 530 600·0,6/3600 | 255,1 |

255,1/330 = 77,3 % = OEE. La mayor pérdida es la de rendimiento (microparadas y velocidad reducida), que no aparece en el MTBF ni en la Ao.

**Disponibilidad del OEE y disponibilidad de mantenimiento no son lo mismo**: la del OEE (92,7 % en el ejemplo) se mide contra el tiempo planificado y cuenta los cambios de formato; la Ao (94,4 %) solo cuenta las paradas por mantenimiento.

## 5. Costo del mantenimiento

| Componente | Qué incluye |
|---|---|
| Directo | Mano de obra (horas-hombre propias por costo horario con cargas sociales), repuestos y materiales, servicios de terceros |
| Indirecto o de falla | Producción perdida durante las paradas no planificadas (margen que no se gana), horas extra para recuperar, descarte, multas por entregas tarde |
| Total | Directo + indirecto |

- Costo de la hora parada: margen de contribución por unidad × unidades por hora que se dejan de hacer, más los costos que siguen corriendo; lo da la empresa.
- Indicadores habituales: costo total por unidad buena; costo directo anual sobre el valor de reposición de los activos. La **EN 15341:2019** (*Maintenance — Maintenance Key Performance Indicators*) define los indicadores económicos de mantenimiento (código y definición exactos: verificar en la norma vigente).
- Un mantenimiento barato en directo puede ser caro en total: en el ejemplo de SKILL.md el costo de la parada es el 52 % del total del mes.
