# Cilindros hidráulicos: medidas, fórmulas y pandeo

Leer este archivo al elegir el diámetro y el vástago de un cilindro, al calcular fuerzas, velocidades y caudales, o al verificar el pandeo. El script `scripts/oleohidraulica.py` (comandos `cilindro` y `pandeo`) hace las cuentas con los mismos datos.

## Fórmulas

| Magnitud | Fórmula | Unidades |
|---|---|---|
| Área del émbolo | A1 = π · D² / 4 | D [mm] → A [mm²]; 1 cm² = 100 mm² |
| Sección del vástago | Av = π · d² / 4 | d [mm] |
| Área anular | A3 = A1 − Av = π · (D² − d²) / 4 | |
| Relación de áreas | φ = A1 / A3 | sin unidad |
| Fuerza de avance | F = p · A1 · η | p [bar] · 0,1 = p [N/mm²]; F [N] |
| Fuerza de retroceso | F = p · A3 · η | |
| Presión para una carga | p = F / (A · η) | con el área del lado que empuja |
| Diámetro mínimo | D = √(4 · F / (π · p · η)) | se adopta el normalizado siguiente |
| Velocidad | v = Q / A, o v [m/s] = Q [L/min] / (6 · A [cm²]) | |
| Tiempo de carrera | t = s / v | s carrera [m] |
| Caudal que sale del otro lado | al avanzar Q / φ; al retroceder Q · φ | L/min |
| Regenerativo | v = Q / Av; F = p · Av · η | el aceite del lado del vástago se suma al de la bomba |
| Intensificación | p3 = (p · A1 − F) / A3; sin carga, p3 = p · φ | al estrangular la salida del lado del vástago |

- Carga vertical: F = m · g (g = 9,80665 m/s²; 1 t ≈ 9,81 kN), más el rozamiento de las guías y, si hay que acelerar, m · a.
- Rendimiento: en sus diagramas de fuerza, HANSA-FLEX toma 95 % para la fuerza de compresión (avance) y 92 % para la de tracción (retroceso) ([Technical Information Hydraulic Cylinders, rev. A 09/2024](https://www.hansa-flex.de/fileadmin/hansaflex/Technical_Information/English/TI-Hydraulic_cylinders_EN_web.pdf)). Si la consigna o el catálogo dan otro valor, se usa ese.
- Presión de cálculo: la de trabajo en el cilindro (descontando las pérdidas de la línea), y para dimensionar mangueras, juntas y pandeo, la máxima que puede aparecer: la de la válvula de alivio o la de intensificación.

## Diámetros normalizados

**ISO 3320** fija la serie métrica de diámetros de cilindro y de vástago para hidráulica y neumática; la edición vigente es **ISO 3320:2013**, que además incluye las relaciones de áreas ([iso.org](https://www.iso.org/standard/61647.html); título y alcance en [iTeh](https://iteh.es/catalog/standards/iso/822bd1ea-a57e-4160-a19b-c12dcf088f6c/iso-3320-2013)). Valores del extracto público de la edición 1987 ([iTeh](https://cdn.standards.iteh.ai/samples/8581/b5a82be6924348abb397c876ebf1d716/ISO-3320-1987.pdf)), confirmados con la IS 8208:2004 de India, idéntica a ISO 3320:1987 ([law.resource.org](https://law.resource.org/pub/in/bis/S01/is.8208.2004.pdf)):

- Diámetro del cilindro [mm]: 8 · 10 · 12 · 16 · 20 · 25 · 32 · 40 · 50 · 63 · 80 · 100 · 125 · 160 · 200 · 250 · 320 · 400 · 500. No preferidos (solo para casos especiales): 90 · 110 · 140 · 180 · 220 · 280 · 360 · 450.
- Diámetro del vástago [mm]: 4 · 5 · 6 · 8 · 10 · 12 · 14 · 16 · 18 · 20 · 22 · 25 · 28 · 32 · 36 · 40 · 45 · 50 · 56 · 63 · 70 · 80 · 90 · 100 · 110 · 125 · 140 · 160 · 180 · 200 · 220 · 250 · 280 · 320 · 360.
- Que la edición 2013 mantenga exactamente estas series: (verificar en la norma vigente).

**Relación de áreas**: ISO 7181 define φ = A1/A3 y elige los vástagos para que φ quede cerca de 1,06 · 1,12 · 1,25 · 1,4 · 1,6 · 2 · 2,5 · 5 ([extracto de ISO 7181:1982](https://cdn.standards.iteh.ai/samples/13795/040ba31ea24642eb8f27cda9d596a7a4/ISO-7181-1982.pdf); revisada en 1991, [iTeh](https://standards.iteh.ai/catalog/standards/iso/cbd6d164-cede-419c-aee2-04f15473f3ce/iso-7181-1982); el contenido pasó al título de ISO 3320:2013, verificar en la norma vigente). Con φ ≈ 2, el retroceso va al doble de velocidad que el avance y el circuito regenerativo da la misma velocidad en los dos sentidos.

### Serie compacta de 160 bar (ISO 6020-2)

ISO 6020-2 fija las medidas de montaje de los cilindros de vástago simple de 16 MPa, serie compacta; la vigente es la 4.ª edición, **ISO 6020-2:2015** ([iTeh](https://standards.iteh.ai/catalog/standards/iso/b5fd5b7d-ed43-48ad-ad52-739c97b6881a/iso-6020-2-2015)). Vástagos por diámetro según el catálogo de cilindros ISO 6020/2 de Confortinet ([PDF](https://www.confortinet.com/images/CIL//CDMDDK/PDF/CD_MD_DK_EN.pdf)); el extracto de la edición 1991 lista el primero y el último de cada fila ([iTeh](https://cdn.standards.iteh.ai/samples/12223/0ca5b179537c44719384c2670b75ae46/ISO-6020-2-1991.pdf)). Áreas y fuerzas teóricas (η = 1) calculadas con el script:

| D [mm] | d [mm] | A1 [cm²] | A3 [cm²] | φ | F avance a 160 bar [kN] | F retroceso a 160 bar [kN] |
|---|---|---|---|---|---|---|
| 25 | 12 / 18 | 4,91 | 3,78 / 2,36 | 1,30 / 2,08 | 7,9 | 6,0 / 3,8 |
| 32 | 14 / 18 / 22 | 8,04 | 6,50 / 5,50 / 4,24 | 1,24 / 1,46 / 1,90 | 12,9 | 10,4 / 8,8 / 6,8 |
| 40 | 18 / 22 / 28 | 12,57 | 10,02 / 8,77 / 6,41 | 1,25 / 1,43 / 1,96 | 20,1 | 16,0 / 14,0 / 10,3 |
| 50 | 22 / 28 / 36 | 19,63 | 15,83 / 13,48 / 9,46 | 1,24 / 1,46 / 2,08 | 31,4 | 25,3 / 21,6 / 15,1 |
| 63 | 28 / 36 / 45 | 31,17 | 25,01 / 20,99 / 15,27 | 1,25 / 1,48 / 2,04 | 49,9 | 40,0 / 33,6 / 24,4 |
| 80 | 36 / 45 / 56 | 50,27 | 40,09 / 34,36 / 25,64 | 1,25 / 1,46 / 1,96 | 80,4 | 64,1 / 55,0 / 41,0 |
| 100 | 45 / 56 / 70 | 78,54 | 62,64 / 53,91 / 40,06 | 1,25 / 1,46 / 1,96 | 125,7 | 100,2 / 86,3 / 64,1 |
| 125 | 56 / 70 / 90 | 122,72 | 98,09 / 84,23 / 59,10 | 1,25 / 1,46 / 2,08 | 196,3 | 156,9 / 134,8 / 94,6 |
| 160 | 70 / 90 / 110 | 201,06 | 162,58 / 137,44 / 106,03 | 1,24 / 1,46 / 1,90 | 321,7 | 260,1 / 219,9 / 169,6 |
| 200 | 90 / 110 / 140 | 314,16 | 250,54 / 219,13 / 160,22 | 1,25 / 1,43 / 1,96 | 502,7 | 400,9 / 350,6 / 256,4 |

- Comparación: el catálogo Rexroth de la CDT3 (tirantes, ISO 6020-2, hasta 210 bar; [RE 17049/07.17](https://hydraulic-pump-valve.com/PDF/Hydraulic%20Cylinder/Bosch%20Rexroth%20Hydraulic%20Cylinder/CDT3...Z-3X.pdf)) publica las mismas relaciones redondeadas; en 32/14 y 160/70 pone el nominal 1,25 (el cálculo da 1,237). El `demo` compara las 26 combinaciones.
- Serie de 250 bar: el cilindro Rexroth CDH1 ([RE 17332/07.17](https://hydraulic-pump-valve.com/PDF/Hydraulic%20Cylinder/Bosch%20Rexroth%20Hydraulic%20Cylinder/CDH1.pdf)) se ofrece en Ø40 a 320 mm con dos vástagos por diámetro (40/22 y 28; 50/28 y 36; 63/36 y 45; 80/45 y 56; 100/56 y 70; 125/70 y 90; 140/90 y 100; 160/100 y 110; 180/110 y 125; 200/125 y 140; 220/140 y 160; 250/160 y 180; 280/180 y 200; 320/200 y 220).
- Para el modelo concreto (carrera máxima, montajes, amortiguación, juntas) manda el catálogo del fabricante.

## Velocidad del vástago y amortiguación

- HANSA-FLEX limita la velocidad del émbolo a 25 m/min (0,42 m/s) con juntas estándar y a 6 m/min (0,10 m/s) al entrar en las posiciones finales; el final de carrera no se usa como tope ([TI Hydraulic Cylinders, 09/2024](https://www.hansa-flex.de/fileadmin/hansaflex/Technical_Information/English/TI-Hydraulic_cylinders_EN_web.pdf)). Más rápido hace falta amortiguación (del cilindro o externa) o frenar antes del final.
- La conexión del cilindro también limita: Rexroth publica para la CDH1 velocidades máximas por diámetro calculadas con 5 m/s en la conexión, de 0,31 m/s en Ø40 a 0,04 m/s en Ø320 ([RE 17332/07.17](https://hydraulic-pump-valve.com/PDF/Hydraulic%20Cylinder/Bosch%20Rexroth%20Hydraulic%20Cylinder/CDH1.pdf)). En el retroceso la conexión del lado del émbolo descarga Q · φ.

## Pandeo del vástago

Método de los catálogos Rexroth (CDH1, [RE 17332/07.17](https://hydraulic-pump-valve.com/PDF/Hydraulic%20Cylinder/Bosch%20Rexroth%20Hydraulic%20Cylinder/CDH1.pdf), y CDT3, [RE 17049/07.17](https://hydraulic-pump-valve.com/PDF/Hydraulic%20Cylinder/Bosch%20Rexroth%20Hydraulic%20Cylinder/CDT3...Z-3X.pdf)):

| Paso | Fórmula |
|---|---|
| Momento de inercia | I = π · d⁴ / 64 ≈ 0,0491 · d⁴ [mm⁴] |
| Longitud libre de pandeo | Lk = β · L, con L la longitud con el vástago afuera según el montaje |
| Esbeltez | λ = 4 · Lk / d (sección circular llena) |
| Esbeltez límite | λg = π · √(E / (0,8 · Re)), con Re la fluencia del material del vástago |
| Si λ > λg (Euler) | F adm = π² · E · I / (ν · Lk²) |
| Si λ ≤ λg (Tetmajer) | F adm = π · d² · (335 − 0,62 · λ) / (4 · ν) |
| Datos | E = 210 000 N/mm² (acero); ν = 3,5 |

- Las constantes 335 y 0,62 son las de la recta de Tetmajer del acero S355 (St 52); para el S235 (St 37) la recta es 310 − 1,14 · λ ([Knickung, tabla de Tetmajer](https://de-academic.com/dic.nsf/dewiki/1249271)). Por eso el script avisa si se carga un Re menor que 355 N/mm²: con un acero más blando la recta queda del lado inseguro y manda el diagrama del fabricante.
- En λg la tensión de Euler vale exactamente 0,8 · Re; con Re = 355 N/mm², λg = 85,4, y las dos fórmulas casi coinciden ahí (284 y 282 N/mm²).
- Fluencia de aceros de vástago, según el fabricante de barras cromadas Ovako: C45E 305 N/mm², 19MnVS6 390 N/mm², 38MnVS6 520 N/mm², Cromax 180X 500 N/mm² ([white paper CO-47 ENG 24:06](https://ovako.com/globalassets/products/hard-chromed/Piston-rods-in-hydraulic-cylinder-White-paper.pdf)). Usar el del vástago real (catálogo del cilindro).
- Coeficiente ν = 3,5: lo usa Rexroth en esos catálogos y HANSA-FLEX en su diagrama de pandeo (caso 2 de Euler).
- La fuerza que se verifica es la **máxima** que puede hacer el cilindro: p de la válvula de alivio por A1, no la carga nominal.
- Norma específica: **ISO/TS 13725:2021**, método para evaluar la carga de pandeo de cilindros según ISO 6020, ISO 6022 e ISO 10762, con el cilindro completamente extendido y un factor de seguridad que elige quien calcula ([iTeh](https://iteh.es/catalog/standards/iso/3a02c4bd-4bf1-4e9b-ae9b-7331f31eba58/iso-ts-13725-2021)). Tiene en cuenta también el tubo y los juegos; las fórmulas de arriba solo el vástago.

### Longitud libre según el montaje

| Caso de Euler | Extremos | Lk | Montaje típico |
|---|---|---|---|
| 1 | Empotrado y libre | 2 · L | Brida o patas fijas y carga sin guiar en el extremo del vástago |
| 2 | Articulado en los dos extremos | L | Charnela o muñón en el cilindro y horquilla o rótula en el vástago |
| 3 | Empotrado y articulado guiado | 0,7 · L (exacto 0,699) | Brida fija y vástago unido con articulación a una carga guiada |
| 4 | Empotrado en los dos extremos | 0,5 · L | Brida fija y carga guiada rígidamente |

- Los catálogos Rexroth dibujan solo Lk = 2 · L, L y 0,7 · L según el montaje (no usan el caso 4); si no se sabe cómo está guiada la carga, tomar el caso más desfavorable posible.
- L se mide con el vástago afuera, desde el punto de fijación del cilindro hasta el de la carga, como indique el catálogo para cada montaje (brida delantera, brida trasera, charnela, muñón, patas).
- Las bases de Euler (factor β, validez con esbeltez alta) están también en **neumatica-electroneumatica**; en hidráulica los vástagos suelen ser cortos y gruesos para la carga, y por eso aparece Tetmajer.

### Ejemplo (el del `demo`)

Prensa con cilindro Ø100/70, brida delantera y puente guiado (caso 3), L = 450 mm, Re = 355 N/mm², fuerza máxima 160 bar · 7854 mm² = 125,66 kN:

- I = 1 178 588 mm⁴; Lk = 0,7 · 450 = 315 mm; λ = 4 · 315 / 70 = 18,0 < λg = 85,4 → Euler no vale.
- Tetmajer: F adm = π · 70² · (335 − 0,62 · 18) / (4 · 3,5) = 356,1 kN ≥ 125,66 kN: verifica.
- Longitud máxima: con Euler, Lk = π · √(E · I / (ν · F)) = 2357 mm (λ = 134,7 > λg, Euler vale) → L máx = 2357 / 0,7 = 3367 mm.

```
python scripts/oleohidraulica.py pandeo --d 70 --L 450 --caso 3 --D 100 --p 160
```
