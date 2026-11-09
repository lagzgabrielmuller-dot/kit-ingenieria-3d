# Datos de corte: fórmulas, valores orientativos y ejemplos

Leer cuando haya que elegir Vc, avance y profundidad, calcular rpm, tiempos o potencia, o justificar los datos de la hoja de proceso. Los valores de catálogo son **orientativos**: son los rangos que publica cada fabricante para su herramienta, en máquinas rígidas. En un torno o una fresadora de escuela conviene empezar por el extremo bajo y respetar las rpm y la potencia de la máquina. Si la cátedra da sus propios datos o su catálogo, se usan esos.

## Fórmulas

| Magnitud | Torno | Fresadora | Unidades |
|---|---|---|---|
| Velocidad de corte | Vc = π·D·n / 1000 | igual (D de la herramienta) | m/min |
| Giro | n = 1000·Vc / (π·D) | igual | rpm |
| Avance de la mesa o del carro | Vf = f·n | Vf = fz·z·n | mm/min |
| Tiempo de una pasada | t = L / Vf | igual | min |
| Caudal de viruta | Q = Vc·ap·f | Q = ap·ae·Vf / 1000 | cm³/min |
| Espesor de viruta | h = f·sen κr | hm = fz·(1 − cos φ)/φ · sen κr; cos φ = 1 − 2·ae/D | mm |
| Fuerza específica | kc = kc1·h^(−mc) | kc = kc1·hm^(−mc) | N/mm² |
| Potencia de corte | Pc = Vc·ap·f·kc / 60 000 | Pc = ap·ae·Vf·kc / (60·10⁶) | kW |
| Potencia en el motor | Pc / η | Pc / η | kW |
| Par en el husillo | M = Pc·30 000 / (π·n) | igual | N·m |

- D: diámetro de la pieza (torno) o de la herramienta (fresadora), mm; f: avance por vuelta, mm/v; fz: avance por diente, mm; z: filos; ap: profundidad (en torno, radial), mm; ae: ancho de contacto de la fresa, mm; L: recorrido a avance, con la entrada y la salida, mm; κr: ángulo de posición del filo; φ: ángulo de contacto de la fresa, en radianes.
- n, Vc, Vf, fz y la potencia de fresado son las de las hojas de fórmulas de Sandvik Coromant ([SC] <https://cdn.sandvik.coromant.com/files/sitecollectiondocuments/services/metal-cutting-e-learning/formulas-and-definitions/formulas-and-deinitions-for-milling-metric-enu.pdf>); kc = kc1·hm^(−mc) y la potencia dividida por η están en el catálogo de Sandvik ([SK] <https://www.directools.com/documents/all/Sandvik_5747275_Catalog.pdf>).
- La potencia de torneado sale de Fc·v: Fc = kc·ap·f [N] y v = Vc/60 [m/s], así que Pc = kc·ap·f·Vc / 60 000 [kW]. El espesor medio de fresado es el promedio de fz·sen φ sobre el arco de contacto; con ranurado completo (ae = D) da hm = 2·fz/π. Las dos cosas se verificaron con Python (la segunda por integración numérica).
- Con G96 la rpm sube al bajar el diámetro (a 200 m/min, en Ø5 serían 12 732 rpm): el límite `G50 S` la corta, y por debajo de ese diámetro la Vc real es menor. `cnc.py perfil` estima el tiempo integrando a lo largo del recorrido con ese límite.
- η (rendimiento de la transmisión de la máquina) no es un dato del catálogo: el script supone 0,8 si no se le da `--eta`.

## Valores orientativos de catálogo

### Torneado con plaquita de metal duro recubierta (Mitsubishi Materials)

Catálogo C010A de plaquitas de torneado ([MT] <https://data.mmc-carbide.com/4416/9575/0602/catalog_c010a_turning_inserts.pdf>, edición en pulgadas, pp. A015 a A024; convertido con 1 SFM = 0,3048 m/min y 1 in = 25,4 mm). Primera recomendación de cada caso:

| Material | Trabajo | Calidad | Vc (m/min) | f (mm/v) | ap (mm) |
|---|---|---|---|---|---|
| Acero al carbono y aleado, 180–280 HB | terminación | NX2525 | 210–300 | 0,08–0,25 | 0,1–1,0 |
| ídem | liviano | MC6115 | 250–480 | 0,10–0,41 | 0,3–2,0 |
| ídem | medio | MC6115 | 230–440 | 0,15–0,51 | 0,3–4,0 |
| Inoxidable, menos de 200 HB | medio | MC7015 | 165–259 | 0,15–0,46 | 0,7–5,0 |
| Fundición | liviano | MC5015 | 204–335 | 0,10–0,41 | 0,3–2,0 |
| Aleación de aluminio | terminación | HTi10 | 300–700 | 0,10–0,41 | 0,2–3,0 |

### Fresado lateral con fresa de metal duro de 3 filos, Ø10 (Mitsubishi Materials iMX S3HV)

Hoja de la cabeza intercambiable iMX S3HV, fresado lateral con L/D = 3, ap = 8 mm y ae = 2 mm ([MF] <https://www.mitsubishicarbide.net/contents/mht/enuk/manual/solid_end_mills_iMX_S3HV.pdf>):

| Material | Vc (m/min) | n (rpm) | fz (mm/diente) | Vf (mm/min) |
|---|---|---|---|---|
| Acero al carbono, aleado o dulce; cobre y sus aleaciones | 150 | 4800 | 0,09 | 1300 |
| Acero pretemplado, acero aleado de herramientas | 120 | 3800 | 0,06 | 680 |
| Inoxidable, aleación de titanio | 100 | 3200 | 0,075 | 720 |

Comprobación: n = 1000·150/(π·10) = 4775 rpm y Vf = 0,09·3·4800 = 1296 mm/min, coherentes con la tabla. Para ranurado los valores son más bajos (ver la hoja original).

### Taladrado con broca de acero rápido recubierta TiN (Dormer A510)

Ficha de las brocas ADX A510, A520 y A553 ([DO] <https://cdn.dgisupply.ca/img/product-images/Asset_URL/Dormer_0390795_Specification_Sheet.pdf>; la A510 es de acero rápido con TiN según su ficha de venta: <https://cromwell.co.uk/shop/cutting-tools/jobber-drills/a510-jobber-drill-8-3mm-normal-helix-high-speed-steel-tin/p/DOR0265183P>). Columna A510, convertida de SFM:

| Grupo Dormer | Material | Vc (m/min) | Código de avance |
|---|---|---|---|
| 1.3 | acero al carbono | 39,9 (131 SFM) | K |
| 1.4 | acero aleado | 29,9 (98 SFM) | H |
| 2.2 | inoxidable austenítico | 14,0 (46 SFM) | I |
| 3.1 | fundición gris hasta 150 HB | 42,1 (138 SFM) | K |
| 6.3 | latón α | 45,1 (148 SFM) | I |
| 7.2 | aluminio aleado, Si menor que 0,5 % | 50,0 (164 SFM) | M |

El avance sale de la tabla de códigos por diámetro (± 25 %): para Ø10, código K = 0,0130 in/v = 0,33 mm/v y código M = 0,0154 in/v = 0,39 mm/v. Ejemplo: broca Ø10 en acero al carbono a 40 m/min → n = 1273 rpm, Vf = 0,33·1273 = 420 mm/min.

Comparación útil: en acero al carbono, la broca de acero rápido trabaja a unos 40 m/min y la plaquita de metal duro en torneado a 230–440 m/min (tablas de arriba). Con herramientas de acero rápido (cuchillas, brocas, fresas) se usan los datos de su fabricante, nunca los del metal duro.

## kc1 y mc por material (ISCAR)

Tabla de grupos de materiales de ISCAR ([IS] catálogo Multi-Master 2018, p. 88: <https://iscar.com/Catalogs/flipview/Multi_Master_Catalog-2018/files/basic-html/page88.html>; misma tabla en <https://www.iscar.com/lms/wp-content/uploads/2021/04/Materials-group.pdf>). Son los valores de `cnc.py --material`; la última columna es kc para h = 0,2 mm, calculada con kc = kc1·h^(−mc).

| `--material` | Grupo ISCAR | Material | HB | kc1 (N/mm²) | mc | kc a h = 0,2 |
|---|---|---|---|---|---|---|
| acero-bajo-c | 1 | acero no aleado C menor que 0,25 %, recocido | 125 | 1350 | 0,21 | 1893 |
| acero-medio-c | 2 | acero no aleado C desde 0,25 %, recocido | 190 | 1500 | 0,22 | 2137 |
| — | 3 | acero no aleado C menor que 0,55 %, bonificado | 250 | 1675 | 0,24 | — |
| acero-aleado | 6 | acero de baja aleación, recocido | 200 | 1775 | 0,24 | 2612 |
| inoxidable | 14 | inoxidable austenítico | 180 | 2150 | 0,20 | 2966 |
| fundicion-gris | 15 | fundición gris ferrítica o perlítica | 180 | 1150 | 0,20 | 1587 |
| — | 17 | fundición nodular ferrítica | 160 | 1225 | 0,25 | — |
| aluminio | 21 | aluminio forjado no bonificable | 60 | 700 | 0,25 | 1047 |
| — | 22 | aluminio forjado bonificable | 100 | 800 | 0,25 | — |
| laton | 27 | latón | 90 | 700 | 0,27 | 1081 |

Otra tabla de ISCAR (<https://www.iscar.com/eCatalog/Ecat/datafileENM/INFO/5092.pdf>) da 1525 para el grupo 2. Entre fabricantes la diferencia es mayor: Seco da para un acero de fácil mecanizado 11SMn30 kc1.1 = 1500 y mc = 0,14 (≈ 1880 N/mm² a h = 0,2, parecido a ISCAR) ([SE] <https://maskin.sde.dk/wp-content/uploads/2025/03/GB-Milling-2025SN1-1.pdf>), y la tabla de Mitsubishi da 3100 MPa para acero dulce a f = 0,2 mm/v ([MK] <https://www.mmc-carbide.com/en_jp/technical_information/formula/co2/turning>), un 64 % más. Por eso la potencia calculada es **aproximada**: para elegir máquina o justificar un motor, usar el kc del catálogo de la herramienta que se va a usar (`--kc`) y dejar margen.

## Ejemplos resueltos (salen de `cnc.py corte`)

**Cilindrado** de acero de bajo carbono, Ø40, Vc 200 m/min, f 0,2 mm/v, ap 2 mm, L 60 mm:
n = 1000·200/(π·40) = 1592 rpm; Vf = 0,2·1592 = 318 mm/min; t = 60/318 = 0,19 min; Q = 200·2·0,2 = 80 cm³/min; kc = 1350·0,2^(−0,21) = 1893 N/mm²; Pc = 200·2·0,2·1893/60 000 = 2,52 kW; en el motor, con η = 0,8, 3,15 kW; par 15,1 N·m.

```
python scripts/cnc.py corte --vc 200 --d 40 --f 0,2 --ap 2 --l 60 --material acero-bajo-c
```

**Fresado lateral** de acero, fresa Ø10 de 3 filos, Vc 150 m/min, fz 0,09 mm, ap 8 mm, ae 2 mm, L 200 mm:
n = 4775 rpm; Vf = 0,09·3·4775 = 1289 mm/min; t = 0,16 min; φ = arccos(1 − 2·2/10) = 53,1°; hm = 0,0388 mm; kc = 2671 N/mm²; Pc = 8·2·1289·2671/(60·10⁶) = 0,92 kW.

```
python scripts/cnc.py corte --maquina fresadora --vc 150 --d 10 --z 3 --fz 0,09 --ap 8 --ae 2 --l 200 --material acero-bajo-c
```

**Límite de rpm**: Vc 250 m/min en Ø12 pide 6631 rpm; con una máquina de 2500 rpm (`--nmax 2500`) queda n = 2500 y la Vc real baja a 94 m/min. Hay que decidir si alcanza (terminación más lenta, peor acabado) o si conviene otra herramienta.

## Criterios para elegir

- **Profundidad**: en desbaste, la mayor que aguanten la herramienta, la sujeción y la potencia; en terminación, poca (décimas) y pareja: por eso se deja sobremetal (el script usa por defecto 0,4 mm en diámetro y 0,1 mm en Z; ajustarlo al rango de ap del inserto de terminación y a lo que pida el profesor).
- **Avance**: manda la terminación superficial y la resistencia del filo; el avance por vuelta no puede ser mayor que lo que admite el radio de punta (ver el catálogo del inserto).
- **Vc**: manda la vida de la herramienta; si la máquina no llega a las rpm, se trabaja con la Vc real.
- **Potencia**: Pc/η menor que la potencia del motor; si no alcanza, bajar ap, f o Vc.
- Revisar la viruta y el ruido en la primera pieza y corregir.
