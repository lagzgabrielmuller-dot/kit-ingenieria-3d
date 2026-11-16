# Bombas, motores hidráulicos, acumuladores, tanque y calor

Leer este archivo al elegir la bomba y el motor eléctrico, al calcular un motor hidráulico, al dimensionar un acumulador o el tanque, o cuando el aceite calienta. Comandos del script: `bomba`, `motor`, `acumulador`, `tanque` y `calor`.

## Bomba

| Magnitud | Fórmula | Unidades |
|---|---|---|
| Caudal real | qv = Vg · n · ηv / 1000 | Vg [cm³/rev], n [rpm], qv [L/min] |
| Cilindrada necesaria | Vg = qv · 1000 / (n · ηv) | se elige la comercial siguiente |
| Torque en el eje | T = Vg · Δp / (20 · π · ηhm) | Δp [bar], T [N·m] |
| Potencia en el eje | P = 2π · T · n / 60 000 = qv · Δp / (600 · ηt) | P [kW] |
| Potencia hidráulica | P = qv · Δp / 600 | |
| Rendimiento total | ηt = ηv · ηhm | |

Fuente: datos técnicos de Rexroth A10VSO ([RE 92714/08.2015](https://hydraulicsonline.com/wp-content/uploads/2019/03/Bosch-Rexroth-A10VSO-series-32.pdf)) y AZPF ([RE 10089/2019-07-17](https://hydraulicsonline.com/wp-content/uploads/2019/03/Bosch-Rexroth-AZPF.pdf)).

- Δp es la presión de salida menos la de entrada; para el motor eléctrico se usa la máxima (la de la válvula de alivio), porque la bomba la puede alcanzar.
- Rendimientos: salen de las curvas del catálogo, medidas a una viscosidad y una temperatura dadas. Como referencia, en el ejemplo de Brendan Casey una bomba de engranajes externos tiene 85 % de rendimiento total y una de pistones de eje inclinado 92 %; con 100 cm³ a 1000 rpm (100 L/min teóricos) entrega 90 L/min a 207 bar (ηv = 90 %) y pide 360 N·m en vez de 329 N·m (ηhm = 91 %), ηt = 82 % ([Power & Motion, 26-06-2023](https://www.powermotiontech.com/hydraulics-at-work/article/21885281/how-to-calculate-hydraulic-pump-and-motor-efficiency)).
- Lo que falta para llegar al 100 % se vuelve calor en el aceite.

### Ejemplos de catálogo

| Bomba | Tipo | Cilindradas [cm³/rev] | Presión | Fuente |
|---|---|---|---|---|
| Rexroth AZPF | Engranajes externos, caudal fijo | 4 · 5,5 · 8 · 11 · 14 · 16 · 19 · 22,5 (series 1x y 2x) · 25 · 28 (serie 2x) | continua: 250 bar hasta 16 cm³; 19 cm³: 210 bar (1x) o 250 bar (2x); 22,5 cm³: 180 o 220 bar; 25 cm³: 195 bar; 28 cm³: 170 bar | [RE 10089/2019-07-17](https://hydraulicsonline.com/wp-content/uploads/2019/03/Bosch-Rexroth-AZPF.pdf) |
| Rexroth A10VSO | Pistones axiales, caudal variable | 45 · 71 · 100 · 140 · 180 | nominal 280 bar, máxima 350 bar | [RE 92714/08.2015](https://hydraulicsonline.com/wp-content/uploads/2019/03/Bosch-Rexroth-A10VSO-series-32.pdf) |

- La AZPF también fija una velocidad mínima según la presión (del orden de 500 a 600 rpm por debajo de 100 bar y más con presiones altas) y una máxima de 2500 a 4000 rpm según el tamaño: verificar la del tamaño elegido.
- Si el ciclo pide mucho caudal a baja presión (acercamiento) y poco a alta presión (prensado), una bomba doble con descarga de la grande o una bomba de caudal variable bajan mucho la potencia del motor y el calor.

### Motor eléctrico

- P motor ≥ p máx · Q / (600 · ηt), con la potencia normalizada siguiente de la serie de **calculos-ingenieria** y la velocidad de la placa (un motor de 4 polos a 50 Hz gira cerca de 1450 rpm; la sincrónica es 1500 rpm, ver **maquinas-electricas**).
- Corriente, arranque y conductor de alimentación: **maquinas-electricas** e **instalaciones-electricas**.
- Acople bomba-motor, chaveta del eje y soporte (linterna): **elementos-de-maquinas** y el catálogo del acople.

## Motor hidráulico

| Magnitud | Fórmula | Unidades |
|---|---|---|
| Caudal que necesita | qv = Vg · n / (1000 · ηv) | L/min |
| Velocidad | n = qv · 1000 · ηv / Vg | rpm |
| Torque | T = Vg · Δp · ηhm / (20 · π) | N·m |
| Potencia de salida | P = 2π · T · n / 60 000 = qv · Δp · ηt / 600 | kW |

Fuente: Rexroth A2FM, [RE 91001-01-X-B2 (04.2016)](https://www.pneu-hyd.co.th/images/Products/rexroth-thailand/industrial-hydraulic/motors/axial-piston-motor/fixed-motor/re91001-01-x-b2_2016-04.pdf). En el motor los rendimientos van al revés que en la bomba: ηv divide el caudal que pide y ηhm multiplica el torque que da.

- Δp = presión de entrada − presión de salida (la contrapresión del retorno resta torque).
- Para un torque y una velocidad pedidos: Vg = 20 · π · T / (Δp · ηhm) y después el caudal (comando `motor --n --T --dp`).
- Ejemplo del `demo`: 80 cm³ con 26,17 L/min y Δp = 140 bar (ηv = 0,95, ηhm = 0,90) → n = 310,8 rpm, T = 160,4 N·m, P = 5,22 kW (entran 6,11 kW).

## Acumuladores

| Tipo | Relación máxima p2 : p0 |
|---|---|
| Vejiga | 4 : 1 |
| Membrana | 8 : 1 típica (hasta 10 : 1) |
| Pistón | sin límite por el elemento separador |

Fuente: HYDAC, [Accumulators Applications Guidelines, 06.21](https://betterfit-us.hydac.com/wp-content/uploads/Accumulator-Application-Guide.pdf). El catálogo de acumuladores de vejiga HYDAC ([3.201.31/04.21](https://hydraulicsonline.com/wp-content/uploads/2022/07/Hydac-Standard-Bladder-Accumulators.pdf)) fija p0 ≤ 0,9 · p1 y p2 : p0 ≤ 4 : 1, como valores máximos y no como carga permanente.

**Precarga** (misma guía de HYDAC): para acumular energía, p0 = 0,9 · p1 (p1 = presión mínima de trabajo); para amortiguar golpes, p0 = 0,6 a 0,9 · pm; para amortiguar pulsaciones, p0 = 0,6 a 0,8 · pm (pm = presión media de trabajo).

**Volumen** (ley de Boyle con exponente n):

- p0 · V0ⁿ = p1 · V1ⁿ = p2 · V2ⁿ, con presiones **absolutas** (manométrica + 1,013 bar).
- Volumen que entrega entre p2 y p1: ΔV = V1 − V2 = V0 · ((p0/p1)^(1/n) − (p0/p2)^(1/n)).
- Volumen nominal necesario: V0 = ΔV / ((p0/p1)^(1/n) − (p0/p2)^(1/n)).
- n = 1 (isotérmico) en procesos lentos, en los que el gas llega a la temperatura ambiente (ciclos de más de 1 min); n = 1,4 (adiabático, nitrógeno) en procesos rápidos (menos de 1 min) ([Salhydro, calculadora de acumuladores](https://www.salhydro.fi/en/technical-support/accumulator-calculator); también Ortwig, [Formelsammlung Hydraulik](https://public.hochschule-trier.de/~ortwig/Downloads/hydraulikformeln.pdf): rápido adiabático, lento isotérmico). Si no se sabe, se calculan los dos y se adopta el mayor.
- Volúmenes nominales de la vejiga estándar HYDAC [L]: 0,5 · 1 · 2,5 · 4 · 5 · 6 · 10 · 13 · 20 · 24 · 32 · 50 · 60 · 80 · 100 · 130 · 160 · 200 (catálogo 3.201.31/04.21).
- Se precarga con nitrógeno, nunca con oxígeno (Salhydro). La precarga cambia con la temperatura: HYDAC pide revisarla para la temperatura ambiente mínima y la máxima.
- Ejemplo del `demo`: mantener la prensa a presión 2 min con la bomba descargada, reponiendo 0,4 L de fugas entre 160 y 140 bar. p0 = 0,9 · 140 = 126 bar. Isotérmico: V0 = 3,58 L; adiabático: V0 = 4,77 L → 5 L. p2/p0 = 1,27 ≤ 4. A 140 bar el cilindro Ø100 todavía hace 104,5 kN (más de 10 t).
- Una banda de presión angosta (p1 cerca de p2) pide un acumulador grande: el gas cambia poco de volumen.

## Tanque

| Caso | Volumen orientativo | Fuente |
|---|---|---|
| Circuito abierto convencional, instalación fija | 3 a 5 veces el caudal de la bomba por minuto, más 10 % de cámara de aire | Brendan Casey, [How to size a hydraulic tank (Power & Motion, 24-03-2015)](https://powermotiontech.com/hydraulics-at-work/article/21884901/how-to-size-a-hydraulic-tank) |
| Fluidos ignífugos HFC y HFD | 5 a 8 veces el caudal por minuto | ídem |
| Máquinas móviles | 1,5 a 2 veces el caudal por minuto | ídem |
| Criterio NFPA citado para industria | 3 a 12 veces el caudal máximo; en móviles, hasta 1 vez | Keith Ellefsen, [Solutions for reservoir design (Power & Motion, 10-09-2015)](https://www.powermotiontech.com/hydraulics/reservoirs-accessories/article/21884877/solutions-for-reservoir-design) |

- Además del volumen por caudal, el nivel tiene que admitir lo que entra y sale de los cilindros diferenciales (el volumen del vástago, Av · s) y lo que guardan los acumuladores. En la prensa del ejemplo, el vástago Ø70 con 300 mm de carrera desplaza 1,15 L.
- El tanque separa el aire, decanta la suciedad y disipa calor; el retorno va lejos de la aspiración.

## Calor

- Calor generado = potencia en el eje − potencia útil. Al Smiley (GPM Hydraulic Consulting) estima que alrededor del 25 % de la potencia eléctrica de entrada se va en pérdidas que calientan el sistema, y explica que se genera calor cada vez que el aceite pasa de alta a baja presión sin hacer trabajo ([Controlling Hydraulic Oil Temperatures, Machinery Lubrication](https://machinerylubrication.com/Articles/Print/30611?id=30611)).
- Por una válvula (alivio, reguladora de caudal, reductora): P = Δp · Q / 600 [kW]. Si la bomba descarga por la válvula de alivio, toda la potencia del eje termina en calor.
- Lo que disipa el tanque: P = ΔT · A · h / 1000 [kW], con A la superficie de paredes y tapa (sin el fondo) en m², ΔT entre aceite y ambiente en K y h = 12 W/(m²·K) en un local normalmente ventilado, 24 con ventilación forzada y 6 con mala circulación de aire (Brendan Casey, [Why your hydraulic machine probably needs an oil cooler (Power & Motion, 15-02-2019)](https://www.powermotiontech.com/fluid-power-basics/accessories/article/21887875/why-your-hydraulic-machine-probably-needs-an-oil-coolerand-a-big-one)). En su ejemplo instala un enfriador del 25 % de la potencia de entrada.
- Temperatura: Casey trabaja con 85 °C como máximo (vida del aceite, las mangueras y las juntas) y, según el grado y el clima, apunta a unos 50 °C; Smiley habla de unos 49 °C (120 °F) con intercambiador y considera demasiado caliente un sistema industrial a más de 60 °C (140 °F). El criterio que manda es la viscosidad: que quede en el rango óptimo de la bomba (ver [aceite-y-canerias.md](aceite-y-canerias.md)).
- Soluciones: centro tándem o válvula de descarga para que la bomba no quede empujando contra la válvula de alivio en reposo; bomba de caudal variable o doble; acumulador con descarga de la bomba; no regular velocidades estrangulando mucho caudal; cañerías más grandes; intercambiador aire-aceite o agua-aceite.
- Ejemplo del `demo`: la bomba de 26,17 L/min descargando a 160 bar pone 6,98 kW hidráulicos y 8,21 kW en el eje: todo es calor. Un tanque de 0,6 × 0,4 × 0,45 m (108 L, 1,14 m² de paredes y tapa) con 25 K de diferencia disipa 12 · 1,14 · 25 / 1000 = 0,342 kW: 24 veces menos. Por eso esa prensa no puede quedar en reposo con la bomba contra la válvula de alivio.

```
python scripts/oleohidraulica.py bomba --Q 25 --p 160 --n 1450
python scripts/oleohidraulica.py acumulador --dV 0.4 --p1 140 --p2 160
python scripts/oleohidraulica.py calor --p 160 --Q 26.17 --area 1.14 --dT 25
```
