# Fresadora Fanuc (serie M): formatos y ejemplos

Leer cuando haya que escribir o corregir un programa de fresadora o de centro de mecanizado. Los programas de ejemplo pasan `cnc.py revisar` sin errores; los datos de corte son de ejemplo (calcularlos con `cnc.py corte` y el catálogo de la herramienta).

Fuentes: [FM] FANUC Series 16i/18i-MB, *Operator's Manual*, B-63534EN/02 (copia pública: <https://www.star-circuit.com/article/pdf/FANUC_OPERATOR_Manual_MB.PDF>); [EM] EMCO WinNC GE Series Fanuc 21 MB, manual del software en español (<https://www.emco-world.com/fileadmin/user_upload/_Group/pics_products/Training_Software/software_manuals/Fanuc_21/Fanuc21MB_SP_C.pdf>).

## Lo básico

- G90 absoluto, G91 incremental; G94 avance en mm/min (al encender) y G95 en mm/vuelta ([FM]).
- G17, G18, G19: planos XY, ZX, YZ; los arcos y la compensación de radio trabajan en el plano elegido ([FM]).
- G54 a G59: sistemas de pieza 1 a 6; quedan definidos después de la vuelta a referencia al encender ([FM]).
- G28: vuelve a la referencia pasando por un punto intermedio, en rápido (cada eje a su velocidad) ([FM]); `G91 G28 Z0.` sube en Z desde donde está.
- Número sin punto decimal: en la unidad mínima (`X1000` = 1 mm), salvo el modo calculadora del parámetro DPI ([FM]).
- M06 cambio de herramienta, M03/M04/M05 husillo, M08/M09 refrigerante, M00/M01 paradas, M02/M30 fin, M98/M99 subprograma ([EM]). El orden de T y M06 (en el mismo bloque o T antes) depende de la máquina.

## Arcos (G02, G03)

- G02 horario y G03 antihorario mirando el plano desde el lado positivo del eje perpendicular (en G17, desde +Z).
- Con R: si el arco pasa de 180°, R va negativo ([FM]).
- Con I, J, K: distancia **incremental** del punto inicial al centro, con signo, aunque esté G90 ([FM]). El círculo completo se programa solo así (punto final igual al inicial).

## Compensaciones

- **Largo**: `G43 H01` (positiva), G44 (negativa), G49 o H0 la anulan; H0 vale siempre 0 ([FM]). Se activa en cada herramienta antes de bajar en Z.
- **Radio**: `G41 D01` a la izquierda, `G42 D01` a la derecha mirando en el sentido del avance; D es el número de corrector (H si el parámetro OFH lo indica) ([FM]). Se activa en un bloque G00 o G01 (en G02/G03 da alarma) con un recorrido de entrada mayor que el radio, y se anula con G40 al salir. Contorno exterior recorrido en sentido horario con G41: fresado en concordancia.

## Ciclos fijos de agujeros

Formato: `G90/G91 G98/G99 G__ X_ Y_ Z_ R_ Q_ P_ F_ K_` ([FM]).

| Dirección | Significado |
|---|---|
| X, Y | posición del agujero |
| Z | fondo (en G91, distancia desde el plano R) |
| R | plano de aproximación (en G91, distancia desde el nivel inicial) |
| Q | profundidad por picada (G73, G83) o corrimiento en el fondo (G76, G87) |
| P | pausa en el fondo |
| F | avance |
| K | repeticiones (K0 guarda los datos sin agujerear) |

| Ciclo | Bajada | En el fondo | Subida | Uso |
|---|---|---|---|---|
| G73 | por picadas | — | rápido | picado rápido (rompe viruta) |
| G74 | avance | pausa, husillo horario | avance | roscado con macho izquierdo |
| G76 | avance | parada orientada | rápido | mandrinado fino |
| G80 | — | — | — | anula el ciclo |
| G81 | avance | — | rápido | taladrado, punteado |
| G82 | avance | pausa | rápido | taladrado o rebaje con pausa |
| G83 | por picadas | — | rápido | taladrado profundo |
| G84 | avance | pausa, husillo antihorario | avance | roscado con macho derecho |
| G85 | avance | — | avance | mandrinado |
| G86 | avance | para el husillo | rápido | mandrinado |
| G87 | avance | husillo horario | rápido | mandrinado inverso |
| G88 | avance | pausa, para el husillo | manual | mandrinado |
| G89 | avance | pausa | avance | mandrinado |

Tabla resumida de [FM]. G98 vuelve al nivel inicial y G99 al plano R; en general G99 entre agujeros y G98 en el último ([FM]). El ciclo sigue activo hasta G80 o un código del grupo 01 (G00, G01, G02, G03) ([FM]), así que cada bloque con X o Y hace otro agujero. Antes de G84 el husillo tiene que girar con una M (horario) y antes de G74 en sentido antihorario ([FM]); en roscado rígido se programa M29 S.. antes o en el bloque del ciclo ([FM]). En G94, F = paso × rpm (M6 × 1 a 300 rpm: F300).

## Programa de ejemplo: contorno, agujeros y roscas

Placa con el cero en la esquina inferior izquierda de la cara superior; contorno de 80 × 40 mm con un redondeo R20 y tres roscas M6 a 20 mm del borde.

```
%
O1000 (PLACA 80X40 - CONTORNO, AGUJEROS Y ROSCAS)
N10 G21 G17 G40 G49 G80 G90 G94
N20 G91 G28 Z0.
N30 G90
N40 T1 M06 (FRESA D10 3 FILOS)
N50 G54 G00 X-20. Y-20. S3180 M03 (VC 100 M/MIN)
N60 G43 H01 Z50. M08
N70 Z5.
N80 G01 Z-3. F300.
N90 G41 D01 X0. Y0. F480. (FZ 0,05 X 3 FILOS X 3180 RPM)
N100 Y40.
N110 X60.
N120 G02 X80. Y20. R20.
N130 G01 Y0.
N140 X0.
N150 G40 G00 X-20. Y-20.
N160 Z50. M09
N170 G91 G28 Z0.
N180 M05
N190 G90
N200 T2 M06 (BROCA D5 PARA M6)
N210 G54 G00 X20. Y20. S2550 M03 (VC 40 M/MIN)
N220 G43 H02 Z50. M08
N230 G99 G83 X20. Y20. Z-15. R2. Q3. F250.
N240 X40.
N250 G98 X60.
N260 G80
N270 G00 Z50. M09
N280 G91 G28 Z0.
N290 M05
N300 G90
N310 T3 M06 (MACHO M6X1)
N320 G54 G00 X20. Y20. S300 M03
N330 G43 H03 Z50. M08
N340 G99 G84 X20. Y20. Z-12. R5. F300. (F = PASO X RPM)
N350 X40.
N360 G98 X60.
N370 G80
N380 G00 Z50. M09
N390 G91 G28 Z0.
N400 M05
N410 M30
%
```

Cuentas del ejemplo (con `cnc.py corte`): n = 1000·100/(π·10) = 3183 rpm → S3180; Vf = 0,05·3·3180 = 477 mm/min → F480; broca n = 1000·40/(π·5) = 2546 rpm → S2550 y F250 = 0,1 mm/v × 2550. La broca de 5 mm es la de la rosca M6 × 1 (d − P). Revisión: `cnc.py revisar placa.nc --rango "X-25:85,Y-25:45,Z-16:60"`.

## Subprogramas

`M98 P51002` llama 5 veces al O1002: las cifras de la izquierda son las repeticiones y las 4 de la derecha el número de programa; sin repeticiones lo llama una vez ([FM]). `M99` termina el subprograma y vuelve al programa que lo llamó ([FM]). Ejemplo: el mismo contorno en tres pasadas de 1 mm, bajando en incremental dentro del subprograma.

```
%
O1100 (CONTORNO EN 3 PASADAS DE 1 MM)
N10 G21 G17 G40 G49 G80 G90 G94
N20 G91 G28 Z0.
N30 G90
N40 T1 M06 (FRESA D10)
N50 G54 G00 X-20. Y-20. S3180 M03
N60 G43 H01 Z50. M08
N70 Z0.
N80 M98 P31101
N90 G90 G00 Z50. M09
N100 G91 G28 Z0.
N110 M05
N120 M30
%
O1101 (UNA PASADA: BAJA 1 MM Y RECORRE EL CONTORNO)
N10 G91 G01 Z-1. F300.
N20 G90 G41 D01 X0. Y0. F480.
N30 Y40.
N40 X80.
N50 Y0.
N60 X0.
N70 G40 G00 X-20. Y-20.
N80 M99
%
```

Al volver de cada llamada la herramienta queda en X−20 Y−20, 1 mm más abajo; después de la tercera, en Z−3.
