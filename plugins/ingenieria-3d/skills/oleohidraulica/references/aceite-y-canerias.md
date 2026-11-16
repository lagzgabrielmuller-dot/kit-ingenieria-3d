# Aceite, cañerías, mangueras y pérdidas de carga

Leer este archivo al elegir el aceite, al calcular su viscosidad a la temperatura de trabajo, al dimensionar caños o mangueras o al calcular una pérdida de carga. Comandos del script: `viscosidad`, `cano` y `perdida`.

## Grados de viscosidad ISO VG (ISO 3448)

El número del grado es la viscosidad cinemática en el punto medio a 40 °C, con ± 10 % de tolerancia ([Anton Paar Wiki, clasificación ISO de viscosidad](https://wiki.anton-paar.com/en/iso-viscosity-classification/), referencia ISO 3448; la edición vigente de la norma: verificar en la norma vigente).

| Grado | Mínimo a 40 °C [mm²/s] | Punto medio [mm²/s] | Máximo [mm²/s] |
|---|---|---|---|
| ISO VG 10 | 9,0 | 10 | 11,0 |
| ISO VG 15 | 13,5 | 15 | 16,5 |
| ISO VG 22 | 19,8 | 22 | 24,2 |
| ISO VG 32 | 28,8 | 32 | 35,2 |
| ISO VG 46 | 41,4 | 46 | 50,6 |
| ISO VG 68 | 61,2 | 68 | 74,8 |
| ISO VG 100 | 90 | 100 | 110 |
| ISO VG 150 | 135 | 150 | 165 |

1 mm²/s = 1 cSt. El grado solo dice la viscosidad a 40 °C: a otra temperatura depende de cada aceite (índice de viscosidad).

## Datos de aceites hidráulicos (hojas técnicas)

| Aceite | ν a 0 °C | ν a 40 °C | ν a 100 °C | Índice de viscosidad | Densidad a 15 °C | Fuente |
|---|---|---|---|---|---|---|
| Mobil Nuto H 32 | | 31,4 | 5,3 | 98 | 0,872 kg/L | [Mobil Argentina, hoja de producto (02-2026)](https://www.mobil.com/es-ar/industrial/pds/gl-xx-nuto-h-series) |
| Mobil Nuto H 46 | | 44,0 | 6,6 | 98 | 0,876 kg/L | ídem |
| Mobil Nuto H 68 | | 63,3 | 8,3 | 98 | 0,882 kg/L | ídem |
| Shell Tellus S3 M 46 | 565 | 46 | 6,8 | 105 | 865 kg/m³ | [hoja técnica v4, 26-09-2012](https://petroleumservicecompany.com/content/pdfs/Shell_Tellus_S3-M46_PDS.pdf) |

- Son valores típicos de producción, no especificación. Nuto H cumple ISO L-HM (ISO 11158) y DIN 51524-2 según la misma hoja.
- El script trae cargados los tres Nuto H (`--vg 32`, `--vg 46`, `--vg 68`); para otro aceite, `--nu40` y `--nu100` de su hoja técnica.

## Viscosidad a la temperatura de trabajo (ASTM D341)

**ASTM D341-20(2025)** da las ecuaciones y gráficos para obtener la viscosidad cinemática de un aceite derivado del petróleo a cualquier temperatura conociéndola a dos temperaturas ([ASTM](https://store.astm.org/d0341-20r25.html)):

- log log Z = A − B · log T, con T en kelvin y logaritmos decimales.
- Z = ν + 0,7 + exp(−1,47 − 1,84 · ν − 0,51 · ν²) (forma que reproduce [Technical Toolboxes](https://help.technicaltoolboxes.com/?p=2144)); para ν de más de 2 mm²/s el término exponencial es despreciable y queda log log (ν + 0,7), la ecuación de Walther.
- Con ν a 40 °C y a 100 °C se despejan A y B; después se calcula ν a la temperatura que haga falta. El script invierte Z numéricamente.
- Control: con los datos de 40 °C y 100 °C del Tellus S3 M 46, la ecuación da 577 mm²/s a 0 °C y la hoja técnica 565 mm²/s (2 % de diferencia); está en el `demo`.

Viscosidad calculada [mm²/s] de los Nuto H:

| Temperatura [°C] | 0 | 10 | 20 | 30 | 40 | 50 | 60 | 70 | 80 | 100 |
|---|---|---|---|---|---|---|---|---|---|---|
| ISO VG 32 | 331 | 158 | 84,8 | 49,7 | 31,4 | 21,1 | 14,9 | 11,0 | 8,4 | 5,3 |
| ISO VG 46 | 542 | 247 | 127 | 71,8 | 44,0 | 28,8 | 19,8 | 14,3 | 10,7 | 6,6 |
| ISO VG 68 | 933 | 403 | 197 | 107 | 63,3 | 40,1 | 27,0 | 19,0 | 14,0 | 8,3 |

### Qué viscosidad pide la bomba

| Bomba | Rango óptimo o recomendado | Límites | Otros datos | Fuente |
|---|---|---|---|---|
| Pistones axiales Rexroth A10VSO | 16 a 36 mm²/s | mínimo 10 mm²/s por menos de 3 min y con menos de 0,3 veces la presión nominal; máximo 1000 mm²/s en el arranque en frío | temperatura −25 a +85 °C en la conexión L; aspiración ≥ 0,8 bar absolutos; limpieza 20/18/15 según ISO 4406 | [RE 92714/08.2015](https://hydraulicsonline.com/wp-content/uploads/2019/03/Bosch-Rexroth-A10VSO-series-32.pdf) |
| Engranajes externos Rexroth AZPF | 20 a 100 mm²/s en servicio continuo | 12 a 800 mm²/s admisible; hasta 2000 mm²/s en el arranque en frío | aspiración 0,7 a 3 bar absolutos; con juntas NBR, −30 a +80 °C; limpieza 20/18/15 (ISO 4406) | [RE 10089/2019-07-17](https://hydraulicsonline.com/wp-content/uploads/2019/03/Bosch-Rexroth-AZPF.pdf) |

- Rexroth pide elegir el aceite para que, en el rango de temperatura de trabajo, la viscosidad quede dentro del óptimo. Con el Nuto H 46 eso es de 45 a 66 °C para la A10VSO y de 24 a 60 °C para la AZPF (salida del comando `viscosidad`); con VG 32, de 37 a 58 °C y de 17 a 51 °C; con VG 68, de 53 a 75 °C y de 31 a 68 °C.
- En frío manda el máximo de arranque: según la ecuación, el Nuto H 46 llega a 1000 mm²/s a unos −7 °C (la AZPF admite hasta 2000 mm²/s, a unos −14 °C). Si el equipo arranca más frío, hace falta otro grado o calentar el aceite.

## Velocidades recomendadas en las líneas

| Línea | Atos (tabla P002-1/E) | Roymech | HANSA-FLEX (máximo) | Hydroscand |
|---|---|---|---|---|
| Aspiración | 1 a 1,5 m/s | 0,6 a 1,2 m/s | 1 m/s | 1 m/s |
| Retorno | 1,5 a 4 m/s | 1,5 a 4 m/s | 3 m/s | 2 a 4 m/s |
| Presión | 4 a 8 m/s | 2 a 5 m/s | 6 m/s | 3 a 5 m/s; no pasar de 8 m/s |

Fuentes: [Atos, tabla P002-1/E](https://atos.com/tables/french/P002.pdf) (usar los valores bajos en baja presión o servicio continuo); [Roymech, Hydraulic tubing](https://roymech.org/Related/Hydrostatics/Hydraulic_tubing.html) (para presiones normales de 100 a 350 bar); [HANSA-FLEX, artículo de la Internationale Hydraulik Akademie, 08-06-2026](https://www.hansa-flex.de/en/magazine/details/hydraulic-pipelines-dimension-correctly-avoid-cracks-in-bent-pipes/); [Hydroscand, cálculo de dimensión de caños](https://hydroscand.se/en-us/fakta-guider/berakning-av-rordimension).

Velocidad máxima en la línea de presión según la presión, de la *Formelsammlung Hydraulik* de H. Ortwig, Hochschule Trier ([PDF](https://public.hochschule-trier.de/~ortwig/Downloads/hydraulikformeln.pdf)):

| Presión | Hasta 50 bar | 50 a 100 bar | 100 a 200 bar | Más de 200 bar |
|---|---|---|---|---|
| v máx | 4 m/s | 4 a 5 m/s | 5 a 6 m/s | 6 a 7 m/s |

El script toma por defecto 1 m/s en aspiración, 3 m/s en retorno y en presión el valor bajo de cada rango de Ortwig (4, 4, 5 y 6 m/s); con `--v` se usa otra.

## Diámetro interior

- d = √(4 · Q / (π · v)); con Q en L/min, v en m/s y d en mm: d = √(21,22 · Q / v). En su nomograma de mangueras Parker usa la constante 21,2025 ([Technisches Handbuch, Katalog 4400/DE](https://www.ludwigmeister.de/content/kataloge/PARKER_Durchflussmengen-Nomogramm.pdf)).
- Se adopta el diámetro interior comercial inmediato superior y se recalcula la velocidad real.
- El caudal de cada línea no siempre es el de la bomba: del lado del émbolo, al retroceder, vuelven Q · φ (con φ = 2, el doble). La línea de retorno y la conexión A del cilindro se dimensionan con ese caudal.
- En la aspiración, además de la velocidad, la presión absoluta en la entrada de la bomba tiene que quedar sobre el mínimo del catálogo: p entrada = p atm + ρ · g · h − Δp aspiración (h positiva si el nivel del aceite está por encima de la bomba). Se verifica en frío, que es cuando la pérdida es mayor.

### Manguera de dos mallas de acero EN 853 2SN / SAE 100 R2 S

| DN | Dash | Pulgadas | Interior [mm] | Presión de trabajo [bar] | Caudal a 1 / 3 / 5 m/s [L/min] |
|---|---|---|---|---|---|
| 6 | -4 | 1/4" | 6,6 | 400 | 2,1 / 6,2 / 10,3 |
| 8 | -5 | 5/16" | 8,3 | 350 | 3,2 / 9,7 / 16,2 |
| 10 | -6 | 3/8" | 9,9 | 330 | 4,6 / 13,9 / 23,1 |
| 12 | -8 | 1/2" | 13,0 | 275 | 8,0 / 23,9 / 39,8 |
| 16 | -10 | 5/8" | 16,4 | 250 | 12,7 / 38,0 / 63,4 |
| 19 | -12 | 3/4" | 19,5 | 215 | 17,9 / 53,8 / 89,6 |
| 25 | -16 | 1" | 26,0 | 165 | 31,9 / 95,6 / 159,3 |
| 31 | -20 | 1 1/4" | 32,5 | 125 | 49,8 / 149,3 / 248,9 |
| 38 | -24 | 1 1/2" | 38,7 | 90 | 70,6 / 211,7 / 352,9 |
| 51 | -32 | 2" | 51,1 | 80 | 123,1 / 369,2 / 615,3 |

- Fuente: [Semperit, DIN EN 853 2SN / SAE 100 R2 S](https://hoses.semperitgroup.com/products/hydraulic-pressure-washer-hoses/braided-spiral-hoses/din-en-853-2-sn-sae-100-r-2-s/) (diámetro interior real del fabricante). Las presiones coinciden con las de la 2SN de [Tubes International](https://www.tubes-international.com/online-catalogue/hydraulic-hose-with-double-steel-braid-en-853-2sn-s/), salvo DN 51, que da 78 bar.
- La presión admisible baja al crecer el diámetro: para caudales grandes a alta presión se usan mangueras espiraladas (EN 856 4SP o 4SH) o caño de acero, con los datos del catálogo.
- La presión de trabajo de la manguera tiene que superar la máxima de esa línea: la de la válvula de alivio, o la de intensificación en el lado del vástago.

## Pérdida de carga (Darcy-Weisbach)

| Paso | Fórmula | Fuente |
|---|---|---|
| Número de Reynolds | Re = v · d / ν (v [m/s], d [m], ν [m²/s]) | |
| Laminar, Re < 2300 | λ = 64 / Re | [Engineering ToolBox](https://engineeringtoolbox.com/amp/laminar-friction-coefficient-d_1032.html); Ortwig |
| Transición | Re entre 2300 y 4000 (el script calcula como turbulento, del lado seguro) | [Wikipedia, Darcy friction factor formulae](https://en.wikipedia.org/wiki/Darcy_friction_factor_formulae) |
| Turbulento, tubo liso | λ = 0,3164 / Re^0,25 (Blasius) | Ortwig: de 2300 a unos 80 000; Wikipedia: hasta Re = 100 000 |
| Turbulento con rugosidad | 1/√λ = −1,8 · log((ε/d / 3,7)^1,11 + 6,9/Re) (Haaland) | Wikipedia |
| Pérdida en el tramo | Δp = λ · (L / d) · ρ · v² / 2 [Pa]; 1 bar = 10⁵ Pa | Ortwig |
| Pérdidas localizadas | Δp = Σζ · ρ · v² / 2, con ζ del fabricante del accesorio | |

- En laminar, Δp = 128 · μ · L · Q / (π · d⁴) (Hagen-Poiseuille, con μ = ρ · ν): la pérdida es proporcional a la viscosidad. Por eso en frío se multiplica: en el ejemplo, de 0,470 bar a 50 °C a 4,04 bar a 10 °C.
- La densidad de la hoja técnica es a 15 °C; a la temperatura de trabajo es algo menor, así que usarla da una pérdida un poco mayor (lado seguro).
- Algunos libros de hidráulica usan λ = 75/Re en laminar para tener en cuenta que el aceite se enfría contra la pared; no se pudo confirmar en una fuente accesible (verificar en la bibliografía de la cátedra). Si la cátedra lo pide: `--laminar 75`.

### Ejemplo (el del `demo`)

Manguera de presión DN 12 (13,0 mm) de 3 m con 26,17 L/min de Nuto H 46:

- A 50 °C: ν = 28,76 mm²/s; v = 3,286 m/s; Re = 1485 (laminar); λ = 0,0431; Δp = 0,470 bar.
- A 10 °C: ν = 247,3 mm²/s; Re = 173; Δp = 4,04 bar (8,6 veces más).
- Aspiración DN 25 de 0,5 m en frío: Δp = 0,042 bar → 0,97 bar absolutos en la entrada (la AZPF pide al menos 0,7).

```
python scripts/oleohidraulica.py perdida --Q 26.17 --d 13 --L 3 --vg 46 --temp 50
python scripts/oleohidraulica.py cano --Q 51.3 --tipo retorno
```
