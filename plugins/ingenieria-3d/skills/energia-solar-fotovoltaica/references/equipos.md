# Equipos: datos de hoja, pérdidas y protecciones de corriente continua

Leer este archivo para citar un dato del módulo, el regulador, el inversor, la batería o el motor del ejemplo, las pérdidas por defecto, o las reglas de cables, fusibles y seccionador. Son los valores que usa `scripts/fotovoltaica.py`; para otro equipo se toman de su hoja de datos. Las marcas son las de las hojas de datos que se consultaron: cualquier equipo equivalente sirve si se verifican los mismos parámetros.

## Módulo del ejemplo

LONGi LR5-72HBD-550M, hoja de datos 20240131V18Beta ([PDF del fabricante publicado por EnergySage](https://public.files.energysage.com/BHXji8WFypGps7lbPKScLg)). Es bifacial: se diseña con los valores de la cara frontal; la ganancia de la cara trasera no se cuenta sobre un techo.

| Dato | STC (1000 W/m², 25 °C, AM 1,5) | NOCT (800 W/m², 20 °C de aire, 1 m/s) |
|---|---|---|
| Potencia máxima Pmax | 550 W | 411,1 W |
| Tensión de circuito abierto Voc | 49,80 V | 46,82 V |
| Corriente de cortocircuito Isc | 13,99 A | 11,29 A |
| Tensión de máxima potencia Vmp | 41,95 V | 39,14 V |
| Corriente de máxima potencia Imp | 13,12 A | 10,51 A |

Eficiencia 21,5 %; NOCT 45 ± 2 °C; coeficientes de temperatura: Isc +0,050 %/°C, Voc −0,265 %/°C, Pmax −0,340 %/°C; tensión máxima del sistema 1500 V CC; corriente máxima de fusible en serie 30 A; temperatura de trabajo −40 °C a +85 °C; 2256 × 1133 × 35 mm; 32,3 kg.

## Temperatura de celda y coeficientes

- **NOCT:** temperatura que alcanzan las celdas en circuito abierto con 800 W/m², aire a 20 °C, viento de 1 m/s y la cara trasera libre. Temperatura de celda: Tc = Ta + (NOCT − 20)·G/800, con G en W/m² ([PVEducation, C. Honsberg y S. Bowden, «Nominal Operating Cell Temperature»](https://www.pveducation.org/pvcdrom/modules-and-arrays/nominal-operating-cell-temperature), que cita a R. G. Ross, 14.ª IEEE PVSC, 1980).
- **Montaje:** PVWatts toma una temperatura nominal de operación instalada (INOCT) de 45 °C para estructuras abiertas y de alrededor de 49 °C para módulos montados sobre el techo (A. P. Dobos, [*PVWatts Version 5 Manual*](http://www.nrel.gov/docs/fy14osti/62641.pdf), NREL/TP-6A20-62641, septiembre de 2014). Con poca ventilación detrás, la celda trabaja más caliente que la NOCT de la hoja.
- **Corrección:** X(T) = X_STC·(1 + c·(T − 25)), con c el coeficiente de la hoja en %/°C.
- **Voc máxima:** con la temperatura mínima del lugar, porque a la salida del sol la celda está a la temperatura del aire y ya hay tensión de circuito abierto. Es la que no puede pasar la tensión máxima del regulador o inversor.
- **Vmp mínima:** con la celda en el día más caluroso (máxima del aire y 1000 W/m²). Si la hoja no da el coeficiente de Vmp, se toma γ − α: de P = V·I, la variación relativa de la potencia es la de la tensión más la de la corriente. Contra la hoja del ejemplo: a NOCT da 38,68 V contra 39,14 V (−1,2 %, del lado seguro). Con γ a NOCT: 550·0,8·(1 − 0,0034·20) = 410,1 W contra 411,1 W (−0,25 %).

## Pérdidas

Pérdidas por defecto de PVWatts v5 (Dobos, 2014). Se combinan multiplicando (1 − p) de cada una; el total de la tabla es 14,08 %. El inversor va aparte: 96 % de rendimiento nominal.

| Pérdida | Valor por defecto | En el script |
|---|---|---|
| Suciedad | 2 % | sí |
| Sombras | 3 % | no: se calcula para cada lugar |
| Nieve | 0 % | no |
| Dispersión (mismatch) | 2 % | sí |
| Cableado | 2 % | sí |
| Conexiones | 0,5 % | sí |
| Degradación inicial (LID) | 1,5 % | sí |
| Tolerancia de placa | 1 % | sí |
| Envejecimiento | 0 % | no |
| Disponibilidad | 3 % | no: cortes de la red o mantenimiento |

Con las seis que usa el script, fp = 0,9132. Otras referencias: PVGIS recomienda 14 % de pérdidas para un sistema a red y usa un rendimiento global de 0,67 para un aislado; el pliego del IDAE para aislados toma PR = 0,7 con inversor y 0,6 con inversor y batería para dimensionar el generador, Pmp,mín = E_D·G_CEM/(G_dm·PR) ([PCT-A-REV, IDAE, febrero de 2009](https://www.solarweb.net/forosolar/attachments/fotovoltaica-sistemas-aislados-la-red/2330d1295707309-hola-soy-dingdon-pct-a30.pdf)). El Global Solar Atlas da para el punto del ejemplo un PR anual implícito de 0,81 ([recurso-solar.md](recurso-solar.md)).

## Regulador

Victron SmartSolar MPPT 150/35 y 150/45 ([manual, especificaciones técnicas](https://www.victronenergy.com/media/pg/Manual_SmartSolar_MPPT_150-35__150-45/en/technical-specifications.html)):

| Dato | 150/35 | 150/45 |
|---|---|---|
| Tensión de batería | 12, 24 o 48 V automática (36 V manual) | ídem |
| Corriente máxima de carga | 35 A | 45 A |
| Potencia FV nominal a 12 / 24 / 48 V | 500 / 1000 / 2000 W | 650 / 1300 / 2600 W |
| Isc FV máxima | 35 A | 45 A |
| Tensión FV máxima de circuito abierto | 150 V | 150 V |
| Rendimiento máximo | 98 % | 98 % |

- El nombre dice la tensión FV máxima y la corriente de carga: 150 V y 45 A. Con más potencia FV que la nominal, el regulador limita la entrada.
- Arranque: la tensión FV tiene que superar la de la batería en 5 V para que empiece a cargar; después alcanza con 1 V más. Absorción por defecto: 14,4 V en 12 V y 57,6 V en 48 V (ajustable).
- La misma corriente de carga maneja el doble de potencia a 24 V y el cuádruple a 48 V: por eso los sistemas grandes van a 48 V.
- Trabaja de −30 °C a +60 °C, con la potencia completa hasta 40 °C.

**PWM o MPPT** (blog de Victron, J. Rushworth, [«Which solar charge controller: PWM or MPPT?»](https://www.victronenergy.com/blog/2014/07/21/which-solar-charge-controller-pwm-or-mppt/), 21/7/2014): el PWM es en esencia una llave que conecta el generador a la batería, y la tensión del generador baja a la de la batería; es una solución barata para sistemas chicos. El MPPT ajusta su tensión de entrada para sacar la máxima potencia y desacopla las tensiones del generador y de la batería; su ventaja es de 10 % a 40 % con celdas frías (menos de 45 °C), muy calientes (más de 75 °C) o con poca irradiancia. El Manual de GD da para el PWM un rendimiento de alrededor de 80 % y para el MPPT 95 % a 98 %, y dice que el MPPT saca un 30 % más de energía de los módulos.

## Inversor

Victron Inverter Smart, versiones de 48 V ([manual, especificaciones técnicas](https://www.victronenergy.com/media/pg/Inverter_Smart/en/technical-specifications.html)). Entrada de 37,2 V a 68 V.

| Modelo | Continua a 25 °C | A 40 °C | A 65 °C | Pico | Rendimiento máximo | Consumo en vacío (modo ECO) |
|---|---|---|---|---|---|---|
| 1600 VA | 1600 VA / 1300 W | 1200 W | 800 W | 3000 VA | 94 % | 11 W (2,1 W) |
| 2000 VA | 2000 VA / 1600 W | 1450 W | 1000 W | 4000 VA | 94 % | 11 W (2,1 W) |
| 3000 VA | 3000 VA / 2400 W | 2200 W | 1700 W | 6000 VA | 95 % | 15 W (2,8 W) |
| 5000 VA | 5000 VA / 4000 W | 3700 W | 2800 W | 10 000 W | 96 % | 20 W (3,2 W) |

El pliego del IDAE pide que el autoconsumo del inversor sin carga no pase el 2 % de su potencia nominal y que las pérdidas diarias por autoconsumo queden por debajo del 5 % del consumo diario (PCT-A-REV, 5.6.9 y 5.6.10). En un aislado chico el consumo en vacío pesa: 15 W durante 24 h son 360 Wh/día.

## Motores: corriente de arranque

WEG, motores monofásicos W22 de 4 polos a 60 Hz ([folleto 50069982, rev. 00, 02/2017](https://static.weg.net/medias/downloadcenter/hf8/h6e/WEG-w22-motor-eletrico-monofasico-50069982-brochure-portuguese-web.pdf)); los valores son de referencia y a 50 Hz se confirman en la hoja del motor:

| Potencia | Ip/In | Rendimiento | cos φ | In a 220 V |
|---|---|---|---|---|
| 0,25 cv (0,18 kW) | 5,0 | 60,4 % | 0,61 | 2,22 A |
| 0,33 cv (0,25 kW) | 5,0 | 56,2 % | 0,64 | 3,16 A |
| 0,5 cv (0,37 kW) | 6,8 | 66,1 % | 0,90 | 2,82 A |
| 0,75 cv (0,55 kW) | 5,8 | 67,8 % | 0,85 | 4,34 A |
| 1 cv (0,75 kW) | 8,5 | 70,3 % | 0,91 | 5,32 A |

La bomba del ejemplo (0,5 cv) toma P = U·I·cos φ = 220·2,82·0,90 = 558 W, unos 560 W, y arranca con S = 220·6,8·2,82 = 4219 VA. En una heladera, la corriente de arranque del compresor (LRA) figura en su placa.

## Baterías

| Dato | Plomo-ácido AGM y GEL (Victron) | LiFePO4 (Victron Lithium Battery Smart) |
|---|---|---|
| Ciclos | AGM: 400 al 80 % de descarga, 600 al 50 %, 1500 al 30 %. GEL: 500, 750 y 1800 | 2500 al 80 %, 3000 al 70 %, 5000 al 50 % (hasta 80 % de la capacidad) |
| Rendimiento de ida y vuelta | 80 % en promedio | 92 % |
| Temperatura | Capacidad nominal a 25 °C | Carga de +5 °C a +50 °C; descarga de −20 °C a +50 °C |
| Capacidad | Nominal en 20 h (C20); en 10 h, 92 % (AGM) y 87 % (GEL) | Nominal a 25 °C |
| Otros | Autodescarga menor que 2 % por mes a 20 °C | Necesita un sistema de gestión (BMS); carga recomendada 14,2 V por cada 12,8 V |

Fuentes: [hoja de datos GEL y AGM de Victron](https://cdn.enf.com.cn/z/pp/2024/5/b197812zjav6pudd/datasheet-gel-and-agm-batteries-en.pdf); [datos técnicos de la Lithium Battery Smart](https://www.victronenergy.com/media/pg/Lithium_Battery_Smart/en/technical-data.html); [hoja de datos LiFePO4 de 12,8 V y 25,6 V](https://www.victronenergy.de/upload/documents/Datasheet-12,8-Volt-lithium-iron-phosphate-batteries-Smart-EN.pdf), que compara 92 % del litio con 80 % del plomo promedio.

Pliego del IDAE para aislados (PCT-A-REV): profundidad de descarga máxima 80 %, o 60 % si las descargas profundas son frecuentes (5.4.3); autonomía mínima de 3 días (4.2.5); capacidad nominal C20 [Ah] no mayor que 25 veces la Isc del generador [A] (5.4.2), para que el generador alcance a cargar el banco; autodescarga no mayor que 6 % por mes a 20 °C (5.4.6). El Manual de GD dice que una batería para renovables se puede descargar al 80 % y da una eficiencia de carga de 90 % a 95 %.

Al poner baterías en paralelo, consultar al fabricante cuántas ramas admite; en litio, que los módulos y el BMS lo permitan.

## Cables y protecciones de corriente continua

- **Resistividad:** cobre recocido 0,017241 Ω·mm²/m a 20 °C (IEC 60028) y 0,00393 1/°C, los mismos de **instalaciones-electricas**; el script la lleva a la temperatura del conductor (70 °C por defecto). Secciones normalizadas de la serie IEC 60228.
- **Caída de tensión:** el pliego del IDAE para aislados pide menos de 1,5 % de la tensión nominal continua en todos los conductores, incluidos los terminales (5.8.2); el Manual de GD recomienda no pasar 1,5 % en los cables de continua y de alterna.
- **Fusibles de string** (IEC 60364-7-712, según la [guía de instalaciones eléctricas de Schneider Electric](https://www.electrical-installation.org/enwiki/PV_System:_how_to_ensure_safety_during_normal_operation)): hacen falta si 1,35·I_RM < (Ns − 1)·Isc, con Ns los strings en paralelo e I_RM la corriente inversa que soporta el módulo (IEC 61730), que en la hoja de datos figura como corriente máxima de fusible en serie. La corriente del fusible del string va entre 1,5 y 2,4 veces la Isc del módulo (712.433.1.101.2) y no puede pasar esa corriente máxima de la hoja; la de un subgenerador, entre 1,25 y 2,4 veces su Isc (712.433.1.101.3). Con un solo string no hay corriente inversa. Con más de 120 V de Voc máxima, doble aislación o aislación reforzada.
- **Corriente de diseño del generador:** el NEC 2017 toma 1,25·Isc (suma de los strings en paralelo) como corriente máxima del circuito (690.8(A)(1)) y pide que las protecciones soporten el 125 % de esa corriente (690.9(B)(1)), o sea 1,56·Isc ([Mersen, *Photovoltaic Protection Note 5*, TT-PVPN5-002, 2018](https://www.mersen.com/sites/default/files/files_imported_ep/TT-PVPN5-Sizing-Fuses-of-Photovoltaic-Systems-per-NEC-Tech-Topic.pdf)).
- **Seccionador:** bipolar y apto para corriente continua, entre el generador y el regulador o inversor, con tensión asignada mayor que la Voc máxima del string y corriente mayor que 1,25·Isc del generador. Si hay fusibles de string, la caja de strings lleva además un interruptor principal (guía de Schneider Electric).
- **Fusible de batería:** lo más cerca posible del borne positivo, con Ib ≤ In ≤ Iz (la corriente del inversor a su potencia continua máxima, el fusible, la corriente admisible del cable; ver **calculos-ingenieria**) y poder de corte en continua mayor que la corriente de cortocircuito de la batería, que da su hoja de datos.
- **Reglamentación argentina:** AEA 90364-7-712, *Sistemas de suministro con paneles solares fotovoltaicos*, edición 2015 según la lista de la AEA (ver **normas-tecnicas-ar**). Sus valores no se leyeron para esta skill (verificar en la norma vigente).
