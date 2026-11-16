# Estudio de métodos y medición del trabajo

Leer antes de hacer un cursograma o un estudio de tiempos. Las cuentas las hacen los comandos `tiempos` y `muestreo` de `scripts/organizacion.py`.

Bibliografía de base:
- OIT, *Introducción al estudio del trabajo*, 4.ª ed. revisada (G. Kanawaty, comp.). Las escalas de valoración están en el cuadro 17, el muestreo del trabajo en el capítulo 19 y un ejemplo de tablas para calcular suplementos por descanso en el anexo 3.
- B. W. Niebel y A. Freivalds, *Ingeniería industrial: métodos, estándares y diseño del trabajo*, 12.ª ed., McGraw-Hill, 2009.

## Estudio de métodos

Se registra el método actual y se lo examina preguntando qué se hace, dónde, cuándo, quién y cómo, y por qué de cada respuesta. Después se idea uno mejor (eliminar, combinar, reordenar o simplificar pasos), se lo implanta y se controla que se mantenga.

| Símbolo | Nombre | Se usa cuando | Ejemplo |
|---|---|---|---|
| ○ | Operación | se modifica, arma o prepara el material | cortar, agujerear, soldar |
| ⇨ | Transporte | el material o el operario se mueve de un lugar a otro | llevar las chapas en zorra |
| □ | Inspección | se verifica calidad o cantidad | medir con calibre, contar |
| D | Espera (demora) | el material espera la próxima acción | piezas en un cajón esperando la prensa |
| ▽ | Almacenamiento | queda guardado y para sacarlo hace falta una orden | depósito de producto terminado |

Fuente: la ASME adoptó este juego de símbolos en 1947, a partir de los de Gilbreth (Wikipedia, «Flow process chart»). La OIT los presenta como símbolos del estudio de métodos (figura 16 de la 4.ª ed.).

Tipos de diagrama:
- **Cursograma sinóptico**: solo operaciones e inspecciones, con la entrada de cada material. Da la vista general del proceso.
- **Cursograma analítico**: todos los pasos con los cinco símbolos, la distancia y el tiempo, siguiendo al material, al operario o al equipo. Termina con un resumen del método actual y del propuesto.
- **Diagrama de recorrido**: el cursograma dibujado sobre el plano de la planta. Muestra las idas y vueltas y los cruces.
- **Diagrama bimanual** y **diagrama de actividades múltiples** (operario y máquina): para estudiar un puesto.

Ejemplo de cursograma analítico (datos inventados, agujereado y plegado de soportes, por lote):

| N.º | Paso | Símbolo | Distancia [m] | Tiempo [min] |
|---|---|---|---|---|
| 1 | Chapas cortadas en el depósito | ▽ | | |
| 2 | A la agujereadora en zorra | ⇨ | 15 | 2,0 |
| 3 | Esperan que se libere la máquina | D | | 4,0 |
| 4 | Agujerear | ○ | | 1,5 |
| 5 | Controlar con calibre | □ | | 1,0 |
| 6 | A la plegadora | ⇨ | 8 | 1,0 |
| 7 | Esperan la plegadora | D | | 10,0 |
| 8 | Plegar | ○ | | 2,0 |
| 9 | Al depósito de semielaborados | ⇨ | 12 | 1,5 |
| 10 | Depósito | ▽ | | |

Resumen: ○ 2, ⇨ 3, □ 1, D 2 y ▽ 2; 35 m y 23 min. Las esperas son 14 de los 23 min, así que lo primero es atacar el cuello de botella, que es la plegadora (comando `capacidad`).

## Estudio de tiempos con cronómetro

1. Elegir un operario calificado que trabaje a ritmo normal y explicarle el estudio.
2. Dividir la tarea en elementos con puntos de corte claros (un sonido o un movimiento) y separar los elementos manuales de los de máquina.
3. Cronometrar N ciclos y anotar la valoración del ritmo.
4. Tiempo normal: TN = TO·V/100.
5. Sumar los suplementos constantes y los variables de la tabla.
6. Tiempo estándar: TS = TN·(1 + S) si los suplementos son un % del tiempo normal, o TS = TN/(1 − S) si son un % de la jornada.
7. Comprobar que el número de observaciones alcanza.

Fuente de las fórmulas: Niebel y Freivalds (2009), TN = TO·C/100 y TE = TN·(1 + holgura) o TN/(1 − holgura). El formulario EGEL Plus IINDU del CENEVAL (2021, p. 8) usa TE = TN·(1 + S). La OIT llama "tiempo básico" al normal y "tiempo tipo" al estándar.

**Valoración.** La OIT compara varias escalas de valoración (cuadro 17 de la 4.ª ed.). El script usa la escala en la que 100 es el ritmo normal. El sistema Westinghouse califica habilidad, esfuerzo, condiciones y consistencia (Niebel y Freivalds, tablas 11.2 a 11.5).

**Número de observaciones.**
- n = (t·s/(k·x̄))², con t de Student para N − 1 grados de libertad. En el ejemplo 10.1 de Niebel y Freivalds, con t = 2,064, s = 0,09, x̄ = 0,30 y k = 0,05, da 153,4 → 154 observaciones. Los valores de t salen de la tabla del NIST/SEMATECH (1.3.6.7.2): al 95 %, 2,262 con 9 grados de libertad y 2,064 con 24.
- Guía rápida de General Electric según la duración del ciclo: de 200 ciclos para 0,10 min a 8 para más de 40 min (Niebel y Freivalds, tabla 10.2).

## Tabla de suplementos (OIT)

| Suplemento | Hombres [%] | Mujeres [%] |
|---|---|---|
| Constante: necesidades personales | 5 | 7 |
| Constante: fatiga básica | 4 | 4 |
| Trabajar de pie | 2 | 4 |
| Postura ligeramente incómoda | 0 | 1 |
| Postura incómoda (inclinado) | 2 | 3 |
| Postura muy incómoda (echado, estirado) | 7 | 7 |
| Iluminación un poco por debajo de lo recomendado / bastante por debajo / muy insuficiente | 0 / 2 / 5 | 0 / 2 / 5 |
| Atención: trabajo de cierta precisión / preciso o fatigoso / de gran precisión o muy fatigoso | 0 / 2 / 5 | 0 / 2 / 5 |
| Ruido continuo / intermitente y fuerte / intermitente y muy fuerte / estridente y fuerte | 0 / 2 / 5 / 5 | 0 / 2 / 5 / 5 |
| Tensión mental: proceso bastante complejo / complejo o con atención dividida / muy complejo | 1 / 4 / 8 | 1 / 4 / 8 |
| Monotonía: algo / bastante / muy monótono | 0 / 1 / 4 | 0 / 1 / 4 |
| Tedio: algo / bastante / muy aburrido | 0 / 2 / 5 | 0 / 2 / 5 (verificar: otras reproducciones de la tabla dan 0 / 1 / 2) |
| Calidad del aire, niveles I, II y III de la tabla | 0 / 5 / 5 a 15 | 0 / 5 / 5 a 15 |
| Uso de fuerza (peso levantado) | según el peso (verificar en la fuente) | |

Fuente: la tabla de la OIT está reproducida como "Holguras recomendadas por ILO" en Niebel y Freivalds (2009), tabla 11.9, y como "Sistema de suplementos", con columnas para hombres y mujeres, en el Formulario EGEL Plus IINDU del CENEVAL (2021), tabla 3. Las descripciones de cada nivel están resumidas. Los valores de la columna de mujeres, del ruido y de la calidad del aire salen del formulario del CENEVAL. Los valores por peso levantado difieren entre versiones (Niebel la da en libras), por eso no se copian (verificar en la tabla que use la cátedra).

La columna de mujeres se transcribió de una copia con el texto mal extraído: antes de usarla, confirmarla con la tabla original de la OIT (verificar).

Se suman los constantes y los variables que correspondan a cada elemento. Por ejemplo, para un trabajo de pie y preciso: 5 + 4 + 2 + 2 = 13 % (comando `tiempos --suplementos 5,4,2,2`).

## Muestreo del trabajo

1. Definir las categorías que se van a contar (máquina trabajando, parada por falta de material, en preparación, etc.).
2. Hacer un estudio piloto para estimar p.
3. Calcular N = z²·p·(1 − p)/e², con e el error absoluto y z = 1,96 al 95 %. Si se fija un error relativo k, e = k·p.
4. Programar los recorridos en momentos al azar, sorteados, a lo largo de varios turnos y días.
5. Calcular p = k/N y el intervalo p ± z·√(p·(1 − p)/N). Si p cambió mucho respecto del piloto, recalcular N.

Ejemplo: 60 paradas en 400 recorridos dan p = 15 % ± 3,5 %. Para ±3 % hacen falta 545 observaciones (`muestreo --ocurrencias 60 --total 400 --error 3`).
