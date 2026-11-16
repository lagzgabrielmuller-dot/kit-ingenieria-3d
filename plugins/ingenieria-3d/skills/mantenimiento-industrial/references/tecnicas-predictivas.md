# Técnicas: lubricación de rodamientos, vibraciones, termografía, alineación y balanceo

Leer cuando haya que calcular cada cuánto y cuánta grasa poner en un rodamiento, evaluar una medición de vibraciones, interpretar una termografía o verificar una alineación o un balanceo. La selección y la vida L10 del rodamiento están en **elementos-de-maquinas**; los datos del motor, en **maquinas-electricas**.

## 1. Relubricación de rodamientos con grasa (método SKF)

Fuente: SKF, catálogo *Rolling bearings*, PUB BU/P1 17000/1, sección B.4 «Lubricación», intervalos de relubricación (diagrama 2, tablas 1 y 2) y procedimientos de relubricación. Valores leídos en la edición en coreano de 2021, págs. 112 a 115 ([PDF en el sitio de SKF](https://cdn.skfmediahub.skf.com/api/public/094466a66aaba637/pdf_preview_medium/094466a66aaba637_pdf)); hay ediciones en otros idiomas con el mismo número de publicación. Método confirmado en el curso de SKF *Lubrication basics* (2015, [transcripción](https://www.skf.com/skf/campaign/aptitudearchive/training/lubasics_v2/presentation_content/external_files/Lub_basics_tscpt.pdf)).

**Paso 1. Factor de velocidad.** A = n·dm [mm/min], con n en rpm y dm = 0,5·(d + D) en mm. Si gira el aro exterior, se usa n·D.

**Paso 2. Factor del rodamiento bf y límite** (tabla 1 de SKF; límites de n·dm en mm/min según la relación de carga C/P; NA: no corresponde):

| Rodamiento | bf | C/P ≥ 15 | C/P ≈ 8 | C/P ≈ 4 |
|---|---|---|---|---|
| Rígido de bolas, de bolas con contacto angular, de bolas a rótula | 1 | 500 000 | 400 000 | 300 000 |
| Rodillos cilíndricos, lado libre | 1,5 | 450 000 | 300 000 | 150 000 |
| Rodillos cilíndricos, lado fijo, carga axial chica o alternante | 2 | 300 000 | 200 000 | 100 000 |
| Rodillos cilíndricos, lado fijo, carga axial chica constante | 4 | 200 000 | 120 000 | 60 000 |
| Rodillos cilíndricos lleno, sin jaula | 4 | NA | NA | 20 000 |
| Agujas con jaula | 3 | 350 000 | 200 000 | 100 000 |
| Rodillos cónicos | 2 | 350 000 | 300 000 | 200 000 |
| Rodillos a rótula, Fa/Fr ≤ e, dm ≤ 800 mm, series 213, 222, 238, 239 | 2 | 350 000 | 200 000 | 100 000 |
| Rodillos a rótula, Fa/Fr ≤ e, dm ≤ 800 mm, series 223, 230, 231, 232, 240, 248, 249 | 2 | 250 000 | 150 000 | 80 000 |
| Rodillos a rótula, Fa/Fr > e, todas las series | 6 | 150 000 | 50 000 | 30 000 |
| Toroidal CARB con jaula | 2 | 350 000 | 200 000 | 100 000 |
| Axial de bolas | 2 | 200 000 | 150 000 | 100 000 |
| Axial de rodillos cilíndricos o de agujas | 10 | 100 000 | 60 000 | 30 000 |
| Axial de rodillos a rótula, arandela de eje girando | 4 | 200 000 | 120 000 | 60 000 |

El script tiene también las filas de rodamientos a rótula con dm > 800 mm y de la serie 241. Si A pasa el límite, la grasa común no alcanza: grasa especial, aceite o consultar a SKF.

**Paso 3. Intervalo del diagrama.** Con A·bf en el eje horizontal y la curva de C/P (≥ 15, ≈ 8 o ≈ 4) se lee tf en horas de funcionamiento, en escala logarítmica. El diagrama vale a 70 °C, con grasa de buena calidad de espesante de litio y aceite mineral, eje horizontal, aro interior girando y ambiente limpio. Ejemplo del curso de SKF: rodamiento 61868 MA a 500 rpm, dm = 380 mm → A = 190 000 mm/min, bf = 1; con carga liviana el intervalo puede llegar a 10 000 h y con carga muy alta baja a 2000 h.

**Paso 4. Ajustes** (tabla 2 de SKF):

| Condición | Ajuste |
|---|---|
| Temperatura de funcionamiento sobre 70 °C, hasta el límite alto de la grasa | La mitad por cada 15 °C de aumento |
| 15 °C o más por debajo de 70 °C | Se puede duplicar, una sola vez; nunca en rodamientos llenos ni axiales |
| Eje vertical | La mitad (la grasa tiende a escurrirse) |
| Vibraciones fuertes, aceleraciones y frenadas frecuentes | Acortar (sin factor: según la experiencia con la máquina) |
| Aro exterior girando o eje con carga excéntrica | Calcular con n·D en vez de n·dm |
| Contaminación | Más relubricación cuanto más entra (sin factor numérico) |
| Agujero d > 300 mm | La mitad |
| Rodillos cilíndricos con jaula J, JA, JB, MA, MB, ML, MP o PHA | La mitad |

SKF no aconseja intervalos de más de 30 000 h (el envejecimiento de la grasa supera la vida esperada de la mayoría de las grasas). Para rodamientos llenos, una nota de la tabla 1 indica dividir el tf por 10 (verificar en el catálogo). El script aplica la regla de la temperatura en forma continua, 0,5^((T − 70)/15): da lo mismo que dividir por 2 en cada escalón de 15 °C y, entre escalones, queda del lado seguro.

**Paso 5. Cantidad de grasa a reponer** (procedimientos de relubricación, pág. 112 de la edición consultada), con Gp en g y D y B en mm (B es el ancho total: T en los cónicos, H en los axiales):

- Por el costado del rodamiento: Gp = 0,005·D·B.
- Por la ranura y los agujeros del aro exterior: Gp = 0,002·D·B.

Llenado inicial: el rodamiento completo y, del espacio libre del alojamiento, alrededor del 40 % si se va a reponer por el costado o del 20 % si se repone por el centro; a muy baja velocidad, cuando hace falta proteger contra la contaminación y la corrosión, del 70 al 100 % (misma fuente).

**Otro fabricante, NSK** ([Bearing ABCs, Grease lubrication](https://www.nsk.com/am-en/tools-resources/knowledge-center/bearing-abcs/grease-lubrication/)): diagrama propio de intervalos para rodamientos radiales de bolas y de rodillos cilíndricos en función del diámetro y la velocidad; sobre 70 °C, la mitad por cada 15 °C; factor de corrección por carga 1,5 con P/C ≤ 0,06, 1 con 0,1, 0,65 con 0,13 y 0,45 con 0,16; en el alojamiento, llenar de 1/2 a 2/3 del espacio libre si la velocidad es hasta el 50 % de la límite, y de 1/3 a 1/2 si es mayor. No mezclar el diagrama de un fabricante con las correcciones del otro.

**Errores**: engrasar de más (la grasa batida calienta el rodamiento); relubricar rodamientos tapados de fábrica (con sellos o placas), que suelen venir engrasados de por vida (SKF, *Grease life in lubricated-for-life deep groove ball bearings*, Evolution 2/04); usar un intervalo en horas de funcionamiento como si fueran horas de calendario; mezclar grasas sin confirmar que sean compatibles. Si la placa o el manual del motor trae el intervalo y los gramos, manda eso.

## 2. Vibraciones

**Qué se mide.** Velocidad de vibración eficaz (RMS) de banda ancha, en mm/s, sobre las tapas de los cojinetes o los soportes, en dos direcciones radiales ortogonales en cada cojinete (en máquinas horizontales se prefieren la vertical y la horizontal); el instrumento tiene que tener respuesta plana al menos de 10 Hz a 1000 Hz, con límite inferior de 2 Hz para máquinas cerca de 600 r/min o por debajo (ISO 20816-3:2022, [muestra en iTeh](https://cdn.standards.iteh.ai/samples/78311/30f79c7c3eca41c1ad7b4321a447bd39/ISO-20816-3-2022.pdf)).

**Norma.** ISO 20816-3:2022, *Mechanical vibration — Measurement and evaluation of machine vibration — Part 3: Industrial machinery with a power rating above 15 kW and operating speeds between 120 r/min and 30 000 r/min* ([ISO](https://www.iso.org/standard/78311.html)). Reemplazó a ISO 10816-3:2009 y a ISO 7919-3:2009, que se fusionaron y se revisaron editorialmente. Valores de las tablas A.1 y A.2, tomados de su adopción por la BIS de India (IS/ISO 20816-3:2022, abril de 2024, [PDF](https://services.bis.gov.in/tmp/MED624436_07052024_1.pdf)) y coincidentes con la ISO 10816-3:2009 según la documentación de Beckhoff ([Vibration assessment](https://infosys.beckhoff.com/content/1033/tf3600_tc3_condition_monitoring/2708344331.html)):

- **Grupo 1**: máquinas grandes, de más de 300 kW; máquinas eléctricas con altura de eje H ≥ 315 mm.
- **Grupo 2**: máquinas medianas, de más de 15 kW hasta 300 kW; máquinas eléctricas con 160 mm ≤ H < 315 mm.
- **Soporte rígido** en una dirección si la frecuencia natural más baja del conjunto máquina-soporte supera a la excitación principal (casi siempre la de giro) en al menos 25 %; si no, flexible.

| Grupo y soporte | A/B [mm/s] | B/C [mm/s] | C/D [mm/s] | A/B, B/C, C/D en desplazamiento eficaz [µm] |
|---|---|---|---|---|
| 1, rígido | 2,3 | 4,5 | 7,1 | 29 / 57 / 90 |
| 1, flexible | 3,5 | 7,1 | 11,0 | 45 / 90 / 140 |
| 2, rígido | 1,4 | 2,8 | 4,5 | 22 / 45 / 71 |
| 2, flexible | 2,3 | 4,5 | 7,1 | 37 / 71 / 113 |

(Los desplazamientos salen de las velocidades suponiendo una frecuencia dominante de 12,5 Hz en el grupo 1 y de 10 Hz en el grupo 2, redondeados en la norma: 4,5 mm/s a 10 Hz dan 71,6 µm y la tabla dice 71.)

**Zonas** (cláusula 6.2.2.1): A, la de las máquinas recién puestas en servicio; B, aceptable para funcionar sin restricciones por largo tiempo; C, insatisfactoria para funcionamiento continuo prolongado, se puede seguir un tiempo limitado hasta que haya oportunidad de corregir; D, lo bastante severa como para dañar la máquina.

**ALARMA y DISPARO** (6.5.2 y 6.5.3): ALARMA = línea de base + 25 % del límite superior de la zona B, normalmente sin pasar 1,25 veces ese límite; DISPARO dentro de la zona C o D, sin pasar 1,25 veces el límite superior de la zona C. **Criterio de cambio** (6.3): un cambio de más del 25 % del límite B/C es significativo, sobre todo si es brusco, aunque la máquina siga en zona A o B. Si dos criterios dan resultados distintos, se toma la clasificación más restrictiva (6.6).

**Máquinas de 15 kW o menos**: quedan fuera de ISO 20816-3. Se evalúa la tendencia contra la línea de base de la misma máquina y el criterio del fabricante; la parte general es ISO 20816-1 (límites: verificar en la norma vigente).

**Diagnóstico por espectro** (SKF, *Vibrations help find faulty components*, Evolution, 1999, [artículo](https://evolution.skf.com/us/vibrations-help-find-faulty-components-3/)): el desbalance da una vibración alta a 1× la velocidad de giro, sin armónicas; la desalineación angular, vibración axial a 1×; la paralela, radial a 2× o 3×; la soltura mecánica, una serie larga de armónicas o de medias armónicas; los defectos de rodamientos aparecen a sus frecuencias características y sus múltiplos, y las bandas laterales a la velocidad del eje indican un daño avanzado. Frecuencias de defecto del rodamiento, deducidas de la cinemática (fr: frecuencia de giro; Z: elementos rodantes; d: su diámetro; dm: diámetro primitivo; α: ángulo de contacto):

- Aro exterior: BPFO = (Z/2)·fr·(1 − (d/dm)·cos α); aro interior: BPFI = (Z/2)·fr·(1 + (d/dm)·cos α).
- Jaula: FTF = (fr/2)·(1 − (d/dm)·cos α); elemento rodante: BSF = (dm/(2·d))·fr·(1 − ((d/dm)·cos α)²).
- Controles: BPFO + BPFI = Z·fr y Z·FTF = BPFO (el `demo` los verifica). La geometría la da el fabricante del rodamiento.

**Errores**: comparar valores pico con eficaces (en una senoidal pura el pico es √2 veces el eficaz); comparar mm/s con mm o µm; medir sobre la carcasa delgada y no sobre el cojinete; evaluar con la tabla una máquina de 15 kW o menos.

## 3. Termografía en equipos eléctricos

Criterio de ANSI/NETA MTS-2007, tabla 100.18, reproducida en la nota de aplicación de Fluke *Electrical Inspections Using Thermal Imaging* (Shermco Industries, 3/2010, [PDF](https://media.fluke.com/e5fe5900-3285-4e45-8896-b10600678538_original%20file.pdf)); verificar en la edición vigente de la norma:

| ΔT entre componentes similares con carga similar | ΔT sobre el aire ambiente | Acción sugerida |
|---|---|---|
| 1 a 3 °C | 1 a 10 °C | Posible deficiencia: investigar |
| 4 a 15 °C | 11 a 20 °C | Deficiencia probable: reparar cuando se pueda |
| — | 21 a 40 °C | Vigilar hasta que se pueda corregir |
| Más de 15 °C | Más de 40 °C | Discrepancia mayor: reparar de inmediato |

El calentamiento va en general con el cuadrado de la corriente, así que la carga en el momento de la medición pesa mucho en el ΔT: anotarla siempre (misma nota). Se mide con la emisividad ajustada (las superficies metálicas brillantes engañan a la cámara) y se compara entre fases. La diferencia de temperatura no permite predecir cuánto falta para la falla ([Infraspection Institute](https://irinfo.org/tip-of-week-alphabeta/setting-temperature-limits)).

## 4. Alineación de ejes

Guía de desalineación máxima aceptable de SKF (TKSA 20, guía rápida MP5370E, 2013, anexo 3, [PDF](https://nonprod.docs.rs-online.com/1e52/0900766b8130b8cc.pdf)); si el fabricante del acoplamiento o de la máquina da otra tolerancia, se usa esa:

| rpm | Desplazamiento paralelo [mm] | Error angular [mm/100 mm] |
|---|---|---|
| 0 a 1000 | 0,13 | 0,10 |
| 1000 a 2000 | 0,10 | 0,08 |
| 2000 a 3000 | 0,07 | 0,07 |
| 3000 a 4000 | 0,05 | 0,06 |
| 4000 a 6000 | 0,03 | 0,05 |

Pata coja: una diferencia de menos de 0,05 mm indica un buen apoyo; si no, suplementar la pata con la mayor diferencia (SKF TKSA 40, MP5363E, 2013, [PDF](https://nonprod.docs.rs-online.com/0b44/0900766b8130b8af.pdf)). La pata coja se corrige antes de alinear.

## 5. Balanceo de rotores rígidos

ISO 21940-11:2016 ([ISO](https://www.iso.org/standard/54074.html)) reemplazó a ISO 1940-1:2003. El grado de calidad G sale de que el producto e·Ω es constante ([muestra en iTeh](https://cdn.standards.iteh.ai/samples/54074/7b5d6915d7e74d65818f33e1aadf70cb/ISO-21940-11-2016.pdf)): G [mm/s] = e [µm]·Ω [rad/s]/1000, con e = U/m el desbalance específico.

- Desbalance residual admisible: Uper [g·mm] = 1000·G·m/Ω = 9549·G·m/n, con m en kg y n en rpm (IRD Balancing, *Balance Quality Requirements of Rigid Rotors*, Technical Paper 1, rev. 2009; [en SlideShare](https://www.slideshare.net/slideshow/tech-paper1balqualityreqmts/41657209)). Ejemplo publicado allí, en unidades inglesas: G 6.3, 500 lb por apoyo, 900 rpm → 21 oz·in por plano (el `demo` lo reproduce con la fórmula métrica).
- Ejemplo: rotor de ventilador de 25 kg a 1480 rpm, G 6,3 → Ω = 154,99 rad/s; e = 40,65 µm; Uper = 1016 g·mm; en dos planos, 508 g·mm cada uno, que a 200 mm del eje son 2,54 g (reparto simple para un rotor simétrico; el reparto entre planos según la geometría está en la norma).

Grados de la tabla de JIS B 0905:1992 (equivalente a la ISO 1940-1), reproducida por [Miki Pulley](https://www.mikipulley.co.jp/en/resources/selection-calculation-guide-rotating-machinery-balance-quality); verificar en la ISO 21940-11 vigente:

| Grado | Ejemplos |
|---|---|
| G 16 | Cardanes con requisitos especiales; piezas de trituradoras y de maquinaria agrícola; componentes de motores de combustión |
| G 6,3 | Equipos de plantas de proceso; tambores de centrífugas; rodillos de papeleras e imprentas; ventiladores; volantes; impulsores de bombas; piezas de máquinas herramienta y maquinaria general; inducidos medianos y grandes (altura de eje de 80 mm o más) sin requisitos especiales |
| G 2,5 | Turbinas de gas y de vapor; rotores rígidos de turbogeneradores; turbocompresores; husillos de máquinas herramienta; inducidos medianos y grandes con requisitos especiales; bombas accionadas por turbina |
| G 1 | Accionamientos de grabadores y equipos de audio; husillos de rectificadoras |
