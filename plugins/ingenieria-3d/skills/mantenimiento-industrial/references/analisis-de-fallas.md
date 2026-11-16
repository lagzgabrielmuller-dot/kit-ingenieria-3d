# Análisis de fallas: Pareto, Ishikawa, 5 porqués y AMFE

Leer cuando haya que priorizar fallas de un registro, buscar la causa raíz de un problema o hacer un AMFE con sus escalas. El script hace el Pareto (`pareto`) y el AMFE (`amfe`) desde un CSV o un JSON; los formatos están al final.

## 1. Registro de fallas: el dato de partida

Una fila por falla, sacada de las órdenes de trabajo: fecha, equipo, causa (o modo de falla), horas de reparación activa y horas de espera. El mismo archivo sirve para el Pareto y para los indicadores (`indicadores --registro`). Ejemplo: [registro-fallas-ejemplo.csv](../plantilla/registro-fallas-ejemplo.csv).

## 2. Diagrama de Pareto

Gráfico de barras ordenadas de mayor a menor, con la línea del porcentaje acumulado, para concentrarse en las causas más importantes. Procedimiento de la ASQ ([Pareto chart](https://asq.org/quality-resources/pareto)): elegir las categorías, la medida (frecuencia, cantidad, costo o tiempo) y el período; juntar los datos; sumar por categoría; ordenar de mayor a menor (lo chico se agrupa en «otros») y agregar el eje de porcentaje con la línea acumulada que termina en 100 %.

El principio lo propuso J. M. Juran, que lo llamó así por el economista Vilfredo Pareto y acuñó los términos «pocos vitales» y «muchos útiles»: pocas causas explican la mayor parte del efecto. El 80/20 es una proporción aproximada, no exacta: en los ejemplos de Juran aparecen valores como 65, 75 u 86 % ([Juran Institute](https://www.juran.com/blog/a-guide-to-the-pareto-principle-80-20-rule-pareto-analysis/)).

- Ordenar por **horas de parada o costo**, no solo por cantidad de fallas: en el ejemplo de SKILL.md el transportador tiene una sola falla, pero es la tercera causa en horas.
- El umbral para las «vitales» (80 % por defecto en el script) es una convención: se puede cambiar con `--umbral`.

## 3. Diagrama de Ishikawa (causa y efecto, espina de pescado)

Creado por Kaoru Ishikawa. Las categorías genéricas son las 6 M ([ASQ, Fishbone](https://asq.org/quality-resources/fishbone)): materiales, máquina, método, medición, mano de obra y medio ambiente (a veces se agrega una séptima, el dinero). Pasos: escribir el efecto en la cabeza; dibujar las ramas principales; en cada una, preguntar «¿por qué pasa?» y anotar causas y subcausas; cuando se acaban las ideas, insistir en las ramas con menos causas; elegir las causas a atacar (la raíz, no el síntoma).

Ejemplo, efecto «envases con bajo nivel de llenado»:

| Rama | Causas posibles |
|---|---|
| Máquina | Junta de la válvula gastada; boquilla tapada; sensor de nivel sucio |
| Método | Juntas que se cambian solo cuando fallan; limpieza del sensor no programada |
| Materiales | Producto más espeso que el de diseño; envases fuera de medida |
| Medición | Control de peso por muestreo cada 2 h: deja pasar lotes |
| Mano de obra | Operador sin instrucción para detectar el goteo |
| Medio ambiente | Salpicaduras de producto sobre la lente del sensor |

## 4. Cinco porqués

Técnica que se atribuye a Taiichi Ohno, padre del sistema de producción de Toyota: preguntar «¿por qué?» una y otra vez, por lo general unas cinco, hasta llegar a la causa raíz. Un problema puede tener varias causas raíz y distintas personas pueden contestar distinto: para análisis más completos se usan métodos como el RCA² ([IHI, 5 Whys](https://www.ihi.org/library/tools/5-whys-finding-root-cause)).

Ejemplo (llenadora del ejemplo de SKILL.md):

1. ¿Por qué salieron envases con bajo nivel? Porque goteaba una válvula de llenado.
2. ¿Por qué goteaba? Porque la junta estaba gastada.
3. ¿Por qué estaba gastada? Porque tenía más horas de uso que su vida normal.
4. ¿Por qué no se cambió antes? Porque las juntas se cambian solo cuando fallan.
5. ¿Por qué? Porque el plan preventivo no tiene esa tarea → acción: cambio programado de juntas (fila 2 del AMFE de SKILL.md).

## 5. AMFE (análisis de modos de falla y sus efectos; en inglés FMEA)

Normas y manuales: IEC 60812:2018, *Failure modes and effects analysis (FMEA and FMECA)* ([IEC webstore](https://webstore.iec.ch/publication/26359)); manual AIAG de FMEA, 4.ª edición (2008); manual AIAG de FMEA de máquinas y equipos (*MFMEA*, 2.ª edición, junio de 2012; trae las tablas Cr1, Cr2 y Cr3 de criterios sugeridos de severidad, ocurrencia y detección, [vista previa en ANSI](https://webstore.ansi.org/preview-pages/AIAG/preview_AIAG+MFMEA-2-2012.pdf)), y el manual conjunto AIAG y VDA (junio de 2019), que reemplazó el NPR por la **prioridad de acción** (AP: alta, media o baja), que pesa primero la severidad, después la ocurrencia y al final la detección, porque el NPR fue criticado por darle demasiado peso a la detección ([QAD, 2020](https://blog.qad.com/2020/10/is-the-new-fmea-handbook-a-game-changer-for-quality)).

### Pasos

1. Definir el equipo, sus funciones y los límites del análisis (qué entra y qué no).
2. Por cada componente: modos de falla (cómo deja de cumplir la función), efectos (qué pasa en la máquina, en la producción y en las personas), causas y controles actuales (cómo se previene o se detecta hoy).
3. Calificar S (severidad del efecto), O (ocurrencia de la causa) y D (detección: qué tan probable es que el control la detecte antes de la falla), de 1 a 10.
4. NPR = S·O·D (de 1 a 1000). Ordenar de mayor a menor.
5. Acciones: primero las severidades de 9 y 10 aunque su NPR sea bajo, después los NPR más altos. Preferir las que bajan la ocurrencia (prevención) a las que solo mejoran la detección.
6. Responsable y fecha de cada acción; recalificar S', O' y D' cuando se implementa.

Guías del manual AIAG (resumidas en el material del curso de la FIU, 2012, que cita a AIAG, 2001: [capítulo 14](https://web.eng.fiu.edu/leet/TQM/chap14_2012.pdf)): un NPR bajo con severidad alta igual merece atención; bajar la severidad exige cambiar el diseño o el proceso; en procesos conviene apuntar a la prevención (bajar O) más que a la detección. No hay un umbral de NPR universal: si la empresa fija uno, se usa ese (`amfe --umbral`).

### Escalas para equipos (AMFE de máquinas)

Escala típica de MFMEA publicada por Quality-One ([MFMEA](https://quality-one.com/mfmea/)); esa página no cita una norma: confirmar con las tablas Cr1 a Cr3 del manual AIAG MFMEA (2012) o con la escala propia de la empresa, y **escribir en el informe la escala usada**.

**Severidad (S)**, por tiempo de parada o producción defectuosa:

| S | Criterio |
|---|---|
| 9 a 10 | Implicancias de seguridad o reglamentarias |
| 8 | Parada de más de 8 h, o producción defectuosa durante más de 4 h |
| 7 | Parada de 4 a 8 h, o producción defectuosa de 2 a 4 h |
| 6 | Parada de 1 a 4 h, o producción defectuosa de 1 a 2 h |
| 5 | Parada de 30 min a 1 h, o producción defectuosa hasta 1 h |
| 4 | Parada de 10 a 30 min, sin producción defectuosa |
| 3 | Parada de hasta 10 min, sin producción defectuosa |
| 2 | Parámetro del proceso fuera de especificación, se corrige durante la producción, sin parada ni defectos |
| 1 | Variación dentro de especificación, se atiende en el mantenimiento normal |

**Ocurrencia (O)**, por MTBF del modo de falla:

| O | MTBF |
|---|---|
| 1 | Más de 10 000 h |
| 2 | 6001 a 10 000 h |
| 3 | 3001 a 6000 h |
| 4 | 2001 a 3000 h |
| 5 | 1001 a 2000 h |
| 6 | 401 a 1000 h |
| 7 | 101 a 400 h |
| 8 | 11 a 100 h |
| 9 | 2 a 10 h |
| 10 | Menos de 1 h |

(La misma página agrega criterios por piezas producidas para 7 a 10, pero repite «1 falla cada 100 piezas» en 8 y 9: usar el MTBF.)

**Detección (D)**, probabilidad de que el control actual detecte la causa o el modo de falla antes de que llegue al efecto (misma escala que el AIAG para diseño; FIU, tabla 14.4):

| D | Probabilidad | D | Probabilidad |
|---|---|---|---|
| 1 | Casi segura | 6 | Baja |
| 2 | Muy alta | 7 | Muy baja |
| 3 | Alta | 8 | Remota |
| 4 | Moderadamente alta | 9 | Muy remota |
| 5 | Moderada | 10 | Incertidumbre absoluta: no hay control o no puede detectarla |

En el AMFE de diseño o de proceso de productos (AIAG) las escalas son otras: S 10 y 9 son «peligroso sin aviso» y «con aviso» (seguridad o reglamentación), y la ocurrencia va por fallas cada mil piezas (FIU, tablas 14.2, 14.3, 14.6 y 14.7).

### Ejemplo: cómo se calificó la fila 2 del AMFE de SKILL.md

Válvulas de llenado, junta gastada: la reparación, con la espera, para la línea unas 2 h → S = 6. El registro tiene 3 fallas en 306 h de funcionamiento: MTBF del modo ≈ 102 h → O = 7. El control actual es una inspección visual al inicio del turno, que detecta algunos goteos → D = 5. NPR = 6·7·5 = 210. Con el cambio preventivo de juntas cada 250 h, se espera un MTBF de 2001 a 3000 h → O' = 4; con el control de nivel en la planilla, D' = 4 → NPR' = 96.

## 6. Formatos para el script

CSV separado por punto y coma (el que exporta una planilla de cálculo en castellano), coma o tabulador, con coma decimal. Columnas del AMFE (los nombres no distinguen mayúsculas ni tildes): `componente`, `modo`, `efecto`, `causa`, `control`, `S`, `O`, `D`, `accion` y, si ya hay acciones, `S2`, `O2` y `D2`. Ejemplo: [amfe-ejemplo.csv](../plantilla/amfe-ejemplo.csv).

JSON: una lista de objetos con las mismas claves, o `{"filas": [...]}`.

```
python mantenimiento.py amfe ../plantilla/amfe-ejemplo.csv --umbral 150
python mantenimiento.py pareto ../plantilla/registro-fallas-ejemplo.csv            (horas de parada por equipo y causa)
python mantenimiento.py pareto ../plantilla/registro-fallas-ejemplo.csv --contar   (cantidad de fallas)
python mantenimiento.py pareto --item "Motor=12,5" --item "Bomba=4" --unidad h
```
