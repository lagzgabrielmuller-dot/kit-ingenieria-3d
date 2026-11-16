# Procedimientos de taller

Leer antes de abrir un circuito frigorífico. Las presiones, los tiempos y las masas del manual del equipo mandan sobre los criterios de esta página. Lo que no se pudo confirmar con una fuente va marcado "(verificar)". Las cuentas salen de `scripts/refrigeracion.py`.

## Antes de empezar

- Identificar el refrigerante por la placa del equipo, nunca por el color del cilindro ni por la presión.
- Elementos de protección: anteojos, guantes para frío y calzado de seguridad; ventilación; matafuego a mano si el refrigerante es inflamable (A2L o A3).
- Herramientas aptas para el refrigerante y su presión: manifold, mangueras, recuperadora y bomba de vacío. Con R-32, R-290 y R-600a, además, aptas para gases inflamables (verificar el marcado del fabricante de la herramienta).
- Cortar la alimentación, bloquear, verificar ausencia de tensión y descargar los capacitores del compresor y de los ventiladores (**higiene-y-seguridad**; el motor, en **maquinas-electricas**).

## 1. Recuperación

1. Conectar manifold, recuperadora y cilindro de recuperación. El cilindro tiene que ser apto para la presión del refrigerante, estar evacuado y rotulado; nunca se mezclan refrigerantes en un mismo cilindro.
2. Recuperar primero el líquido (es más rápido) y después el vapor, hasta el vacío que indique el manual de la recuperadora (verificar el valor en ese manual).
3. Pesar el cilindro antes y después: la diferencia es la masa recuperada; anotarla.
4. No superar el 80 % de llenado o la masa máxima marcada en el cilindro (verificar en el cilindro). El motivo es la dilatación del líquido: el R-410A líquido pasa de 1059 kg/m³ a 25 °C a 907 kg/m³ a 50 °C, es decir, ocupa un 17 % más (10 % el R-134a y el R-22); un cilindro lleno de líquido revienta al calentarse.
5. El refrigerante recuperado se recicla o se entrega para su disposición según la normativa ambiental de la jurisdicción (verificar con la autoridad local). No se ventea.

## 2. Barrido con nitrógeno al soldar

- Mientras se suelda, nitrógeno seco a bajo caudal, con regulador, circulando por el caño y con una salida abierta para que no levante presión. Así no se forma cascarilla de óxido de cobre adentro, que después tapa el filtro secador, el capilar o la válvula de expansión.
- En un circuito que tuvo R-32, R-290 o R-600a: recuperar, barrer con nitrógeno hasta que el detector no marque gas y recién entonces calentar.
- Nunca oxígeno (con aceite puede explotar) ni aire comprimido (mete humedad).

## 3. Prueba de estanqueidad

1. Presurizar con nitrógeno seco a la presión de prueba que indique el fabricante, sin superar la presión máxima admisible (PS) de la placa de la unidad. Las normas de seguridad de sistemas frigoríficos (ISO 5149, EN 378) fijan los criterios de diseño y de ensayo (verificar en la norma vigente).
2. Buscar las pérdidas con espuma en uniones soldadas, conexiones flare y válvulas, o con un detector electrónico apto para el gas usado.
3. Esperar el tiempo que pida el fabricante y corregir por temperatura con la ley de los gases, en presiones absolutas y temperaturas en K: p2 = p1·T2/T1. Ejemplo: 30 bar man. a 25 °C dan (30 + 1,013)·293,15/298,15 − 1,013 = 29,48 bar man. a 20 °C, 0,52 bar menos sin ninguna pérdida (1 K cambia la presión absoluta en 1/298 = 0,34 %). Solo una caída mayor que la explicada por la temperatura indica pérdida.
4. Liberar el nitrógeno antes del vacío.

## 4. Vacío y prueba de caída

1. Bomba de vacío de dos etapas con aceite limpio, mangueras cortas y de buen diámetro; si las válvulas de servicio lo permiten, sacar los obuses acelera el vacío.
2. Vacuómetro electrónico, lo más lejos posible de la bomba: el manómetro del manifold no mide vacío fino.
3. Bajar hasta **500 micrones**: 500 µmHg = 0,5 mmHg = 66,7 Pa = 0,67 mbar (1 mmHg = 133,3224 Pa, NIST SP 811). El agua se evapora cuando la presión queda debajo de su presión de saturación a la temperatura del caño, y al evaporarse se enfría; por eso hace falta llegar bien abajo. Temperatura de saturación del agua (hielo) según la presión, con la ecuación de Hyland y Wexler (ASHRAE 2017, cap. 1, la de **secado-y-psicrometria**):

   | Presión | 500 micrones | 1000 micrones | 5000 micrones |
   |---|---|---|---|
   | Pa | 66,7 | 133,3 | 666,6 |
   | t de saturación del agua | −24,5 °C | −17,3 °C | 1,2 °C |

4. **Prueba de caída:** cerrar la válvula hacia la bomba y mirar el vacuómetro (habitual, 10 min; verificar en el manual del equipo):
   - sube un poco y se estabiliza (criterio habitual: por debajo de unos 1000 micrones; verificar): queda humedad; seguir con el vacío o barrer con nitrógeno y volver a evacuar;
   - sube sin parar hacia la presión atmosférica: hay una pérdida; volver a la prueba de estanqueidad;
   - casi no se mueve: listo para cargar.
5. El vacío se rompe con el refrigerante (o con nitrógeno si se sigue trabajando), nunca con aire.

## 5. Carga

1. **Por peso**, con balanza electrónica: la masa de la placa más la adicional por cañería. La carga "por presión" sirve solo como verificación.
2. **Mezclas de la serie 400** (R-410A, R-404A): siempre en fase líquida (cilindro con tubo buzo o invertido, según indique el cilindro). Sus componentes se evaporan distinto (fraccionamiento): el vapor del cilindro no tiene la composición de la mezcla. Los refrigerantes puros (R-134a, R-32, R-22, R-290, R-600a) pueden cargarse como vapor.
3. El líquido entra por la línea de líquido con el equipo parado, o por la succión dosificado con el compresor andando, sin mandarle golpes de líquido.
4. Hidrocarburos: las cargas son chicas (ver la placa), con balanza de buena resolución, sin fuentes de ignición cerca y con el equipo y la herramienta aptos.
5. Después de cargar: controlar SH y SC (`refrigeracion.py diagnostico`) y registrar presiones, temperaturas, corriente y masa cargada.

## 6. Carga adicional por metro de cañería

- m = (L − L0)·k: L, largo real de la cañería entre unidades (una sola vía); L0, largo cubierto por la carga de fábrica; k, en g/m, del manual (depende del refrigerante y del diámetro de la línea de líquido).
- Sin el dato, una estimación física es la línea de líquido llena: k ≈ ρl·π·di²/4. Caño de 1/4" (6,35 mm) con 0,8 mm de pared: di = 4,75 mm, 17,7 cm³/m; con R-410A líquido a 35 °C (1005 kg/m³), 17,8 g/m. `refrigeracion.py adicional --ref R-410A --largo 12 --precarga 7.5 --diametro 1/4` → 80 g. Manda el manual: algunos fabricantes también fijan un largo mínimo o piden quitar carga en cañerías cortas.

## 7. Registro

Fecha, equipo, refrigerante, masa recuperada y cargada, presiones, temperaturas, SH, SC, corriente y pérdidas encontradas. La planilla y la frecuencia de las inspecciones van en el plan de mantenimiento (**mantenimiento-industrial**).
