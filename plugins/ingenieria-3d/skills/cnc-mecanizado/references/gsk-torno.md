# Controles GSK de torno (928TC, 928TE, 980TD): diferencias con Fanuc

Leer cuando la máquina tenga un control GSK (GSK CNC Equipment Co., Guangzhou), frecuentes en tornos CNC de escuela. Acá va solo lo que se confirmó en los manuales públicos de GSK (copias en sitios de manuales; el sitio del fabricante no se pudo consultar). Lo demás: **manual de la máquina y profesor**. El fabricante del torno además configura el PLC (funciones M, gamas de velocidad, torreta), así que dos tornos con el mismo control pueden programarse distinto.

## Antes de programar una máquina GSK

1. Anotar el modelo exacto del control (928TC, 928TCa, 928TE, 928TEa, 928TE II, 980TD, 980TDb, 980TDc…): cambian mucho entre sí.
2. Conseguir un programa que ya funcione en **esa** máquina (del profesor o del taller) y compararlo línea por línea con el propio: nombre del programa, numeración de bloques, forma de la T, de la S y de las M, ciclos y valores de X (si hay un corrimiento fijo, se nota enseguida: por ejemplo, X que no coincide con el diámetro del plano).
3. Averiguar cómo se toma el cero pieza (correctores de herramienta o `G50` en un punto conocido) y cuál es el punto de cambio de herramienta.
4. Si el husillo no tiene variador, averiguar qué rpm da cada gama (S1, S2…) y elegir la más cercana a la calculada (sin pasarse en Vc).
5. Simular en un simulador que tenga ese control, o al menos con un programa Fanuc equivalente, y probar en vacío y bloque a bloque.

## GSK980TD

Fuente: [GD] *GSK980TD Turning Machine CNC System User Manual*, libro 1 (programación), software V06.03.23 (<https://manualmachine.com/gsk/gsk980td/4712531-user-manual/>).

- Es el más parecido a Fanuc sistema A. Lista de G: G00, G01, G02, G03, G04, G28, G32 (roscado de paso constante), **G33 (ciclo de roscado con macho en Z)**, G34 (paso variable), G40, G41, G42, G50 (sistema de coordenadas), G65 (macro), G70 a G76, G90, G92, G94, G96, G97, G98 (mm/min), G99 (mm/vuelta).
- Programa: `O` + 4 cifras (O0000 a O9999). X en diámetro cuando el parámetro NO.001 Bit2 vale 0; U y W incrementales.
- Herramienta: `T0101` = herramienta 1 con su corrector; `T0100` anula el corrector. Hasta 32 posiciones; el cambio lo maneja el PLC.
- Velocidad: con gamas, `S00` a `S04` son salidas que define el PLC (S0 apaga); con variador, S en rpm (0 a 9999) o en m/min con G96, por una salida de 0 a 10 V. M41 a M44: cambio automático de gama.
- Funciones M del PLC estándar: M03, M04, M05, M08, M09, M10/M11 contrapunta, M12/M13 plato (sujeta y suelta), M32/M33 lubricación, M98 (ejemplo del manual: `M98 P21006`), M99, M00, M02, M30. El resto de las M las define el PLC y el fabricante de la máquina puede cambiarlas.
- Avances: G98 de 0 a 8000 mm/min; G99 de 0,0001 a 500 mm/vuelta.
- **GSK980TDc**: el ciclo de roscado G92 lleva además J, K y L (`G92 X(U) Z(W) F J K L`), que no están en el G92 de Fanuc ([GC] <https://www.manualslib.com/manual/1595889/Gsk-Gsk980tdc.html>).

## GSK928TC

Fuente: [GC9] *GSK928TC Turning CNC System User Manual*, parte de operación (<https://manualmachine.com/gsk/gsk928tc/4712520-user-manual>).

- Programa: `%` y dos cifras (`%00`, `%20`); cada bloque empieza con N y 4 cifras (`N0010`), con incremento fijado por el parámetro P23.
- Herramienta: T de **dos cifras**, herramienta y corrector: `T22` = herramienta 2 con corrector 2, `T31` = herramienta 3 con corrector 1; corrector 0 anula (`T40`).
- Velocidad: con SCOD = 0, salidas S1 a S4 (gamas); con SCOD = 1, códigos S00 a S15; con MDSP = 1, salida analógica de 0 a 10 V (variador). Es decir, `S2` puede ser "gama 2" y no 2 rpm.
- G26, G27 y G29 vuelven al punto de referencia del programa (qué eje mueve cada uno: ver el manual); los ejemplos del manual empiezan con `G50 X100 Z100`.
- Funciones M que lista: M03, M04, M05, M08, M09, M10, M11, M32, M33, M21 a M24 (su función depende de la máquina).
- Según una tabla comparativa de un distribuidor (no del manual), el 928TCa no tiene compensación de radio de punta (G41/G42), G34 ni otras funciones del 928TEa ([PC] <https://paycnc.com/info/gsk928tea-gsk928tca-differences_i0096.html>): verificar en el manual de la máquina.

## GSK928TE (928TE, 928TEa, 928TE II)

Fuentes: [GT] *GSK928TE/GSK928TC Turning Machine CNC System User Manual* (<https://manualmachine.com/gsk/gsk928te/4712523-user-manual>; índice y alcance en <https://www.manualslib.com/manual/2557757/Gsk-Gsk928te.html>, software V3.20); [GE] *GSK928TEa Turning CNC System User Manual* (<https://manualmachine.com/gsk/gsk928tea/4712525-user-manual>); [GE2] *GSK928TE II Turning CNC System User Manual* (<https://manualmachine.com/gsk/gsk928teii/4712524-user-manual/>).

- G00 hace un movimiento **no lineal** entre el punto inicial y el final ([GT]): aproximar desde zonas libres.
- 928TE II: programas `%00` a `%99`, bloques N con 4 cifras (incremento P23), salidas S1 a S4, códigos S0 a S15 o 0 a 10 V ([GE2]).
- 928TEa ([GE]):
  - G: G00, G01, G02, G03, G04, G05, G26, G28, G30, G31, G32, G33, G34, G40, G41, G42, G50, G51, G71 a G76, G90, G92, G94, G96, G97, G98, G99; G22/G80 repiten una parte del programa.
  - G26: vuelta al punto de referencia en X, Z (e Y); G28: vuelta al cero máquina; G50 fija el sistema de pieza y G51 lo restituye.
  - **Estado al encender: G00, G40, G97, G98**. Arranca en mm/min: si se programa F0.2 pensando en mm/vuelta sin escribir G99, la herramienta casi no avanza.
  - Herramientas `T01□□` a `T16□□` (hasta 16).
  - S01 a S04 para 4 gamas directas, 16 gamas en BCD o salida analógica.
  - M que lista: M00, M02, M20, M30, M03, M04, M05, M08, M09, M10, M11, M12, M32, M33, M41 a M44, M47/M48, M78 a M80, M91 a M99, M21 a M24; M60 a M74 las define el usuario.
- Índice del manual del 928TEa ([GE3] <https://www.manualslib.com/manual/1593748/Gsk-Gsk928tea.html>). Las páginas con el formato de cada ciclo no se pudieron leer: las direcciones de cada bloque se toman del manual de la máquina.
  - **G33 es el roscado y G32 el ciclo de roscado con macho**, al revés que en el 980TD (G32 roscado, G33 macho, [GD]): un bloque copiado de un control al otro cambia de función.
  - Ciclos simples: G90 cilindrado exterior (corte axial), G92 roscado, G94 refrentado interior o exterior (también cónico), G74 agujereado profundo en la cara frontal, G75 ranurado.
  - Ciclos compuestos: G71 desbaste axial, G72 desbaste frontal, G73 ciclo de corte cerrado, G76 roscado múltiple; G22 y G80, repetición de una parte del programa.
  - G27, G29, G81 y G84 no figuran en ese índice. En el 928TC no se confirmó cuál de G32 y G33 es el roscado.

## Mismo nombre, otra función

En el GSK928TD (otro modelo de la familia 928) M10 y M11 sujetan y sueltan el plato, M41 a M44 eligen la gama y el estado al encender también es G98 ([TD] *GSK928TD Turning CNC System User Manual*, <https://paycnc.com/u_file/2107/file/a29bc1aff0.pdf>), mientras que en el 980TD M10/M11 son de la contrapunta y M12/M13 del plato ([GD]). Por eso las M de un programa no se copian de una máquina a otra sin mirar su manual.

## Qué hace el script con estos controles

- `cnc.py revisar` avisa de números sin punto decimal y de F menor que 5 sin G99 escrito (el caso de arrancar en G98). Lee programas `%00` y T de dos cifras, pero sus chequeos están pensados para Fanuc: un ciclo con otro formato puede dar avisos de más o pasar sin revisar.
- `cnc.py perfil --modo pasadas` genera el desbaste con G00/G01 solos, útil cuando el ciclo de desbaste del control tiene otro formato. Después hay que adaptar el encabezado (nombre del programa, T, S) a la máquina.
