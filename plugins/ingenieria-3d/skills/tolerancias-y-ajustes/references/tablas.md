# Tablas de tolerancias y ajustes

Leer cuando haga falta citar un valor de tabla, calcular a mano o revisar de dónde sale un número. Son los mismos valores que carga `scripts/tolerancias.py`. En los escalones, «18 a 30» quiere decir de más de 18 hasta 30 mm inclusive: 30 mm va en ese escalón y 18 mm en el anterior.

## Fuentes y cómo se verificaron

Las normas ISO e IRAM son pagas; estos valores se tomaron de reproducciones públicas y se compararon con código (unas 3100 comparaciones, sin diferencias con los valores cargados salvo las erratas de las fuentes que se anotan al final):

| Tabla | Fuentes contrastadas |
|---|---|
| Tolerancias fundamentales IT01 a IT18 (ISO 286-1:2010, tabla 1) | [Wikipedia, «IT Grade»](https://en.wikipedia.org/wiki/IT_Grade); [Engineers Edge, «International Tolerance (IT) Grades Table»](https://host.engineersedge.com/international_tol.htm); paquete npm [standards-mcp-server](https://www.npmjs.com/package/standards-mcp-server) 0.3.0 (MIT) |
| Desviaciones fundamentales de ejes y agujeros (ISO 286-1) | Límites de clases publicados en: [Miki Pulley, tablas de JIS B 0401](https://www.mikipulley.co.jp/en/resources/standards-fitting-tolerances) (3 a 500 mm); [Misumi, tablas de JIS B 0401-2](https://uk.misumi-ec.com/files/images/techblog/1_general-tolerances/tolerance-tables-according-to-ji.pdf) (c9 y la fila hasta 3 mm); [SimplyBearings, «ISO 286 Limits and Fits»](https://simplybearings.co.uk/shop/Info-Pages-ISO-Limits/c4746_4779/index.html) (3 a 400 mm); [Wikipedia, «Engineering fit»](https://en.wikipedia.org/wiki/Engineering_fit) (hasta 120 mm); juegos de los ajustes de BS 4500:1969 en el Machinery's Handbook, 31.ª ed., tabla 3 de «British Standard Metric ISO Limits and Fits» (hasta 500 mm); ejemplo de K7 en [RoyMech](https://roymech.org/Useful_Tables/ISO_Tolerances.html); tablas en código de standards-mcp-server |
| ISO 2768-1:1989 | [Wikipedia en alemán, «ISO 2768»](https://de.wikipedia.org/wiki/ISO_2768); standards-mcp-server |
| ISO 2768-2:1989 | [Wikipedia en alemán, «ISO 2768»](https://de.wikipedia.org/wiki/ISO_2768) (una sola fuente pública: verificar en la norma vigente) |
| Grados N de rugosidad | [Wikipedia, «Surface roughness»](https://en.wikipedia.org/wiki/Surface_roughness), tabla de conversión |

## Tolerancias fundamentales IT [µm] (ISO 286-1:2010, tabla 1)

| Escalón [mm] | IT01 | IT0 | IT1 | IT2 | IT3 | IT4 | IT5 | IT6 | IT7 | IT8 | IT9 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| hasta 3 | 0,3 | 0,5 | 0,8 | 1,2 | 2 | 3 | 4 | 6 | 10 | 14 | 25 |
| 3 a 6 | 0,4 | 0,6 | 1 | 1,5 | 2,5 | 4 | 5 | 8 | 12 | 18 | 30 |
| 6 a 10 | 0,4 | 0,6 | 1 | 1,5 | 2,5 | 4 | 6 | 9 | 15 | 22 | 36 |
| 10 a 18 | 0,5 | 0,8 | 1,2 | 2 | 3 | 5 | 8 | 11 | 18 | 27 | 43 |
| 18 a 30 | 0,6 | 1 | 1,5 | 2,5 | 4 | 6 | 9 | 13 | 21 | 33 | 52 |
| 30 a 50 | 0,6 | 1 | 1,5 | 2,5 | 4 | 7 | 11 | 16 | 25 | 39 | 62 |
| 50 a 80 | 0,8 | 1,2 | 2 | 3 | 5 | 8 | 13 | 19 | 30 | 46 | 74 |
| 80 a 120 | 1 | 1,5 | 2,5 | 4 | 6 | 10 | 15 | 22 | 35 | 54 | 87 |
| 120 a 180 | 1,2 | 2 | 3,5 | 5 | 8 | 12 | 18 | 25 | 40 | 63 | 100 |
| 180 a 250 | 2 | 3 | 4,5 | 7 | 10 | 14 | 20 | 29 | 46 | 72 | 115 |
| 250 a 315 | 2,5 | 4 | 6 | 8 | 12 | 16 | 23 | 32 | 52 | 81 | 130 |
| 315 a 400 | 3 | 5 | 7 | 9 | 13 | 18 | 25 | 36 | 57 | 89 | 140 |
| 400 a 500 | 4 | 6 | 8 | 10 | 15 | 20 | 27 | 40 | 63 | 97 | 155 |

| Escalón [mm] | IT10 | IT11 | IT12 | IT13 | IT14 | IT15 | IT16 | IT17 | IT18 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| hasta 3 | 40 | 60 | 100 | 140 | 250 | 400 | 600 | 1000 | 1400 |
| 3 a 6 | 48 | 75 | 120 | 180 | 300 | 480 | 750 | 1200 | 1800 |
| 6 a 10 | 58 | 90 | 150 | 220 | 360 | 580 | 900 | 1500 | 2200 |
| 10 a 18 | 70 | 110 | 180 | 270 | 430 | 700 | 1100 | 1800 | 2700 |
| 18 a 30 | 84 | 130 | 210 | 330 | 520 | 840 | 1300 | 2100 | 3300 |
| 30 a 50 | 100 | 160 | 250 | 390 | 620 | 1000 | 1600 | 2500 | 3900 |
| 50 a 80 | 120 | 190 | 300 | 460 | 740 | 1200 | 1900 | 3000 | 4600 |
| 80 a 120 | 140 | 220 | 350 | 540 | 870 | 1400 | 2200 | 3500 | 5400 |
| 120 a 180 | 160 | 250 | 400 | 630 | 1000 | 1600 | 2500 | 4000 | 6300 |
| 180 a 250 | 185 | 290 | 460 | 720 | 1150 | 1850 | 2900 | 4600 | 7200 |
| 250 a 315 | 210 | 320 | 520 | 810 | 1300 | 2100 | 3200 | 5200 | 8100 |
| 315 a 400 | 230 | 360 | 570 | 890 | 1400 | 2300 | 3600 | 5700 | 8900 |
| 400 a 500 | 250 | 400 | 630 | 970 | 1550 | 2500 | 4000 | 6300 | 9700 |

Desde IT6, cada cinco grados la tolerancia se multiplica por 10 (IT11 = 10·IT6, IT12 = 10·IT7…); la única excepción en la tabla es el escalón de 3 a 6 mm, donde IT6 = 8 µm e IT11 = 75 µm (comprobado con código).

Origen: para IT5 a IT18, la norma redondea k·i, con i = 0,45·∛D + 0,001·D [µm], D la media geométrica del escalón [mm] (√(18·30) = 23,24 mm para el de 18 a 30) y k = 7, 10, 16, 25, 40, 64, 100, 160, 250, 400, 640, 1000, 1600 y 2500. Comprobado con código: para más de 3 mm, k·i se aparta de la tabla hasta un 8,4 % (IT5 a IT11) por los redondeos; en el escalón hasta 3 mm se aparta más. Siempre se usa la tabla.

## Desviaciones fundamentales de ejes [µm] (ISO 286-1)

Ejes c a g: la tabla da la desviación superior es (negativa) y ei = es − IT. Ejes k a s: da la inferior ei y es = ei + IT. Eje h: es = 0; js: ±IT/2. La k vale para IT4 a IT7 (fuera de eso el script no la calcula: verificar en ISO 286-2).

| Escalón [mm] | c | d | e | f | g | k (IT4 a IT7) | m | n | p | r | s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| hasta 3 | −60 | −20 | −14 | −6 | −2 | 0 | +2 | +4 | +6 | +10 | +14 |
| 3 a 6 | −70 | −30 | −20 | −10 | −4 | +1 | +4 | +8 | +12 | +15 | +19 |
| 6 a 10 | −80 | −40 | −25 | −13 | −5 | +1 | +6 | +10 | +15 | +19 | +23 |
| 10 a 14 | −95 | −50 | −32 | −16 | −6 | +1 | +7 | +12 | +18 | +23 | +28 |
| 14 a 18 | −95 | −50 | −32 | −16 | −6 | +1 | +7 | +12 | +18 | +23 | +28 |
| 18 a 24 | −110 | −65 | −40 | −20 | −7 | +2 | +8 | +15 | +22 | +28 | +35 |
| 24 a 30 | −110 | −65 | −40 | −20 | −7 | +2 | +8 | +15 | +22 | +28 | +35 |
| 30 a 40 | −120 | −80 | −50 | −25 | −9 | +2 | +9 | +17 | +26 | +34 | +43 |
| 40 a 50 | −130 | −80 | −50 | −25 | −9 | +2 | +9 | +17 | +26 | +34 | +43 |
| 50 a 65 | −140 | −100 | −60 | −30 | −10 | +2 | +11 | +20 | +32 | +41 | +53 |
| 65 a 80 | −150 | −100 | −60 | −30 | −10 | +2 | +11 | +20 | +32 | +43 | +59 |
| 80 a 100 | −170 | −120 | −72 | −36 | −12 | +3 | +13 | +23 | +37 | +51 | +71 |
| 100 a 120 | −180 | −120 | −72 | −36 | −12 | +3 | +13 | +23 | +37 | +54 | +79 |
| 120 a 140 | −200 | −145 | −85 | −43 | −14 | +3 | +15 | +27 | +43 | +63 | +92 |
| 140 a 160 | −210 | −145 | −85 | −43 | −14 | +3 | +15 | +27 | +43 | +65 | +100 |
| 160 a 180 | −230 | −145 | −85 | −43 | −14 | +3 | +15 | +27 | +43 | +68 | +108 |
| 180 a 200 | −240 | −170 | −100 | −50 | −15 | +4 | +17 | +31 | +50 | +77 | +122 |
| 200 a 225 | −260 | −170 | −100 | −50 | −15 | +4 | +17 | +31 | +50 | +80 | +130 |
| 225 a 250 | −280 | −170 | −100 | −50 | −15 | +4 | +17 | +31 | +50 | +84 | +140 |
| 250 a 280 | −300 | −190 | −110 | −56 | −17 | +4 | +20 | +34 | +56 | +94 | +158 |
| 280 a 315 | −330 | −190 | −110 | −56 | −17 | +4 | +20 | +34 | +56 | +98 | +170 |
| 315 a 355 | −360 | −210 | −125 | −62 | −18 | +4 | +21 | +37 | +62 | +108 | +190 |
| 355 a 400 | −400 | −210 | −125 | −62 | −18 | +4 | +21 | +37 | +62 | +114 | +208 |
| 400 a 450 | −440 | −230 | −135 | −68 | −20 | +5 | +23 | +40 | +68 | +126 | +232 |
| 450 a 500 | −480 | −230 | −135 | −68 | −20 | +5 | +23 | +40 | +68 | +132 | +252 |

## Agujeros

- **H**: EI = 0. **JS**: ±IT/2 (sin redondear: JS7 de 18 a 30 mm = ±10,5 µm, igual en las tablas de Miki Pulley y SimplyBearings).
- **F y G**: espejo del eje de la misma letra: EI = −es (F7 de 25 mm: EI = +20 µm, ES = +41 µm).
- **K y N hasta IT8, P hasta IT7**: ES = −ei + Δ, con el ei del eje de la misma letra (para K, el de k de IT4 a IT7) y Δ = ITn − ITn−1. Hasta 3 mm, Δ = 0. Ejemplo: K7 de 18 a 30 mm, ES = −2 + 8 = +6 µm y EI = 6 − 21 = −15 µm.
- **P por encima de IT7**: ES = −ei, sin Δ (P8 de 30 a 50 mm: −26/−65 µm, igual que SimplyBearings).
- K y N por encima de IT8, y las letras no cargadas (A, B, C, D, E, J, M, R a ZC en agujeros; a, b, j, t a zc en ejes): tomarlas de ISO 286-2 (verificar).

Δ [µm], calculado como ITn − ITn−1 (coincide con la tabla de Δ de standards-mcp-server):

| Escalón [mm] | IT3 | IT4 | IT5 | IT6 | IT7 | IT8 |
|---|---:|---:|---:|---:|---:|---:|
| hasta 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| 3 a 6 | 1 | 1,5 | 1 | 3 | 4 | 6 |
| 6 a 10 | 1 | 1,5 | 2 | 3 | 6 | 7 |
| 10 a 18 | 1 | 2 | 3 | 3 | 7 | 9 |
| 18 a 30 | 1,5 | 2 | 3 | 4 | 8 | 12 |
| 30 a 50 | 1,5 | 3 | 4 | 5 | 9 | 14 |
| 50 a 80 | 2 | 3 | 5 | 6 | 11 | 16 |
| 80 a 120 | 2 | 4 | 5 | 7 | 13 | 19 |
| 120 a 180 | 3 | 4 | 6 | 7 | 15 | 23 |
| 180 a 250 | 3 | 4 | 6 | 9 | 17 | 26 |
| 250 a 315 | 4 | 4 | 7 | 9 | 20 | 29 |
| 315 a 400 | 4 | 5 | 7 | 11 | 21 | 32 |
| 400 a 500 | 5 | 5 | 7 | 13 | 23 | 34 |

## Tolerancias generales ISO 2768-1 [mm]

Cotas lineales (salvo aristas matadas):

| Clase | 0,5 a 3 | 3 a 6 | 6 a 30 | 30 a 120 | 120 a 400 | 400 a 1000 | 1000 a 2000 | 2000 a 4000 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| f (fina) | ±0,05 | ±0,05 | ±0,1 | ±0,15 | ±0,2 | ±0,3 | ±0,5 | — |
| m (media) | ±0,1 | ±0,1 | ±0,2 | ±0,3 | ±0,5 | ±0,8 | ±1,2 | ±2 |
| c (gruesa) | ±0,2 | ±0,3 | ±0,5 | ±0,8 | ±1,2 | ±2 | ±3 | ±4 |
| v (muy gruesa) | — | ±0,5 | ±1 | ±1,5 | ±2,5 | ±4 | ±6 | ±8 |

Aristas matadas (radios exteriores y alturas de chaflán): f y m ±0,2 (0,5 a 3), ±0,5 (3 a 6), ±1 (más de 6); c y v ±0,4, ±1 y ±2.

Ángulos, según el largo del lado más corto:

| Clase | hasta 10 | 10 a 50 | 50 a 120 | 120 a 400 | más de 400 |
|---|---|---|---|---|---|
| f y m | ±1° | ±0°30' | ±0°20' | ±0°10' | ±0°5' |
| c | ±1°30' | ±1° | ±0°30' | ±0°15' | ±0°10' |
| v | ±3° | ±2° | ±1° | ±0°30' | ±0°20' |

Por debajo de 0,5 mm la tolerancia se indica junto a la cota (verificar en la norma vigente).

## Tolerancias generales geométricas ISO 2768-2 [mm]

Contrastadas con una sola fuente pública: verificar en la norma vigente.

| Rectitud y planitud | hasta 10 | 10 a 30 | 30 a 100 | 100 a 300 | 300 a 1000 | 1000 a 3000 |
|---|---:|---:|---:|---:|---:|---:|
| H | 0,02 | 0,05 | 0,1 | 0,2 | 0,3 | 0,4 |
| K | 0,05 | 0,1 | 0,2 | 0,4 | 0,6 | 0,8 |
| L | 0,1 | 0,2 | 0,4 | 0,8 | 1,2 | 1,6 |

| Perpendicularidad (lado más corto) y simetría | hasta 100 | 100 a 300 | 300 a 1000 | 1000 a 3000 |
|---|---:|---:|---:|---:|
| H perpendicularidad | 0,2 | 0,3 | 0,4 | 0,5 |
| K perpendicularidad | 0,4 | 0,6 | 0,8 | 1 |
| L perpendicularidad | 0,6 | 1 | 1,5 | 2 |
| H simetría | 0,5 | 0,5 | 0,5 | 0,5 |
| K simetría | 0,6 | 0,6 | 0,8 | 1 |
| L simetría | 0,6 | 1 | 1,5 | 2 |

Oscilación circular: H 0,1; K 0,2; L 0,5.

## Grados N de rugosidad (planos viejos)

| Grado | N12 | N11 | N10 | N9 | N8 | N7 | N6 | N5 | N4 | N3 | N2 | N1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Ra [µm] | 50 | 25 | 12,5 | 6,3 | 3,2 | 1,6 | 0,8 | 0,4 | 0,2 | 0,1 | 0,05 | 0,025 |

Fuente: tabla de conversión de Wikipedia, «Surface roughness». En los planos actuales se escribe el parámetro con su valor (por ejemplo Ra 1,6).

## Erratas encontradas en las fuentes

Las celdas siguientes no cierran consigo mismas (la diferencia entre sus límites no es la IT) y no se usaron:

- SimplyBearings: K6 de 6 a 10 mm figura +2/−6 (la IT6 es 9 µm: −7); f6 de 120 a 180 mm figura −43/−48 (−68).
- Machinery's Handbook, tabla 3 (BS 4500): H7/s6 de 250 a 315 mm figura con juego máximo −126 y −112 (con su propio juego mínimo y Tf = 84 µm da −106 y −118); H7/k6 de 315 a 400 mm figura −53 (es +53).
- Wikipedia, «Engineering fit»: c11 de 6 a 10 mm leída como −80/−205 (con IT11 = 90 µm es −80/−170).
