# Tablas de elementos de máquinas

Leer cuando haga falta un valor de tabla para un cálculo a mano o para citar la fuente en un informe. Los mismos valores están cargados en `scripts/elementos.py`.

## Tornillos métricos (ISO 898-1)

| Clase | Rm mín. [MPa] | Fluencia mín. [MPa] | Sp, tensión bajo carga de prueba [MPa] |
|---|---|---|---|
| 4.6 | 400 | 240 (ReL) | 225 |
| 4.8 | 420 | 340 (Rpf) | 310 |
| 5.6 | 500 | 300 (ReL) | 280 |
| 5.8 | 520 | 420 (Rpf) | 380 |
| 6.8 | 600 | 480 (Rpf) | 440 |
| 8.8, d ≤ 16 mm | 800 | 640 (Rp0,2) | 580 |
| 8.8, d > 16 mm | 830 | 660 (Rp0,2) | 600 |
| 9.8 (solo d ≤ 16 mm) | 900 | 720 (Rp0,2) | 650 |
| 10.9 | 1040 | 940 (Rp0,2) | 830 |
| 12.9 | 1220 | 1100 (Rp0,2) | 970 |

Fuente: ISO 898-1, tabla de propiedades mecánicas; valores confirmados con las tablas técnicas de TR Fastenings y Bossard. La designación se lee así: 8.8 → Rm nominal 8·100 = 800 MPa y fluencia nominal 0,8·800 = 640 MPa.

Paso grueso (ISO 261/262): M3 0,5 · M4 0,7 · M5 0,8 · M6 1 · M8 1,25 · M10 1,5 · M12 1,75 · M14 2 · M16 2 · M18 2,5 · M20 2,5 · M22 2,5 · M24 3 · M27 3 · M30 3,5 · M33 3,5 · M36 4.

Área resistente (ISO 898-1): As = π/4·((d2 + d3)/2)², con d2 = d − 0,649519·P y d3 = d − 1,226869·P. Da M6 20,1 · M8 36,6 · M10 58,0 · M12 84,3 · M16 157 · M20 245 · M24 353 · M30 561 mm² (la tabla de la norma, redondeada).

## Chavetas paralelas (DIN 6885-1)

| Eje, más de … hasta [mm] | b × h [mm] |
|---|---|
| 6 a 8 | 2 × 2 |
| 8 a 10 | 3 × 3 |
| 10 a 12 | 4 × 4 |
| 12 a 17 | 5 × 5 |
| 17 a 22 | 6 × 6 |
| 22 a 30 | 8 × 7 |
| 30 a 38 | 10 × 8 |
| 38 a 44 | 12 × 8 |
| 44 a 50 | 14 × 9 |
| 50 a 58 | 16 × 10 |
| 58 a 65 | 18 × 11 |
| 65 a 75 | 20 × 12 |
| 75 a 85 | 22 × 14 |
| 85 a 95 | 25 × 14 |
| 95 a 110 | 28 × 16 |
| 110 a 130 | 32 × 18 |

Fuente: DIN 6885-1, tabla publicada por fasten.it. Las profundidades del chavetero (t1 en el eje, t2 en el cubo) y las tolerancias se toman de la norma o del catálogo del proveedor.

## Fatiga (Shigley, cap. 6)

- Se' = 0,5·Sut si Sut ≤ 1400 MPa; si no, 700 MPa.
- Acabado superficial ka = a·Sut^b (Sut en MPa): rectificado a = 1,58, b = −0,085; maquinado o estirado en frío 4,51 y −0,265; laminado en caliente 57,7 y −0,718; forjado 272 y −0,995.
- Tamaño kb (eje que gira): 1,24·d^−0,107 para 2,79 ≤ d ≤ 51 mm; 1,51·d^−0,157 para 51 < d ≤ 254 mm.
- Confiabilidad ke: 50 % → 1; 90 % → 0,897; 95 % → 0,868; 99 % → 0,814; 99,9 % → 0,753; 99,99 % → 0,702.

## Engranajes rectos

Factor de forma de Lewis Y, ángulo de presión 20°, diente normal (Shigley, tabla 14-2):

| z | Y | z | Y | z | Y |
|---|---|---|---|---|---|
| 12 | 0,245 | 19 | 0,314 | 34 | 0,371 |
| 13 | 0,261 | 20 | 0,322 | 38 | 0,384 |
| 14 | 0,277 | 21 | 0,328 | 43 | 0,397 |
| 15 | 0,290 | 22 | 0,331 | 50 | 0,409 |
| 16 | 0,296 | 24 | 0,337 | 60 | 0,422 |
| 17 | 0,303 | 26 | 0,346 | 75 | 0,435 |
| 18 | 0,309 | 28 | 0,353 | 100 | 0,447 |
|  |  | 30 | 0,359 | 150 / 300 / 400 | 0,460 / 0,472 / 0,480 |

Cremallera: 0,485. Factor dinámico con V en m/s: perfil fundido (3,05 + V)/3,05; fresado (6,1 + V)/6,1; generado con fresa madre o cepillado (3,56 + √V)/3,56; rectificado o afeitado √((5,56 + √V)/5,56).

## Soldadura (Shigley, cap. 9)

Electrodos (Sut / Sy del metal de aporte, MPa): E60XX 427/345 · E70XX 482/393 · E80XX 551/462 · E90XX 620/531 · E100XX 689/600 · E120XX 827/737. Corte admisible en la garganta según AWS: 0,30·Sut del electrodo.

## Rodamientos: vida de diseño orientativa

| Tipo de máquina | L10h [h] |
|---|---|
| Instrumentos y herramientas de uso esporádico | 1000 |
| Electrodomésticos y ventiladores chicos | 2000 a 4000 |
| Uso intermitente: herramientas de mano, aparejos de taller, maquinaria agrícola | 4000 a 8000 |
| Uso intermitente con alta confiabilidad: equipos auxiliares de centrales, transportadores, ascensores | 8000 a 15 000 |
| 8 a 16 h por día: motores fijos, reductores, grúas | 15 000 a 30 000 |
| Máquinas herramienta en general | 20 000 a 30 000 |
| Servicio continuo: bombas, ventiladores, compresores, trituradoras, transportadores | 40 000 a 60 000 |
| Servicio continuo con alta seguridad: papeleras, centrales, plantas de agua, barcos | 100 000 a 200 000 |

Fuente: ayuda de Autodesk Inventor, "Guiding Values of Basic Bearing Life Lh" (resumida). El catálogo del fabricante (SKF, FAG, NSK) da C, C0 y los factores X e Y de cada rodamiento.
