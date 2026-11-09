---
name: cnc-mecanizado
description: "Programación CNC de torno y fresadora con código ISO (G y M) estilo Fanuc: estructura segura del programa, cero pieza, G54 a G59, correctores T0101, G96 con límite G50, compensación de radio y de largo, ciclos de torno (G71, G70, G72, G73, G74, G75, G76, G90, G92, G94) y de fresadora (G81 a G89), subprogramas, datos de corte (n, Vf, tiempo y potencia con kc), hoja de proceso, simulación y prueba en la máquina, y diferencias de los controles GSK de escuela (928TC, 928TE, 980TD). Trae un script que calcula datos de corte, genera el programa de torneado de un perfil y revisa archivos .nc. Es de mecanizado, no de impresión 3D (para laminar con OrcaSlicer está la skill gcode). Usar cuando se pida un programa CNC o código G para el torno o la fresadora, revisar o corregir un programa, calcular rpm, avance o tiempo de mecanizado, armar la hoja de proceso o simular en WinUnisoft."
---

# Programación CNC de torno y fresadora (código ISO, estilo Fanuc)

Base: Fanuc de torno (serie T, sistema de códigos G **A**, el que describen sus manuales) y de fresadora (serie M). Otros controles cambian ciclos, formatos y funciones M: **siempre manda el manual de la máquina y el profesor**. Si el pedido es imprimir en 3D, no es esta skill (ver `gcode` en `cad-3d-comunidad`); si es la geometría de la pieza, ver **planos-tecnicos** y **modelado-3d-cad**.

## Método (siempre)

1. **Datos**: plano, material y estado, bruto (diámetro × largo o placa), sujeción, máquina y **modelo exacto del control**, herramientas disponibles (código del inserto o de la fresa) y límites de la máquina (rpm, potencia, recorridos).
2. **Hoja de proceso**: operaciones en orden, herramienta, Vc, n, f, ap y tiempo (calculados con el script; plantilla abajo).
3. **Programa**: encabezado seguro → por herramienta: cambio en zona segura, giro, aproximación, mecanizado, retiro → cierre. Cada número con punto decimal (`X20.`), comentarios entre paréntesis en mayúsculas sin acentos.
4. **Revisar** con `cnc.py revisar` y **simular** con el bruto y las herramientas cargados.
5. **En la máquina**: en vacío, bloque a bloque y con el avance rápido y el de corte bajos (ver más abajo).

## Script `scripts/cnc.py`

Python 3.9+, solo biblioteca estándar, acepta coma decimal. `python scripts/cnc.py demo salida` corre todo junto (corte, perfil y revisar sobre el perfil generado y sobre un programa con errores a propósito) y termina en "Demo OK". `--help` en cada subcomando.

```
python scripts/cnc.py corte --vc 200 --d 40 --f 0,2 --ap 2 --l 60 --material acero-bajo-c
python scripts/cnc.py corte --maquina fresadora --vc 150 --d 10 --z 3 --fz 0,09 --ap 8 --ae 2 --l 200 --material acero-bajo-c
python scripts/cnc.py perfil --puntos "16;0 20;-2 20;-15 30;-25 30;-40" --bruto 34 --t-term T0202 --vc-term 220 --salida pieza.nc
python scripts/cnc.py perfil ... --modo pasadas      # G01 explícitos, para controles sin G71
python scripts/cnc.py revisar pieza.nc --rango "X0:110,Z-41:110"
```

- `corte`: n (con `--nmax`, limita y recalcula la Vc real), Vf, tiempo, caudal de viruta, kc, potencia de corte, potencia en el motor (η = 0,8 supuesto, `--eta`), par y una fila para la hoja de proceso.
- `perfil`: torneado exterior de un perfil monótono (de la cara hacia el plato, diámetros que no bajan; se supone la cara refrentada en Z0). Desbaste con G71 o con pasadas y perfilado con sobremetal, terminación (G70 o contorno), opción `--g42`, punto de cambio `--cambio "X100 Z100"`. Los datos de corte por defecto son de ejemplo: cambiarlos.
- `revisar`: errores (mecanizar sin M03/M04, G01/G02/G03 sin F, G96 sin G50 S, cambio de herramienta sin retiro, falta M30, coordenadas fuera de `--rango`, G41/G42 en un arco, contorno de G71 inexistente, punto decimal en P/Q de G74/G75) y avisos (números sin punto, G98/G99, G71 tipo II o no monótono, G43, roscar con G96, M98 a programas que no están). Sale con código 1 si hay errores. No reemplaza la simulación.

## Referencias (leer según el caso)

- `references/fanuc-torno.md`: al escribir o corregir un programa de torno con ciclos; formatos de G70 a G76 y G90/G92/G94, sistemas A, B y C, y ejemplos (refrentado y cilindrado, perfil, rosca M20 × 1,5, agujero, ranura, subprograma).
- `references/fanuc-fresadora.md`: programas de fresadora; compensaciones, ciclos G73 a G89, ejemplo completo (contorno, agujeros y roscas) y subprogramas.
- `references/datos-de-corte.md`: al elegir Vc, f y ap o calcular potencia; tablas de catálogo con su fuente, kc1 y mc por material y ejemplos resueltos.
- `references/hoja-de-proceso.md`: al armar la hoja de proceso o la lista de herramientas (plantilla y ejemplo).
- `references/gsk-torno.md`: si la máquina tiene un control GSK (928TC, 928TE, 980TD).

## Ceros y coordenadas

- **Cero máquina** (referencia): lo fija el fabricante; se vuelve con G28 por un punto intermedio (`G28 U0. W0.` en torno, `G91 G28 Z0.` en fresadora). **Cero pieza**: lo elige el programador; en torno, en el eje y en la cara terminada; en fresadora, en una esquina o en el centro de la cara superior.
- **Fresadora**: G54 a G59 eligen uno de 6 sistemas de pieza cargados en la tabla de decalajes; G54 queda activo al encender ([FM]).
- **Torno**: X va **en diámetro** ([FT]). En el sistema A lo incremental se escribe con **U y W**, no con G91 ([FT]). `T0101` = herramienta 1 con corrector 1; el corrector 0 cancela (`T0100`) ([FT], [ET]). Cada corrector guarda las medidas de esa herramienta (geometría y desgaste) con las que el control lleva su punta al cero pieza.
- G20 pulgadas / G21 mm; G17, G18, G19 eligen el plano (G18 en torno).

## Estructura del programa

Torno (sale de `cnc.py perfil`; versión completa en `references/fanuc-torno.md`):

```
%
O0001 (PERFIL)
N10 G21 G40 G97 G99            (MM - SIN COMPENSACION - RPM FIJAS - MM/V)
N20 G00 X100. Z100.            (PUNTO DE CAMBIO)
N30 T0101                      (DESBASTE)
N40 G50 S2000                  (LIMITE DE RPM PARA G96)
N50 G96 S180 M03
N60 G00 X36. Z2. M08           (PUNTO DE PARTIDA, FUERA DEL BRUTO)
N70 G71 U1. R0.5
N80 G71 P90 Q150 U0.4 W0.1 F0.25
N90 G00 X16.                   (CONTORNO N90 A N150)
...
N160 G00 X100.                 (RETIRO: PRIMERO X, DESPUES Z)
N170 Z100.
N180 T0202 ...                 (TERMINACION CON G70 P90 Q150)
N250 M05
N260 M30
%
```

Fresadora (completo en `references/fanuc-fresadora.md`): `G21 G17 G40 G49 G80 G90 G94` → `G91 G28 Z0.` → `T1 M06` → `G54 G00 X.. Y.. S.. M03` → `G43 H01 Z50. M08` → mecanizado → `G00 Z50. M09` → `G91 G28 Z0.` → `M05` → siguiente herramienta → `M30`.

Reglas del encabezado y el cierre: cancelar compensaciones y ciclos al empezar; en torno, **G50 S antes de G96** y G99 explícito; aproximar en rápido a un punto fuera del bruto y delante de la cara; cambiar de herramienta solo en el punto de cambio; retirar primero en X (torno exterior) o en Z (fresadora) y después lo demás; M05 y M09 antes de M30.

## Funciones G principales

| Código | Torno (Fanuc T, sistema A) | Fresadora (Fanuc M) |
|---|---|---|
| G00 / G01 | rápido / lineal con F | igual |
| G02 / G03 | arco horario / antihorario, con R o con I y K | con R o con I y J |
| G28 | vuelta a referencia por un punto intermedio | igual |
| G32 | roscado de paso constante (F = paso) | — |
| G40 / G41 / G42 | compensación de radio de punta: anula / izquierda / derecha | de radio de fresa (D) |
| G43 / G44 / G49 | — | compensación de largo + / − / anula (H; H0 = 0) |
| G50 | límite de rpm (`G50 S`) o fijar coordenadas (`G50 X Z`) | anula escala |
| G54 a G59 | sistemas de pieza (si el control los tiene) | sistemas de pieza 1 a 6 |
| G70 a G76 | ciclos múltiples (abajo) | G73, G74, G76 son ciclos de agujero |
| G80 | — | anula ciclo de agujero |
| G81 a G89 | — | ciclos de agujero (abajo) |
| G90 / G92 / G94 | ciclos simples: cilindrado / roscado / refrentado | G90 absoluto / G91 incremental |
| G94 / G95 | — | avance mm/min / mm/vuelta |
| G96 / G97 | Vc constante (S en m/min) / rpm fijas | — |
| G98 / G99 | avance mm/min / mm/vuelta | en ciclos: vuelve al plano inicial / al plano R |

Fuentes: tablas de G de [FT] (sistemas A, B y C) y [FM]. En los sistemas B y C del torno cambian varios números: el límite de rpm pasa de G50 a G92 y el avance por vuelta de G99 a G95 ([FT]); en el C, que usa por ejemplo el simulador EMCO WinNC Fanuc 21 TB, G90/G91 son absoluto e incremental y G70/G71 pulgadas y milímetros ([ET]). Hay que averiguar cuál usa la máquina.

**Arcos**: con R, el arco de más de 180° lleva R negativo y el círculo completo se programa con I, J, K; I, J, K son siempre la distancia **incremental del punto inicial al centro**, con signo, aunque esté G90 ([FM]). En torno, I suele ir en radio (verificar en el manual de la máquina). El sentido G02/G03 se ve distinto según la torreta esté delante o detrás del eje: comprobarlo en la simulación.

## Compensaciones

- **Radio de punta (torno)**: con G41/G42 el control corrige el error del radio de la plaquita en conos, chaflanes y arcos; en la tabla de correctores van el radio R y la **punta imaginaria** (números 1 a 8; 0 y 9 cuando se programa el centro de la punta) ([FT]). G41 deja la pieza a la derecha de la trayectoria y G42 a la izquierda ([FT]); en torneado exterior hacia el plato suele ser G42 e interior G41 (verificar con la figura del manual). El radio de punta sale de las dos últimas cifras del código ISO de la plaquita: CNMG 120404, 120408 y 120412 tienen 0,4, 0,8 y 1,2 mm ([MT]).
- **Radio de fresa**: G41 a la izquierda y G42 a la derecha mirando en el sentido del avance, con D (número de corrector; H si el parámetro OFH lo indica). Se activa en un bloque G00 o G01 con un recorrido de entrada (en G02/G03 da alarma) y se anula con G40 al salir ([FM]).
- **Largo (fresadora)**: G43 H.. después de cada cambio, antes de bajar en Z; G49 o H0 la anulan ([FM]).

## Ciclos de torno (Fanuc, sistema A)

| Ciclo | Formato | Uso |
|---|---|---|
| G90 | `G90 X(U) Z(W) F` (cono: `R` en radio) | cilindrado simple, vuelve al punto de partida |
| G92 | `G92 X(U) Z(W) F(paso)` (cono: `R`) | roscado simple, una pasada por bloque |
| G94 | `G94 X(U) Z(W) F` (cono: `R`) | refrentado simple |
| G71 | `G71 U(Δd) R(e)` / `G71 P(ns) Q(nf) U(Δu) W(Δw) F S T` | desbaste longitudinal de un contorno ns a nf |
| G72 | `G72 W(Δd) R(e)` / `G72 P Q U W F S T` | desbaste transversal (refrentado) |
| G73 | `G73 U(Δi) W(Δk) R(d)` / `G73 P Q U W F S T` | repetición de perfil (piezas forjadas o con rebajes) |
| G70 | `G70 P(ns) Q(nf)` | terminación del contorno de G71, G72 o G73 |
| G74 | `G74 R(e)` / `G74 X(U) Z(W) P(Δi) Q(Δk) R(Δd) F` | agujereado con picoteo en Z (sin X: solo en el eje) |
| G75 | `G75 R(e)` / `G75 X(U) Z(W) P(Δi) Q(Δk) R(Δd) F` | ranurado radial con picoteo |
| G76 | `G76 P(m)(r)(a) Q(Δdmin) R(d)` / `G76 X(U) Z(W) R(i) P(k) Q(Δd) F(L)` | roscado en varias pasadas |

Reglas confirmadas en [FT]: en G71 **tipo I** el bloque ns lleva solo X (con Z es tipo II) y el contorno tiene que ser monótono en X y en Z; Δd va en radio y sin signo; Δu (en diámetro) y Δw dejan el sobremetal con su signo; las F, S y T del contorno se ignoran en el desbaste y valen en G70; P y Q de G74/G75 **no admiten punto decimal**. En G76, m es la cantidad de pasadas de terminación, r el chaflán de salida en décimas de paso y a el ángulo de la herramienta (`P021060` = 2 pasadas, 1,0 × paso, 60°); Δdmin, d, k y Δd van en la unidad mínima. Para roscar se usa **G97**, no G96 ([F0]). Ejemplos resueltos (G90, G94, G71/G70, G76 de M20 × 1,5, G74, G75): `references/fanuc-torno.md`.

## Ciclos de fresadora (G73, G74, G76, G81 a G89)

`G90/G91 G98/G99 G8x X Y Z R Q P F K` — X, Y: posición del agujero; Z: fondo; R: plano de aproximación; Q: profundidad por picada (G73, G83) o corrimiento (G76, G87); P: pausa; K: repeticiones. G98 vuelve al plano inicial y G99 al plano R (lo usual: G99 entre agujeros y G98 en el último, o para saltar una sujeción). Queda activo hasta G80 o un código del grupo 01 (G00, G01, G02, G03) ([FM]).

| G73 | G74 | G76 | G81 | G82 | G83 | G84 | G85 | G86 | G87 | G88 | G89 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| picado rápido | roscado izquierdo (M04) | mandrinado fino | taladrado | con pausa en el fondo | picado profundo | roscado derecho (M03) | mandrinado, sale en avance | sale con husillo parado | mandrinado inverso | pausa y parada manual | pausa, sale en avance |

Antes de G84 o G74 el husillo tiene que estar girando en el sentido que corresponde ([FM]). En roscado con macho, F = paso × n en G94 (o el paso en G95).

## Subprogramas

`M98 P51002` llama 5 veces al O1002 (las primeras cifras son las repeticiones; las últimas 4, el número de programa); sin repeticiones lo llama una vez; el subprograma termina con `M99` y vuelve al bloque siguiente ([FM]). En torno, un subprograma en U/W (incremental) repite una ranura o un perfil corrido.

## Funciones M habituales

M00 parada · M01 parada opcional · M02 fin · M03 giro horario · M04 antihorario · M05 para el husillo · M06 cambio de herramienta (fresadora) · M08 / M09 refrigerante · M30 fin de programa · M98 / M99 subprograma ([ET], [EM]). Casi todas las M las define el fabricante de la máquina en su PLC (por ejemplo M10 a M13 para plato o contrapunta cambian entre modelos, ver la sección GSK): verificar en el manual de la máquina.

## Parámetros de corte

| Magnitud | Torno | Fresadora |
|---|---|---|
| Giro | n = 1000·Vc / (π·D), D de la pieza | n = 1000·Vc / (π·D), D de la herramienta |
| Avance | Vf = f·n (f en mm/v) | Vf = fz·z·n (fz en mm/diente, z filos) |
| Tiempo | t = L / Vf por pasada (L con entrada y salida) | igual |
| Caudal de viruta | Q = Vc·ap·f [cm³/min] | Q = ap·ae·Vf / 1000 [cm³/min] |
| Espesor de viruta | h = f·sen κr | hm = fz·(1 − cos φ)/φ, con cos φ = 1 − 2·ae/D |
| Potencia de corte | Pc = Vc·ap·f·kc / 60 000 [kW] | Pc = ap·ae·Vf·kc / (60·10⁶) [kW] |

kc = kc1·h^(−mc) (Kienzle; fórmulas de giro, avance y potencia de fresado como en Sandvik Coromant [SC]); potencia en el motor = Pc/η. Con G96 la rpm crece al bajar el diámetro: a Vc = 200 m/min en Ø5 serían 12 732 rpm, por eso el G50 S. Si la n calculada supera la de la máquina, la Vc real baja (el script lo muestra).

Valores orientativos de catálogo (rango del fabricante; empezar por abajo en máquinas chicas): torneado de acero al carbono o aleado 180–280 HB con plaquita de metal duro recubierta, desbaste medio Vc 230–440 m/min, f 0,15–0,51 mm/v, ap 0,3–4 mm; inoxidable < 200 HB Vc 165–259 m/min; aluminio Vc 300–700 m/min ([MT], convertido de pulgadas). Broca de acero rápido recubierta en acero al carbono ≈ 40 m/min ([DO]). Fresa de metal duro Ø10 de 3 filos en acero, fresado lateral: Vc 150 m/min, fz 0,09 mm ([MF]). Tabla completa, kc1 y mc por material (ISCAR) y ejemplos: `references/datos-de-corte.md`.

## Hoja de proceso

Encabezado: pieza, plano, material, bruto, máquina y control, sujeción, cero pieza, autor, fecha. Una fila por operación:

| N.º | Operación | Herramienta (T y corrector) | Vc (m/min) | n (rpm) | f (mm/v) o fz | ap (mm) | Vf (mm/min) | L (mm) | Pasadas | t (min) | Observaciones |
|---|---|---|---|---|---|---|---|---|---|---|---|

El script `corte` imprime la fila lista. Al final, tiempo total y un croquis con el cero pieza y la sujeción. Plantilla completa y ejemplo resuelto: `references/hoja-de-proceso.md`.

## Simulación antes de la máquina

- **WinUnisoft MultiCNC** (Alecop): simulador educativo de programas CNC en la PC ([WU], [WV]). Si la versión trae varios controles, elegir el de la máquina; cargar el bruto con sus medidas y cada herramienta en el gestor con su número y corrector, y mirar el arranque de material y las colisiones.
- **CNC Simulator Pro**: pago; fresadoras de 2 a 4 ejes y tornos, códigos ISO y ciclos inspirados en Fanuc ([CS]).
- **NC Viewer**: visualiza la trayectoria en el navegador ([NV]); si no dibuja un ciclo (G71, G76…), comprobarlo en un simulador del control.
- **Simulador gratuito de Fagor**: fresado y torneado, 3 ejes y 1 husillo, sin vencimiento ([FS]); sirve si la máquina es Fagor.
- En el simulador: el bruto real, las herramientas con su radio, el cero pieza donde se va a tomar, y comprobar cada cambio de herramienta y cada aproximación rápida.

## Verificación en la máquina

1. Cargar y comparar el programa con el simulado; revisar correctores (geometría y desgaste) y el cero pieza.
2. **En vacío**: sin pieza, o con el cero corrido en Z (+50 o lo que indique el profesor), avance rápido al 25 % o menos.
3. **Bloque a bloque** en el primer recorrido con pieza, con la sobreescritura de avance baja y la mano en la parada; mirar la cuenta "falta por recorrer" antes de cada aproximación.
4. Primer corte con poco ap; medir y corregir el desgaste del corrector, no el programa.
5. G00 puede no ir en línea recta: Fanuc puede mover cada eje a su velocidad rápida por separado, según un parámetro ([FM]), y GSK lo describe como movimiento no lineal ([GT]). Aproximar con X y Z de seguridad (fuera del bruto y delante de la cara).

## Errores frecuentes

- **Número sin punto**: en Fanuc, `X10` vale 10 en la unidad mínima (0,010 mm), salvo que el control esté en modo calculadora ([FM]). Escribir siempre `X10.`.
- **X en radio** en vez de diámetro; I en diámetro.
- **G96 sin G50 S**: las rpm se disparan al llegar al centro (refrentado, tronzado).
- **F0.2 con G98** (mm/min): la herramienta casi no avanza; en torno se usa G99 para mm/v. Al revés, F200 en G99 es un choque.
- Cambiar de herramienta sin retirar o con la torreta cerca del plato o de la contrapunta; salir en Z antes que en X en un exterior.
- Activar G41/G42 en un arco o sin recorrido de entrada; olvidar G40 o G43.
- G71 con un contorno que no es monótono, o con Z en el bloque ns sin querer el tipo II.
- Roscar con G96; P y Q de G76 escritos con punto.
- Olvidar M08 y M09; terminar sin M05 ni M30.
- Usar los datos de corte de un catálogo sin mirar la potencia y las rpm máximas de la máquina.

## Controles GSK de torno de escuela (928TC, 928TE, 980TD)

Diferencias con Fanuc confirmadas en sus manuales (detalle y enlaces en `references/gsk-torno.md`):

- **980TD**: muy parecido a Fanuc sistema A (G70–G76, G90/G92/G94, G96/G97, G98/G99, U/W, `T0101`, `O` + 4 cifras, M98/M99); G33 es roscado con macho y G32 roscado ([GD]). El 980TDc agrega J, K y L en G92 ([GC]).
- **928TC y 928TE**: el programa se llama `%` + 2 cifras y cada bloque lleva N + 4 cifras ([GC9], [GE2]); en el 928TC, `T22` = herramienta 2 con corrector 2 (dos cifras) y G26/G27/G29 vuelven al punto de referencia del programa; sus ejemplos empiezan con `G50 X100 Z100` ([GC9]); el 928TEa usa `T01□□` y arranca en **G98 (mm/min)** ([GE]).
- **Velocidades**: sin variador, S1 a S4 (o S00 a S15) son **gamas** de la máquina, no rpm; con variador, S en rpm por la salida analógica ([GC9], [GD]).
- Las M (plato, contrapunta, lubricación) cambian de modelo a modelo y las define el PLC del fabricante ([GD]).

Cada máquina o taller puede tener convenciones propias (por ejemplo, un corrimiento fijo de las coordenadas respecto del diámetro, o solo algunas rpm escalonadas): conseguir un programa que ya funcione en esa máquina, compararlo con el propio y preguntar. **Siempre mandan el manual de la máquina y el profesor.** Si el control es Siemens, Fagor o Heidenhain, usar su manual de programación: los ciclos y varias funciones cambian.

## Antes de entregar

1. `cnc.py revisar` sin errores (con `--rango` de los recorridos de la máquina) y los avisos explicados.
2. Simulación con bruto y herramientas: sin choques, la pieza simulada coincide con el plano (medir dos o tres cotas).
3. Hoja de proceso con los mismos T, S, F y tiempos que el programa.
4. Comentarios en el programa: pieza, autor, cero pieza, herramientas.

[FT]: https://www.cnc.info.pl/download/file.php?id=7509 "FANUC 30i/31i/32i-A, User's Manual (lathe system) B-63944EN-1/02 (copia pública)"
[FM]: https://www.star-circuit.com/article/pdf/FANUC_OPERATOR_Manual_MB.PDF "FANUC 16i/18i-MB Operator's Manual B-63534EN/02 (copia pública)"
[F0]: https://www.slideshare.net/slideshow/fanuc-0itd-users-manualpdf/259106078 "FANUC 0i-TD User's Manual B-64304EN-1/01 (copia pública)"
[ET]: https://www.emco-world.com/fileadmin/user_upload/_Group/pics_products/Training_Software/software_manuals/Fanuc_21/Fanuc21TB_SP_C.pdf "EMCO WinNC Fanuc 21 TB"
[EM]: https://www.emco-world.com/fileadmin/user_upload/_Group/pics_products/Training_Software/software_manuals/Fanuc_21/Fanuc21MB_SP_C.pdf "EMCO WinNC Fanuc 21 MB"
[GD]: https://manualmachine.com/gsk/gsk980td/4712531-user-manual/ "GSK980TD User Manual, programación"
[GC]: https://www.manualslib.com/manual/1595889/Gsk-Gsk980tdc.html "GSK980TDc"
[GC9]: https://manualmachine.com/gsk/gsk928tc/4712520-user-manual "GSK928TC User Manual"
[GE]: https://manualmachine.com/gsk/gsk928tea/4712525-user-manual "GSK928TEa User Manual"
[GE2]: https://manualmachine.com/gsk/gsk928teii/4712524-user-manual/ "GSK928TE II User Manual"
[GT]: https://manualmachine.com/gsk/gsk928te/4712523-user-manual "GSK928TE/GSK928TC User Manual"
[SC]: https://cdn.sandvik.coromant.com/files/sitecollectiondocuments/services/metal-cutting-e-learning/formulas-and-definitions/formulas-and-deinitions-for-milling-metric-enu.pdf "Sandvik Coromant, fórmulas de fresado"
[MT]: https://data.mmc-carbide.com/4416/9575/0602/catalog_c010a_turning_inserts.pdf "Mitsubishi Materials, catálogo C010A de plaquitas de torneado"
[MF]: https://www.mitsubishicarbide.net/contents/mht/enuk/manual/solid_end_mills_iMX_S3HV.pdf "Mitsubishi Materials, iMX S3HV"
[DO]: https://cdn.dgisupply.ca/img/product-images/Asset_URL/Dormer_0390795_Specification_Sheet.pdf "Dormer A510 ADX"
[WU]: https://www.advanceduninstaller.com/Winunisoft-multicnc-version-4_5-569e83bbdd78fbe07ecd619cb079f727-application.htm "Winunisoft MultiCNC, Alecop S. Coop."
[WV]: https://www.vicomtech.org/upload/download/publicaciones/20061019_AitorMoreno_SIMUMEKU_inproceedings_75.pdf "SIMUMEK (Vicomtech), menciona WinUniSoft"
[CS]: https://cncsimulator.freshdesk.com/support/solutions/articles/12000101844-cnc-simulator-pro-overview "CNC Simulator Pro"
[NV]: https://toolpath.com/blog/why-nc-viewer-joined-toolpath "NC Viewer"
[FS]: https://fagorautomation.com/en/?p=854034 "Fagor, simulador CNC gratuito"
