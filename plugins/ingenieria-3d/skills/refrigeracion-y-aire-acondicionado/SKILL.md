---
name: refrigeracion-y-aire-acondicionado
description: "Refrigeración y aire acondicionado para mantenimiento y reparación de equipos: ciclo de compresión de vapor (diagrama p-h, caudal másico, potencia del compresor, COP, EER, relación de compresión), tablas presión-temperatura en bar y psi de R-134a, R-410A, R-32, R-22, R-600a, R-290 y R-404A, diagnóstico por presiones, sobrecalentamiento y subenfriamiento, procedimientos de taller (recuperación, nitrógeno, estanqueidad, vacío, carga por peso), carga térmica de un ambiente en W y frigorías/h, seguridad y normativa (Montreal, Kigali, etiqueta IRAM 62406). Usar cuando se trabaje con un aire acondicionado, una heladera o una cámara frigorífica, o se pregunte cuántas frigorías necesito, la tabla presión temperatura, cómo medir sobrecalentamiento o subenfriamiento, cómo cargar gas o hacer vacío, datos del R-410A o el R-134a, por qué no enfría o cuánto da el COP."
---

# Refrigeración y aire acondicionado

Un equipo de frío mueve calor del evaporador (lado de baja) al condensador (lado de alta) con un refrigerante que se evapora y se condensa. Casi todo el diagnóstico de taller sale de dos presiones y dos temperaturas de caño comparadas con la tabla de saturación. `scripts/refrigeracion.py` (Python 3.9+, solo biblioteca estándar) trae las tablas de siete refrigerantes generadas con CoolProp 8.0 y hace las cuentas en formato de memoria de cálculo (presentación en **calculos-ingenieria**). Aire húmedo: **secado-y-psicrometria**. Coeficiente U de muros y aislaciones: **transferencia-de-calor**. Motor del compresor: **maquinas-electricas**. Planes de mantenimiento: **mantenimiento-industrial**.

## Ciclo de compresión de vapor

Componentes: compresor, condensador, dispositivo de expansión (capilar, válvula de expansión termostática o electrónica) y evaporador; además filtro secador, visor de líquido y, en los equipos frío/calor, válvula inversora de cuatro vías. En el diagrama p-h: 1 salida del evaporador (vapor sobrecalentado), 2 descarga del compresor, 3 salida del condensador (líquido subenfriado), 4 entrada al evaporador (mezcla líquido-vapor, h4 = h3 porque la expansión no intercambia calor ni trabajo).

| Magnitud | Fórmula | Unidades |
|---|---|---|
| Efecto refrigerante | qe = h1 − h4 | kJ/kg |
| Caudal másico | ṁ = Q0/qe | kg/s |
| Trabajo y potencia isentrópicos | ws = h2s − h1; Ps = ṁ·ws | kJ/kg; kW |
| Potencia real del compresor | P = Ps/ηis; h2 = h1 + ws/ηis | kW |
| Calor en el condensador | Qc = ṁ·(h2 − h3) = Q0 + P | kW |
| Coeficiente de performance | COP = Q0/P | adimensional |
| EER | EER = COP·3,412 (1 W = 3,412 BTU/h) | BTU/(h·W) |
| Relación de compresión | rc = pc/pe, con presiones **absolutas** | adimensional |
| COP de Carnot (límite) | Te/(Tc − Te), en K | adimensional |
| Caudal aspirado | V = ṁ·v1 | m³/h |

SH (sobrecalentamiento) = t1 − t de rocío a la presión de evaporación; SC (subenfriamiento) = t de burbuja a la presión de condensación − t3. En las mezclas, el script toma la evaporación y la condensación como temperaturas de rocío.

### Ejemplo (es el `demo`)

Split de R-410A de 3,5 kW (12 000 BTU/h), evaporación 5 °C, condensación 45 °C, SH 5 K, SC 5 K, ηis = 0,70 (valor supuesto para el ejemplo: el real sale de la hoja del compresor).

```
python refrigeracion.py ciclo --ref R-410A --tevap 5 --tcond 45 --sh 5 --sc 5 --capacidad 3.5 --eta 0.7
```

| Resultado | Valor |
|---|---|
| Presiones | baja 9,331 bar abs = 8,32 bar man.; alta 27,261 bar abs = 26,25 bar man.; rc = 2,92 |
| Entalpías | h1 = 428,44 kJ/kg (10,0 °C); h2s = 458,54 kJ/kg (66,8 °C); h3 = h4 = 265,76 kJ/kg (39,9 °C) |
| Efecto refrigerante y caudal | qe = 162,68 kJ/kg; ṁ = 3,5/162,68 = 0,02151 kg/s = 77,5 kg/h |
| Compresor isentrópico | ws = 30,10 kJ/kg; Ps = 0,648 kW; COP = 5,41 |
| Con ηis = 0,70 | P = 0,925 kW; COP = 3,78 (EER 12,91); descarga a 76,8 °C; Qc = 4,425 kW = 3,5 + 0,925 |
| Referencias | caudal aspirado 2,24 m³/h; COP de Carnot 6,95 |

Con CoolProp 8.0 directo (sin tablas): ṁ = 0,021507 kg/s, COP isentrópico 5,406, descarga isentrópica 66,9 °C; diferencias menores que 0,1 % y 0,1 K. El COP del ciclo no es el EER de la etiqueta, que incluye ventiladores, el compresor real y las condiciones de ensayo de la norma.

El R-600a es un fluido "seco": con poco SH la compresión isentrópica termina dentro de la campana (el script lo resuelve y avisa); en heladeras se trabaja con mucho SH en la succión gracias al intercambiador con el capilar.

## Refrigerantes

`python refrigeracion.py info` imprime esta tabla.

| Refrigerante | Composición | Seguridad | PCA AR4 / AR5 | PAO | Ebullición a 1 atm | Uso típico |
|---|---|---|---|---|---|---|
| R-134a | HFC puro | A1 | 1430 / 1300 | 0 | −26,1 °C | heladeras anteriores a los hidrocarburos, aire de autos, enfriadores |
| R-410A | R-32/R-125 50/50 % en masa | A1 | 2088 / 1924 | 0 | −51,4 °C | splits y equipos centrales |
| R-32 | HFC puro | A2L | 675 / 677 | 0 | −51,7 °C | splits de fabricación reciente |
| R-22 | HCFC puro | A1 | 1810 / 1760 | 0,055 | −40,8 °C | equipos viejos (en eliminación) |
| R-600a | isobutano | A3 | ≈ 3 (verificar) | 0 | −11,7 °C | heladeras y freezers domésticos |
| R-290 | propano | A3 | ≈ 3 (verificar) | 0 | −42,1 °C | equipos comerciales compactos, portátiles, bombas de calor |
| R-404A | R-125/R-143a/R-134a 44/52/4 % en masa | A1 | 3922 / 3943 | 0 | −46,2 / −45,5 °C | cámaras frigoríficas |

Fuentes: seguridad según ISO 817 y ANSI/ASHRAE 34 (A = baja toxicidad; 1 no inflamable, 2L levemente inflamable, 3 altamente inflamable); PCA (GWP) a 100 años del IPCC AR4 (el que usa la enmienda de Kigali) y AR5, y PAO del R-22 del Protocolo de Montreal, anexo C: valores no confirmados en línea al armar la skill (verificar en la edición vigente). El PCA de las mezclas es el promedio en masa de los componentes (el demo lo recalcula). Ebullición y composiciones: CoolProp 8.0. R-410A y R-404A son mezclas zeotrópicas casi azeotrópicas: a una misma presión condensan entre la temperatura de burbuja y la de rocío (deslizamiento de unos 0,1 K en el R-410A y de 0,7 a 0,3 K en el R-404A entre −40 y 50 °C), y por eso se cargan en fase líquida.

Presión manométrica de saturación en bar (psi entre paréntesis); en las mezclas, rocío del lado de baja (−25 a 5 °C) y burbuja del lado de alta (40 y 50 °C):

| Refrigerante | −25 °C | −10 °C | 5 °C | 40 °C | 50 °C |
|---|---:|---:|---:|---:|---:|
| R-134a | 0,05 (1) | 0,99 (14) | 2,48 (36) | 9,15 (133) | 12,17 (176) |
| R-410A | 2,28 (33) | 4,71 (68) | 8,32 (121) | 23,24 (337) | 29,69 (431) |
| R-32 | 2,33 (34) | 4,81 (70) | 8,50 (123) | 23,77 (345) | 30,40 (441) |
| R-22 | 1,00 (15) | 2,53 (37) | 4,83 (70) | 14,32 (208) | 18,41 (267) |
| R-600a | −0,43 (−6) | 0,07 (1) | 0,85 (12) | 4,30 (62) | 5,84 (85) |
| R-290 | 1,02 (15) | 2,44 (35) | 4,50 (65) | 12,68 (184) | 16,12 (234) |
| R-404A | 1,46 (21) | 3,29 (48) | 6,01 (87) | 17,28 (251) | 22,09 (320) |

Tablas completas de −40 a 65 °C cada 5 °C, con burbuja y rocío, en [references/tabla-presion-temperatura.md](references/tabla-presion-temperatura.md): leerlas para trabajar con el manifold o citar un valor. Para otra temperatura o presión: `refrigeracion.py saturacion --ref R-410A --t 5` → rocío 8,32 bar man. (120,6 psi), burbuja 8,35 bar man.; `saturacion --ref R-134a --p 2` → 0,79 °C. Valores negativos: vacío.

## Diagnóstico por presiones, sobrecalentamiento y subenfriamiento

**Cómo se mide**
1. Equipo andando hasta que presiones y temperaturas se estabilicen (habitual 10 a 15 min; verificar en el manual), con filtros limpios y puertas o ventanas como en uso normal.
2. Manifold en la toma de baja (válvula de servicio de succión) y, si existe, en la de alta. Muchos splits domésticos tienen solo la toma de baja: entonces se trabaja con el SH y se carga por peso.
3. Termómetro de contacto o pinza en el caño de succión a unos centímetros de la válvula de servicio y en el caño de líquido, aislado del aire.
4. Con la tabla del refrigerante correcto: SH = t succión − t rocío(p baja); SC = t burbuja(p alta) − t líquido. La presión manométrica se pasa a absoluta sumando la atmosférica (el script lo hace; `--patm` para la altura).

**Valores orientativos** (aire acondicionado con condensador por aire; mandan la placa y el manual del equipo): con válvula de expansión SH 4 a 8 K a la salida del evaporador y SC 4 a 7 K; con capilar u orificio fijo, SH 5 a 12 K en condiciones de diseño y SC 2 a 6 K; condensación 8 a 17 K arriba del aire exterior; evaporación 14 a 22 K abajo del aire de retorno. Son rangos de uso común en el oficio, no confirmados con una fuente única (verificar con el fabricante).

| Falla | Presión de baja | Presión de alta | SH | SC | Otros indicios |
|---|---|---|---|---|---|
| Falta de refrigerante (pérdida) | baja | baja | alto | bajo | corriente baja, burbujas en el visor, aceite en la pérdida |
| Exceso de refrigerante | alta | alta | bajo | alto | corriente alta, riesgo de líquido al compresor |
| Restricción (filtro secador, capilar, válvula) | baja | normal | alto | alto | salto de temperatura o escarcha en la restricción |
| Poco aire en el evaporador (filtro, turbina) | baja | baja o normal | bajo | normal | evaporador escarchado |
| Condensador sucio o sin aire | alta | alta | normal o bajo | normal o bajo | condensación muy arriba del ambiente, corriente alta |
| Compresor ineficiente | alta | baja | normal o alto | bajo | corriente baja, alta y baja cerca |
| Aire o incondensables | normal o alta | alta | normal | alto (aparente) | parado y frío, la presión supera a la de saturación a la temperatura ambiente |

Tabla orientativa de la práctica de taller (verificar con la guía del fabricante del equipo).

```
python refrigeracion.py diagnostico --ref R-410A --pbaja 6 --palta 20 --tsuccion 15 --tliquido 33 --tamb 30 --tinterior 24
```
→ evaporación −4,0 °C (rocío) y condensación 34,2 °C (burbuja); SH = 15 − (−4,0) = 19,0 K, alto; SC = 34,2 − 33 = 1,2 K, bajo; condensación 4,2 K sobre el ambiente y evaporación 28,0 K bajo el aire interior: compatible con **falta de refrigerante**. Con `--unidad psi` las presiones van en psi; `--expansion capilar` y `--sh-objetivo` o `--sc-objetivo` cambian los rangos. La lectura orienta: se confirma con la corriente del compresor, las temperaturas del aire y la búsqueda de la pérdida.

## Procedimientos de taller

Paso a paso, criterios y cuentas en [references/procedimientos-taller.md](references/procedimientos-taller.md); leerlo antes de abrir un circuito.

- **Recuperación:** el refrigerante no se ventea; se pasa con máquina recuperadora a un cilindro de recuperación apto para esa presión, sin superar el 80 % de llenado o la masa máxima marcada (verificar en el cilindro), y se pesa.
- **Barrido con nitrógeno:** al soldar, nitrógeno seco circulando a bajo caudal para que no se forme óxido adentro de los caños (después tapa filtros y capilares).
- **Prueba de estanqueidad:** con nitrógeno seco, nunca oxígeno ni aire, a la presión que indique el fabricante sin superar la presión máxima admisible (PS) de la placa. La presión cambia con la temperatura: p2 = p1·T2/T1 en absolutas; 30 bar man. a 25 °C pasan a 29,48 bar man. a 20 °C sin ninguna pérdida.
- **Vacío:** bomba de dos etapas y vacuómetro electrónico hasta 500 micrones (500 µmHg = 66,7 Pa = 0,67 mbar; a esa presión el agua del circuito se evapora a unos −24 °C). Después, prueba de caída con la bomba aislada: si sube y se estabiliza, queda humedad; si sube sin parar, hay pérdida. Criterio habitual: no superar unos 1000 micrones en 10 min (verificar en el manual del equipo).
- **Carga:** por peso, con balanza, la masa de la placa. Las mezclas de la serie 400 (R-410A, R-404A) se cargan en fase líquida para no cambiar su composición; el líquido entra dosificado por la succión con el compresor andando o por la línea de líquido con el equipo parado.
- **Carga adicional por metro:** m = (L − L0)·k, con L0 el largo que cubre la carga de fábrica y k en g/m del manual. `refrigeracion.py adicional --ref R-410A --largo 12 --precarga 7.5 --gpm 20` → 90 g. Sin dato, `--diametro 1/4` lo estima: línea de líquido de 1/4" × 0,8 mm llena de R-410A líquido a 35 °C = 17,8 g/m (manda el fabricante).

## Carga térmica de un ambiente (método simplificado)

| Rubro | Fórmula |
|---|---|
| Paredes y techo | Q = U·A·(ΔT + ΔTsol), ΔT = te − ti; ΔTsol para superficies al sol |
| Vidrios | Q = U·A·ΔT + A·FS·I (FS factor solar del vidrio con su protección, I irradiancia en W/m²) |
| Aire exterior (infiltración y ventilación) | V = n·Vol/3600 + Vvent; Qs = ρ·V·(1006 + 1860·We)·ΔT; Ql = ρ·V·(2 501 000 + 1860·ti)·(We − Wi), ρ = 1,2 kg/m³ |
| Personas | N·(qs + ql) según la actividad |
| Iluminación y equipos | potencia instalada o en uso, en W |

Resultado en W y en frigorías/h: 1 frigoría/h = 1 kcal/h = 1,163 W; 1 TR = 12 000 BTU/h = 3,517 kW; 1 BTU/h = 0,2931 W (NIST SP 811). Las capacidades de los equipos son por hora: "3000 frigorías" significa 3000 frig/h = 3,49 kW = 11 905 BTU/h. Datos de personas, ΔTsol y el método completo en [references/carga-termica.md](references/carga-termica.md).

Ejemplo (es el `demo`, con datos supuestos): un aula de 8 m × 6 m × 3 m con 30 personas sentadas, exterior 35 °C y 40 %, interior 24 °C y 50 %; techo de chapa aislado al sol U = 0,6 W/(m²·K) en 48 m² con ΔTsol = 20 K; 36 m² de paredes exteriores con U = 1,8; 6 m² de vidrio U = 5,8, FS = 0,6 e I = 350 W/m²; una renovación por hora más 300 m³/h de ventilación; 400 W de iluminación y 300 W de equipos.

```
python refrigeracion.py carga --largo 8 --ancho 6 --alto 3 --superficie "techo;0,6;48;20" --superficie "paredes;1,8;36" --ventana "ventanas;6;5,8;0,6;350" --renovaciones 1 --aire-exterior 300 --personas 30 --actividad oficina --iluminacion 400 --equipos 300
```

Techo 893 W, paredes 713 W, vidrios 383 + 1260 W, aire exterior 1681 W sensibles + 1821 W latentes, personas 2100 + 1350 W, iluminación 400 W, equipos 300 W. Total **10 900 W = 9372 frig/h = 37 192 BTU/h = 3,10 TR**, factor de calor sensible 0,71 (227 W/m²). Se elige un equipo con esa capacidad en las condiciones de diseño, no solo la nominal.

## Seguridad

- **Inflamables:** R-290 y R-600a (A3) arden con muy poca concentración; R-32 (A2L) es levemente inflamable. Sin llamas ni chispas cerca, ventilación, recuperación antes de soldar y barrido con nitrógeno, herramientas y detectores aptos, y solo en equipos diseñados para ese gas. Los límites de carga por equipo están en IEC 60335-2-24 (heladeras) e IEC 60335-2-40 (aire acondicionado) (verificar en la edición vigente).
- **Quemaduras por frío:** el líquido que escapa hierve a −26 °C (R-134a) o a −51 °C (R-410A, R-32): guantes y anteojos, nunca aflojar una conexión con presión.
- **Presión:** R-410A y R-32 trabajan a unas 1,6 veces la presión manométrica del R-22 (23,2 contra 14,3 bar man. a 40 °C): manifold, mangueras y cilindros aptos; nunca calentar un cilindro con llama.
- **Asfixia:** los refrigerantes son más pesados que el aire y desplazan el oxígeno en sótanos y cámaras.
- **Eléctrica:** cortar, bloquear y verificar ausencia de tensión; descargar los capacitores (ver **higiene-y-seguridad**).

## Marco normativo argentino

- **Etiqueta de eficiencia energética:** IRAM 62406:2007, obligatoria para aires acondicionados split y compactos desde la Disposición 859/2008 de la Dirección Nacional de Comercio Interior; estándar mínimo clase A por la Resolución 228/2014 (organismo: verificar). Escala de A (verde, más eficiente) a G (rojo). Fuente: [argentina.gob.ar, etiquetado en eficiencia energética](https://www.argentina.gob.ar/economia/energia/eficiencia-energetica/etiquetado-en-eficiencia-energetica) y [texto de la Disposición 859/2008](https://www.argentina.gob.ar/normativa/nacional/norma-147008/texto). Los límites de EER de cada clase están en la norma (verificar).
- **Protocolo de Montreal** (sustancias que agotan la capa de ozono, como el HCFC-22): aprobado por la Ley 23.778 (verificar); los HCFC se eliminan por etapas con un remanente para servicio técnico hasta 2040 (verificar el calendario vigente).
- **Enmienda de Kigali** (reducción de los HFC, como R-134a, R-410A y R-404A, medida en toneladas de CO2 equivalente con el PCA del AR4): aprobada por la Ley 27.559 (verificar).
- Detalle, lo confirmado y lo que falta confirmar: [references/fuentes-y-verificacion.md](references/fuentes-y-verificacion.md). Higiene y seguridad en el trabajo: **higiene-y-seguridad** y **normas-tecnicas-ar**.

## Errores frecuentes

- Usar la tabla de otro refrigerante, o la presión manométrica donde va la absoluta (relación de compresión, propiedades).
- En las mezclas, calcular el SH con la temperatura de burbuja o el SC con la de rocío.
- Medir con el equipo recién arrancado, con filtros sucios o con el termómetro al aire.
- "Completar" gas por presión sin buscar la pérdida ni pesar; cargar una mezcla en fase vapor.
- Cortar el vacío al llegar a 500 micrones sin hacer la prueba de caída.
- Confundir frigorías con frigorías/h, la capacidad nominal con la de diseño o el COP del ciclo con el EER de la etiqueta.
- Olvidar la carga latente (personas y aire exterior) o la radiación por vidrios.

## Verificación

- `python refrigeracion.py demo` tiene que terminar en `DEMO OK` (48 controles): presiones de los siete refrigerantes fuera de los nodos de la tabla, el ciclo del ejemplo, un ciclo de cámara con R-404A y uno de R-600a con compresión húmeda contra CoolProp 8.0 directo, el diagnóstico, la carga térmica contra la cuenta a mano, las conversiones, el PCA de las mezclas y la carga adicional.
- Exactitud contra CoolProp: presión de saturación 0,005 %, entalpías 0,15 kJ/kg, caudal y COP 0,1 %, descarga 0,1 K, de −50 a 65 °C. Cómo se generaron las tablas: [references/fuentes-y-verificacion.md](references/fuentes-y-verificacion.md).
- En el equipo, el balance cierra: Qc = Q0 + P, y la presión con el equipo parado y frío coincide con la de saturación a la temperatura ambiente.
- Para una entrega importante, revisión independiente con **equipo-de-modelos** o **revision-tecnica**.

Uso del script: `python scripts/refrigeracion.py <comando> --help` (comandos: saturacion, tabla, diagnostico, ciclo, carga, convertir, adicional, info, demo).
