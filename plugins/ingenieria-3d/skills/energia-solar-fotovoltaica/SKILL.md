---
name: energia-solar-fotovoltaica
description: "Dimensionado de sistemas solares fotovoltaicos en Argentina, aislados (off-grid) y conectados a la red (generación distribuida), con memoria de cálculo: horas de sol pico (HSP) del Atlas solar argentino, PVGIS, NASA POWER o Global Solar Atlas, tabla de consumos (Wh/día y potencia simultánea), cantidad de paneles con pérdidas desglosadas, conexión en serie y en paralelo con corrección de Voc y Vmp por temperatura (NOCT), regulador PWM o MPPT, banco de baterías (autonomía, profundidad de descarga, 12, 24 o 48 V, plomo-ácido o LiFePO4), inversor (potencia continua y arranque de motores), cables, fusibles y seccionador de continua, inclinación, sombras, energía anual y Ley 27.424. Usar cuando pregunten cuántos paneles necesito para mi casa, calcular el banco de baterías, qué regulador MPPT o PWM conviene, cuánta energía genera un panel de 550 W, qué inclinación darle a los paneles solares, un sistema aislado para un campo, qué inversor para una heladera o una bomba, o cómo conectar paneles a la red."
---

# Energía solar fotovoltaica

`scripts/fotovoltaica.py` (Python 3.9+, solo biblioteca estándar) hace cada cuenta e imprime fórmula, reemplazo y resultado con coma decimal, listo para la memoria de cálculo (presentación en **calculos-ingenieria**; el informe, con **informe-tecnico**). Acepta números con coma o con punto. La parte de alterna (circuitos, caída de tensión en alterna, diferencial, puesta a tierra) va con **instalaciones-electricas**, y la reglamentación AEA con **normas-tecnicas-ar**. Si la consigna o el docente dan otros valores, mandan esos.

Leer según el caso:

- [references/recurso-solar.md](references/recurso-solar.md): de dónde sacar las HSP y cómo consultar cada fuente, la tabla de ciudades, los datos del punto del ejemplo, la inclinación, la orientación y las sombras.
- [references/equipos.md](references/equipos.md): hojas de datos del módulo, el regulador, el inversor, las baterías y los motores, las pérdidas por defecto y las reglas de cables, fusibles y seccionador.
- [references/marco-legal.md](references/marco-legal.md): para un sistema conectado a la red: Ley 27.424, qué quedó vigente, categorías de usuario-generador y adhesión provincial.

## Método para un sistema aislado

### 1. Recurso solar

HSP [h/día] = H_T [kWh/m²·día] / 1 kW/m²: la irradiación diaria en el **plano de los módulos** dividida por 1000 W/m². En un aislado con consumo parejo se diseña con el **peor mes**, que en la Argentina es junio; en un conectado a la red, con el total del año.

| Fuente | Qué da | Cómo |
|---|---|---|
| Atlas de Energía Solar de la República Argentina (UNLu, 2007) | Mapas mensuales de irradiación global horizontal (kWh/m²·día) | Leer la isolínea y pasarla al plano inclinado con los coeficientes del Anexo II de la *Guía del recurso solar* (2019) |
| PVGIS 5.3 (Comisión Europea) | Irradiación mensual a la inclinación que se elija | Web o API `MRcalc` con `selectrad=1&angle=…`; en Sudamérica usa SARAH3 en parte y ERA5 donde no llega el satélite (ver qué base usa el punto) |
| NASA POWER | Global y difusa horizontal, temperatura | API de climatología, comunidad RE |
| Global Solar Atlas 2 (Banco Mundial, Solargis) | GHI, difusa, GTI a la inclinación óptima, PVOUT | Web o `api.globalsolaratlas.info/data/lta?loc=lat,lon` |

PVGIS y el Global Solar Atlas dan totales del mes: se dividen por los días del mes. Las URL, la cobertura de cada base y la tabla orientativa de diez ciudades están en [references/recurso-solar.md](references/recurso-solar.md).

### 2. Consumo

Tabla de cargas: cantidad n, potencia P [W], horas por día h y si puede funcionar junto con las demás.

- Energía diaria en alterna: E_CA = Σ n·P·h [Wh/día].
- Potencia simultánea: P_sim = Σ n·P de las cargas que pueden coincidir [W].
- Energía de continua que sale de la batería: E_CC = E_CA/η_inv + P0·t, con P0 el consumo en vacío del inversor y t las horas que queda encendido (24 h si no tiene modo de ahorro).

La heladera se carga con su energía diaria (etiqueta) o con las horas equivalentes del compresor, no con 24 h a potencia plena.

### 3. Tensión del sistema

Se elige para que las corrientes de continua sean manejables: I = P/(η·V). Un inversor de 2400 W con 95 % toma 211 A a 12 V, 105 A a 24 V y 53 A a 48 V. Además, un mismo regulador maneja más potencia a más tensión (el MPPT 150/45 del ejemplo: 650 W a 12 V, 1300 W a 24 V y 2600 W a 48 V). Con varios kWh por día o con motores, 48 V deja corrientes y secciones razonables.

### 4. Paneles

- Temperatura de celda: Tc = Ta + (NOCT − 20)·G/800 [°C], con Ta la temperatura media del mes de diseño y G = 1000 W/m² (del lado seguro para un cálculo mensual).
- Factor de temperatura: fT = 1 + γ·(Tc − 25), con γ el coeficiente de Pmax [%/°C] de la hoja.
- Otras pérdidas: fp = Π(1 − p_i), por defecto las de PVWatts: suciedad 2 %, dispersión 2 %, cableado 2 %, conexiones 0,5 %, degradación inicial 1,5 % y tolerancia de placa 1 % → fp = 0,9132. Las sombras se calculan aparte.
- Energía por módulo: E_mód = P·HSP·fT·fp [Wh/día].
- Energía que tiene que entregar el generador: E_FV = E_CC/(η_reg·η_bat).
- Cantidad: N = E_FV/E_mód, redondeada hacia arriba a un múltiplo de los módulos por string.

### 5. Serie, paralelo y temperatura

- Voc máxima, con la mínima del lugar (a la salida del sol la celda está a la temperatura del aire): Voc,máx = Voc·(1 + β·(T_mín − 25)), con β el coeficiente de Voc (negativo). Por string: Ns·Voc,máx.
- Vmp mínima, con la celda en el día más caluroso: Tc = T_máx + (NOCT − 20)·1000/800 y Vmp,mín = Vmp·(1 + βVmp·(Tc − 25)). Si la hoja no da βVmp, se toma γ − α (de P = V·I): del lado seguro.
- Ns entre ⌈(V_bat,máx + margen)/Vmp,mín⌉ y ⌊V_máx/Voc,máx⌋. Strings en paralelo: Np = N/Ns, todos iguales.

### 6. Regulador

MPPT, con los datos de su hoja:

- Voc,máx del string ≤ tensión FV máxima del regulador (en frío; si se pasa, se rompe).
- Vmp,mín del string ≥ V_bat,máx + 5 V (lo que pide el fabricante del ejemplo para arrancar).
- 1,25·Np·Isc ≤ Isc FV máxima del regulador (1,25: corriente máxima del circuito según el NEC 690.8).
- Corriente de carga P_FV/V_bat ≤ la del regulador, y P_FV ≤ potencia FV nominal a esa tensión.

PWM: conecta el generador a la batería y la tensión de los módulos baja a la de la batería, así que aprovecha P ≈ V_bat·Imp·Np. Sirve con módulos de tensión acorde a la batería; con un módulo de 550 W (Vmp 41,95 V) en 12 V se aprovecha 13,5 V·13,12 A = 177 W, el 32 %. La corriente del PWM: I ≥ 1,25·Isc·Np.

### 7. Banco de baterías

- Capacidad: C = E_CC·N_aut/PD [Wh] y C/V [Ah], con N_aut los días de autonomía (el pliego del IDAE pide como mínimo 3) y PD la profundidad de descarga.
- Módulos: V/V_mód en serie y C/C_mód en paralelo, redondeado hacia arriba; autonomía real = C_adoptada·PD/E_CC.

| | Plomo-ácido (AGM, GEL) | LiFePO4 |
|---|---|---|
| PD de diseño | 0,5 (AGM 600 ciclos y GEL 750 al 50 %; 400 y 500 al 80 %) | 0,8 (2500 ciclos al 80 %) |
| Rendimiento de ida y vuelta | 80 % en promedio | 92 % |
| Cuidados | C20 ≤ 25·Isc del generador (IDAE) para que se cargue; capacidad nominal en 20 h a 25 °C | No cargar debajo de 5 °C; necesita BMS |

Fuentes: hojas de datos de Victron y pliego del IDAE, en [references/equipos.md](references/equipos.md).

### 8. Inversor

- Potencia continua a la temperatura del local (la hoja da la potencia a 25 °C y a 40 °C) ≥ P_sim.
- Pico: (P_sim − P_motor) + U·(Ip/In)·In del motor mayor, en VA. Ip/In sale de la placa o del catálogo: 5,0 a 8,5 en los motores monofásicos de 0,25 a 1 cv de WEG; en una heladera, la corriente de arranque del compresor (LRA) de su placa. No se suman dos arranques si no pueden coincidir.
- Corriente de continua para el cable y el fusible: I = P_cont,máx/(η·V_bat).

### 9. Cables y protecciones de continua

- Sección mínima por caída: S = 2·I·L·ρ/ΔU [mm²], con L el largo de ida, ρ = 0,017241·(1 + 0,00393·(t − 20)) Ω·mm²/m y ΔU ≤ 1,5 % de la tensión del tramo (pliego del IDAE y Manual de GD). Se adopta la sección normalizada siguiente y se verifica la corriente admisible (Ib ≤ In ≤ Iz) como en **instalaciones-electricas**.
- Fusible de string: hace falta si 1,35·I_fus,máx < (Ns − 1)·Isc, con I_fus,máx la corriente máxima de fusible en serie de la hoja del módulo; va entre 1,5·Isc y el menor de 2,4·Isc e I_fus,máx (IEC 60364-7-712). Fusibles para fotovoltaica, aptos para continua.
- Seccionador bipolar de continua entre generador y regulador: tensión ≥ Voc,máx del string y corriente ≥ 1,25·Np·Isc.
- Fusible de batería junto al borne positivo, con poder de corte en continua mayor que el cortocircuito de la batería. La reglamentación argentina es la AEA 90364-7-712 (verificar en la norma vigente).

### 10. Inclinación, orientación y sombras

- Orientación al norte. Máxima energía anual: cerca de la latitud, unos grados menos (33° en Buenos Aires según el Manual de GD; 30° en el punto del ejemplo según el Global Solar Atlas).
- Aislado con consumo parejo: más inclinación para el invierno; el pliego del IDAE da |φ| + 10° para el mes de invierno. `inclinacion` compara inclinaciones con un modelo isotrópico (del lado seguro).
- Separación entre filas (Manual de GD): d = L·sen β/tg(90° − |φ| − 23,5° − 7°), para tener al menos 4 h de sol el día más corto.

## Sistema conectado a la red

- Energía anual: E = Σ P·H_m·fT_m·fp·η_inv, mes a mes con la temperatura de cada mes, o rápida: E = P·HSP·PR, con el PR del desglose o de la fuente (0,80 en el ejemplo; el Global Solar Atlas da 0,81 en ese punto). Inversor de red: 96 % (PVWatts) o el de su hoja.
- Ley 27.424 (vigente): el usuario-generador consume lo que genera e inyecta el excedente; la factura muestra el neto, y cada kWh inyectado se paga con una tarifa de inyección acorde al precio estacional del mercado mayorista (art. 12). El DNU 70/2023 (art. 176) derogó los artículos 16 a 37: fondo FODIS y beneficios fiscales. Conviene dimensionar para el autoconsumo.
- Categorías (Resolución SE 235/2024): pequeño hasta 3 kW, mediano hasta 300 kW, mayor hasta 12 MW. Rige en cada provincia que adhiere (total o parcialmente) o según su régimen propio: consultar al ente regulador provincial y a la distribuidora. Lo instala un instalador calificado y la distribuidora pone un medidor bidireccional. Detalle y fuentes en [references/marco-legal.md](references/marco-legal.md).

## Comandos

| Comando | Qué hace |
|---|---|
| `consumo --carga "nombre;n;P;h[;no]" … --eta-inv 0,95 --p0 15` | Tabla de cargas, E_CA, P_sim y E_CC |
| `paneles --E 5086,3 --hsp 3,751 --P 550 --gamma -0,34 --ta 10,875 --serie 2` | Pérdidas desglosadas y cantidad de módulos |
| `temperatura --voc --vmp --beta --gamma --alfa --tmin --tmax --serie` | Voc en frío y Vmp en calor |
| `regulador … --serie 2 --paralelo 2 --vbat 51,2 --vbat-max 57,6 --vmax 150 --iscmax 45 --imax 45` | Ventana de tensión y corrientes del MPPT; con `--tipo pwm`, la potencia aprovechada |
| `baterias --E 5086,3 --dias 3 --V 51,2 --v-modulo 51,2 --ah-modulo 100` | Capacidad, módulos y autonomía; `--tecnologia plomo` para plomo-ácido |
| `inversor --P 1030 --motor "220;2,82;6,8;560" --cont 2200 --pico 6000` | Potencia continua, pico de arranque y corriente de continua |
| `cable --I 13,12 --L 10 --U 83,9 --limite 1,5` | Sección por caída de tensión en continua |
| `fusibles --isc 13,99 --mocpr 30 --strings 4` | Si hacen falta fusibles de string, su rango, y el seccionador |
| `energia --P 550 --hsp 5,505 --pr 0,80` o con `--gti` y `--temp` (12 valores) | Energía diaria y anual |
| `inclinacion --lat -33,89 --ghi … --dif … --totales --beta 30 45` | HSP mes a mes según la inclinación y separación entre filas |

## Ejemplo resuelto (el del demo)

Casa de campo sin red en la zona rural cercana a Pergamino (−33,89°; −60,57°). Global Solar Atlas (consulta del 16/11/2026): óptimo anual 30°; en junio, 112,53 kWh/m² a 30° → HSP = 3,751 h y temperatura media 10,9 °C. Módulo de 550 W (LONGi LR5-72HBD-550M: Voc 49,80 V, Vmp 41,95 V, Isc 13,99 A, Imp 13,12 A, β −0,265 %/°C, γ −0,340 %/°C, α +0,050 %/°C, NOCT 45 °C, fusible máximo 30 A). Supuestos del ejemplo: mínima −10 °C y máxima 40 °C (confirmar con el SMN para el lugar).

| Carga | n | P [W] | h | E [Wh/día] |
|---|---|---|---|---|
| Lámparas LED | 10 | 9 | 5 | 450 |
| Heladera con freezer | 1 | 150 | 8 | 1200 |
| Televisor LED | 1 | 100 | 5 | 500 |
| Notebook y cargadores | 2 | 60 | 4 | 480 |
| Router wifi | 1 | 10 | 24 | 240 |
| Bomba de 0,5 cv (WEG: 2,82 A, cos φ 0,90) | 1 | 560 | 2 | 1120 |
| Lavarropas (no coincide con la bomba) | 1 | 500 | 1 | 500 |

| Paso | Resultado |
|---|---|
| Consumo | E_CA = 4490 Wh/día; P_sim = 1030 W; con un inversor de 48 V y 3000 VA (95 %, 15 W en vacío): E_CC = 4490/0,95 + 15·24 = 5086,3 Wh/día |
| Paneles | Tc = 10,9 + 25·1000/800 = 42,1 °C; fT = 0,9418; fp = 0,9132; E_mód = 550·3,751·0,9418·0,9132 = 1774,3 Wh/día; E_FV = 5086,3/(0,95·0,92) = 5819,6 Wh/día; N = 3,28 → 4 módulos, 2 en serie × 2 en paralelo (2200 W); margen 22 % |
| Temperatura | Voc,máx = 49,80·(1 + 0,00265·35) = 54,42 V → 108,84 V por string ≤ 150 V; con 3 en serie, 163,3 V: no sirve. Vmp,mín = 41,95·(1 − 0,0039·46,25) = 34,38 V → 68,77 V ≥ 57,6 + 5 = 62,6 V |
| Regulador | MPPT 150/45: 1,25·2·13,99 = 34,98 A ≤ 45 A; 2200/51,2 = 42,97 A ≤ 45 A; 2200 W ≤ 2600 W |
| Baterías | LiFePO4 de 51,2 V, 3 días, PD 0,8: C = 5086,3·3/0,8 = 19 074 Wh = 372,5 Ah → 4 módulos de 100 Ah (20 480 Wh), 3,22 días. En plomo-ácido a 48 V y PD 0,5: 635,8 Ah, con C20/Isc = 22,7 < 25 |
| Inversor | Pico = (1030 − 560) + 220·6,8·2,82 = 4689 VA: el de 2000 VA (4000 VA de pico) no alcanza; el de 3000 VA (2200 W a 40 °C, 6000 VA de pico) sí. I_CC = 2400/(0,95·48) = 52,63 A |
| Cables | Cada string, 10 m: S = 2·13,12·10·0,02063/1,258 = 4,30 mm² → 6 mm² (1,08 %). Batería-inversor, 2 m: 6,03 mm² → 10 mm² (0,90 %), y verificar Iz |
| Protecciones | Con 2 strings no hace falta fusible de string (1,35·30 = 40,5 A ≥ 13,99 A); con 4 sí, entre 21,0 A y 30 A. Seccionador ≥ 108,8 V y ≥ 35 A |
| Inclinación | A 45° junio recibe 9,6 % más que a 30° (modelo isotrópico): conviene si la estructura lo permite |

Conectado a la red en el mismo lugar: 6 módulos (3,3 kWp) con un inversor de 3 kW (usuario-generador pequeño): 5329 kWh/año mes a mes (PR 0,804), 0,71 % menos que el PVOUT del Global Solar Atlas. Un módulo de 550 W genera ahí 888 kWh/año, 2,43 kWh/día de promedio (en junio, el 56 % que en diciembre).

## Errores frecuentes

- Usar la HSP horizontal, o la media del año, para un aislado: va la del plano de los módulos en el peor mes.
- Tomar los totales mensuales de PVGIS o del Global Solar Atlas como si fueran diarios.
- Olvidar el consumo en vacío del inversor: 15 W durante 24 h son 360 Wh/día.
- Verificar el string con la Voc a 25 °C: en una mañana de −10 °C sube 9 % y puede romper el regulador.
- No mirar la Vmp en calor: si queda por debajo de V_bat + 5 V, el MPPT no arranca.
- Poner un PWM con un módulo de 550 W (Vmp 41,95 V) en 12 V: se pierden dos tercios de la potencia.
- Elegir el inversor por la potencia continua y no por el arranque del motor.
- Calcular el banco sin la profundidad de descarga, o cargar litio por debajo de 5 °C.
- Calcular la caída de tensión de continua con un solo conductor (es ida y vuelta: 2·L) o con ρ a 20 °C.
- Usar fusibles o llaves de alterna en el circuito de continua.
- Dimensionar un conectado a la red para inyectar todo como si el kWh inyectado valiera lo mismo que el consumido.

## Verificación

`python fotovoltaica.py demo` tiene que terminar en `DEMO OK` (sale con código 1 si algo no coincide). Reproduce el ejemplo y además controla: la HSP del Global Solar Atlas contra la medición de la red solarimétrica de la UNLu en Pergamino (2,2 %); la potencia y la Vmp a NOCT calculadas contra la hoja del módulo (−0,25 % y −1,2 %); la energía anual mes a mes contra el PVOUT del Global Solar Atlas (−0,71 %); la fórmula cerrada de R̄b contra una integración numérica; el modelo isotrópico contra el GTI del Global Solar Atlas (2,6 % a 4,9 % por debajo); y la separación entre filas del ejemplo del Manual de GD (1,38 m). Para una entrega, una revisión independiente con **equipo-de-modelos** o **revision-tecnica**.
