# Materiales: conductividad, emisividad y temperatura de superficie

Leer para elegir la k de una capa, la emisividad de una superficie o el criterio de temperatura de contacto, con su fuente. Si la consigna, el fabricante o la norma dan otro valor, manda ese. `calor.py materiales` lista los que trae cargados el script.

## Conductividad de materiales de construcción y aislantes (temperatura de edificios)

Fuente: Municipalidad de Rosario, [lista de materiales](https://www.rosario.gob.ar/web/sites/default/files/lista_de_materiales.pdf) de las planillas de cálculo higrotérmico. El documento no cita la norma; sus valores son del tipo de IRAM 11601 (el de hormigón de piedra de 2400 kg/m³, 1,63 W/(m·K), coincide con el que atribuye a IRAM 11601 el trabajo de [UTN FRC, 2016](https://ria.utn.edu.ar/bitstreams/64df7944-3f58-45a2-b56e-162d975e9cc5/download)). Verificar en la norma vigente antes de citarlos como IRAM.

| Material | λ [W/(m·K)] |
|---|---|
| Acero / acero inoxidable | 58 / 17 |
| Ladrillo macizo común de 1600 / 1800 / 2000 kg/m³ | 0,81 / 0,91 / 1,10 |
| Hormigón de piedra de 1800 / 2000 / 2200 / 2400 / 2500 kg/m³ | 0,97 / 1,16 / 1,40 / 1,63 / 1,74 |
| Hormigón armado de 2500 kg/m³ | 2,30 |
| Fieltro de lana de vidrio de 9 a 10 / 11 a 14 / 15 a 18 kg/m³ | 0,045 / 0,043 / 0,040 |
| Panel de lana de vidrio de 19 a 30 / 31 a 45 / 46 a 100 kg/m³ | 0,037 / 0,034 / 0,033 |
| Lana mineral de 30 a 50 / 51 a 70 / 71 a 150 kg/m³ | 0,042 / 0,040 / 0,038 |
| Poliuretano rígido de 30 a 60 kg/m³: placas sin protección / entre barreras de vapor / proyectado entre barreras de vapor | 0,027 / 0,024 / 0,022 |
| Poliestireno expandido de 15 / 20 / 25 / 30 kg/m³ | 0,037 / 0,035 / 0,033 / 0,032 |

Cámaras de aire no ventiladas en paredes (misma fuente, resistencia R en m²·K/W): entre superficies no metálicas, de 2 a 4 cm: 0,16; de 5 a 10 cm: 0,17; con una o ambas superficies metálicas, de 2 a 4 cm: 0,31. Una cámara de 5 cm no vale e/k_aire = 0,05/0,0251 = 2 m²·K/W: adentro hay convección y radiación.

## Metales y otros (libros)

| Material | k [W/(m·K)] | Fuente |
|---|---|---|
| Aluminio puro, 300 K | 237 | Incropera, 6.ª ed., tabla A.1 (dato de los ejemplos 2.1 y 11.6 en el [compañero de FOSSEE](https://git.fossee.in/Scilab-TBC-Uploads/.git/plain/latex/book_534.pdf)); también Muzychka y Yovanovich |
| Cobre puro, 300 K | 401 | Muzychka y Yovanovich, *Thermal Spreading and Contact Resistance* (Wiley-ASME, 2023), [tabla C.1](https://www.oreilly.com/library/view/thermal-spreading-and/9781394187522/b03.xhtml) |
| Acero inoxidable AISI 304 / AISI 316, 300 K | 14,9 / 13,4 | Muzychka y Yovanovich, tabla C.1 / Incropera, tabla A.1 (ejemplo 7.5 en FOSSEE; Muzychka da 13,3) |
| Ladrillo de arcilla refractaria, 478 K | 1,0 | Incropera, tabla A.3 (ejemplo 4.3 en FOSSEE) |
| Vidrio celular, 285 K | 0,055 | Incropera, tabla A.3 (ejemplo 3.5) |
| Aislante de fibra de vidrio, 300 K | 0,038 | Incropera, tabla A.3 (ejemplo 9.5) |

## Aislantes industriales: k según la temperatura media

La k de una lana sube con la temperatura (conducción del aire de los poros y radiación entre fibras). Se toma a la temperatura media de la capa, (T_caliente + T_fría)/2; el script lo hace solo con `MATERIAL:mm:T1=k1/T2=k2/...`.

| Producto | k [W/(m·K)] a la temperatura media indicada | Máximo de servicio | Fuente |
|---|---|---|---|
| Panel de lana de vidrio ISOVER TECH Slab 3.0 (40 y 50 mm) | −20 °C: 0,030 · 10 °C: 0,034 · 50 °C: 0,038 · 100 °C: 0,047 · 150 °C: 0,058 · 200 °C: 0,070 · 250 °C: 0,085 | 300 °C | [ficha técnica](https://isover.es/documents/ficha-tecnica/ft-tech-slab-3.0-es.pdf) (EN 12667, mayo de 2026) |
| Manta de lana de vidrio ISOVER CLIMCOVER Lamela Mat (con aluminio) | 10 °C: 0,036 · 50 °C: 0,044 · 100 °C: 0,056 · 150 °C: 0,072 | aire hasta 300 °C con el revestimiento a 100 °C como máximo | [ficha técnica](https://www.isover.es/documents/ficha-tecnica/ft-climcover-lamela-mat-es.pdf) (EN 12667 y EN 12939) |
| Coquilla de lana de roca ROCKWOOL ProRox PS 960, 100 kg/m³ o más | 50 °C: 0,040 · 100 °C: 0,046 · 150 °C: 0,054 · 200 °C: 0,064 · 250 °C: 0,077 · 300 °C: 0,092 · 350 °C: 0,112 | 650 °C; con revestimiento de aluminio, la superficie a 80 °C como máximo | [ficha técnica](https://rti.rockwool.com/syssiteassets/tools--documentation/products-industrial/product-data-sheets/spanish/rti-prorox-ps-960_wr-tech_es.pdf) (EN ISO 8497, abril de 2026) |

Máximos que admiten las normas ASTM de materiales, según el [NIA, *Materials and Systems*](https://insulation.org/training-tools/designguide/materials-and-systems/), pasados de Btu·in/(h·ft²·°F) a W/(m·K) con el factor 0,14423 (calculado): sirven como valor conservador si no hay ficha.

| Norma y material | k máxima | Uso |
|---|---|---|
| ASTM C547, coquilla de fibra mineral (todos los tipos) | 0,036 a 38 °C de media | de 454 a 760 °C según el tipo |
| ASTM C553, manta de fibra mineral, tipo I | 0,052 a 24 °C; 0,110 a 149 °C | tipos I a III hasta 232 °C |
| ASTM C533, silicato de calcio, tipo I / IA y II | 0,059 / 0,072 a 38 °C | hasta 649 °C (tipo I) y 927 °C (tipo II) |
| ASTM C1029, poliuretano proyectado | 0,023 (sin temperatura media en la fuente) | de −30 a 107 °C |

## Emisividad de superficies

| Superficie (a unos 27 °C) | ε |
|---|---|
| Chapa de aluminio comercial / pulida / gofrada / oxidada / anodizada | 0,1 / 0,04 / 0,2 / 0,1 a 0,2 / 0,8 |
| Pintura de aluminio | 0,5 |
| Acero aluminizado (aluminio y cinc) | 0,06 |
| Acero galvanizado nuevo y brillante / galvanizado por inmersión u opaco | 0,1 / 0,3 |
| Acero inoxidable nuevo y limpio | 0,2 |
| Hierro o acero / metal pintado | 0,8 / 0,8 |
| Cobre muy pulido / oxidado | 0,03 / 0,8 |
| Revestimientos de PVC, PVDC o PET; masilla de color; goma; elastómeros | 0,9 |
| Lona | 0,7 a 0,9 |

Fuente: NIA, *Mechanical Insulation Design Guide*, [Design Data, tabla 1](https://insulation.org/training-tools/designguide/design-data/) (datos de ASHRAE).

| Superficie (emisividad normal) | ε |
|---|---|
| Acero pulido / oxidado / chapa laminada / chapa gruesa rugosa | 0,08 / 0,79 / 0,6 / 0,9 |
| Cinc, galvanizado | 0,23 |
| Aluminio pulido / oxidado / anodizado | 0,04 / 0,1 / 0,72 |
| Ladrillo / mortero / arcilla | 0,93 / 0,93 / 0,91 |
| Pintura / esmalte / vidrio / papel | 0,95 / 0,9 / 0,88 / 0,92 |

Fuente: CIBSE Guide C, tabla C3.7, reproducida en la [ayuda de IES VE](https://help.iesve.com/ve2026/table_23_emissivities_of_various_materials__table_c3_7_cibse_guide_.htm). Son valores normales: para la emisividad hemisférica la misma fuente indica multiplicar por 1,2 en metales brillantes, 0,95 en otras superficies lisas y 0,98 en las rugosas.

La emisividad de una chapa cambia con el uso: el galvanizado brillante (0,1) se vuelve opaco (0,3) y el acero se oxida (0,8). Para pérdidas máximas conviene la ε alta; para la temperatura de superficie más alta, la baja.

## Temperatura de superficie segura

- ASTM C1055 toma 60 °C (140 °F) como temperatura máxima de superficies metálicas para un contacto de 5 s, el tiempo más probable en la industria, según el [NIA](https://insulation.org/training-tools/designguide/materials-and-systems/) y la nota técnica de [Johns Manville](https://jm.com/en/blog/2015/february/too-hot-to-handle); esta última agrega que muchos ingenieros de proceso usan 49 °C (120 °F). No se consultó la norma: verificar en la norma vigente.
- En superficies no metálicas (revestimientos plásticos, masillas) la piel se calienta menos y se admite más; los umbrales según material y tiempo de contacto están en ISO 13732-1 (verificar en la norma vigente).
- Para la Argentina no se encontró un límite de temperatura de superficie en las fuentes consultadas: verificar en la norma vigente y con **normas-tecnicas-ar**. Si la consigna da un valor, se usa ese.
