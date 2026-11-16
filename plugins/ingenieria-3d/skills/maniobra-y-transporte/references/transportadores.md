# Transportadores continuos: tablas, deducciones y fuentes

Leer cuando haga falta un valor de tabla para calcular a mano una cinta, un tornillo sinfín o un elevador de cangilones, citar la fuente en un informe o entender de dónde sale una fórmula. Los mismos valores están cargados en `scripts/transporte.py`. Lo marcado "(verificar)" no se pudo confirmar con la norma.

## Fuentes

| Fuente | Qué se toma | Acceso |
|---|---|---|
| IS 11592:2000, *Selection and design of belt conveyors — Code of practice* (Bureau of Indian Standards) | Ancho útil (cl. 8.4.3), secciones (tablas 7 y 8), factor por inclinación (tabla 9), velocidades máximas (tablas 4 a 6), fórmula de la fuerza en el tambor (ec. 5 y 6), f (cl. 8.5.1.1), rendimientos (tabla 12), μ (tablas 16 y 20) | [law.resource.org](https://law.resource.org/pub/in/bis/S08/is.11592.2000.pdf) |
| IS 8730:1997, *Classification and codification of bulk materials* (BIS) | Inclinación máxima recomendada por material (tabla 3) | [law.resource.org](https://law.resource.org/pub/in/bis/S08/is.8730.1997.pdf) |
| Artículo del tomo 61 (2018) de la Universidad de Minería y Geología St. Ivan Rilski (Sofía), pp. 18-22 | Ejemplos resueltos de sección por DIN 22101 (cita la tabla 3 del manual de bandas de Dunlop) y por CEMA (cita la tabla 4 del manual de rodillos HA 200 de Sandvik) | [mgu.bg](https://mgu.bg/wp-content/uploads/2025/03/Tom61-MEMF-2018-18-22.pdf) |
| MEKA, *Belt conveyor capacity calculation* (resume el manual de MEKA, pp. 116-117) | Velocidades típicas por ancho y material; ángulo dinámico de 15° a 25° | [mekaglobal.com](https://www.mekaglobal.com/en/blog/belt-conveyor-capacity-calculation) |
| KWS Manufacturing, *Screw Conveyor Engineering Guide* (según CEMA 350) | Capacidad a 1 rpm, rpm máximas, factores de potencia y tabla de materiales | [capacidad](https://www.kwsmfg.com/engineering-guides/screw-conveyor/screw-conveyor-capacity/) · [potencia](https://www.kwsmfg.com/engineering-guides/screw-conveyor/screw-conveyor-horsepower/) · [materiales](https://www.kwsmfg.com/engineering-guides/screw-conveyor/bulk-material-table/) |

DIN 22101 (*Stetigförderer — Gurtförderer für Schüttgüter*), ISO 5048:1989 (*Belt conveyors with carrying idlers — Calculation of operating power and tensile forces*) y CEMA (*Belt Conveyors for Bulk Materials* y CEMA 350 para sinfines) son pagas; acá se usan a través de las fuentes de la tabla.

## Cinta transportadora

### Sección de carga

- Ancho útil: b = 0,9·B − 0,05 m para B ≤ 2 m y b = B − 0,25 m para B > 2 m (IS 11592, cl. 8.4.3; el ejemplo de DIN 22101 del artículo usa el mismo).
- Terna: rodillo central de largo l3 y laterales a λ. Largo útil de cada lateral l1 = (b − l3)/2; ancho de la carga en los bordes x = l3 + 2·l1·cos λ; altura del trapecio l1·sen λ.
- Parte de abajo (trapecio): A2 = (l3 + x)/2·l1·sen λ.
- Sobrecarga en arco de círculo tangente al ángulo θ en los bordes (CEMA): radio R = (x/2)/sen θ y A1 = R²·(θ − sen θ·cos θ) = (x/2)²·(θ − sen θ·cos θ)/sen² θ, con θ en radianes.
- Sobrecarga en triángulo con el ángulo dinámico β (DIN 22101, según el manual de Dunlop): A1 = x²·tg β/4.
- Banda plana: x = b y A = A1.

Para la misma sección, el β de DIN es menor que el θ de CEMA: en el artículo, β = 16,5° equivale a θ = 25° (relación 0,66). La IS 11592 (cl. 8.4.3.2) toma 20° como ángulo de sobrecarga normal para materiales de flujo normal.

Comprobaciones (están en el `demo`):

| Caso | Fórmula del script | Fuente |
|---|---|---|
| B 1200 mm, terna 30°, l3 465 mm, triángulo β 15° | A = 0,1612 m² | 580 m³/h a 1 m/s → 0,1611 m² (tabla 3 de Dunlop) |
| Igual, arco θ 25° | A = 0,1682 m² | 0,169 m² (tabla 4 de Sandvik) |
| Banda plana 500 mm, θ 10° / 30° | 0,00467 / 0,01449 m² | 0,0047 / 0,0145 m² (IS 11592, tabla 8) |
| Banda plana 1000 mm, θ 10° / 20° / 30° | 0,0211 / 0,0427 / 0,0654 m² | 0,0210 / 0,0427 / 0,0653 m² (IS 11592, tabla 8) |

Los valores de la tabla 8 coinciden con el arco de círculo (diferencias menores que 1 %) y no con un triángulo ni con una parábola, que dan de 3 % a 60 % más.

Largo del rodillo central de la terna, por ancho de banda (DIN 22107; verificar con el catálogo de rodillos, salvo 1200 mm → 465 mm, que confirma la tabla 2 de Dunlop citada en el artículo):

| B [mm] | 400 | 500 | 650 | 800 | 1000 | 1200 | 1400 | 1600 | 1800 | 2000 | 2200 | 2400 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| l3 [mm] | 160 | 200 | 250 | 315 | 380 | 465 | 530 | 600 | 670 | 750 | 800 | 900 |

### Factor por inclinación K (IS 11592, tabla 9)

| δ [°] | 0 a 2 | 4 | 6 | 8 | 10 | 12 | 14 | 16 | 18 | 20 | 21 | 22 | 23 | 24 | 25 | 26 | 27 | 28 | 29 | 30 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| K | 1,00 | 0,99 | 0,98 | 0,97 | 0,95 | 0,93 | 0,91 | 0,89 | 0,85 | 0,81 | 0,78 | 0,76 | 0,73 | 0,71 | 0,68 | 0,66 | 0,64 | 0,61 | 0,59 | 0,56 |

Capacidad: Iv = 3600·A·v·K [m³/h] e Im = Iv·ρ [t/h, con ρ en t/m³] (IS 11592, ec. 1). La norma limita la capacidad de diseño al 90 % de la calculada, y al 75 % en bandas de hasta 600 mm (cl. 8.4.5), por la alimentación despareja.

### Velocidad máxima (IS 11592, tablas 4 a 6)

Factor de velocidad = factor de tamaño + factor de abrasividad.

- Tamaño (tabla 4): 0 grano fino a polvo (menos de 10 mm); 1 granular sin clasificar (menos de 25 mm); 2 granular clasificado; 3 sin clasificar con menos del 60 % de terrones grandes; 4 con los terrones del tamaño máximo. Si el material levanta polvo, la norma suma un factor (4 para grano fino; verificar cómo se combina).
- Abrasividad (tabla 5): 1 no abrasivo (granos de cereal, chips de madera); 2 poco abrasivo (agregados, carbón, sal); 3 abrasivo (escoria, caliza, pellets); 4 muy abrasivo (mineral de hierro, granito, coque).

| Ancho de banda [mm] | Factor 1 | 2 | 3 y 4 | 5 y 6 | 7 y 8 |
|---|---|---|---|---|---|
| hasta 500 | 2,50 | 2,30 | 2,00 | 1,65 | 1,45 |
| 600 a 650 | 3,00 | 2,75 | 2,38 | 2,00 | 1,75 |
| 750 a 800 | 3,50 | 3,20 | 2,75 | 2,35 | 2,05 |
| 950 a 1050 | 4,00 | 3,65 | 3,15 | 2,65 | 2,35 |
| 1200 a 2000 | 4,50 | 4,12 | 3,55 | 3,00 | 2,62 |

Velocidades máximas en m/s. Para un ancho entre dos filas, el script toma la fila de abajo (del lado seguro). MEKA da valores parecidos por tipo de material: con 800 mm, 3,75 m/s para granulares que fluyen bien, 3,0 a 3,5 m/s para piedra partida, carbón y tierra, y 2,75 m/s para mineral duro y piedra.

### Inclinación máxima

- Por material: IS 8730:1997, tabla 3, columna "Recommended maximum inclination" (para cintas convencionales en las que el material puede rodar hacia atrás). Ejemplo: cemento portland, 1500 kg/m³, ángulo de reposo 39°, inclinación máxima 20° a 23°. Para granos, sacar el valor de esa tabla o del fabricante de la banda (verificar: no se pudo leer la fila en la copia digital).
- Banda plana: hasta 6°; en bajada, no más de 12° (IS 11592, cl. 8.1.2 y tabla 2).
- Límite práctico general de 20° a 25° (MEKA). Más arriba: banda con nervios o tacos (fabricante).

### Fuerza en el tambor y potencia

FU = C·f·L·g·[m'R + (2·m'G + m'L)·cos δ] + m'L·g·H + FS (IS 11592, ec. 6; es la forma de DIN 22101 e ISO 5048), con m'R la masa de las partes que giran de los rodillos superiores e inferiores por metro, m'G la de la banda y m'L la de la carga, todas en kg/m. La ec. 5 suma las resistencias secundarias una por una en lugar de usar C, y vale para cualquier largo.

- f, coeficiente ficticio de rozamiento (cl. 8.5.1.1): 0,020 para cintas bien alineadas; 0,016 en condiciones favorables; hasta 0,030 en desfavorables; 0,012 en cintas en bajada que necesitan motor freno.
- C, coeficiente de resistencias secundarias (DIN 22101 / ISO 5048, verificar en la norma vigente): la IS 11592 lo da solo en un gráfico (fig. 6) y avisa que con L < 80 m es incierto (cl. 8.5.1.2).

| L [m] | 80 | 100 | 150 | 200 | 300 | 400 | 500 | 600 | 700 | 800 | 900 | 1000 | 1500 | 2000 | 2500 | 5000 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C | 1,92 | 1,78 | 1,58 | 1,45 | 1,31 | 1,25 | 1,20 | 1,17 | 1,14 | 1,12 | 1,10 | 1,09 | 1,06 | 1,05 | 1,04 | 1,03 |

- FS: resistencias especiales (raspadores, faldones, trippers). Para trippers, la IS 11592 multiplica FU por (1 + β·nt) con β de sus tablas 13 y 14.
- Potencia en el tambor PA = FU·v; en el motor PM = PA/η. Rendimientos de la IS 11592, tabla 12: reductor de engranajes cerrado de 1, 2 y 3 trenes, hasta 98, 96 y 94 %; cadena cerrada en baño de aceite, hasta 98 %; correas en V, 95 %; correa dentada, 95 a 98 %.
- Arranque: la tabla 15 de la IS 11592 da un coeficiente de 1,8 a 2,2 para motor jaula con arranque directo y acople rígido, 1,5 a 1,6 con acople hidráulico y 1,2 con estrella-triángulo y acople elástico. Elección del motor en **maquinas-electricas**.

### Tensiones

- Euler-Eytelwein: T1/T2 ≤ e^(μ·α), con α el arco abrazado en radianes. Con FU = T1 − T2: T2 ≥ FU/(e^(μ·α) − 1) y T1 = FU + T2.
- μ de diseño: 0,25 tambor desnudo y 0,35 revestido (IS 11592, tabla 20, que da e^(μ·α) = 2,19 y 3,00 a 180°; 2,39 y 3,39 a 200°; 2,85 y 4,33 a 240°; 4,80 y 9,02 a 360°).
- μ según el estado (IS 11592, tabla 16):

| Estado | Acero liso | Caucho con dibujo | Poliuretano con dibujo | Cerámico con dibujo |
|---|---|---|---|---|
| Seco | 0,35 a 0,40 | 0,40 a 0,45 | 0,35 a 0,40 | 0,40 a 0,45 |
| Mojado con agua limpia | 0,10 | 0,35 | 0,35 | 0,35 a 0,40 |
| Mojado y sucio (barro, arcilla) | 0,05 a 0,10 (verificar) | 0,25 a 0,30 | 0,20 | 0,35 |

- Flecha entre rodillos: la tensión mínima en el ramal cargado es T ≥ a0·(m'G + m'L)·g/(8·h/a), con a0 el paso de los rodillos y h/a la flecha admisible, del orden del 1 % (verificar con el fabricante o DIN 22101). Sale de la catenaria aproximada por una parábola. Si da más que T2 de Euler, manda y se logra con el contrapeso.
- T1/B [N/mm] se compara con la tensión de trabajo de la banda del catálogo; la banda se elige con esa tensión, el material y los espesores de cobertura.

### Seguridad (Dec. 351/79, Anexo I, cap. 15)

Art. 127: los transportadores con resistencia para su carga, pasarelas para cruzarlos y dispositivos de parada. Art. 130: resguardos en los puntos de contacto de las cintas hasta 1 m del tambor, y los fosos cubiertos con rejas o barandas. Art. 131: los transportadores helicoidales, totalmente cubiertos. Art. 132: transportadores neumáticos. Bloqueo y etiquetado en **higiene-y-seguridad**.

## Transportador a tornillo sinfín (CEMA 350, por KWS)

Capacidad: Q = 60·(π/4)·(D² − d²)·p·n·φ [m³/h] con D (hélice), d (tubo) y p (paso) en m; en CEMA, C1 = 0,7854·(Ds² − Dp²)·P·K·60/1728 [ft³/h por rpm] con pulgadas. Con tubo de 2⅜ in (sinfines de 6 y 9 in) y 3½ in (12 in) la fórmula reproduce la tabla de KWS con diferencias menores que 1 %.

Capacidad a 1 rpm [ft³/h] y rpm máximas recomendadas (KWS, para materiales no abrasivos que fluyen libre; KWS recomienda ir más despacio en la industria):

| D [in] | 15 % | 30 % A | 30 % B | 45 % | rpm máx. 15 % | 30 % A | 30 % B | 45 % |
|---|---|---|---|---|---|---|---|---|
| 6 | 0,8 | 1,5 | 1,5 | 2,2 | 60 | 120 | 60 | 165 |
| 9 | 2,7 | 5,5 | 5,5 | 8,2 | 55 | 100 | 55 | 155 |
| 12 | 6,5 | 12,9 | 12,9 | 19,4 | 50 | 90 | 50 | 145 |
| 14 | 10,4 | 20,8 | 20,8 | 31,2 | 50 | 85 | 50 | 140 |
| 16 | 15,6 | 31,2 | 31,2 | 46,7 | 45 | 80 | 45 | 130 |

1 ft³/h = 0,02832 m³/h. Ejemplo de KWS: cal viva, hélice cortada y plegada (factor 3,75) con paso corto (1,50): capacidad de selección 1,50·3,75·333 = 1873 ft³/h; en el de 16 in, 1873/31,2 = 60 rpm.

Materiales (tabla de KWS; la densidad pasa a kg/m³ por 16,02):

| Material | lb/ft³ | Llenado | Fm |
|---|---|---|---|
| Maíz desgranado | 45 | 45 % | 0,4 |
| Trigo | 45 a 48 | 45 % | 0,4 |
| Soja en grano | 45 a 50 | 45 % | 0,5 |
| Arroz descascarado | 45 a 49 | 45 % | 0,4 |
| Avena | 26 | 45 % | 0,6 |
| Harina de trigo | 33 a 40 | 30 % A | 0,6 |
| Harina de soja fría | 35 a 45 | 30 % A | 0,6 |
| Azúcar refinada granulada seca | 50 a 55 | 30 % A | 1,0 a 1,2 |
| Aserrín seco | 10 a 13 | 30 % A | 1,4 |
| Carbón bituminoso | 40 a 60 | 30 % A | 0,9 |
| Caliza agrícola | 68 | 30 % A | 2,0 |
| Cemento portland | 94 | 30 % B | 1,4 |
| Sal seca fina | 70 a 80 | 30 % B | 1,7 |
| Ceniza volante | 30 a 45 | 30 % B | 2,0 |
| Arena de banco húmeda | 110 a 130 | 15 % | 2,8 |

La tabla de KWS no explica las clases A y B de 30 %; tienen las mismas capacidades y distintas rpm máximas. El script usa el promedio de la densidad y el Fm mayor del rango.

Potencia (CEMA 350, en unidades inglesas): HPf = L·N·Fd·Fb/10⁶ (vacío) y HPm = C·L·W·Ff·Fm·Fp/10⁶ (material), con L en ft, N en rpm, C en ft³/h y W en lb/ft³; total = (HPf + HPm)·Fo/e. KWS escribe las fórmulas como imagen y nombra los mismos factores (DF, HBF, MF).

- Fd, factor de diámetro: 4 in 12; 6 in 18; 9 in 31; 12 in 55; 14 in 78; 16 in 106; 18 in 135; 20 in 165; 24 in 235; 30 in 377; 36 in 549.
- Fb, cojinetes intermedios: de bolas, rodillos o sin cojinete 1,0; bronce o madera 1,7; plástico, nylon, UHMW o teflón 2,0; hierro duro o stellite 4,4.
- Ff, hélice especial: cortada 1,10 / 1,15 / 1,2 con 15 / 30 / 45 %; cortada y plegada 1,50 / 1,7 con 30 / 45 %; de cinta 1,05 / 1,14 / 1,20.
- Fp, paletas por paso: 1 → 1,29; 2 → 1,58; 3 → 1,87; 4 → 2,16.
- e, rendimiento del accionamiento: 0,88 típico con reductor montado en el eje (0,85 a 0,95).
- Fo, sobrecarga: si HPf + HPm es menor que 5 hp, CEMA lo corrige con un gráfico (en KWS, "Corrected Material HP Chart"); no está en el script, se ingresa con `--fo`.

El método es para sinfín horizontal. Inclinado, la capacidad baja y la potencia sube: el script suma solo la elevación ṁ·g·H y avisa; el resto, con el fabricante (verificar).

## Elevador de cangilones

Capacidad: Q = 3,6·(V/a)·v·φ [m³/h], con V el volumen del cangilón en litros, a la separación en m, v la velocidad en m/s y φ el llenado (0,75 por defecto en el script; verificar con el catálogo del cangilón). Qm = Q·ρ.

Descarga en la cabeza, por el polo de la resultante:

- Sobre un grano a radio r giran juntos el peso (g hacia abajo) y la fuerza centrífuga (ω²·r hacia afuera). La recta de la resultante corta la vertical del eje del tambor siempre en el mismo punto, el polo P, a hp = g/ω² sobre el eje (el `demo` lo comprueba en 18 posiciones). Con n en rpm: hp = 894/n² [m].
- hp menor que el radio del tambor (v² > g·r): manda la fuerza centrífuga y el material sale despedido: descarga centrífuga, la de los elevadores de granos.
- hp mayor que el radio del borde exterior del cangilón: manda el peso y el material cae por el borde interior: descarga por gravedad (cangilones continuos, materiales frágiles o pesados).
- Entre los dos: descarga mixta.
- Para que el material empiece a salir arriba del tambor: ω²·rc = g, con rc el radio al centro del cangilón: n = 29,9/√rc [rpm] = 42,3/√D con D = 2·rc en m.

Potencia teórica de elevación P = ṁ·g·H = Qm·H/367 [kW con Qm en t/h]; el fabricante suma el dragado en la bota y los rozamientos (verificar con el catálogo). Correas o cadenas de accionamiento en **elementos-de-maquinas**.
