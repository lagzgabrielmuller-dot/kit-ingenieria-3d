# Torno Fanuc (serie T, sistema de códigos G A): formatos y ejemplos

Leer cuando haya que escribir o corregir un programa de torno con ciclos. Todo lo que dice "verificar" no se pudo confirmar en un manual público: confirmarlo en el manual de la máquina. Los cuatro programas de ejemplo pasan `cnc.py revisar` sin errores; igual hay que simularlos.

Fuentes: [FT] FANUC 30i/31i/32i-MODEL A, *User's Manual (For Lathe System)*, B-63944EN-1/02 (copia pública: <https://www.cnc.info.pl/download/file.php?id=7509>); [F0] FANUC 0i-TD, *User's Manual*, B-64304EN-1/01 (<https://www.slideshare.net/slideshow/fanuc-0itd-users-manualpdf/259106078>); [ET] EMCO WinNC GE Series Fanuc 21 TB, manual del software en español (<https://www.emco-world.com/fileadmin/user_upload/_Group/pics_products/Training_Software/software_manuals/Fanuc_21/Fanuc21TB_SP_C.pdf>).

## Sistema de códigos G

El torno Fanuc tiene tres sistemas de códigos G (A, B y C), elegidos por parámetro; los manuales describen el A ([FT]). Equivalencias que más confunden:

| Función | A | B | C |
|---|---|---|---|
| Fijar coordenadas / límite de rpm | G50 | G92 | G92 |
| Cilindrado simple | G90 | G77 | G20 |
| Roscado simple | G92 | G78 | G21 |
| Refrentado simple | G94 | G79 | G24 |
| Terminación / desbaste longitudinal | G70 / G71 | G70 / G71 | G72 / G73 |
| Avance mm/min / mm/vuelta | G98 / G99 | G94 / G95 | G94 / G95 |
| Roscado de paso constante | G32 | G33 | G33 |

En el A lo absoluto o incremental se elige con la letra (X/U, Z/W), no con G90/G91 ([FT]). El simulador EMCO WinNC Fanuc 21 TB usa el C: G70/G71 pulgadas y mm, G72 ciclo de terminación, G90/G91 absoluto e incremental ([ET]). Si un programa "de Fanuc" no coincide con esta tabla, probablemente es de otro sistema.

## Coordenadas, herramienta y velocidades

- X en diámetro ([FT]); U y W son incrementales. `G50 X.. Z..` fija las coordenadas de la posición actual (otra forma de definir el cero pieza) y `G50 S..` limita las rpm ([FT]).
- `T0101`: las dos primeras cifras eligen la posición de la torreta y las dos últimas el corrector ([ET]); con corrector 0 la compensación queda anulada (`T0100`) ([FT]).
- `G96 S180`: S en m/min; hace falta fijar antes la velocidad máxima ([FT]) con `G50 S..`. Con G96 no se rosca: se usa G97 ([F0]).
- `G99 F0.2`: mm/vuelta; `G98 F100.`: mm/min.

## Ciclos simples (G90, G92, G94)

- `G90 X(U) Z(W) F` cilindrado; con `R` (en radio, con signo) hace un cono ([FT]). Movimiento: rápido en X hasta la cota, corte en Z, corte de vuelta en X hasta la X de partida y rápido en Z al punto de partida ([FT]).
- `G92 X(U) Z(W) F(paso)` roscado de una pasada (admite una `Q` opcional: ver el manual) y `G94 X(U) Z(W) F` refrentado; los dos con `R` para cono ([FT]).
- X, Z y R son modales y comunes a los tres: para repetir el ciclo con otra profundidad basta un bloque con la nueva X ([FT]).

```
%
O0101 (REFRENTADO G94 Y CILINDRADO G90)
N10 G21 G40 G97 G99
N20 G00 X100. Z100.
N30 T0101 (DESBASTE EXTERIOR)
N40 G50 S2000
N50 G96 S180 M03
N60 G00 X42. Z1. M08 (PARTIDA: BRUTO D40 CON 1 MM EN LA CARA)
N70 G94 X0. Z0. F0.2 (REFRENTADO HASTA EL CENTRO)
N80 G00 Z2.
N90 G90 X38. Z-30. F0.25 (CILINDRADO EN 3 PASADAS)
N100 X36.
N110 X34.
N120 G00 X100. M09
N130 Z100.
N140 M05
N150 M30
%
```

## Ciclos múltiples (G70 a G76)

| Ciclo | Bloques | Qué es cada dirección |
|---|---|---|
| G71 desbaste longitudinal | `G71 U(Δd) R(e);` `G71 P(ns) Q(nf) U(Δu) W(Δw) F S T;` | Δd: profundidad por pasada, en radio y sin signo; e: retiro; ns, nf: primer y último bloque del contorno; Δu, Δw: sobremetal en X (en diámetro) y en Z, con signo ([FT]) |
| G72 desbaste transversal | `G72 W(Δd) R(e);` `G72 P Q U W F S T;` | igual que G71, con las pasadas en Z ([FT]) |
| G73 repetición de perfil | `G73 U(Δi) W(Δk) R(d);` `G73 P Q U W F S T;` | Δi, Δk: distancia total de alivio (el material a sacar) en X y en Z, en radio y con signo; d: cantidad de pasadas ([FT]) |
| G70 terminación | `G70 P(ns) Q(nf);` | recorre el contorno con las F, S y T escritas en él ([FT]) |
| G74 agujereado en Z | `G74 R(e);` `G74 X(U) Z(W) P(Δi) Q(Δk) R(Δd) F;` | e: retroceso en cada picada; Δk: profundidad por picada; sin X ni P es solo agujereado en el eje ([FT]) |
| G75 ranurado en X | `G75 R(e);` `G75 X(U) Z(W) P(Δi) Q(Δk) R(Δd) F;` | como G74 con los ejes cambiados; sin Z ni Q es una sola ranura ([FT]) |
| G76 roscado múltiple | `G76 P(m)(r)(a) Q(Δdmin) R(d);` `G76 X(U) Z(W) R(i) P(k) Q(Δd) F(L);` | m: pasadas de terminación (1 a 99); r: chaflán de salida en décimas de paso (00 a 99); a: ángulo de la herramienta (80, 60, 55, 30, 29 o 0); Δdmin: pasada mínima; d: sobremetal de terminación; X: diámetro de fondo; i: diferencia de radios en rosca cónica; k: altura del filete (en radio); Δd: primera pasada; L: paso ([FT]) |

Reglas ([FT]):
- G71 **tipo I**: el bloque ns lleva solo X (o U); si lleva también Z (o W) es **tipo II**, que admite rebajes en X pero tiene que ser monótono en Z. El tipo I necesita un contorno monótono en X y en Z.
- Las F, S y T del contorno (ns a nf) no se usan en G71, G72 ni G73 (valen las de ese bloque) y sí en G70; los G96/G97 escritos dentro del contorno tampoco se usan en el desbaste.
- P y Q de G74 y G75 no admiten punto decimal; e, Δi y Δk van en la unidad mínima. En G76, Δdmin, d, k y Δd van en la unidad mínima (0,001 mm): `P920` = 0,92 mm.
- Dentro de la compensación de radio de punta los ciclos pueden comportarse distinto según el modelo: verificar en el manual.

### Perfil con G71 y G70 (sale de `cnc.py perfil`)

Puntos `16;0 20;-2 20;-15 30;-25 30;-40`, bruto Ø34, desbaste T0101 y terminación T0202:

```
%
O0001 (PERFIL)
N10 G21 G40 G97 G99 (MM - SIN COMPENSACION - RPM FIJAS - MM/V)
N20 G00 X100. Z100. (PUNTO DE CAMBIO)
N30 T0101 (DESBASTE)
N40 G50 S2000 (LIMITE DE RPM PARA G96)
N50 G96 S180 M03 (VC CONSTANTE)
N60 G00 X36. Z2. M08 (PUNTO DE PARTIDA)
N70 G71 U1. R0.5
N80 G71 P90 Q150 U0.4 W0.1 F0.25
N90 G00 X16. (CONTORNO)
N100 G01 Z0. F0.1
N110 X20. Z-2.
N120 Z-15.
N130 X30. Z-25.
N140 Z-40.
N150 X36.
N160 G00 X100. (RETIRO EN X)
N170 Z100.
N180 T0202 (TERMINACION)
N190 G50 S2000
N200 G96 S220 M03
N210 G00 X36. Z2. M08 (PUNTO DE PARTIDA)
N220 G70 P90 Q150
N230 G00 X100. M09 (RETIRO: PRIMERO X)
N240 Z100.
N250 M05
N260 M30
%
```

Con `--modo pasadas` el mismo perfil sale con G01 explícitos: 8 pasadas de 0,978 mm que terminan donde tocan el perfil más el sobremetal (redondeadas hacia el lado seguro), un perfilado con el sobremetal que saca los escalones de los conos y el contorno final. Sirve para controles sin G71 o con otro formato. Con `--g42` la terminación lleva compensación de radio de punta (cargar R y la punta imaginaria en el corrector).

### Rosca M20 × 1,5 con G76

Altura del filete de la rosca métrica ISO exterior: h3 = 17·H/24 = 0,6134·P, con H = 0,866·P (de d3 = d1 − H/6, ISO 965-1). Para P = 1,5: h3 = 0,920 mm y diámetro de fondo d3 = 20 − 2·0,920 = 18,16 mm (verificado con Python; el inserto de rosca y la tabla del taller pueden pedir otro valor).

```
%
O0103 (ROSCA M20X1.5 CON G76)
N10 G21 G40 G97 G99
N20 G00 X100. Z100.
N30 T0303 (HERRAMIENTA DE ROSCAR 60 GRADOS)
N40 G97 S600 M03 (RPM FIJAS PARA ROSCAR)
N50 G00 X22. Z5. M08 (PARTIDA CON ENTRADA DE VARIOS PASOS)
N60 G76 P021060 Q100 R50
N70 G76 X18.16 Z-20. P920 Q300 F1.5
N80 G00 X100. M09
N90 Z100.
N100 M05
N110 M30
%
```

`P021060`: 2 pasadas de terminación, chaflán de 1,0 paso, herramienta de 60°; `Q100`: pasada mínima 0,1 mm; `R50`: sobremetal de terminación 0,05 mm; `P920`: altura 0,92 mm; `Q300`: primera pasada 0,3 mm. Si el control toma R del primer bloque con punto decimal, el valor cambia: verificar en el manual de la máquina. Las rpm de roscado dependen del inserto y de la máquina.

### Agujero con G74 y ranura con G75

```
%
O0104 (AGUJERO G74 Y RANURA G75)
N10 G21 G40 G97 G99
N20 G00 X100. Z100.
N30 T0404 (BROCA D8 EN EL CENTRO)
N40 G97 S1590 M03
N50 G00 X0. Z5. M08
N60 G74 R0.5
N70 G74 Z-20. Q3000 F0.1 (PICADAS DE 3 MM)
N80 G00 Z100. M09 (EN UN AGUJERO SE SALE PRIMERO EN Z)
N90 X100.
N100 T0505 (RANURADOR DE 3 MM)
N110 G97 S600 M03
N120 G00 X36. Z-20. M08
N130 G75 R0.5
N140 G75 X28. P1500 F0.05 (PICADAS RADIALES DE 1,5 MM)
N150 G00 X100. M09
N160 Z100.
N170 M05
N180 M30
%
```

S1590 sale de n = 1000·40/(π·8) ≈ 1592 rpm (broca de acero rápido en acero, ver `datos-de-corte.md`); los avances son de ejemplo: tomarlos del catálogo de la broca y del ranurador.

## Compensación de radio de punta (G40, G41, G42)

- En la tabla de correctores: radio de punta R y dirección de la punta imaginaria (1 a 8; 0 y 9 cuando se programa el centro de la punta) ([FT]).
- G41: la pieza queda a la derecha de la trayectoria; G42: a la izquierda ([FT]). Exterior hacia el plato, normalmente G42; interior, G41 (verificar con la figura del manual según la torreta).
- Se activa en un bloque G00 o G01 (en G02/G03 da alarma) y se anula con G40 en el retiro ([FT]).
- Sin compensación, un cono o un chaflán quedan con un error que depende del radio de punta: para medidas precisas, compensar o corregir el contorno.

## Subprogramas en torno

`M98 P(veces)(programa)` y `M99` como en fresadora (ver `fanuc-fresadora.md`). Un subprograma en U y W (incremental) sirve para repetir una ranura o un perfil corrido; el principal posiciona y llama:

```
%
O0020
N10 G21 G99 G40
N20 G00 X100. Z100.
N30 T0101
N40 G50 S2000
N50 G96 S150 M03
N60 G00 X32. Z2. M08
N70 M98 P30021 (3 VECES EL O0021)
N80 G00 X100. M09
N90 Z100.
N100 M05
N110 M30
%
O0021 (BAJA 1 MM EN RADIO Y CILINDRA 20 MM)
N10 G00 U-2.
N20 G01 W-22. F0.2
N30 G00 U1.
N40 W22.
N50 U-1.
N60 M99
%
```

Cada llamada deja la herramienta 2 mm más abajo en diámetro (U−2 neto) y en la misma Z de partida. Se revisa con `cnc.py revisar` igual que un programa común.
