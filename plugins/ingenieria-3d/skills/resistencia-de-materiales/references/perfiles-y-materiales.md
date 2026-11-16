# Perfiles laminados y materiales

Leer para elegir un perfil, citar un valor de catálogo o un material con su fuente, o hacer la cuenta a mano. Los mismos datos están cargados en `scripts/resistencia.py` (`perfiles IPN`, `seccion perfil --nombre IPN200`). Antes de comprar o entregar, confirmar contra el catálogo del proveedor que se va a usar: medidas y tolerancias cambian poco entre fabricantes, pero cambian.

Ejes: y es el eje fuerte (paralelo a las alas) y z el débil. i = √(I/A) está calculado con los valores de la tabla. Peso: G ≈ 0,785·A [kg/m con A en cm²] (acero de 7850 kg/m³). En la Argentina, los perfiles doble T de alas inclinadas, los U de alas inclinadas y los ángulos de alas iguales tienen norma IRAM-IAS U 500-511, U 500-509 y U 500-558 (títulos según el CIRSOC 301-2005, A.3.1); las tablas de abajo son de catálogos europeos con las mismas series.

## IPN (doble T de alas inclinadas)

Fuente: ArcelorMittal, catálogo de perfiles, página «IPN» (medidas según EN 10365:2017): https://sections.arcelormittal.com/repository2/Sections/Sections_MB_ArcelorMittal_FR_EN_DE_IPN.pdf. Medidas en mm.

| IPN | h | b | tw | tf | A [cm²] | G [kg/m] | Iy [cm⁴] | Wy [cm³] | iy [cm] | Iz [cm⁴] | Wz [cm³] | iz [cm] |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 80 | 80 | 42 | 3,9 | 5,9 | 7,6 | 5,9 | 77,8 | 19,5 | 3,20 | 6,29 | 3,00 | 0,91 |
| 100 | 100 | 50 | 4,5 | 6,8 | 10,6 | 8,3 | 171 | 34,2 | 4,02 | 12,2 | 4,88 | 1,07 |
| 120 | 120 | 58 | 5,1 | 7,7 | 14,2 | 11,1 | 328 | 54,7 | 4,81 | 21,5 | 7,41 | 1,23 |
| 140 | 140 | 66 | 5,7 | 8,6 | 18,2 | 14,3 | 573 | 81,9 | 5,61 | 35,2 | 10,7 | 1,39 |
| 160 | 160 | 74 | 6,3 | 9,5 | 22,8 | 17,9 | 935 | 117 | 6,40 | 54,7 | 14,8 | 1,55 |
| 180 | 180 | 82 | 6,9 | 10,4 | 27,9 | 21,9 | 1450 | 161 | 7,21 | 81,3 | 19,8 | 1,71 |
| 200 | 200 | 90 | 7,5 | 11,3 | 33,4 | 26,2 | 2140 | 214 | 8,00 | 117 | 26,0 | 1,87 |
| 220 | 220 | 98 | 8,1 | 12,2 | 39,5 | 31,1 | 3060 | 278 | 8,80 | 162 | 33,1 | 2,03 |
| 240 | 240 | 106 | 8,7 | 13,1 | 46,1 | 36,2 | 4250 | 354 | 9,60 | 221 | 41,7 | 2,19 |
| 260 | 260 | 113 | 9,4 | 14,1 | 53,3 | 41,9 | 5740 | 442 | 10,38 | 288 | 51,0 | 2,32 |
| 280 | 280 | 119 | 10,1 | 15,2 | 61 | 47,9 | 7590 | 542 | 11,15 | 364 | 61,2 | 2,44 |
| 300 | 300 | 125 | 10,8 | 16,2 | 69 | 54,2 | 9800 | 653 | 11,92 | 451 | 72,2 | 2,56 |
| 320 | 320 | 131 | 11,5 | 17,3 | 77,7 | 61 | 12 510 | 782 | 12,69 | 555 | 84,7 | 2,67 |
| 340 | 340 | 137 | 12,2 | 18,3 | 86,7 | 68 | 15 700 | 923 | 13,46 | 674 | 98,4 | 2,79 |
| 360 | 360 | 143 | 13 | 19,5 | 97 | 76,1 | 19 610 | 1090 | 14,22 | 818 | 114 | 2,90 |
| 380 | 380 | 149 | 13,7 | 20,5 | 107 | 84 | 24 010 | 1260 | 14,98 | 975 | 131 | 3,02 |
| 400 | 400 | 155 | 14,4 | 21,6 | 117,7 | 92,4 | 29 210 | 1460 | 15,75 | 1160 | 149 | 3,14 |
| 450 | 450 | 170 | 16,2 | 24,3 | 146,9 | 115 | 45 850 | 2040 | 17,67 | 1730 | 203 | 3,43 |
| 500 | 500 | 185 | 18 | 27 | 179,4 | 141 | 68 740 | 2750 | 19,57 | 2480 | 268 | 3,72 |
| 550 | 550 | 200 | 19 | 30 | 212 | 166 | 99 180 | 3610 | 21,63 | 3490 | 349 | 4,06 |
| 600 | 600 | 215 | 21,6 | 32,4 | 253,7 | 199 | 139 000 | 4630 | 23,41 | 4670 | 434 | 4,29 |

## UPN (U de alas inclinadas)

Fuente: STAD, «Technical data of sections», tabla UPN (distribuidor; el documento aclara que los datos son indicativos): https://www.stad.fr/downloads/pdf/stad-technical-data-of-sections.pdf. Coinciden con los valores habituales de la serie DIN 1026-1 (verificar con el catálogo del proveedor). Falta la distancia e del baricentro al dorso del alma: tomarla del catálogo si hace falta (uniones, corte excéntrico).

| UPN | h | b | tw | tf | A [cm²] | G [kg/m] | Iy [cm⁴] | Wy [cm³] | iy [cm] | Iz [cm⁴] | Wz [cm³] | iz [cm] |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 80 | 80 | 45 | 6 | 8 | 11 | 8,6 | 106 | 26,5 | 3,10 | 19,4 | 6,36 | 1,33 |
| 100 | 100 | 50 | 6 | 8,5 | 13,5 | 10,6 | 206 | 41,2 | 3,91 | 29,3 | 8,49 | 1,47 |
| 120 | 120 | 55 | 7 | 9 | 17 | 13,3 | 364 | 60,7 | 4,63 | 43,2 | 11,1 | 1,59 |
| 140 | 140 | 60 | 7 | 10 | 20,4 | 16 | 605 | 86,4 | 5,45 | 62,7 | 14,8 | 1,75 |
| 160 | 160 | 65 | 7,5 | 10,5 | 24 | 18,8 | 925 | 116 | 6,21 | 85,3 | 18,3 | 1,89 |
| 180 | 180 | 70 | 8 | 11 | 28 | 22 | 1350 | 150 | 6,94 | 114 | 22,4 | 2,02 |
| 200 | 200 | 75 | 8,5 | 11,5 | 32,2 | 25,3 | 1910 | 191 | 7,70 | 148 | 27 | 2,14 |
| 220 | 220 | 80 | 9 | 12,5 | 37,4 | 29,4 | 2690 | 245 | 8,48 | 197 | 33,6 | 2,30 |
| 240 | 240 | 85 | 9,5 | 13 | 42,3 | 33,2 | 3600 | 300 | 9,23 | 248 | 39,6 | 2,42 |
| 260 | 260 | 90 | 10 | 14 | 48,3 | 37,9 | 4820 | 371 | 9,99 | 317 | 47,7 | 2,56 |
| 280 | 280 | 95 | 10 | 15 | 53,3 | 41,8 | 6280 | 448 | 10,85 | 399 | 57,2 | 2,74 |
| 300 | 300 | 100 | 10 | 16 | 58,8 | 46,2 | 8030 | 535 | 11,69 | 495 | 67,8 | 2,90 |

## Ángulos de alas iguales

STAD publica el área, el peso y el radio de raíz r1, pero deja casi todas las inercias en blanco (https://www.stad.fr/en/sections-products-ranges-l). Por eso las propiedades de abajo están **calculadas** con las medidas, con el radio de raíz r1 y un radio de borde r2 = r1/2 (con ese r2 las áreas dan las de STAD), con `seccion angulo`. Se compararon con los valores que STAD sí da: L 100 × 100 × 10, I = 177 cm⁴ y W = 24,6 cm³ (calculado 176,7 y 24,62); L 120 × 120 × 12, I = 368 cm⁴, W = 42,7 cm³ e i = 3,65 cm (calculado 367,7; 42,73; 3,65). El resto: verificar con el catálogo del proveedor.

e: distancia del baricentro al dorso de cada ala. I, W e i: respecto de los ejes paralelos a las alas (W = I/(a − e), a la punta del ala). Iu e Iv: ejes principales (u a 45°, sobre la bisectriz; v perpendicular); **iv es el radio de giro mínimo**, el que manda en el pandeo de un ángulo solo.

| L a × a × t | r1 [mm] | A [cm²] (STAD) | G [kg/m] | e [cm] | I [cm⁴] | W [cm³] | i [cm] | Iu [cm⁴] | Iv [cm⁴] | iv [cm] |
|---|---|---|---|---|---|---|---|---|---|---|
| 40 × 40 × 4 | 6 | 3,08 (3,08) | 2,42 | 1,12 | 4,47 | 1,55 | 1,21 | 7,1 | 1,86 | 0,78 |
| 50 × 50 × 5 | 7 | 4,80 (4,80) | 3,77 | 1,40 | 10,96 | 3,05 | 1,51 | 17,4 | 4,55 | 0,97 |
| 60 × 60 × 6 | 8 | 6,91 (6,91) | 5,42 | 1,69 | 22,79 | 5,29 | 1,82 | 36,1 | 9,44 | 1,17 |
| 70 × 70 × 7 | 9 | 9,40 (9,40) | 7,38 | 1,97 | 42,30 | 8,41 | 2,12 | 67,1 | 17,50 | 1,36 |
| 80 × 80 × 8 | 10 | 12,27 (12,30) | 9,63 | 2,26 | 72,25 | 12,58 | 2,43 | 114,6 | 29,88 | 1,56 |
| 100 × 100 × 10 | 12 | 19,15 (19,20) | 15,04 | 2,82 | 176,7 | 24,62 | 3,04 | 280,3 | 73,01 | 1,95 |
| 120 × 120 × 12 | 13 | 27,54 (27,54) | 21,62 | 3,40 | 367,7 | 42,73 | 3,65 | 583,7 | 151,6 | 2,35 |

Cómo se calculan (con Steiner y el producto de inercia): dos rectángulos (a × t y t × (a − t)), más la enjuta de la raíz (cuadrado r1 × r1 menos un cuarto de círculo: área (1 − π/4)·r1², baricentro a 0,2234·r1 de la esquina) y menos las dos enjutas de los bordes (con r2). Los ejes principales salen de Iu,v = (Iy + Iz)/2 ± √(((Iy − Iz)/2)² + Iyz²). El método se verificó por integración en una grilla fina (coincidencia de cuatro cifras).

## Materiales

| Material | fy [MPa] | fu [MPa] | E [MPa] | Fuente |
|---|---|---|---|---|
| Acero estructural F-24 | 235 | 370 | 200 000 | fy: ejemplos de aplicación del CIRSOC 303 (2009), «Acero F24 (Fy = 235 MPa)». fu: los ejemplos del CIRSOC 301 (2005 y 2018) usan Fy = 235 MPa y Fu = 370 MPa para el acero de los perfiles, sin nombrar el grado (verificar en la IRAM-IAS U 500-503 vigente) |
| Acero estructural F-36 | 355 (verificar) | (verificar) | 200 000 | no se encontró en los documentos abiertos del CIRSOC: tomarlo de la IRAM-IAS U 500-503 o del certificado del proveedor |
| SAE 1010 laminado en caliente / estirado en frío | 180 / 300 | 320 / 370 | ≈ 207 000 | Shigley, *Diseño en ingeniería mecánica*, tabla A-20 (mínimos estimados; verificar en la edición que se use) |
| SAE 1020 laminado / estirado | 210 / 390 | 380 / 470 | ≈ 207 000 | ídem (verificar) |
| SAE 1045 laminado / estirado | 310 / 530 | 570 / 630 | ≈ 207 000 | ídem (verificar) |
| Aluminio 6061-T6 | ≈ 240 mínimo; ≈ 276 típico (verificar) | ≈ 260 mínimo; ≈ 310 típico (verificar) | ≈ 70 000 | E: Podut (2018), cap. 8 («E aluminio ≈ 70 GPa»); resistencias: hoja del proveedor o del fabricante del perfil (verificar) |

Propiedades del acero que fija el CIRSOC 301-2005 (A.3.5): E = 200 000 MPa; G = 77 200 MPa; ν = 0,30; α = 12·10⁻⁶ 1/°C; peso específico 77,3 kN/m³. La bibliografía de máquinas usa 207 GPa y G = 83 GPa para el ASTM A36 (Podut, 2018, cap. 9): la diferencia de 3,5 % va directo a la flecha y al giro, así que se aclara cuál se usó. Para el aluminio: α ≈ 23·10⁻⁶ 1/°C y G ≈ 26 000 MPa (verificar).

- Los aceros F se designan, en la práctica, con su fluencia en kgf/mm² (24 kgf/mm² = 235 MPa) (verificar en la norma). Equivalencias aproximadas con otras normas: comparar composición y propiedades, no solo el nombre (ver **normas-tecnicas-ar**).
- SAE 1010, 1020 y 1045 son aceros de construcción mecánica (IRAM 1010, 1020 y 1045 tienen la misma composición): sus propiedades dependen del estado (laminado, estirado, normalizado, templado y revenido) y del diámetro; para un valor de proyecto, el certificado del proveedor. El ensayo para medirlas está en **ensayos-materiales**.
- En corte puro, la fluencia vale τy = 0,577·fy (von Mises) o 0,5·fy (Tresca).
