# Plantillas: plan preventivo, orden de trabajo, planilla de inspección, registro de fallas y hoja de AMFE

Leer cuando haya que armar un plan de mantenimiento preventivo, una orden de trabajo o una planilla de inspección para un trabajo práctico o para la planta. Se copian en Markdown (o se pasan a una planilla de cálculo) y se completan; los ejemplos son los de la llenadora de SKILL.md, con datos inventados. Para entregarlas dentro de un informe, ver **informe-tecnico**.

## 1. Plan de mantenimiento preventivo

Encabezado: planta, línea, equipo y código, criticidad (A, B o C según las consecuencias de la falla), responsable del plan, fecha y revisión, documentos de base (manual del fabricante, AMFE, registro de fallas).

| N.º | Componente | Tarea | Tipo | Frecuencia | Fuente de la frecuencia | Quién | Parada | Duración | Materiales y repuestos | Criterio de aceptación |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Motor principal, rodamientos (abiertos, con engrasador) | Relubricar | Lubricación | tf ajustado por el método SKF, o el de la placa del motor | Catálogo SKF; manual del motor | Mantenimiento | Según el manual | 15 min | Grasa indicada por el fabricante: 12,5 g por rodamiento (Gp = 0,005·100·25 para un 6309) | Temperatura estable después de engrasar |
| 2 | Motor principal | Medir vibración en los dos cojinetes, dos direcciones radiales | Predictiva | Mensual | AMFE, fila 1 | Mantenimiento | No (en marcha) | 20 min | Vibrómetro | ISO 20816-3, grupo 2 rígido: zona A o B; ALARMA 1,8 mm/s |
| 3 | Válvulas de llenado | Cambiar juntas | Cambio programado | Cada 250 h de funcionamiento | AMFE, fila 2 | Mantenimiento | Sí, con bloqueo | 1 h | Juntas (código del fabricante) | Sin goteo en la prueba de llenado |
| 4 | Sensor de nivel | Limpiar la lente y probar con envase patrón | Autónomo | Cada cambio de turno | AMFE, fila 3 | Operador | Sí, breve | 5 min | Paño, envase patrón | Rechaza el envase patrón |
| 5 | Cadena de la estrella | Lubricar | Autónomo | Diaria | AMFE, fila 4 | Operador | Según el manual | 5 min | Lubricante indicado | Cadena sin puntos secos |
| 6 | Cadena de la estrella | Medir el estiramiento | Inspección | Mensual | AMFE, fila 4 | Mantenimiento | Sí, con bloqueo | 20 min | Cinta o calibre | Límite del fabricante de la cadena |
| 7 | Acople motor-reductor | Controlar la alineación | Inspección | Después de cada intervención en el motor o el reductor | Buena práctica | Mantenimiento | Sí, con bloqueo | 1 h | Alineador o comparadores | Guía SKF a 1480 rpm: ≤ 0,10 mm y ≤ 0,08 mm/100 mm |
| 8 | Tablero de la línea | Termografía con la línea en carga | Predictiva | La que fije el plan de la empresa | Plan de la empresa | Mantenimiento o terceros | No | 30 min | Cámara termográfica | Tabla de NETA: sin anomalías de prioridad 1 o 2 |

Cómo se arma, paso a paso:

1. **Inventario y criticidad**: lista de equipos con código y ubicación; criticidad según qué pasa si fallan (seguridad, ambiente, producción, calidad, costo).
2. **Fuentes de las tareas**: manual del fabricante (manda), modos de falla del AMFE, registro de fallas, normas (lubricación, vibraciones, seguridad).
3. **Una tarea por modo de falla**, con su tipo (por tiempo, por condición o autónomo), frecuencia en horas de funcionamiento o de calendario, quién la hace, si hace falta parar y bloquear, duración, materiales y criterio de aceptación medible.
4. **Agrupar en rutas y calendario**: por equipo y frecuencia, y aprovechar las paradas planificadas para lo que necesita la máquina detenida.
5. **Repuestos críticos en stock**: los que hoy generan espera (bajan el MDT y suben la Ao).
6. **Registrar y revisar**: una orden de trabajo por tarea; mensualmente el cumplimiento del plan, el MTBF, la disponibilidad y el OEE; con esos datos se alargan o acortan las frecuencias.

## 2. Orden de trabajo (OT)

| Campo | Contenido |
|---|---|
| N.º de OT / fecha y hora del aviso | |
| Equipo, código y ubicación | |
| Solicitante | |
| Tipo | Correctivo / preventivo / predictivo / mejora |
| Prioridad | Emergencia / urgente / programable |
| Síntoma o tarea pedida | |
| Seguridad | Bloqueo y etiquetado (sí/no); energías a aislar; permisos; elementos de protección personal |
| Hora de parada del equipo | |
| Hora de comienzo de la reparación | |
| Hora de fin de la reparación | |
| Hora de puesta en marcha y prueba | |
| Tiempo de reparación activa (TTR) y tiempo de espera | Para el registro de fallas |
| Trabajo realizado | |
| Causa encontrada (modo de falla y causa raíz) | |
| Repuestos y materiales (código, cantidad, costo) | |
| Personal y horas-hombre | |
| Entrega y recepción (firma de mantenimiento y de producción) | |
| Observaciones y acciones propuestas | |

Con las horas de la OT salen el TTR (comienzo a fin de la reparación, más la prueba) y la espera (parada a comienzo); con eso se calculan el MTTR, el MDT y la Ao.

## 3. Planilla de inspección (ruta)

Encabezado: equipo y código, frecuencia, inspector, fecha, hora, estado de la máquina (en marcha o parada y bloqueada).

| N.º | Punto | Qué controlar | Criterio | Valor medido | Bien / Mal | Observación |
|---|---|---|---|---|---|---|
| 1 | Motor, cojinete lado acople | Vibración eficaz radial, vertical y horizontal | Zona A o B de ISO 20816-3 (grupo 2 rígido: ≤ 2,8 mm/s); ALARMA 1,8 mm/s | | | |
| 2 | Motor, cojinete lado opuesto | Ídem | Ídem | | | |
| 3 | Motor | Temperatura de la carcasa y de los cojinetes | Comparar con la medición anterior y con el otro cojinete | | | |
| 4 | Motor | Ruido anormal | Sin golpes ni chirridos | | | |
| 5 | Válvulas de llenado | Goteo | Sin goteo | | | |
| 6 | Sensor de nivel | Lente limpia; rechazo del envase patrón | Rechaza el patrón | | | |
| 7 | Cadena de la estrella | Lubricación y tensión | Sin puntos secos; tensión según el manual | | | |
| 8 | Protecciones y paradas de emergencia | Colocadas y funcionando | Todas | | | |

Una medición fuera de criterio genera una OT; el valor se guarda para la tendencia.

## 4. Registro de fallas

Una fila por falla, con columnas `fecha`, `equipo`, `causa`, `reparacion_h` y `espera_h` (coma decimal, separado por punto y coma). Es la entrada de `indicadores --registro` y de `pareto`. Ejemplo: [registro-fallas-ejemplo.csv](../plantilla/registro-fallas-ejemplo.csv).

## 5. Hoja de AMFE

Encabezado: equipo, función, límites del análisis, equipo de trabajo, escala usada (con su fuente), fecha y revisión.

| N.º | Componente | Función | Modo de falla | Efecto | S | Causa | O | Control actual | D | NPR | Acción recomendada | Responsable y fecha | Acción hecha | S' | O' | D' | NPR' |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

El script lee la versión corta (sin función ni responsable) en CSV: [amfe-ejemplo.csv](../plantilla/amfe-ejemplo.csv). Escalas y método en [analisis-de-fallas.md](analisis-de-fallas.md). El procedimiento de bloqueo del equipo está en [seguridad-bloqueo.md](seguridad-bloqueo.md).
