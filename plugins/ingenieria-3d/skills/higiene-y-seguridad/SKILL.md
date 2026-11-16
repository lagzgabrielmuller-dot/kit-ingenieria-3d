---
name: higiene-y-seguridad
description: "Higiene y seguridad en el trabajo en Argentina para técnicos electromecánicos, con cálculo y fuente oficial: carga de fuego en kg/m² de madera equivalente, riesgo, resistencia al fuego, potencial extintor y cantidad de matafuegos según el Decreto 351/79; clases de fuego y agentes extintores; dosis de ruido, nivel equivalente, tiempo permitido y protectores auditivos; estrés térmico (TGBH) y ventilación; riesgo eléctrico (distancias y consignación); máquinas, EPP, trabajo en altura, señalización y matriz de riesgos con jerarquía de controles. Usar cuando se pregunte por higiene y seguridad, la Ley 19.587, el Decreto 351/79 o la ART, cómo calcular la carga de fuego, cuántos matafuegos poner o qué clase de fuego es, el ruido en el taller o la dosis de ruido, qué EPP usar, el riesgo eléctrico, el bloqueo y etiquetado, la señalización de seguridad o una matriz de riesgos."
---

# Higiene y seguridad en el trabajo

`scripts/seguridad.py` (Python 3.9+, solo biblioteca estándar) hace cada cuenta e imprime fórmula, reemplazo, resultado y la fuente del valor normativo, con coma decimal (presentación de la memoria en **calculos-ingenieria**). El mapa general de normas, con fechas, links y forma de citarlas, está en **normas-tecnicas-ar**; acá va lo que hace falta para calcular y decidir.

**Alcance:** orienta un trabajo práctico o un estudio previo. No reemplaza al profesional de higiene y seguridad matriculado: el servicio de higiene y seguridad lo dirige un profesional habilitado (Dec. 1338/96, art. 11), que firma las mediciones y los estudios.

## Marco legal

| Norma | Para qué se usa |
|---|---|
| [Ley 19.587](https://www.argentina.gob.ar/normativa/nacional/17612/texto) | Objetivos (art. 4), medidas y obligaciones del empleador (arts. 8 y 9) y del trabajador (art. 10) |
| [Dec. 351/79](https://www.argentina.gob.ar/normativa/nacional/32030/actualizacion) | Reglamento: Anexo I por capítulos (11 ventilación, 12 iluminación, 13 ruido, 14 eléctricas, 15 máquinas, 18 incendio, 19 EPP) y anexos técnicos ([texto en AFIP](https://biblioteca.afip.gob.ar/dcp/DEC_C_000351_1979_02_05)) |
| [Ley 24.557](https://www.argentina.gob.ar/normativa/nacional/27971/texto) | Riesgos del trabajo: ART o autoseguro (art. 3), prevención (art. 4), accidente de trabajo, in itinere y enfermedad profesional (art. 6), obligaciones de cada parte (art. 31), SRT (arts. 35 y 36) |
| Dec. 1338/96 | Servicios de medicina y de higiene y seguridad (art. 3) y quién puede dirigirlos (art. 11) |
| Dec. 911/96 | Construcción: caída a distinto nivel, barandas, señalización, matafuegos y electricidad en obra |
| Res. MTEySS 295/03 | Valores límite: ruido (Anexo V), estrés térmico, ergonomía, sustancias |
| Res. SRT 84/12, 85/12, 900/15 y 886/15 | Protocolos de iluminación, ruido, puesta a tierra y ergonomía (fechas y validez en **normas-tecnicas-ar**) |
| Res. SRT 299/11 | EPP certificados y constancia de entrega firmada por cada trabajador |
| [Res. SRT 3068/14](https://www.boletinoficial.gob.ar/detalleAviso/primera/115737/20141120) | Trabajos con tensión en instalaciones de hasta 1 kV (adopta el documento AEA 95705) |

Capítulos del Dec. 351/79 con sus artículos, artículos clave de cada norma y fuentes: [references/marco-legal.md](references/marco-legal.md). Leerlo para armar el marco normativo de un informe o para buscar en qué capítulo está un tema.

## Método

1. Delimitar el sector o el puesto y listar los peligros: incendio, ruido, calor, eléctrico, mecánico, altura.
2. Priorizar con la matriz de riesgos (`riesgo`).
3. Calcular (carga de fuego) o medir con el protocolo de la SRT que corresponda.
4. Comparar con el valor límite, citando norma y artículo, anexo o tabla.
5. Elegir controles según la jerarquía y volver a evaluar.
6. Documentar datos, fuente de cada valor, resultado y responsable (redacción con **informe-tecnico**).

## Carga de fuego y matafuegos (Dec. 351/79, Anexo VII y arts. 176 a 180)

Qf = Σ(Pi·PCi)/(18,41·S)

- Qf: carga de fuego [kg/m² de madera equivalente]; Pi: masa de cada material [kg]; PCi: poder calorífico inferior [MJ/kg]; S: superficie del sector de incendio [m²].
- 18,41 MJ/kg es la madera patrón (Anexo VII, 1.2); equivale a 4400 kcal/kg con 1 kcal = 4,184 kJ.
- Se cuentan también los materiales del edificio. Los líquidos y gases de tuberías, barriles y depósitos se reparten sobre todo el sector (Anexo VII, 1.2).
- El decreto no trae poderes caloríficos: el script usa la tabla 1.4 del RD 2267/2004 de España (comando `materiales`) y acepta un valor propio con `NOMBRE=kg:MJkg`.
- **Riesgo del sector** (Anexo VII, 1.5):
  - 1 explosivo;
  - 2 inflamable: punto de inflamación de hasta 40 °C (1.ª categoría) o de 41 a 120 °C (2.ª);
  - 3 muy combustible (madera, papel, tejidos de algodón);
  - 4 combustible (determinados plásticos, cueros, lanas);
  - 5 poco combustible; 6 incombustible; 7 refractario.
- Se toma el riesgo de la actividad predominante. En residencial, administrativo, espectáculos y cultura, los riesgos 1 y 2 no se permiten (cuadro 2.1).

| Qf [kg/m²] | Resistencia al fuego, ventilación natural (riesgo 3 / 4) | Potencial A (riesgo 3 / 4) | Potencial B (riesgo 2 / 3) |
|---|---|---|---|
| hasta 15 | F 30 / F 30 | 1 A / 1 A | 6 B / 4 B |
| 16 a 30 | F 60 / F 30 | 2 A / 1 A | 8 B / 6 B |
| 31 a 60 | F 90 / F 60 | 3 A / 2 A | 10 B / 8 B |
| 61 a 100 | F 120 / F 90 | 6 A / 4 A | 20 B / 10 B |
| más de 100 | F 180 / F 120 | se determina en cada caso | se determina en cada caso |

Fuente: Anexo VII, cuadro 2.2.1 y tablas 1 y 2. El Boletín Oficial publicó los cuadros 2.2.1 y 2.2.2 sin rotular. Se toma el 2.2.1 para ventilación natural y el 2.2.2 para mecánica, como interpreta Red Proteger (verificar en la norma vigente).

**Matafuegos:**
- Como mínimo 1 cada 200 m², con un recorrido máximo de 20 m hasta uno para fuego A y de 15 m para fuego B (art. 176).
- Con líquidos inflamables de más de 1 m² de superficie: 1 unidad B cada 0,1 m² (art. 177).
- Si hay equipos con tensión, matafuegos aptos para clase C (art. 178).
- Están prohibidos el tetracloruro de carbono y el bromuro de metilo (art. 180); cada equipo lleva tarjeta y registro de inspecciones (arts. 183 a 186).

Tablas completas (riesgos 1 a 5, ventilación mecánica, cuadro 2.1, poderes caloríficos): [references/incendio.md](references/incendio.md). Leerlas para otro riesgo, para ventilación mecánica o para citar una celda.

**Ejemplo resuelto** (lo reproduce el `demo`). Depósito de 15 m × 30 m (S = 450 m²), un solo sector, ventilación natural, riesgo 3, con 4000 kg de madera, 3000 kg de cartón y 1200 kg de polietileno:
- Q = 4000·18,41 + 3000·16,7 + 1200·42 = 73 640 + 50 100 + 50 400 = 174 140 MJ.
- Qf = 174 140/(18,41·450) = 21,02 kg/m², tramo de 16 a 30 kg/m².
- Resultado: F 60, potencial 2 A (y 6 B si puede haber fuego B) y ⌈450/200⌉ = 3 matafuegos, distribuidos para que ningún punto quede a más de 20 m de recorrido.

`python seguridad.py carga-fuego --largo 15 --ancho 30 --material madera=4000 --material carton=3000 --material polietileno=1200 --riesgo 3`

## Clases de fuego y agentes extintores

| Clase (art. 176) | Qué arde | Agentes aptos | No usar |
|---|---|---|---|
| A | Sólidos: madera, papel, telas, gomas, plásticos | Agua, espuma, polvo ABC | — |
| B | Líquidos inflamables, grasas, pinturas, ceras, gases | Polvo ABC o BC, CO₂, espuma | Chorro de agua |
| C | Materiales o equipos con corriente eléctrica | CO₂, polvo ABC o BC | Agua, espuma |
| D | Metales combustibles: magnesio, titanio, potasio, sodio | Polvo especial para metales | Agua, CO₂ |

- Las clases y sus ejemplos son del art. 176.
- Los agentes aptos y el "no usar" son los criterios de uso general; confirmarlos con la etiqueta del equipo y la IRAM 3517 (verificar en la norma vigente). La clase K (aceites de cocina) no figura en el decreto.
- **Ubicación:** a la vista, accesible y libre de obstáculos, cerca del riesgo y de las salidas.
- **Señalización:** según IRAM 10005; la altura de montaje y la chapa baliza, según la IRAM 3517 (verificar en la norma vigente).

## Ruido (Res. MTEySS 295/03, Anexo V)

- Ti = 8 h/2^((Li − 85)/3): tiempo permitido por día a Li [dBA].
- D = Σ(Ci/Ti) ≤ 1, con Ci el tiempo a Li [h]. Se cuentan las exposiciones de 80 dBA o más.
- LAeq,Te = 10·log(Σ ti·10^(Li/10)/Te) [dBA]; LAeq,8h lleva 8 h en el denominador. Pico: hasta 140 dBC sin protector.
- El criterio (85 dBA, 3 dB) está en **normas-tecnicas-ar**. La guía práctica N.º 2 de la SRT toma la fila de tabla inmediata superior cuando el nivel no figura (87 dBA → fila de 88 dBA → 4 h): `--criterio tabla`.
- **Protector auditivo**, con medición en dBA: L' = LAeq − (NRR − 7), según OSHA 29 CFR 1910.95, apéndice B (EE. UU.; la normativa argentina consultada no da un método).
- La protección auditiva es obligatoria arriba del límite (Dec. 351/79, art. 196). Antes, bajar el ruido en la fuente (Ley 19.587, art. 9 f).

**Ejemplo:** 2 h a 94 dBA, 3 h a 88 dBA y 3 h a 82 dBA.
- D = 2/1 + 3/4 + 3/16 = 2,9375 (293,8 %): supera el límite.
- LAeq,8h = 89,7 dBA; a ese nivel se permiten 2,73 h por día.
- Con un protector de NRR 25: 89,7 − 18 = 71,7 dBA.

`python seguridad.py ruido --exp 94:2 --exp 88:3 --exp 82:3 --nrr 25`

## Estrés térmico y ventilación

- **TGBH** [°C] (Res. 295/03): sin carga solar, 0,7·TBH + 0,3·TG; con carga solar, 0,7·TBH + 0,2·TG + 0,1·TBS.
- Corrección por ropa: + 3,5 °C con buzo de tela y + 5 °C con doble tela. Se compara con el límite según la carga de trabajo y el régimen trabajo-descanso.
- Ejemplo: TBH 24 °C y TG 32 °C dan 26,4 °C, que verifica para trabajo moderado al 100 % (límite 27,5 °C). Con buzo de tela da 29,9 °C, que solo verifica con 25 % de trabajo.
- **Ventilación mínima** (Dec. 351/79, art. 66): 6 personas en 60 m³ tienen 10 m³ cada una; con actividad sedentaria se toma la fila de 9 m³ (21 m³/h por persona), y el caudal mínimo es 126 m³/h.
- Tablas, mediciones y protectores: [references/ruido-calor-ventilacion.md](references/ruido-calor-ventilacion.md). Leerlo para los tiempos por nivel, los límites de TGBH o la tabla de ventilación.

## Iluminación

Mínimos legales del Dec. 351/79, Anexo IV (tablas en **normas-tecnicas-ar**); medición con el protocolo de la Res. SRT 84/12; cálculo por el método de los lúmenes con **calculos-ingenieria** o **instalaciones-electricas**.

## Riesgo eléctrico (Dec. 351/79, cap. 14 y Anexo VI)

- **Niveles** (1.1.1): muy baja tensión hasta 50 V; baja más de 50 V hasta 1000 V; media más de 1000 V hasta 33 000 V; alta más de 33 000 V.
- **Tensión de seguridad** (1.1.2): 24 V respecto a tierra en ambientes secos y húmedos.
- **Las cinco reglas de oro son la consignación** (1.1.4):
  - a) corte visible de toda fuente de tensión;
  - b) bloqueo de los aparatos de corte en posición de apertura;
  - c) verificación de ausencia de tensión;
  - d) puesta a tierra y en cortocircuito en todos los puntos por donde pueda llegar tensión;
  - e) señalización y delimitación de la zona. Bloquear no habilita a trabajar: hace falta la consignación completa (1.1.3).
- **Bloqueo y etiquetado (LOTO):** la máquina en reparación se señaliza y su interruptor se bloquea con candado; la llave la tiene quien repara (art. 109). El procedimiento en mantenimiento está en **mantenimiento-industrial**.
- **Distancias mínimas** (1.1.5, comando `distancia`): hasta 50 V, ninguna; de 50 V a 33 kV, 0,80 m (de 1 a 33 kV, 0,60 m con pantallas aislantes); 66 kV, 0,90 m; 132 kV, 1,50 m; 150 kV, 1,65 m; 220 kV, 2,10 m; 330 kV, 2,90 m; 500 kV, 3,60 m.
- **Trabajos con tensión** de hasta 1 kV: Res. SRT 3068/14. **Puesta a tierra y protecciones:** **instalaciones-electricas**; el protocolo de medición (Res. SRT 900/15), en **normas-tecnicas-ar**.

## Máquinas, trabajo en altura y EPP

- **Máquinas** (Dec. 351/79, cap. 15; aparatos para izar, cables y eslingas en **maniobra-y-transporte**):
  - seguras, y si generan riesgo, con protección (art. 103);
  - motores con parada a distancia desde un lugar seguro (art. 104);
  - transmisiones protegidas (art. 105);
  - resguardos eficaces que solo se sacan a propósito (art. 106);
  - mantenimiento con la máquina detenida cuando haga falta (art. 108);
  - bloqueo con candado (art. 109).
- **Altura:**
  - cinturón de seguridad en todo trabajo en altura con peligro de caída; prohibidos los cables metálicos como cuerda salvavidas (art. 200);
  - en obra, riesgo de caída desde 2 m (Dec. 911/96, art. 54);
  - barandas de 1 m y redes a no más de 3 m bajo el plano de trabajo (art. 52);
  - cinturón desde 2,50 m (art. 112).
- **EPP** (cap. 19):
  - de uso individual y obligatorio una vez determinada su necesidad (arts. 188 y 189);
  - casco (art. 192), protección ocular (arts. 193 a 195), auditiva (art. 196);
  - calzado con puntera de acero si hay riesgo de aplastamiento (art. 197) y guantes (art. 198);
  - protección respiratoria revisada al menos una vez por mes (art. 199);
  - certificados y con constancia de entrega firmada por cada trabajador (Res. SRT 299/11).
- Detalle de artículos, señalización y matriz: [references/electrico-maquinas-epp.md](references/electrico-maquinas-epp.md). Leerlo para citar un artículo o completar una matriz.

## Señalización y evaluación de riesgos

- **Normas de color:** el Dec. 351/79 (Anexo IV, «Color») remite a IRAM 10005, IRAM 2507 (cañerías) e IRAM-DEF D 10-54 (códigos de color).
- **Significados de uso general** (IRAM 10005; verificar en la norma vigente):
  - rojo: prohibición y equipos contra incendio;
  - amarillo: advertencia;
  - verde: condición segura y salvamento;
  - azul: obligación.

| Probabilidad | Ligeramente dañino | Dañino | Extremadamente dañino |
|---|---|---|---|
| Baja | Trivial | Tolerable | Moderado |
| Media | Tolerable | Moderado | Importante |
| Alta | Moderado | Importante | Intolerable |

- La matriz es la de 3 × 3 de «Evaluación de riesgos laborales» del INSHT de España (verificar en la fuente); la empresa o la cátedra pueden usar otra.
- La acción para cada nivel la da el comando `riesgo`; por ejemplo, con riesgo importante no se empieza el trabajo hasta reducirlo.
- **Jerarquía de controles:** eliminar, sustituir, controles de ingeniería, controles administrativos (procedimientos, señalización, capacitación) y, al final, EPP.
- Base de la jerarquía: la Ley 19.587 pide prevenir, reducir, eliminar o aislar los riesgos (art. 4 b). La guía del legajo técnico de la Provincia de Buenos Aires usa el EPP solo cuando el riesgo no se puede eliminar o reducir. El orden de cinco pasos es el de ISO 45001:2018, 8.1.2 (verificar en la norma vigente).

## Errores frecuentes

- Dividir por el poder calorífico del material en lugar de 18,41 MJ/kg, o mezclar kcal con MJ.
- Usar la superficie del edificio en lugar de la del sector de incendio, u olvidar los materiales del edificio y los líquidos almacenados.
- Bajar de tramo una carga intermedia: 15,4 kg/m² va al tramo de 16 a 30, del lado seguro.
- Creer que alcanza con el potencial extintor: también rigen el de 1 cada 200 m² y los recorridos de 20 m y 15 m.
- Agua o espuma sobre un tablero con tensión (fuego clase C).
- Promediar decibeles en forma aritmética, o mezclar minutos con horas en la dosis.
- Restar el NRR entero a una medición en dBA (va NRR − 7), o poner protectores sin intentar bajar el ruido en la fuente.
- Bloquear el interruptor y trabajar sin verificar la ausencia de tensión ni poner a tierra.
- Usar la fórmula de TGBH con sol en un local cerrado, u olvidar la corrección por ropa.
- Evaluar la probabilidad contando un control que todavía no existe.

## Verificación

1. `python seguridad.py demo` tiene que terminar en `DEMO OK`. Controla con cuentas a mano:
   - los ejemplos de arriba y la equivalencia 18,41 MJ/kg = 4400 kcal/kg;
   - los tiempos de la guía de la SRT (82 dBA → 16 h, 88 dBA → 4 h, 91 dBA → 2 h), su ejemplo 1 con el criterio de tabla (D = 1,5), la tabla de distancias del Anexo VI y las 9 celdas de la matriz.
2. Control cruzado del ruido: D ≈ 10^((LAeq,8h − 85)/10). Difieren menos de 1 %, por usar 3 dB en lugar de 3,01 dB.
3. Cada valor del informe lleva su norma y su artículo, anexo o tabla. Lo marcado "verificar" se confirma antes de entregar.
4. Para una entrega, una revisión independiente con **revision-tecnica** o **equipo-de-modelos**.

Uso del script: `python seguridad.py --help` lista los comandos `carga-fuego`, `materiales`, `ruido`, `tgbh`, `ventilacion`, `distancia`, `riesgo` y `demo`.
